# AGENTS.md & ARCHITECTURE.md Templates

Copy these templates into the root of any Spec-First repository during **Wave 1** initialization.

---

## 1. `AGENTS.md` (Project Constitution)

```markdown
# AGENTS.md - Spec-First, Disposable Code Constitution (5-Layer Edition)

This repository operates under the **Spec-First, Disposable Code (Regenerative Architecture)** paradigm. All autonomous coding agents, IDE assistants, and human contributors must follow these structural mechanics without exception.

---

## 1. Artifact Authority Hierarchy

Files in this repository are strictly partitioned into **Permanent Authoritative Sources**, **Committed Synthesized Build Artifacts**, and **Operational Deployment Envelopes**:

| Directory / File | Status | Role | Modification Policy |
| :--- | :--- | :--- | :--- |
| `contracts/` | **PERMANENT** | Strict I/O schemas, protocols, SQL migrations, and error unions | Edit deliberately; requires static type verification (`pyright` / `tsc --noEmit`) |
| `specs/` | **PERMANENT** | Cell invariants, complexity ceilings, failure matrices, anti-goals | Authoritative source of behavioral truth |
| `tests/` | **PERMANENT** | Black-box contract, property (`Hypothesis` / `fast-check`), and replay suites | Frozen prior to synthesis via `regen_guard.py prepare <cell>` |
| `dist/` | **COMMITTED ARTIFACT** | LLM-synthesized implementation satisfying `contracts/` & `tests/` | **Read-only (`0444`). Never hand-patch.** Managed exclusively via `regen_guard.py` |
| `deploy/` | **COMMITTED DEPLOY** | Production container manifests (`Dockerfile`, `docker-compose.yml`) | Declarative zero-inference deployment configs |
| `README.md` | **OPERATIONAL RUNBOOK** | Architecture diagram, env table, IAM setup, and CLI instructions | Must be kept synchronized with `dist/main/` |
| `scratch/` | **EPHEMERAL** | Timeboxed spikes and hermetic context bundles (`context_<cell>.md`) | Git-ignored; never imported by `contracts/`, `tests/`, or `dist/` |

---

## 2. The Zero-Patch Mandate & Provenance Lock (`dist/<cell>/.spec-lock.json`)

1. **No Direct Edits in `dist/`:** Files inside `dist/<cell>/` are machine-compiled artifacts locked with `chmod 0444` and attested by `dist/<cell>/.spec-lock.json`. Never run `chmod +w` to hand-edit or apply tactical band-aids to `dist/`.
2. **Pre-Synthesis Test Freezing:** Always run `python3 scripts/regen_guard.py prepare <cell>` before synthesizing a cell. This wipes `dist/<cell>/`, locks the upstream SHA-256 of `contracts/`, `specs/`, and `tests/` in `scratch/.freeze_<cell>.json`, and generates `scratch/context_<cell>.md`.
3. **The Two-Strike Repair Limit:** During synthesis, at most **2 automated repair attempts** are permitted. Modifying `tests/`, `contracts/`, or `specs/` during a repair retry will cause `regen_guard.py seal <cell>` to abort with `[TEST/SPEC TAMPER DETECTED]`. If attempt 2 fails, run `python3 scripts/regen_guard.py unlock <cell>` and fix the ambiguity in `specs/`.
4. **Topological Rebuild Enforcement:** After editing any shared file in `contracts/`, run `python3 scripts/regen_guard.py stale` and regenerate all impacted cells in the exact topological order reported.

---

## 3. Cellular Classifications & Quantitative Ceilings

| Cell Role | Seal Command | Max Size | Allowed Coupling & I/O |
| :--- | :--- | :--- | :--- |
| **Pure Domain** (`domain`) | `regen_guard.py seal <cell>` | 350 LOC / 4,500 tokens | Zero I/O, zero env reads, zero cross-cell `dist/` imports. Must have `@given` or `fc.assert` property tests. |
| **I/O Adapter** (`adapter`) | `regen_guard.py seal <cell> --adapter` | 150 LOC / 2,000 tokens | Accepts injected DB connection or HTTP transport port (`fetch`/`httpx`). Zero global state or env reads. |
| **Composition Root** (`entrypoint`) | `regen_guard.py seal main --entrypoint` | 200 LOC / 2,500 tokens | Sole cell permitted to read `os.environ` / `process.env` and wire sibling `dist/<cell>` modules together. |

---

## 4. Standard Regeneration Loop

```bash
# 1. Inspect topological rebuild queue
python3 scripts/regen_guard.py stale

# 2. Wipe dist/<cell>, freeze upstream hashes, and pack hermetic context
python3 scripts/regen_guard.py prepare <cell>

# 3. Synthesize dist/<cell>/ in a single pass from scratch/context_<cell>.md

# 4. Run static typechecks and verification suite
# Python: uv run ruff check && uv run pyright && uv run pytest
# TS:     bun x biome check . && bun x tsc --noEmit && bun test

# 5. Audit budgets, verify test freeze, write .spec-lock.json, and chmod 0444
python3 scripts/regen_guard.py seal <cell> [--adapter | --entrypoint]
```
```

---

## 2. `ARCHITECTURE.md` (3-Wave Execution Tracker Template)

```markdown
# System Architecture & 3-Wave Execution Tracker

## 1. Cellular Directed Acyclic Graph (DAG)

| Cell ID | Role (`domain` \| `adapter` \| `entrypoint`) | Contract File | Upstream Contract Dependencies | Target Seal Command |
| :--- | :--- | :--- | :--- | :--- |
| `<ingestor_cell>` | `adapter` | `contracts/<ingestor>_contract.(py\|ts)` | `(none)` | `seal <ingestor_cell> --adapter` |
| `<policy_cell>` | `domain` | `contracts/<policy>_contract.(py\|ts)` | `<ingestor_cell>` | `seal <policy_cell>` |
| `<actuator_cell>` | `adapter` | `contracts/<actuator>_contract.(py\|ts)` | `<policy_cell>` | `seal <actuator_cell> --adapter` |
| `main` | `entrypoint` | `contracts/main_contract.(py\|ts)` | `<ingestor_cell>`, `<policy_cell>`, `<actuator_cell>` | `seal main --entrypoint` |

## 2. 3-Wave Completion Gates

### Wave 1: Contracts & Behavioral Specifications
- [ ] All Layer 1 schemas authored in `contracts/` (including `main_contract`)
- [ ] All Layer 2 behavioral specs authored in `specs/*.spec.md`
- [ ] Static type check passes on contracts (`pyright contracts/` or `tsc --noEmit`)
- [ ] `python3 scripts/regen_guard.py stale` confirms 0 circular dependencies

### Wave 2: Hermetic Cell Compilation (`domain` & `adapter` cells)
- [ ] `<ingestor_cell>`: Tests written -> `prepare` -> Synthesized -> Tests pass -> `seal --adapter`
- [ ] `<policy_cell>`: Property & contract tests written -> `prepare` -> Synthesized -> Tests pass -> `seal`
- [ ] `<actuator_cell>`: Tests written -> `prepare` -> Synthesized -> Tests pass -> `seal --adapter`

### Wave 3: Composition Root & Operational Envelope
- [ ] `main`: CLI contract tests written -> `prepare main` -> Synthesized `--dry-run` entrypoint -> `seal main --entrypoint`
- [ ] `deploy/Dockerfile` and `deploy/docker-compose.yml` authored
- [ ] `README.md` operational runbook authored (env table, IAM, dry-run, deploy)
- [ ] Final verification gate: `python3 scripts/regen_guard.py verify` and `python3 scripts/regen_guard.py stale` report 0 errors and 0 stale cells
```
