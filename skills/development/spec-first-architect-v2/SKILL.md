---
name: spec-first-architect-v2
description: Initialize, scaffold, and govern Spec-First, Disposable Code (Regenerative Architecture) repositories in Python (uv) or TypeScript (bun/vp). Enforces a 5-layer committed dist/ topology, 3-Wave Execution Protocol, hermetic context packing (prepare), pre-synthesis test freezing, AST/ESM transitive contract dependency hashing, topological staleness detection (stale), stateful/I/O boundary isolation, and mandatory Composition Root (dist/main/), deploy/ manifests, and operational README runbooks. Use when the user asks to initialize a spec-driven codebase, scaffold disposable code cells, extract a spec from exploratory code, audit staleness, or enforce zero-patch regeneration rules.
---

# Spec-First Architect v2 (`spec-first-architect-v2`)

Scaffold and govern software repositories using the **Spec-First, Disposable Code (Regenerative Architecture)** paradigm in Python (`uv`) or TypeScript (`bun` / `vp`). This skill shifts the authoritative source of truth to declarative contracts, behavioral specifications, and black-box verification harnesses, treating all synthesized implementation code in `dist/` as a read-only (`chmod 0444`), cryptographically locked build artifact committed to Git for deterministic zero-inference deployments.

## When to Use

- Initializing a new Python or TypeScript repository built for LLM-assisted regenerative synthesis
- Generating or auditing `AGENTS.md` and `ARCHITECTURE.md` to enforce zero-patch, delete-and-regenerate rules across multi-cell systems
- Executing the **3-Wave Execution Protocol** so multi-cell projects never halt prematurely after writing component specs
- Packing hermetic synthesis context (`regen_guard.py prepare <cell>`) and sealing synthesized implementation cells (`regen_guard.py seal <cell>`)
- Detecting transitive contract changes across Python AST and TypeScript ESM imports and computing the topological rebuild order (`regen_guard.py stale`)
- Isolating stateful subsystems (append-only SQL migrations, injected DuckDB/SQLite `:memory:` twins, and 150-LOC HTTP transport micro-adapters)
- Reverse-ratcheting an exploratory spike in `scratch/` into permanent contracts, specs, and property tests

---

## 1. The 5-Layer Committed `dist/` Repository Topology

```text
project-root/
├── AGENTS.md                        # Constitutional rules & zero-patch synthesis procedures
├── ARCHITECTURE.md                  # Cell DAG, contract ownership & 3-Wave completion tracker
├── README.md                        # Layer 5: CLI runbook, env table, IAM & deploy guide
├── contracts/                       # Layer 1 (Permanent): Schemas, Protocols, SQL DDL
│   ├── migrations/                  # Append-only SQL migrations (never synthesized)
│   ├── <cell>_contract.(py|ts)      # Pydantic v2 / Zod schemas & injected port interfaces
│   └── main_contract.(py|ts)        # Runtime configuration schema for Composition Root
├── specs/                           # Layer 2 (Permanent): Cellular behavioral invariants
│   ├── <cell>.spec.md               # Complexity bounds, failure matrix, anti-goals
│   └── main.spec.md                 # Pipeline wiring & CLI flag specification
├── tests/                           # Layer 3 (Permanent): Black-box & property verification
│   ├── contract/                    # Deterministic I/O & wire-fixture replay tests
│   ├── property/                    # Hypothesis (Py) / fast-check (TS) fuzzing suites
│   └── fixtures/                    # Recorded VCR/JSONL wire payloads from scratch/ spikes
├── dist/                            # Layer 4 (Committed Artifact): Disposable synthesized code
│   ├── <cell>/                      # Domain or Adapter cell (chmod 0444)
│   │   ├── __init__.py | index.ts
│   │   └── .spec-lock.json          # SHA-256 provenance binding Layers 1-3 to Layer 4
│   └── main/                        # Layer 5 Composition Root (--entrypoint, chmod 0444)
│       ├── __main__.py | index.ts
│       └── .spec-lock.json
├── deploy/                          # Layer 5 (Deployment Envelope)
│   ├── Dockerfile                   # Zero-inference production container
│   └── docker-compose.yml           # Resource-bounded service orchestration
├── scratch/                         # Ephemeral: Git-ignored spike & hermetic context sandbox
└── scripts/
    ├── init_spec_project.py         # Project and starter cell scaffolder
    └── regen_guard.py               # Provenance lock, context packer & DAG staleness analyzer
```

---

## 2. Quantitative Cell Classifications & Budgets

Every module in `dist/<cell>/` is classified into one of three strict roles enforced by `scripts/regen_guard.py`:

| Cell Classification | Seal Command | Max Output Size | Max Inbound Context | Purity & Coupling Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **Pure Domain Cell** (`domain`) | `seal <cell>` | 350 LOC / 4,500 tokens | 8,000 tokens | 100% pure logic. Zero I/O, zero env reads, zero cross-cell `dist/` imports. Requires `@given` (`Hypothesis`) or `fc.assert` (`fast-check`) property tests. |
| **I/O Adapter Cell** (`adapter`) | `seal <cell> --adapter` | 150 LOC / 2,000 tokens | 8,000 tokens | Quarantined I/O boundary. Accepts injected DB handle or HTTP transport port (`fetch`/`httpx`). Zero domain policy logic, zero env reads, zero sibling `dist/` imports. |
| **Composition Root** (`entrypoint`) | `seal main --entrypoint` | 200 LOC / 2,500 tokens | 8,000 tokens | Sole cell permitted to read `os.environ` / `process.env` / `Bun.env`, instantiate concrete SDK/DB handles, and wire sibling `dist/<cell>` entrypoints together. |

---

## 3. The 3-Wave Execution Protocol (Mandatory End-to-End Gate)

Never attempt to generate a multi-cell project in a single monolithic pass, and **never conclude a request after only writing component specs**. Execute and verify work strictly across three sequential waves tracked in `ARCHITECTURE.md`:

### Wave 1: Architecture DAG, Contracts & Specifications
1. Author `ARCHITECTURE.md` defining the cellular DAG, classifying every cell (`domain`, `adapter`, `entrypoint`), mapping upstream contract dependencies, and creating a Wave 1-3 completion checklist.
2. Author all Layer 1 schemas in `contracts/` (including `contracts/main_contract.*`) and Layer 2 behavioral specs in `specs/` (including `specs/main.spec.md`).
3. **Wave 1 Verification Gate:**
   - Run static type checking (`uv run pyright contracts/` or `bun x tsc --noEmit`) to prove all contracts compile cleanly.
   - Run `python3 scripts/regen_guard.py stale` to verify zero circular dependencies (`[DAG_CYCLE_ERROR]`) and inspect the topological build order.

### Wave 2: Hermetic Cell-by-Cell Compilation
Iterate through each `domain` and `adapter` cell in the exact topological order output by `python3 scripts/regen_guard.py stale --names-only`:
1. Author black-box contract tests (`tests/contract/`) and property-based fuzzing tests (`tests/property/`) for `<cell>`.
2. Run `python3 scripts/regen_guard.py prepare <cell>` to wipe `dist/<cell>/`, freeze the upstream test/contract SHA-256 hash in `scratch/.freeze_<cell>.json`, and emit the hermetic prompt bundle `scratch/context_<cell>.md`.
3. Synthesize `dist/<cell>/` in a single pass using *only* `scratch/context_<cell>.md`.
4. Run static analysis and tests (`pytest` or `bun test`). Up to **2 automated repair retries** are allowed. Modifying `tests/` or `contracts/` during a repair retry is mechanically blocked by `.freeze_<cell>.json`.
5. Seal the cell via `python3 scripts/regen_guard.py seal <cell> [--adapter]` and mark it `[x] Sealed` in `ARCHITECTURE.md`.

### Wave 3: Composition Root & Operational Envelope
1. Author `tests/contract/test_main.py` (or `main.contract.test.ts`) verifying `--dry-run --once` CLI execution.
2. Run `python3 scripts/regen_guard.py prepare main`, synthesize `dist/main/`, and seal via `python3 scripts/regen_guard.py seal main --entrypoint`.
3. Generate `deploy/Dockerfile`, `deploy/docker-compose.yml`, and the root `README.md` operational runbook (architecture diagram, environment variable table, minimum IAM permissions, `--dry-run` CLI examples, and Docker Compose deployment instructions).
4. **Wave 3 Verification Gate:** Run `python3 scripts/regen_guard.py verify` and `python3 scripts/regen_guard.py stale` (confirming `0 stale cells`) and execute a `--dry-run --once` smoke test.

---

## 4. Cascading Rebuilds & Reverse Ratcheting

### Workflow A: Cascading Rebuild After Shared Contract Edits
Whenever a shared schema in `contracts/` is updated:
1. Run `python3 scripts/regen_guard.py stale` to detect all cells whose transitive Python AST or TypeScript ESM contract dependencies changed, sorted in topological order (`domain -> adapter -> entrypoint`).
2. Rebuild and re-seal each listed cell in sequence using `prepare <cell>` -> synthesize -> test -> `seal <cell>`.

### Workflow B: Reverse Ratcheting (`scratch/` Spike or Bug -> Spec Update)
When open-ended exploration is required or a production edge case is discovered:
1. Prototype inside `scratch/spike_<topic>.(py|ts)` under a strict 45-minute timebox. Never copy code from `scratch/` into `dist/`.
2. Extract discovered schemas into `contracts/`, edge cases into `specs/<cell>.spec.md`, and regression/fuzzing assertions into `tests/`.
3. Delete `scratch/spike_*`, run `python3 scripts/regen_guard.py stale`, and execute clean-slate synthesis for all affected cells.

---

## 5. Supplementary Reference Files

Load the following markdown resource files via `skills:get_skill_resources` when executing specific workflows:

- `references/agents-template.md`: Drop-in `AGENTS.md` and `ARCHITECTURE.md` templates prescribing the 5-layer hierarchy, `.spec-lock.json` provenance rules, and the 3-Wave checklist.
- `references/spec-template.md`: Clinical tabular template for `specs/<cell>.spec.md` files.
- `references/stateful-subsystems.md`: Boundary bifurcation patterns for append-only SQL migrations, injected DuckDB/SQLite `:memory:` twin fuzzing, 150-LOC HTTP adapters, and Composition Root (`dist/main/`) wiring.
- `references/lateral-variations.md`: Decision matrix and playbooks for Property-Driven Synthesis, Shadow-Spec Extraction, Multi-Target Tournament Compilation, and Mutation-Locked Verification.
- `references/automation-scripts.md`: Complete, self-contained Python 3 source code for `scripts/regen_guard.py` (with `stale`, `prepare`, `unlock`, `seal`, and `verify`), `scripts/init_spec_project.py`, and `.githooks/pre-commit`.
