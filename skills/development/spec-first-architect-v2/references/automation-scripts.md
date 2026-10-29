# Automation Scripts Reference (`regen_guard.py`, `init_spec_project.py` & Pre-Commit Hook)

When initializing or governing a Spec-First repository, write these scripts to `scripts/regen_guard.py`, `scripts/init_spec_project.py`, and `.githooks/pre-commit`.

---

## 1. `scripts/regen_guard.py` (Full Provenance, Context Packer & Topological Staleness Engine)

```python
#!/usr/bin/env python3
"""
regen_guard.py - Hermetic Context Packer, Pre-Synthesis Test Freezer, Topological
Staleness Detector & Provenance Gatekeeper.
Supports both Python (AST) and TypeScript/ESM transitive contract dependency resolution.

Usage:
  python3 scripts/regen_guard.py stale [--json | --names-only]       # Detect stale/unsealed cells & print topological rebuild order
  python3 scripts/regen_guard.py prepare <cell>                      # Wipe dist/<cell>, freeze upstream hash, emit scratch/context_<cell>.md
  python3 scripts/regen_guard.py unlock <cell>                       # Wipe dist/<cell> & clear freeze lock
  python3 scripts/regen_guard.py seal <cell> [--adapter|--entrypoint]# Verify test-freeze, audit LOC/AST, write .spec-lock.json, chmod 0444
  python3 scripts/regen_guard.py verify                              # Pre-commit & CI provenance check across all cells
"""

from __future__ import annotations

import argparse
import ast
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys

CELL_BUDGETS = {
    "domain": {"max_loc": 350, "max_tokens": 4500},
    "adapter": {"max_loc": 150, "max_tokens": 2000},
    "entrypoint": {"max_loc": 200, "max_tokens": 2500},
}
CELL_TYPE_PRIORITY = {"domain": 0, "adapter": 1, "entrypoint": 2}
MAX_INBOUND_CONTEXT_TOKENS = 8000
CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".mts"}
TS_EXTS = {".ts", ".tsx", ".js", ".mts"}

FORBIDDEN_NON_ENTRYPOINT_PATTERNS = [
    (
        re.compile(r"\bos\.environ\b|\bos\.getenv\b|\bprocess\.env\b|\bBun\.env\b"),
        "Direct environment read outside dist/main (--entrypoint)",
    ),
    (
        re.compile(r"duckdb\.connect\s*\(\s*['\"][^:][^'\"]*['\"]"),
        "Hardcoded DuckDB path (inject connection handle)",
    ),
    (
        re.compile(r"sqlite3\.connect\s*\(\s*['\"][^:][^'\"]*['\"]"),
        "Hardcoded SQLite path (inject connection handle)",
    ),
]

PROPERTY_TEST_MARKERS = re.compile(
    r"(@given\b|from\s+hypothesis\s+import|fc\.assert\b|fc\.property\b)"
)

TS_IMPORT_RE = re.compile(
    r"""(?:import|export)\s+(?:type\s+)?(?:[\s\S]*?\s+from\s+)?['"]([^'"]+)['"]|import\s*\(\s*['"]([^'"]+)['"]\s*\)"""
)
COMMENT_STRIP_RE = re.compile(r"//.*?$|/\*[\s\S]*?\*/", re.MULTILINE)


def strip_ts_comments(text: str) -> str:
    return COMMENT_STRIP_RE.sub("", text)


def extract_ts_specifiers(text: str) -> list[str]:
    clean = strip_ts_comments(text)
    specifiers: list[str] = []
    for m in TS_IMPORT_RE.finditer(clean):
        spec = m.group(1) or m.group(2)
        if spec:
            specifiers.append(spec.strip())
    return specifiers


def resolve_ts_module_path(source_file: Path, specifier: str, repo_root: Path) -> Path | None:
    if specifier.startswith("."):
        base_cand = (source_file.parent / specifier).resolve()
    else:
        normalized = re.sub(r"^(?:@/|~/)+", "", specifier)
        if not (normalized.startswith("contracts/") or normalized.startswith("dist/")):
            return None
        base_cand = (repo_root / normalized).resolve()

    candidates: list[Path] = [base_cand]
    if base_cand.suffix in {".js", ".mjs", ".cjs"}:
        stem_path = base_cand.with_suffix("")
        candidates.extend([
            stem_path.with_suffix(".ts"),
            stem_path.with_suffix(".tsx"),
            stem_path.with_suffix(".d.ts"),
        ])
    elif not base_cand.suffix:
        candidates.extend([
            base_cand.with_suffix(".ts"),
            base_cand.with_suffix(".tsx"),
            base_cand.with_suffix(".d.ts"),
            base_cand.with_suffix(".js"),
            base_cand / "index.ts",
            base_cand / "index.d.ts",
        ])

    for cand in candidates:
        if cand.is_file():
            try:
                return cand.relative_to(repo_root)
            except ValueError:
                return None
    return None


def extract_python_imports(source_file: Path, repo_root: Path, prefix: str = "contracts") -> list[Path]:
    try:
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    found: list[Path] = []
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.ImportFrom):
            if node.module:
                if node.level > 0 and prefix in source_file.parts:
                    parent = source_file.parent
                    for _ in range(node.level - 1):
                        parent = parent.parent
                    rel_mod = parent / Path(*node.module.split("."))
                    modules.append(rel_mod.as_posix().replace("/", "."))
                else:
                    modules.append(node.module)
                for alias in node.names:
                    modules.append(f"{node.module}.{alias.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)

        for mod in modules:
            if mod.startswith(f"{prefix}.") or mod == prefix:
                base = Path(*mod.split("."))
                for cand in (base.with_suffix(".py"), base / "__init__.py", base / "__main__.py"):
                    full = (repo_root / cand).resolve()
                    if full.is_file():
                        try:
                            found.append(full.relative_to(repo_root))
                        except ValueError:
                            pass
    return found


def resolve_transitive_contracts(seed_files: list[Path]) -> list[Path]:
    repo_root = Path.cwd().resolve()
    visited: set[Path] = set()
    discovered_contracts: set[Path] = set()
    queue: deque[Path] = deque(p for p in seed_files if p.exists())

    while queue:
        current = queue.popleft()
        if current in visited or not current.is_file():
            continue
        visited.add(current)

        new_refs: list[Path] = []
        if current.suffix == ".py":
            new_refs.extend(extract_python_imports(current, repo_root, prefix="contracts"))
        elif current.suffix in TS_EXTS:
            text = current.read_text(encoding="utf-8")
            for spec in extract_ts_specifiers(text):
                resolved = resolve_ts_module_path(current, spec, repo_root)
                if resolved is not None and resolved.parts and resolved.parts[0] == "contracts":
                    new_refs.append(resolved)

        for ref in new_refs:
            if ref not in discovered_contracts:
                discovered_contracts.add(ref)
            if ref not in visited:
                queue.append(ref)

    return sorted(discovered_contracts)


def sha256_manifest(paths: list[Path]) -> str:
    hasher = hashlib.sha256()
    for p in sorted(set(paths)):
        if p.is_file() and p.name != ".spec-lock.json" and "__pycache__" not in p.parts:
            hasher.update(p.as_posix().encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(p.read_bytes())
            hasher.update(b"\0")
    return hasher.hexdigest()


def collect_direct_upstream(cell: str) -> list[Path]:
    matched: list[Path] = []
    for root in (Path("contracts"), Path("specs"), Path("tests")):
        if root.exists():
            matched.extend(
                p for p in root.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts and (cell in p.name or cell in p.parts)
            )
    return sorted(set(matched))


def collect_upstream(cell: str, extra_seed_files: list[Path] | None = None) -> list[Path]:
    matched = collect_direct_upstream(cell)
    seeds = list(matched) + (extra_seed_files or [])
    matched.extend(resolve_transitive_contracts(seeds))
    return sorted(set(matched))


def collect_dist_code(cell_dir: Path) -> list[Path]:
    if not cell_dir.exists():
        return []
    return sorted(p for p in cell_dir.rglob("*") if p.is_file() and p.suffix in CODE_EXTS)


def set_writable(cell_dir: Path, writable: bool) -> None:
    if not cell_dir.exists():
        return
    for p in cell_dir.rglob("*"):
        if p.is_file():
            mode = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) if writable else (
                stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            )
            os.chmod(p, mode)


def discover_all_cells() -> list[str]:
    cells: set[str] = set()
    dist_root = Path("dist")
    if dist_root.exists():
        for p in dist_root.iterdir():
            if p.is_dir() and not p.name.startswith("."):
                cells.add(p.name)

    specs_root = Path("specs")
    if specs_root.exists():
        for p in specs_root.glob("*.spec.md"):
            cells.add(p.name[: -len(".spec.md")])
        for p in specs_root.iterdir():
            if p.is_dir() and not p.name.startswith("."):
                cells.add(p.name)

    contracts_root = Path("contracts")
    if contracts_root.exists():
        for p in contracts_root.iterdir():
            if p.is_dir() and p.name != "migrations" and not p.name.startswith("."):
                cells.add(p.name)
            elif p.is_file() and p.suffix in CODE_EXTS:
                stem = p.stem
                for suffix in ("_contract", ".contract"):
                    if stem.endswith(suffix):
                        cells.add(stem[: -len(suffix)])
                        break
    return sorted(cells)


def infer_cell_type(cell: str) -> str:
    lock_path = Path("dist") / cell / ".spec-lock.json"
    if lock_path.exists():
        try:
            data = json.loads(lock_path.read_text(encoding="utf-8"))
            if data.get("cell_type") in CELL_BUDGETS:
                return str(data["cell_type"])
        except Exception:
            pass
    if cell == "main":
        return "entrypoint"
    spec_path = Path("specs") / f"{cell}.spec.md"
    if spec_path.exists():
        text = spec_path.read_text(encoding="utf-8")
        if "--entrypoint" in text:
            return "entrypoint"
        if "--adapter" in text or "Adapter" in text:
            return "adapter"
    if any(k in cell for k in ("adapter", "ingestor", "actuator", "client", "store", "repo")):
        return "adapter"
    return "domain"


def map_contract_owner(contract_path: Path, all_cells: list[str]) -> str | None:
    for cell in all_cells:
        if (
            cell in contract_path.parts
            or contract_path.name.startswith(f"{cell}_contract.")
            or contract_path.name.startswith(f"{cell}.contract.")
            or contract_path.stem == cell
        ):
            return cell
    return None


def build_cell_dag(all_cells: list[str]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    repo_root = Path.cwd().resolve()
    forward: dict[str, set[str]] = {c: set() for c in all_cells}
    reverse_deps: dict[str, set[str]] = {c: set() for c in all_cells}

    for cell in all_cells:
        cell_dir = Path("dist") / cell
        dist_files = collect_dist_code(cell_dir)
        upstream_files = collect_upstream(cell, extra_seed_files=dist_files)

        for uf in upstream_files:
            if uf.parts and uf.parts[0] == "contracts":
                owner = map_contract_owner(uf, all_cells)
                if owner and owner != cell:
                    forward[owner].add(cell)
                    reverse_deps[cell].add(owner)

        for df in dist_files:
            text = df.read_text(encoding="utf-8")
            if df.suffix == ".py":
                for m in re.finditer(r"\bfrom\s+dist\.([a-zA-Z0-9_]+)\b|\bimport\s+dist\.([a-zA-Z0-9_]+)\b", text):
                    target = m.group(1) or m.group(2)
                    if target in all_cells and target != cell:
                        forward[target].add(cell)
                        reverse_deps[cell].add(target)
            elif df.suffix in TS_EXTS:
                for spec in extract_ts_specifiers(text):
                    resolved = resolve_ts_module_path(df, spec, repo_root)
                    if resolved and len(resolved.parts) >= 2 and resolved.parts[0] == "dist":
                        target = resolved.parts[1]
                        if target in all_cells and target != cell:
                            forward[target].add(cell)
                            reverse_deps[cell].add(target)

    for cell in all_cells:
        if infer_cell_type(cell) == "entrypoint":
            for other in all_cells:
                if other != cell and infer_cell_type(other) != "entrypoint":
                    forward[other].add(cell)
                    reverse_deps[cell].add(other)

    return forward, reverse_deps


def topological_sort_cells(cells_subset: set[str], forward: dict[str, set[str]]) -> tuple[list[str], list[str]]:
    in_degree: dict[str, int] = {c: 0 for c in cells_subset}
    for u in cells_subset:
        for v in forward.get(u, set()):
            if v in cells_subset:
                in_degree[v] += 1

    ready = [c for c, deg in in_degree.items() if deg == 0]
    ordered: list[str] = []

    while ready:
        ready.sort(key=lambda c: (CELL_TYPE_PRIORITY.get(infer_cell_type(c), 99), c))
        curr = ready.pop(0)
        ordered.append(curr)
        for nxt in sorted(forward.get(curr, set())):
            if nxt in in_degree:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    ready.append(nxt)

    cycles = sorted(c for c in cells_subset if c not in ordered)
    return ordered, cycles


def inspect_staleness() -> dict[str, object]:
    all_cells = discover_all_cells()
    forward, reverse_deps = build_cell_dag(all_cells)

    cell_status: dict[str, dict[str, object]] = {}
    stale_cells: set[str] = set()

    for cell in all_cells:
        c_type = infer_cell_type(cell)
        cell_dir = Path("dist") / cell
        lock_path = cell_dir / ".spec-lock.json"
        dist_files = collect_dist_code(cell_dir)
        upstream = collect_upstream(cell, extra_seed_files=dist_files)
        current_up_sha = sha256_manifest(upstream)
        current_dist_sha = sha256_manifest(dist_files)

        reasons: list[str] = []
        changed_drivers: list[str] = []

        if not lock_path.exists() or not dist_files:
            reasons.append("UNSEALED")
        else:
            try:
                lock = json.loads(lock_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                reasons.append("CORRUPT_LOCKFILE")
                lock = {}

            if lock:
                if current_dist_sha != lock.get("dist_sha256"):
                    reasons.append("DIST_TAMPERED")
                if current_up_sha != lock.get("upstream_sha256"):
                    reasons.append("UPSTREAM_CHANGED")
                    old_files = set(lock.get("upstream_files", []))
                    cur_files = {p.as_posix() for p in upstream}
                    added_or_removed = sorted(old_files ^ cur_files)
                    if added_or_removed:
                        changed_drivers.extend(added_or_removed)
                    else:
                        changed_drivers.extend(p.as_posix() for p in upstream if p.parts and p.parts[0] == "contracts")

        is_stale = len(reasons) > 0
        if is_stale:
            stale_cells.add(cell)

        seal_flag = " --entrypoint" if c_type == "entrypoint" else (" --adapter" if c_type == "adapter" else "")
        cell_status[cell] = {
            "cell": cell,
            "cell_type": c_type,
            "stale": is_stale,
            "reasons": reasons,
            "depends_on": sorted(reverse_deps.get(cell, set())),
            "upstream_files": [p.as_posix() for p in upstream],
            "changed_drivers": changed_drivers,
            "commands": [
                f"python3 scripts/regen_guard.py prepare {cell}",
                f"# Synthesize dist/{cell}/ from scratch/context_{cell}.md and run tests",
                f"python3 scripts/regen_guard.py seal {cell}{seal_flag}",
            ],
        }

    queue = deque(stale_cells)
    while queue:
        curr = queue.popleft()
        for down in forward.get(curr, set()):
            if down not in stale_cells:
                stale_cells.add(down)
                reasons_list = cell_status[down]["reasons"]  # type: ignore[index]
                assert isinstance(reasons_list, list)
                reasons_list.append(f"UPSTREAM_CELL_STALE({curr})")
                cell_status[down]["stale"] = True
                queue.append(down)

    ordered_stale, cycles = topological_sort_cells(stale_cells, forward)
    ordered_all, _ = topological_sort_cells(set(all_cells), forward)

    return {
        "stale_count": len(ordered_stale),
        "has_cycles": len(cycles) > 0,
        "cycle_cells": cycles,
        "regeneration_order": ordered_stale,
        "full_dag_order": ordered_all,
        "cells": [cell_status[c] for c in ordered_stale],
    }


def cmd_stale(as_json: bool, names_only: bool) -> int:
    report = inspect_staleness()
    if as_json:
        print(json.dumps(report, indent=2))
        return 1 if report["has_cycles"] else 0

    if report["has_cycles"]:
        print(
            f"[DAG_CYCLE_ERROR] Circular dependency detected among cells: {', '.join(report['cycle_cells'])}",  # type: ignore[arg-type]
            file=sys.stderr,
        )
        return 1

    order: list[str] = report["regeneration_order"]  # type: ignore[assignment]
    if names_only:
        if order:
            print(" ".join(order))
        return 0

    if not order:
        print("OK: 0 stale cells. All committed dist/ artifacts are synchronized with upstream contracts, specs, and tests.")
        return 0

    print(f"STALE CELLS DETECTED ({len(order)} cell(s) require regeneration in topological order):\n")
    print(f"{'Step':<6} {'Cell':<22} {'Type':<12} {'Staleness Trigger':<32} {'Upstream Dependencies'}")
    print("-" * 96)
    cells_list: list[dict[str, object]] = report["cells"]  # type: ignore[assignment]
    for idx, item in enumerate(cells_list, start=1):
        reasons_str = ", ".join(item["reasons"])  # type: ignore[arg-type]
        deps_str = ", ".join(item["depends_on"]) or "(root)"  # type: ignore[arg-type]
        print(f"{idx:<6} {str(item['cell']):<22} {str(item['cell_type']):<12} {reasons_str:<32} {deps_str}")

    print("\nRecommended Topological Regeneration Sequence:")
    for idx, item in enumerate(cells_list, start=1):
        cmds: list[str] = item["commands"]  # type: ignore[assignment]
        print(f"  # Step {idx}: {item['cell']} ({item['cell_type']})")
        print(f"  {cmds[0]} && {cmds[2]}")
    return 0


def audit_cell(
    cell: str, dist_files: list[Path], upstream_files: list[Path], cell_type: str
) -> tuple[int, int, list[str]]:
    loc = 0
    chars = 0
    errors: list[str] = []
    budget = CELL_BUDGETS[cell_type]
    repo_root = Path.cwd().resolve()

    for f in dist_files:
        text = f.read_text(encoding="utf-8")
        chars += len(text)
        loc += sum(
            1 for ln in text.splitlines()
            if ln.strip() and not ln.strip().startswith(("#", "//", "/*", "*"))
        )
        if cell_type != "entrypoint":
            for regex, reason in FORBIDDEN_NON_ENTRYPOINT_PATTERNS:
                if regex.search(text):
                    errors.append(f"{f.as_posix()}: {reason}")

            for m in re.finditer(r"\bfrom\s+dist\.([a-zA-Z0-9_]+)\b|\bimport\s+dist\.([a-zA-Z0-9_]+)\b", text):
                imported_cell = m.group(1) or m.group(2)
                if imported_cell != cell:
                    errors.append(
                        f"{f.as_posix()}: Cross-cell Python import 'dist.{imported_cell}' forbidden in {cell_type} cell. "
                        f"Wire cells inside dist/main (--entrypoint)."
                    )

            if f.suffix in TS_EXTS:
                for spec in extract_ts_specifiers(text):
                    resolved = resolve_ts_module_path(f, spec, repo_root)
                    if resolved and len(resolved.parts) >= 2 and resolved.parts[0] == "dist":
                        target_cell = resolved.parts[1]
                        if target_cell != cell:
                            errors.append(
                                f"{f.as_posix()}: Cross-cell TS import '{spec}' (-> dist/{target_cell}) forbidden in {cell_type} cell. "
                                f"Wire cells inside dist/main (--entrypoint)."
                            )

    if cell_type == "domain":
        test_files = [p for p in upstream_files if "tests" in p.parts]
        has_prop_test = any(PROPERTY_TEST_MARKERS.search(p.read_text(encoding="utf-8")) for p in test_files)
        if not has_prop_test:
            errors.append(
                f"Domain cell '{cell}' lacks property-based fuzzing markers (@given or fc.assert/fc.property) in tests/."
            )

    tokens = chars // 4
    if loc > budget["max_loc"]:
        errors.append(f"LOC ceiling breached: {loc} LOC (max {budget['max_loc']} for {cell_type}).")
    if tokens > budget["max_tokens"]:
        errors.append(f"Token budget breached: ~{tokens} tokens (max {budget['max_tokens']} for {cell_type}).")
    return loc, tokens, errors


def cmd_prepare(cell: str) -> int:
    upstream = collect_upstream(cell)
    if not upstream:
        print(f"ERROR: No upstream contracts/specs/tests found for cell '{cell}'.", file=sys.stderr)
        return 1

    cell_dir = Path("dist") / cell
    set_writable(cell_dir, True)
    if cell_dir.exists():
        shutil.rmtree(cell_dir)
    cell_dir.mkdir(parents=True, exist_ok=True)

    scratch_dir = Path("scratch")
    scratch_dir.mkdir(exist_ok=True)
    sections: list[str] = [
        f"# Hermetic Synthesis Context: `{cell}`\n",
        "Synthesize `dist/" + cell + "/` in a single pass to satisfy these exact contracts, specs, and tests.\n",
        "Do NOT modify any file in `contracts/`, `specs/`, or `tests/`.\n",
    ]
    total_chars = 0
    for p in upstream:
        content = p.read_text(encoding="utf-8")
        total_chars += len(content)
        ext = p.suffix.lstrip(".") or "text"
        sections.append(f"## File: `{p.as_posix()}`\n```{ext}\n{content}\n```\n")

    est_inbound_tokens = total_chars // 4
    if est_inbound_tokens > MAX_INBOUND_CONTEXT_TOKENS:
        print(
            f"[CONTEXT OVERFLOW] Upstream context for '{cell}' is ~{est_inbound_tokens} tokens "
            f"(max {MAX_INBOUND_CONTEXT_TOKENS}). Split the cell specification.",
            file=sys.stderr,
        )
        return 1

    context_path = scratch_dir / f"context_{cell}.md"
    context_path.write_text("\n".join(sections), encoding="utf-8")

    freeze_path = scratch_dir / f".freeze_{cell}.json"
    freeze_payload = {
        "cell": cell,
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "inbound_tokens": est_inbound_tokens,
        "upstream_sha256": sha256_manifest(upstream),
        "upstream_files": [p.as_posix() for p in upstream],
    }
    freeze_path.write_text(json.dumps(freeze_payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"[PREPARED & FROZEN] Wiped dist/{cell}/ | Bundled {len(upstream)} transitive files (~{est_inbound_tokens} tokens) "
        f"into {context_path.as_posix()}"
    )
    return 0


def cmd_unlock(cell: str) -> int:
    cell_dir = Path("dist") / cell
    set_writable(cell_dir, True)
    if cell_dir.exists():
        shutil.rmtree(cell_dir)
    cell_dir.mkdir(parents=True, exist_ok=True)
    freeze_path = Path("scratch") / f".freeze_{cell}.json"
    if freeze_path.exists():
        freeze_path.unlink()
    print(f"[UNLOCKED] Purged dist/{cell}/ and cleared test-freeze state.")
    return 0


def cmd_seal(cell: str, cell_type: str) -> int:
    cell_dir = Path("dist") / cell
    dist_files = collect_dist_code(cell_dir)
    if not dist_files:
        print(f"ERROR: No implementation files found in dist/{cell}/", file=sys.stderr)
        return 1

    upstream = collect_upstream(cell, extra_seed_files=dist_files)
    if not upstream:
        print(f"ERROR: No upstream contracts/specs/tests found for '{cell}'.", file=sys.stderr)
        return 1

    current_upstream_sha = sha256_manifest(upstream)
    freeze_path = Path("scratch") / f".freeze_{cell}.json"
    if freeze_path.exists():
        freeze_data = json.loads(freeze_path.read_text(encoding="utf-8"))
        frozen_files = [Path(p) for p in freeze_data.get("upstream_files", []) if Path(p).exists()]
        if sha256_manifest(frozen_files) != freeze_data.get("upstream_sha256"):
            print(
                f"[TEST/SPEC TAMPER DETECTED] Upstream files for '{cell}' were modified after 'prepare'.\n"
                f"Weakening tests or mutating contracts mid-synthesis is forbidden. Re-run 'prepare {cell}'.",
                file=sys.stderr,
            )
            return 1

    loc, tokens, errors = audit_cell(cell, dist_files, upstream, cell_type)
    if errors:
        for err in errors:
            print(f"[AUDIT FAILURE] {err}", file=sys.stderr)
        return 1

    set_writable(cell_dir, True)
    lock_path = cell_dir / ".spec-lock.json"
    payload = {
        "cell": cell,
        "cell_type": cell_type,
        "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": {"loc": loc, "estimated_tokens": tokens},
        "upstream_files": [p.as_posix() for p in upstream],
        "upstream_sha256": current_upstream_sha,
        "dist_sha256": sha256_manifest(dist_files),
    }
    lock_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    set_writable(cell_dir, False)

    if freeze_path.exists():
        freeze_path.unlink()
    print(f"[SEALED] dist/{cell}/ ({loc} LOC, ~{tokens} tokens, type={cell_type}) locked 0444.")
    return 0


def cmd_verify() -> int:
    dist_root = Path("dist")
    if not dist_root.exists():
        return 0

    failures: list[str] = []
    for cell_dir in sorted(p for p in dist_root.iterdir() if p.is_dir()):
        cell = cell_dir.name
        lock_path = cell_dir / ".spec-lock.json"
        if not lock_path.exists():
            failures.append(f"[{cell}] Missing dist/{cell}/.spec-lock.json.")
            continue

        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        cell_type = lock.get("cell_type", "domain")
        dist_files = collect_dist_code(cell_dir)
        upstream = collect_upstream(cell, extra_seed_files=dist_files)

        _, _, audit_errors = audit_cell(cell, dist_files, upstream, cell_type)
        failures.extend(f"[{cell}] {e}" for e in audit_errors)

        if sha256_manifest(dist_files) != lock.get("dist_sha256"):
            failures.append(f"[{cell}] TAMPER DETECTED in dist/{cell}/. Direct patching is prohibited.")
        if sha256_manifest(upstream) != lock.get("upstream_sha256"):
            failures.append(
                f"[{cell}] STALE ARTIFACT: Upstream contracts/specs/tests changed without regenerating dist/{cell}/. "
                f"Run 'python3 scripts/regen_guard.py stale' for rebuild order."
            )

    if failures:
        print("SPEC-FIRST PROVENANCE VERIFICATION FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("OK: All committed dist/ cells match upstream provenance locks and isolation rules.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Spec-First Provenance Lock & Hermetic Context Packer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_stale = sub.add_parser("stale", help="Detect stale/unsealed cells and output topological regeneration order")
    stale_group = p_stale.add_mutually_exclusive_group()
    stale_group.add_argument("--json", action="store_true", help="Emit machine-readable JSON staleness report")
    stale_group.add_argument("--names-only", action="store_true", help="Print space-separated cell names in topological order")

    p_prep = sub.add_parser("prepare")
    p_prep.add_argument("cell")

    p_un = sub.add_parser("unlock")
    p_un.add_argument("cell")

    p_se = sub.add_parser("seal")
    p_se.add_argument("cell")
    group = p_se.add_mutually_exclusive_group()
    group.add_argument("--adapter", action="store_true", help="150 LOC / 2000 token I/O adapter cell")
    group.add_argument("--entrypoint", action="store_true", help="200 LOC / 2500 token Composition Root cell")

    sub.add_parser("verify")

    args = parser.parse_args()
    if args.cmd == "stale":
        return cmd_stale(args.json, args.names_only)
    if args.cmd == "prepare":
        return cmd_prepare(args.cell)
    if args.cmd == "unlock":
        return cmd_unlock(args.cell)
    if args.cmd == "seal":
        c_type = "entrypoint" if args.entrypoint else ("adapter" if args.adapter else "domain")
        return cmd_seal(args.cell, c_type)
    return cmd_verify()


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 2. Git Pre-Commit Gatekeeper (`.githooks/pre-commit`)

Configure Git (`git config core.hooksPath .githooks` and `chmod +x .githooks/pre-commit`):

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Verify cryptographic lock consistency between (contracts + specs + tests) and dist/
python3 scripts/regen_guard.py verify

# 2. Block accidental commits of scratch spike files
if git diff --cached --name-only | grep -qE '^scratch/'; then
  echo "ERROR: Attempted to commit files in scratch/. Extract findings to specs/ and delete scratch/ files." >&2
  exit 1
fi
```
