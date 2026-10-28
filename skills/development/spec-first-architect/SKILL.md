---
name: spec-first-architect
description: Initialize, scaffold, and manage Spec-First, Disposable Code (Regenerative Architecture) projects in Python or TypeScript. Generates the 4-layer directory tree, prescriptive AGENTS.md governance rules, forward synthesis workflows (SPEC to implementation), reverse-ratcheting workflows (implementation to SPEC update), module size and token/time regeneration budgets, and lateral architectural variations. Use when the user asks to initialize a spec-driven codebase, scaffold disposable code modules, extract a spec from exploratory code, or enforce zero-patch regeneration rules.
---
# Spec-First Architect

Scaffold and govern software repositories using the Spec-First, Disposable Code (Regenerative Architecture) paradigm in Python or TypeScript. This skill shifts the authoritative source of truth to declarative contracts, behavioral specifications, and black-box verification harnesses, treating all implementation code in `src/` as a disposable build artifact that is deleted and regenerated rather than patched.

## When to Use

- Initializing a new Python or TypeScript repository built for LLM-assisted regenerative synthesis
- Generating or auditing an `AGENTS.md` file to enforce zero-patch, delete-and-regenerate rules for coding agents
- Converting a declarative specification (`specs/`) and type contract (`contracts/`) into a disposable implementation (`src/`)
- Reverse-ratcheting an exploratory spike or a patched implementation back into updated specifications and test assertions
- Enforcing quantitative module boundaries, line-of-code ceilings, and token or latency regeneration budgets
- Selecting or configuring lateral variations such as Property-Driven Synthesis, Shadow-Spec Extraction, or Tournament Compilation

## 1. The 4-Layer Repository Anatomy

Always structure Spec-First projects around four strict architectural layers plus an isolated scratchpad for bounded spikes. Physical directory separation prevents accidental mutation of contracts during implementation synthesis.

```text
project-root/
├── AGENTS.md                  # Prescriptive governance rules for coding agents
├── contracts/                 # LAYER 1 (Permanent): Strict data schemas, interfaces, error types
│   └── <module>.contract.(py|ts)
├── specs/                     # LAYER 2 (Permanent): High-density behavioral specifications
│   └── <module>.spec.md
├── tests/                     # LAYER 3 (Permanent): Black-box verification harness
│   ├── contract/              # Deterministic I/O and edge-case assertion suites
│   ├── property/              # Generative fuzzing (Hypothesis / fast-check)
│   └── benchmarks/            # Latency, throughput, and memory ceiling checks
├── src/                       # LAYER 4 (Disposable): Ephemeral synthesized implementation
│   └── <module>/              # Isolated cellular module directory (safe to rm -rf)
├── scratch/                   # EPHEMERAL SPIKES: Git-ignored sandbox for timeboxed exploration
└── scripts/
    └── audit_boundaries.py    # Automated LOC, token budget, and import boundary linter
```

### Layer Responsibilities

- **Layer 1 - Contract Layer (`contracts/` - Permanent):** Contains executable data schemas, state transition types, protocol interfaces, and explicit error taxonomies (`Pydantic` and `typing.Protocol` in Python; `Zod` and `.d.ts` interfaces in TypeScript). Zero business or control-flow logic is permitted here.
- **Layer 2 - Behavioral Spec (`specs/` - Permanent):** One clinical markdown document per module defining invariants, algorithmic complexity ceilings, failure handling matrices, permitted third-party libraries, and explicit anti-goals.
- **Layer 3 - Verification Harness (`tests/` - Permanent):** Black-box tests that import only from `contracts/` and the public entry point of `src/<module>`. Tests must never mock or inspect private internal functions of `src/`.
- **Layer 4 - Ephemeral Implementation (`src/` - Disposable):** Synthesized implementation code that wires `contracts/` together to pass `tests/`. No domain knowledge is allowed to exist solely in `src/`.

## 2. Cellular Module Boundaries and Regeneration Budgets

For deletion and regeneration to remain cheaper than debugging, every module in `src/<module>` must adhere to strict quantitative ceilings. If a module exceeds these limits, split its contract into two sub-modules before writing implementation code.

| Metric | Hard Ceiling | Target Optimum | Rationale |
| :--- | :--- | :--- | :--- |
| **Module Implementation Size** | 350 LOC | 120 - 250 LOC | Prevents context-window degradation and attention drift during synthesis |
| **Regeneration Token Budget** | 4,500 output tokens | 1,500 - 2,500 tokens | Keeps single-pass synthesis under 30 seconds and eliminates truncation |
| **Regeneration Wall-Clock Time** | 45 seconds | Under 20 seconds | Ensures wiping and regenerating is faster than manual step-through debugging |
| **Cyclomatic Complexity** | 10 per function | Under 6 per function | Reduces branching hallucinations and simplifies property-based test coverage |
| **Tactical Patch Count** | 2 consecutive patches | 0 patches (Wipe first) | Exceeding 2 patches indicates a flawed spec or broken contract abstraction |
| **Cross-Module Coupling** | 0 internal imports | Contract-only imports | Modules in `src/a` may only interact with `src/b` via `contracts/b` types |

## 3. Procedure: Forward Synthesis (SPEC to Implementation)

Execute this sequence whenever creating a new module or compiling a spec change into working code.

1. **Lock the Contract (`contracts/<module>`):** Define all input schemas, output schemas, configuration structs, and domain error types. Run static type checking (`mypy --strict` or `tsc --noEmit`) to verify the contract compiles in isolation.
2. **Author the Behavioral Spec (`specs/<module>.spec.md`):** Document state invariants, deterministic ordering rules, resource ceilings, and explicit anti-goals using the template in `references/spec-template.md`.
3. **Lock the Verification Harness (`tests/`):** Write black-box contract tests for every documented edge case and at least one property-based fuzzer test (`Hypothesis` or `fast-check`) validating the invariants across randomized inputs. Verify that the test suite fails cleanly due to missing implementation.
4. **Wipe Target Implementation Directory:** Run `rm -rf src/<module> && mkdir -p src/<module>` to guarantee zero residual state or dead files from prior iterations.
5. **Synthesize Implementation (`src/<module>`):** Generate the implementation using only `contracts/<module>`, `specs/<module>.spec.md`, and `tests/` as context.
6. **Verify and Audit Budgets:** Run the verification suite and boundary audit script. If tests fail or LOC/token ceilings are breached, do not patch `src/` more than once; refine the spec or contract and repeat from Step 4.

## 4. Procedure: Reverse Ratcheting (Implementation or Spike to SPEC Update)

Execute this sequence when open-ended exploration in `scratch/` yields a working prototype, or when a production bug / edge case is discovered in `src/<module>`.

1. **Freeze Implementation Edits:** Stop applying tactical patches to `src/<module>` or `scratch/`. Treat the existing code as a read-only specimen containing implicit domain discoveries.
2. **Extract Implicit Knowledge (Diff Discovery):** Inspect the exploratory or patched code to identify:
   - New data fields, coercions, or validation rules not present in `contracts/<module>`
   - Implicit edge cases, retry heuristics, or state guards buried in `if/else` or `try/except` blocks
   - Newly discovered external library quirks or performance bottlenecks
3. **Ratchet the Contract and Spec:** Update `contracts/<module>` with the newly discovered data constraints and append the behavioral edge cases and failure modes to `specs/<module>.spec.md`.
4. **Encode Failure Assertions in Harness:** Add deterministic regression tests and property assertions in `tests/` that specifically reproduce the discovered edge cases.
5. **Purge the Specimen:** Delete the exploratory script in `scratch/` or wipe `rm -rf src/<module>`.
6. **Clean-Slate Regeneration:** Execute Forward Synthesis (Step 5 of Workflow 3) from the updated spec and contract to prove the permanent artifacts capture 100% of the required behavior without relying on the deleted code.

## 5. Default Stack Tooling

When initializing a project, default to the latest fast, deterministic tooling for the requested language unless the user specifies otherwise:

- **TypeScript Stack:** `bun` or `vp` (Vite+) for runtime and package management, `zod` for runtime contract validation, `vitest` and `fast-check` for contract and property testing, `tsc --noEmit` for strict boundary checking.
- **Python Stack:** `uv` for environment and dependency management, `pydantic` (v2) and `typing.Protocol` for contracts, `pytest` and `hypothesis` for verification, `ruff` and `mypy --strict` for linting and static typing.

## 6. Supplementary Resources

Load the following resource files via `skills:get_skill_resources` when executing specific parts of this workflow:

- `references/agents-template.md`: Complete, drop-in `AGENTS.md` file prescribing Spec-First mechanics, forbidden agent behaviors, and regeneration protocols.
- `references/spec-template.md`: Standardized markdown template for module-level `specs/<module>.spec.md` files, including token budgets and anti-goals.
- `references/lateral-variations.md`: Architectural guide and decision matrix for Property-Driven Synthesis, Shadow-Spec Extraction, Tournament Compilation, and Mutation-Locked Verification.
- `scripts/init_spec_project.py`: Automated Python 3 CLI scaffolder that initializes a Python or TypeScript Spec-First repository with the 4-layer tree, `AGENTS.md`, boundary auditor, and starter module templates.

## Gotchas

- **Leaking Implementation Details into Tests:** Never import private helper functions from `src/<module>` into `tests/`. If a test breaks when the internal algorithm of `src/<module>` changes (while I/O behavior stays identical), the test violates black-box isolation.
- **Over-Sized Modules:** If a specification requires more than 350 lines of implementation code to satisfy, the LLM synthesis pass will begin dropping edge-case constraints. Decompose the module into smaller pipeline stages connected by explicit contract schemas.
- **Prose Inflation in Specs:** Keep `specs/<module>.spec.md` clinical and tabular. Long narrative paragraphs dilute attention; use markdown tables for state transitions, error mappings, and boundary conditions.
