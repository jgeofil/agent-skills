#!/usr/bin/env python3
"""
Scaffold a Spec-First, Disposable Code (Regenerative Architecture) repository
for Python or TypeScript, including the 5-layer committed dist/ topology,
3-Wave ARCHITECTURE.md, regen_guard.py provenance engine, and starter cell artifacts.

Usage:
    python3 init_spec_project.py --name my-service --lang py --cell core
    python3 init_spec_project.py --name my-app --lang ts --cell parser
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DIRS = [
    "contracts",
    "contracts/migrations",
    "specs",
    "tests/contract",
    "tests/property",
    "tests/benchmarks",
    "dist",
    "deploy",
    "scratch",
    "scripts",
]


def write_file(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip(), encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def install_regen_guard(root: Path) -> None:
    target = root / "scripts" / "regen_guard.py"
    sibling = Path(__file__).parent / "regen_guard.py"
    if sibling.exists():
        content = sibling.read_text(encoding="utf-8")
    else:
        raise FileNotFoundError(
            "scripts/regen_guard.py not found alongside init_spec_project.py"
        )
    write_file(target, content, mode=0o755)


def scaffold_architecture_md(root: Path, cell: str) -> None:
    content = f"""# System Architecture & 3-Wave Execution Plan

Autonomous, Spec-First Regenerative Architecture DAG for `{root.name}`.

---

## 1. Cellular Topology DAG

```mermaid
graph TD
    CR["dist/main (Composition Root)"] --> CELL["dist/{cell} (Pure Domain)"]
    CR --> ADAPT["(External Adapters / Envs)"]
```

### Cell Registry
| Cell ID | Classification | Contract Path | Specification Path | Implementation Path |
| :--- | :--- | :--- | :--- | :--- |
| `{cell}` | `domain` | `contracts/{cell}_contract.*` | `specs/{cell}.spec.md` | `dist/{cell}/` |
| `main` | `entrypoint` | `contracts/main_contract.*` | `specs/main.spec.md` | `dist/main/` |

---

## 2. 3-Wave Completion Checklist

### Wave 1: Architecture DAG, Contracts & Specifications
- [x] Initial `ARCHITECTURE.md` topology codified
- [x] `contracts/{cell}_contract.*` authored
- [x] `contracts/main_contract.*` authored
- [x] `specs/{cell}.spec.md` authored
- [x] `specs/main.spec.md` authored
- [ ] Static type check gate passed

### Wave 2: Hermetic Cell-by-Cell Compilation
- [x] `tests/property/` fuzzer for `{cell}` authored
- [x] `dist/{cell}/` synthesized and sealed (`.spec-lock.json` committed)

### Wave 3: Composition Root & Operational Envelope
- [x] `dist/main/` synthesized and sealed with `--entrypoint`
- [x] `deploy/Dockerfile` and `deploy/docker-compose.yml` authored
- [x] Root `README.md` operational runbook written
- [ ] End-to-end smoke test passed (`--dry-run --once`)
"""
    write_file(root / "ARCHITECTURE.md", content)


def scaffold_deployment(root: Path, lang: str) -> None:
    if lang == "py":
        dockerfile = """FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY contracts/ ./contracts/
COPY dist/ ./dist/

USER 1000:1000
ENTRYPOINT ["uv", "run", "python", "-m", "dist.main"]
"""
    else:
        dockerfile = """FROM oven/bun:1-slim
WORKDIR /app

COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile --production

COPY contracts/ ./contracts/
COPY dist/ ./dist/

USER 1000:1000
ENTRYPOINT ["bun", "dist/main/index.js"]
"""
    write_file(root / "deploy" / "Dockerfile", dockerfile)

    compose = f"""services:
  {root.name}:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    restart: unless-stopped
    environment:
      ENFORCEMENT_MODE: "${{ENFORCEMENT_MODE:-DRY_RUN}}"
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: "0.25"
"""
    write_file(root / "deploy" / "docker-compose.yml", compose)


def scaffold_readme(root: Path, lang: str, cell: str) -> None:
    run_cmd = (
        "uv run python -m dist.main --dry-run --once"
        if lang == "py"
        else "bun dist/main/index.js --dry-run --once"
    )
    test_cmd = "uv run pytest" if lang == "py" else "bun test"
    content = f"""# {root.name}

Spec-First, Disposable Code service with committed `dist/` provenance locks (`.spec-lock.json`).

---

## 1. Pipeline Architecture
Data flow wires through the `dist/main` Composition Root into sealed component cells:
```text
Host Environment -> dist/main (CLI/Entrypoint) -> dist/{cell}
```

---

## 2. Environment Variables
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `ENFORCEMENT_MODE` | `string` | `DRY_RUN` | Operation mode (`DRY_RUN` or `ENFORCE`) |

---

## 3. Local Verification & Runbook

### Run Tests & Verify Provenance Locks
```bash
{test_cmd}
python3 scripts/regen_guard.py verify
```

### Local Dry-Run Invocation
```bash
{run_cmd}
```

### Regenerate a Cell Cleanly
```bash
python3 scripts/regen_guard.py prepare {cell}
# Synthesize dist/{cell}/ from scratch/context_{cell}.md
{test_cmd}
python3 scripts/regen_guard.py seal {cell}
```

### Deploy
```bash
docker compose -f deploy/docker-compose.yml up -d --build
```
"""
    write_file(root / "README.md", content)


def scaffold_python(root: Path, cell: str) -> None:
    write_file(
        root / "pyproject.toml",
        f"""[project]
name = "{root.name}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.9.0"]

[project.optional-dependencies]
dev = ["pytest>=8.3.0", "hypothesis>=6.112.0", "pyright>=1.1.380", "ruff>=0.6.0"]

[tool.pyright]
include = ["contracts", "dist", "tests"]
""",
    )
    cap = cell.capitalize()
    write_file(
        root / "contracts" / f"{cell}_contract.py",
        f"""from __future__ import annotations
from typing import Protocol
from pydantic import BaseModel, ConfigDict, Field


class {cap}Input(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    values: list[float] = Field(default_factory=list)


class {cap}Output(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    count: int
    total: float


class {cap}Processor(Protocol):
    def execute(self, payload: {cap}Input) -> {cap}Output:
        ...
""",
    )

    write_file(
        root / "contracts" / "main_contract.py",
        """from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    enforcement_mode: Literal["DRY_RUN", "ENFORCE"] = "DRY_RUN"
""",
    )

    write_file(
        root / "tests" / "property" / f"test_{cell}_properties.py",
        f"""from hypothesis import given, strategies as st
from contracts.{cell}_contract import {cap}Input
from dist.{cell} import process_{cell}


@given(st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6)))
def test_{cell}_count_invariant(values: list[float]) -> None:
    payload = {cap}Input(values=values)
    result = process_{cell}(payload)
    assert result.count == len(values)
""",
    )

    write_file(
        root / "dist" / cell / "__init__.py",
        f"""from __future__ import annotations
from contracts.{cell}_contract import {cap}Input, {cap}Output


def process_{cell}(payload: {cap}Input) -> {cap}Output:
    return {cap}Output(count=len(payload.values), total=float(sum(payload.values)))
""",
    )

    write_file(
        root / "dist" / "main" / "__main__.py",
        f"""from __future__ import annotations
import argparse
import json
import os
from contracts.main_contract import RuntimeConfig
from contracts.{cell}_contract import {cap}Input
from dist.{cell} import process_{cell}


def main() -> int:
    parser = argparse.ArgumentParser(description="Runner")
    parser.add_argument("--dry-run", action="store_true", help="Audit mode")
    parser.add_argument("--once", action="store_true", help="Single run")
    args = parser.parse_args()

    mode = "DRY_RUN" if args.dry_run else os.environ.get("ENFORCEMENT_MODE", "DRY_RUN")
    cfg = RuntimeConfig(enforcement_mode=mode)  # type: ignore[arg-type]

    result = process_{cell}({cap}Input(values=[1.0, 2.0, 3.0]))
    output = {{"config": cfg.model_dump(), "result": result.model_dump()}}
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
    )

    # Seal cells using regen_guard
    guard = root / "scripts" / "regen_guard.py"
    subprocess.run([sys.executable, str(guard), "seal", cell], cwd=root, check=True)
    subprocess.run(
        [sys.executable, str(guard), "seal", "main", "--entrypoint"],
        cwd=root,
        check=True,
    )


def scaffold_typescript(root: Path, cell: str) -> None:
    write_file(
        root / "package.json",
        f"""{{
  "name": "{root.name}",
  "version": "0.1.0",
  "type": "module",
  "scripts": {{
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "verify": "python3 scripts/regen_guard.py verify"
  }},
  "dependencies": {{
    "zod": "^3.23.8"
  }},
  "devDependencies": {{
    "fast-check": "^3.22.0",
    "typescript": "^5.6.2",
    "vitest": "^2.1.1"
  }}
}}
""",
    )
    write_file(
        root / "tsconfig.json",
        """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noEmit": true
  },
  "include": ["contracts/**/*", "dist/**/*", "tests/**/*"]
}
""",
    )
    cap = cell.capitalize()
    write_file(
        root / "contracts" / f"{cell}.contract.ts",
        f"""import {{ z }} from "zod";

export const {cap}InputSchema = z.object({{
  values: z.array(z.number().finite()).readonly(),
}}).strict();

export const {cap}OutputSchema = z.object({{
  count: z.number().int().nonnegative(),
  total: z.number().finite(),
}}).strict();

export type {cap}Input = z.infer<typeof {cap}InputSchema>;
export type {cap}Output = z.infer<typeof {cap}OutputSchema>;
""",
    )

    write_file(
        root / "contracts" / "main.contract.ts",
        """import { z } from "zod";

export const RuntimeConfigSchema = z.object({
  enforcementMode: z.enum(["DRY_RUN", "ENFORCE"]).default("DRY_RUN"),
}).strict();

export type RuntimeConfig = z.infer<typeof RuntimeConfigSchema>;
""",
    )

    write_file(
        root / "tests" / "property" / f"{cell}.property.test.ts",
        f"""import {{ describe, it, expect }} from "vitest";
import fc from "fast-check";
import {{ {cap}InputSchema }} from "../../contracts/{cell}.contract";
import {{ execute{cap} }} from "../../dist/{cell}/index";

describe("{cell} property invariants", () => {{
  it("preserves exact element count across arbitrary finite number arrays", () => {{
    fc.assert(
      fc.property(fc.array(fc.double({{ noNaN: true, noDefaultInfinity: true, min: -1e6, max: 1e6 }})), (values) => {{
        const parsed = {cap}InputSchema.parse({{ values }});
        const output = execute{cap}(parsed);
        expect(output.count).toBe(values.length);
      }})
    );
  }});
}});
""",
    )

    write_file(
        root / "dist" / cell / "index.ts",
        f"""import {{ type {cap}Input, type {cap}Output, {cap}OutputSchema }} from "../../contracts/{cell}.contract";

export function execute{cap}(input: {cap}Input): {cap}Output {{
  const total = input.values.reduce((acc, v) => acc + v, 0);
  return {cap}OutputSchema.parse({{
    count: input.values.length,
    total,
  }});
}}
""",
    )

    write_file(
        root / "dist" / "main" / "index.ts",
        f"""import {{ RuntimeConfigSchema }} from "../../contracts/main.contract";
import {{ execute{cap} }} from "../{cell}/index";

export function run(): void {{
  const mode = process.argv.includes("--dry-run") ? "DRY_RUN" : (process.env.ENFORCEMENT_MODE || "DRY_RUN");
  const cfg = RuntimeConfigSchema.parse({{ enforcementMode: mode }});
  const res = execute{cap}({{ values: [1, 2, 3] }});
  console.log(JSON.stringify({{ config: cfg, result: res }}, null, 2));
}}

run();
""",
    )

    # Seal cells using regen_guard
    guard = root / "scripts" / "regen_guard.py"
    subprocess.run([sys.executable, str(guard), "seal", cell], cwd=root, check=True)
    subprocess.run(
        [sys.executable, str(guard), "seal", "main", "--entrypoint"],
        cwd=root,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a Spec-First Disposable Code repository."
    )
    parser.add_argument(
        "--name", required=True, help="Target project directory name or path"
    )
    parser.add_argument(
        "--lang",
        choices=["py", "ts"],
        required=True,
        help="Primary language stack (py or ts)",
    )
    parser.add_argument(
        "--cell", default="core", help="Initial starter cell name (default: core)"
    )
    args = parser.parse_args()

    root = Path(args.name).resolve()
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)

    # Note: dist/ is committed, not ignored!
    write_file(
        root / ".gitignore",
        """scratch/*
!scratch/.gitkeep
__pycache__/
*.py[oc]
node_modules/
.venv/
.DS_Store
""",
    )
    write_file(root / "scratch" / ".gitkeep", "")

    install_regen_guard(root)

    ext = "py" if args.lang == "py" else "ts"
    write_file(
        root / "specs" / f"{args.cell}.spec.md",
        f"""# SPEC: {args.cell}

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `{args.cell}` |
| **Cell Classification** | `Pure Domain Cell` |
| **Contract Path** | `contracts/{args.cell}_contract.{ext}` |
| **Committed Artifact Path** | `dist/{args.cell}/` (Sealed via `.spec-lock.json`) |
| **Max Implementation Size** | 250 LOC (Hard Ceiling: 350 LOC) |
| **Max Inbound Context** | 8,000 Tokens |

## 2. Core Invariants
1. Output `count` must equal exact length of input `values`.
2. Input payload must remain immutable during execution.
3. No external network or disk side-effects permitted.
""",
    )
    write_file(
        root / "specs" / "main.spec.md",
        f"""# SPEC: main (Composition Root & CLI Entrypoint)

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `main` (`--entrypoint`) |
| **Contract Path** | `contracts/main_contract.{ext}` |
| **Committed Artifact Path** | `dist/main/` |
| **Max Implementation Size** | 200 LOC / 2,500 Tokens |

## 2. Pipeline Orchestration Sequence
1. Parse environment options into validated `RuntimeConfig`.
2. `--dry-run` flag forces `DRY_RUN` mode.
3. Wire and execute `dist.{args.cell}` cell.
""",
    )

    scaffold_architecture_md(root, args.cell)
    scaffold_deployment(root, args.lang)
    scaffold_readme(root, args.lang, args.cell)

    if args.lang == "py":
        scaffold_python(root, args.cell)
    else:
        scaffold_typescript(root, args.cell)

    print(f"Initialized Spec-First 5-Layer ({args.lang.upper()}) repository at: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
