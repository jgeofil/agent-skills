---
name: spec-first-architect
description: Scaffolds and governs Spec-First, Disposable Code repositories in Python (uv) or TypeScript (bun/vp) using a 5-layer committed dist/ topology, 3-Wave Execution Protocol, hermetic context packing, and cryptographic .spec-lock.json provenance.
---

# Spec-First Architect (`spec-first-architect`)

## 1. Core Mandate: Disposable Implementation
Treat the LLM as a deterministic compiler:
- **Permanent Source of Truth (Layers 1–3):** `contracts/`, `specs/`, and `tests/` are the sole human/agent-authored domain assets.
- **Committed Compilation Target (Layer 4):** `dist/<cell>/` holds disposable, LLM-synthesized implementation code committed to Git for zero-inference production deployment. No `src/` directory exists.
- **Operational Envelope (Layer 5):** `dist/main/` (Composition Root), `deploy/` (container manifests), and `README.md` (operational runbook) wire the cells into a deployable system.
- **The Zero-Patch Rule:** Never hand-edit or patch files inside `dist/`. All files in `dist/` are locked read-only (`chmod 0444`) and attested by `dist/<cell>/.spec-lock.json`.

---

## 2. The 5-Layer Committed `dist/` Topology
```text
project-root/
├── AGENTS.md                        # Constitutional rules & synthesis procedures
├── ARCHITECTURE.md                  # Cell DAG & 3-Wave completion tracker
├── README.md                        # Layer 5: CLI runbook, env table, deploy guide
├── contracts/                       # Layer 1 (Permanent): Schemas, Protocols, SQL DDL
│   ├── migrations/                  # Append-only SQL migrations (never synthesized)
│   ├── <cell>_contract.(py|ts)      # Pydantic v2 / Zod schemas & injected port interfaces
│   └── main_contract.(py|ts)        # Runtime configuration schema for Composition Root
├── specs/                           # Layer 2 (Permanent): Cellular behavioral invariants
│   ├── <cell>.spec.md               # Complexity bounds, failure matrix, anti-goals
│   └── main.spec.md                 # Pipeline wiring & CLI flag specification
├── tests/                           # Layer 3 (Permanent): Black-box & property verification
│   ├── contract/                    # Boundary & wire-fixture replay tests
│   └── property/                    # Hypothesis (Py) / fast-check (TS) fuzzing suites
├── dist/                            # Layer 4 (Committed Artifact): Disposable synthesized code
│   ├── <cell>/                      # Domain or Adapter cell (chmod 0444)
│   │   ├── __init__.py | index.ts
│   │   └── .spec-lock.json          # SHA-256 provenance binding Layers 1-3 to Layer 4
│   └── main/                        # Layer 5 Composition Root (--entrypoint, chmod 0444)
│       ├── __main__.py | index.ts
│       └── .spec-lock.json
├── deploy/                          # Layer 5 (Deployment Manifests)
│   ├── Dockerfile
│   └── docker-compose.yml
├── scratch/                         # Ephemeral: Git-ignored spike & hermetic context sandbox
└── scripts/
    └── regen_guard.py               # Provenance lock manager, context packer & budget gatekeeper
```

---

## 3. Quantitative Cell Boundaries

| Cell Classification | Seal Flag | Max Output Size | Max Inbound Context | Special Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Pure Domain Cell** | `seal <cell>` | 350 LOC / 4,500 tokens | 8,000 tokens | Zero I/O, zero env reads, requires property fuzzing (`@given` / `fc.assert`) |
| **I/O Adapter Cell** | `seal <cell> --adapter` | 150 LOC / 2,000 tokens | 8,000 tokens | Accepts injected DB handle or HTTP transport; zero domain logic |
| **Composition Root** | `seal main --entrypoint` | 200 LOC / 2,500 tokens | 8,000 tokens | Permitted to read `os.environ`/`process.env` and import sibling `dist/<cell>` APIs |

---

## 4. The 3-Wave Execution Protocol (Mandatory for Multi-Cell Projects)
Never attempt to generate an entire multi-cell repository in a single monolithic pass, and never halt after writing component specs. Execute and verify work strictly across three sequential waves tracked in `ARCHITECTURE.md`:

### Wave 1: Architecture DAG, Contracts & Specifications
1. Author `ARCHITECTURE.md` listing every cell (`domain`, `adapter`, `entrypoint`), its upstream contract dependencies, and a markdown completion checklist for Waves 1–3.
2. Author all Layer 1 schemas in `contracts/` (including `contracts/main_contract.*`) and Layer 2 behavioral specs in `specs/` (including `specs/main.spec.md`).
3. **Wave 1 Gate:** Run strict static type checking (`uv run pyright contracts/` or `bun x tsc --noEmit`) to verify all contracts compile cleanly before writing tests or implementations.

### Wave 2: Hermetic Cell-by-Cell Compilation
Iterate through each domain and adapter cell defined in `ARCHITECTURE.md` one at a time:
1. Author black-box contract tests (`tests/contract/`) and property-based fuzzing suites (`tests/property/`) for `<cell>`.
2. Execute **Procedure A (Hermetic Forward Synthesis)** using `python3 scripts/regen_guard.py prepare <cell>` followed by synthesis, test execution, and `python3 scripts/regen_guard.py seal <cell> [--adapter]`.
3. **Wave 2 Gate:** Mark `<cell>` as `[x] Sealed` in `ARCHITECTURE.md` only after `.spec-lock.json` is written and permissions are locked `0444`.

### Wave 3: Composition Root & Operational Envelope
1. Execute `python3 scripts/regen_guard.py prepare main` and synthesize `dist/main/` to wire environment configs, I/O adapters, and domain cells together with a mandatory `--dry-run` flag.
2. Seal the entrypoint via `python3 scripts/regen_guard.py seal main --entrypoint`.
3. Author `deploy/Dockerfile`, `deploy/docker-compose.yml`, and the root `README.md` runbook (architecture diagram, environment variable table, local `--dry-run` invocation, and deployment instructions).
4. **Wave 3 Gate:** Run `python3 scripts/regen_guard.py verify` and execute a `--dry-run --once` smoke test.

---

## 5. Cellular Synthesis Procedures

### Procedure A: Hermetic Forward Synthesis (`SPEC -> dist/<cell>`)
1. **Verify Upstream Layers:** Ensure `contracts/<cell>*`, `specs/<cell>.spec.md`, and `tests/**/<cell>*` are complete.
2. **Prepare Hermetic Context & Freeze Tests:**
   - Run `python3 scripts/regen_guard.py prepare <cell>`.
   - This command atomically unlocks and deletes `dist/<cell>/*` (preventing the agent from reading or anchoring on legacy code), locks the pre-synthesis upstream SHA-256 in `scratch/.freeze_<cell>.json`, verifies the 8,000-token inbound ceiling, and writes the self-contained prompt bundle to `scratch/context_<cell>.md`.
3. **Single-Pass Synthesis:**
   - Read *only* `scratch/context_<cell>.md`. Do not read other cells in `dist/`.
   - Synthesize `dist/<cell>/` in a single pass.
4. **Two-Strike Verification Loop:**
   - Run static analysis (`ruff check && pyright` or `biome check && tsc --noEmit`) and the cell test suite (`pytest` or `bun test`).
   - Maximum **2 automated repair attempts** are permitted. **Forbidden:** Modifying `tests/`, `contracts/`, or `specs/` during a repair loop (enforced by `.freeze_<cell>.json`).
   - If attempt 2 fails, run `python3 scripts/regen_guard.py unlock <cell>` to wipe the broken implementation and escalate the specification defect.
5. **Cryptographic Seal:**
   - Run `python3 scripts/regen_guard.py seal <cell> [--adapter | --entrypoint]` to verify unchanged upstream hashes, audit LOC/token budgets, write `dist/<cell>/.spec-lock.json`, and lock files to `0444`.

### Procedure B: Reverse Ratcheting (`scratch/ or Bug -> SPEC`)
1. Isolate exploratory spikes in `scratch/` (strict 45-minute timebox) or capture failing production payloads.
2. Codify discovered types in `contracts/<cell>*`, behavioral invariants in `specs/<cell>.spec.md`, and regression/property tests in `tests/**/<cell>*`.
3. Delete `scratch/*` spike code and execute **Procedure A** from Step 2 (`prepare`).

---

## Reference Documentation
- [AGENTS.md Constitution Template](references/agents-template.md): Complete repository rules and agent constraints.
- [Stateful Subsystems Guide](references/stateful-subsystems.md): Append-only migrations, in-memory twin fuzzing, and HTTP micro-adapters.
- [Composition Root Guide](references/composition-root.md): Designing `dist/main/`, `--entrypoint` authorization, container manifests, and operational runbooks.
- [Specification Template](references/spec-template.md): Tabular specifications for domain cells and composition roots.
- [Lateral Variations](references/lateral-variations.md): Tournament compilation, property-only synthesis, and mutation-locked verification.
