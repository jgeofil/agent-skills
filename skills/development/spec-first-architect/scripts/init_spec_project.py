#!/usr/bin/env python3
"""
Scaffold a Spec-First, Disposable Code (Regenerative Architecture) repository
for Python or TypeScript, including the 4-layer directory tree, AGENTS.md,
boundary auditing script, and starter module artifacts.

Usage:
    python3 init_spec_project.py --name my-service --lang py --module example
    python3 init_spec_project.py --name my-app --lang ts --module parser
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

DIRS = [
    "contracts",
    "specs",
    "tests/contract",
    "tests/property",
    "tests/benchmarks",
    "src",
    "scratch",
    "scripts",
]

AUDIT_SCRIPT = '''#!/usr/bin/env python3
"""Audit Spec-First module size, token budget estimates, and boundary isolation."""
from __future__ import annotations
import sys
from pathlib import Path

MAX_LOC = 350
MAX_EST_TOKENS = 4500


def count_code_lines(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    return sum(
        1 for line in lines
        if line.strip() and not line.strip().startswith(("#", "//", "/*", "*"))
    )


def estimate_tokens(path: Path) -> int:
    # Clinical heuristic: ~4 characters per token for source code
    return len(path.read_text(encoding="utf-8")) // 4


def main() -> int:
    src_root = Path("src")
    if not src_root.exists():
        print("OK: src/ directory does not exist yet.")
        return 0

    violations: list[str] = []
    for mod_dir in sorted(p for p in src_root.iterdir() if p.is_dir()):
        mod_loc = 0
        mod_tokens = 0
        for code_file in mod_dir.rglob("*"):
            if code_file.suffix in {".py", ".ts", ".tsx", ".js"}:
                mod_loc += count_code_lines(code_file)
                mod_tokens += estimate_tokens(code_file)
                content = code_file.read_text(encoding="utf-8")
                for other_mod in src_root.iterdir():
                    if other_mod.is_dir() and other_mod.name != mod_dir.name:
                        if f"src.{other_mod.name}." in content or f"../{other_mod.name}/" in content:
                            violations.append(
                                f"[COUPLING] {code_file} imports directly from sibling module '{other_mod.name}'"
                            )

        print(f"Module '{mod_dir.name}': {mod_loc} LOC | ~{mod_tokens} tokens")
        if mod_loc > MAX_LOC:
            violations.append(
                f"[LOC_CEILING] Module '{mod_dir.name}' has {mod_loc} LOC (max {MAX_LOC}). Split contract."
            )
        if mod_tokens > MAX_EST_TOKENS:
            violations.append(
                f"[TOKEN_BUDGET] Module '{mod_dir.name}' estimates ~{mod_tokens} tokens (max {MAX_EST_TOKENS})."
            )

    if violations:
        print("\\nBOUNDARY VIOLATIONS DETECTED:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1

    print("\\nAll modules within Spec-First regeneration budgets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip(), encoding="utf-8")


def scaffold_python(root: Path, module: str) -> None:
    write_file(
        root / "pyproject.toml",
        f"""
[project]
name = "{root.name}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.9.0"]

[project.optional-dependencies]
dev = ["pytest>=8.3.0", "hypothesis>=6.112.0", "mypy>=1.11.0", "ruff>=0.6.0"]

[tool.mypy]
strict = true
""",
    )
    write_file(
        root / "contracts" / f"{module}_contract.py",
        f"""
from __future__ import annotations
from typing import Protocol
from pydantic import BaseModel, ConfigDict, Field


class {module.capitalize()}Input(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    values: list[float] = Field(default_factory=list)


class {module.capitalize()}Output(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    count: int
    total: float


class {module.capitalize()}Error(Exception):
    \"\"\"Base domain error emitted by {module}.\"\"\"


class {module.capitalize()}Processor(Protocol):
    def execute(self, payload: {module.capitalize()}Input) -> {module.capitalize()}Output:
        ...
""",
    )
    write_file(
        root / "tests" / "property" / f"test_{module}_properties.py",
        f"""
from hypothesis import given, strategies as st
from contracts.{module}_contract import {module.capitalize()}Input
from src.{module} import process_{module}


@given(st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6)))
def test_{module}_count_invariant(values: list[float]) -> None:
    payload = {module.capitalize()}Input(values=values)
    result = process_{module}(payload)
    assert result.count == len(values)
""",
    )
    write_file(
        root / "src" / module / "__init__.py",
        f"""
from __future__ import annotations
from contracts.{module}_contract import {module.capitalize()}Input, {module.capitalize()}Output


def process_{module}(payload: {module.capitalize()}Input) -> {module.capitalize()}Output:
    return {module.capitalize()}Output(count=len(payload.values), total= float(sum(payload.values)))
""",
    )


def scaffold_typescript(root: Path, module: str) -> None:
    write_file(
        root / "package.json",
        f"""
{{
  "name": "{root.name}",
  "version": "0.1.0",
  "type": "module",
  "scripts": {{
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "audit": "python3 scripts/audit_boundaries.py"
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
        """
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noEmit": true
  },
  "include": ["contracts/**/*", "src/**/*", "tests/**/*"]
}
""",
    )
    cap = module.capitalize()
    write_file(
        root / "contracts" / f"{module}.contract.ts",
        f"""
import {{ z }} from "zod";

export const {cap}InputSchema = z.object({{
  values: z.array(z.number().finite()).readonly(),
}}).strict();

export const {cap}OutputSchema = z.object({{
  count: z.number().int().nonnegative(),
  total: z.number().finite(),
}}).strict();

export type {cap}Input = z.infer<typeof {cap}InputSchema>;
export type {cap}Output = z.infer<typeof {cap}OutputSchema>;

export interface {cap}Service {{
  execute(input: {cap}Input): {cap}Output;
}}
""",
    )
    write_file(
        root / "tests" / "property" / f"{module}.property.test.ts",
        f"""
import {{ describe, it, expect }} from "vitest";
import fc from "fast-check";
import {{ {cap}InputSchema }} from "../../contracts/{module}.contract";
import {{ execute{cap} }} from "../../src/{module}/index";

describe("{module} property invariants", () => {{
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
        root / "src" / module / "index.ts",
        f"""
import {{ type {cap}Input, type {cap}Output, {cap}OutputSchema }} from "../../contracts/{module}.contract";

export function execute{cap}(input: {cap}Input): {cap}Output {{
  const total = input.values.reduce((acc, v) => acc + v, 0);
  return {cap}OutputSchema.parse({{
    count: input.values.length,
    total,
  }});
}}
""",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a Spec-First Disposable Code repository.")
    parser.add_argument("--name", required=True, help="Target project directory name or path")
    parser.add_argument("--lang", choices=["py", "ts"], required=True, help="Primary language stack (py or ts)")
    parser.add_argument("--module", default="core", help="Initial starter module name (default: core)")
    args = parser.parse_args()

    root = Path(args.name).resolve()
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)

    write_file(root / ".gitignore", "scratch/*\n!scratch/.gitkeep\n__pycache__/\nnode_modules/\n.venv/\ndist/\n")
    write_file(root / "scratch" / ".gitkeep", "")
    write_file(root / "scripts" / "audit_boundaries.py", AUDIT_SCRIPT)
    (root / "scripts" / "audit_boundaries.py").chmod(0o755)

    ext = "py" if args.lang == "py" else "ts"
    write_file(
        root / "specs" / f"{args.module}.spec.md",
        f"""
# SPEC: {args.module}

## 1. Module Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Module ID** | `{args.module}` |
| **Contract Path** | `contracts/{args.module}_contract.{ext}` |
| **Implementation Path** | `src/{args.module}/` |
| **Max Implementation Size** | 250 LOC (Hard Ceiling: 350 LOC) |
| **Max Regeneration Budget** | 2,500 Output Tokens / 25s Wall-Clock |

## 2. Core Invariants
1. Output `count` must equal exact length of input `values`.
2. Input payload must remain immutable during execution.
3. No external network or disk side-effects permitted.
""",
    )

    if args.lang == "py":
        scaffold_python(root, args.module)
    else:
        scaffold_typescript(root, args.module)

    print(f"Initialized Spec-First ({args.lang.upper()}) repository at: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
