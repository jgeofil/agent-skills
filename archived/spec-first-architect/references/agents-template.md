# AGENTS.md — Spec-First, Disposable Code Constitution

This repository operates under the **Spec-First, Disposable Code (Regenerative Architecture)** paradigm. All autonomous coding agents, IDE assistants, and human contributors must follow these constitutional mechanics without exception.

---

## 1. Non-Negotiable Core Directives

`dist/` contains machine-synthesized build artifacts committed to Git for deterministic, zero-inference production deployment.

1. **NEVER hand-edit or patch files in `dist/`.** All files in `dist/` are locked read-only (`chmod 0444`) and guarded by SHA-256 provenance hashes in `dist/<cell>/.spec-lock.json`.
2. **Two-Way Provenance Lock:** Modifying `dist/<cell>/` without running the full synthesis seal, or modifying upstream contracts (`contracts/`), specifications (`specs/`), or tests (`tests/`) without regenerating and sealing `dist/<cell>/`, will fail verification in pre-commit hooks and CI.
3. **Two-Strike Repair Limit:** If synthesized code in `dist/<cell>/` fails typechecking or tests after 2 automated repair attempts, **HALT** immediately. Wipe `dist/<cell>/` via `python3 scripts/regen_guard.py unlock <cell>` and fix the root specification (`specs/<cell>.spec.md`) or contracts (`contracts/`). Never weaken or mutate tests, contracts, or specs during a repair loop (enforced by `scratch/.freeze_<cell>.json`).

---

## 2. Stateful & External I/O Boundary Rules

Persisted state and external endpoints require explicit boundary quarantine:

- **No Global State or Env Reads in `dist/`:** Synthesized domain and adapter cells in `dist/` are strictly forbidden from calling `os.environ` or `process.env`. Inject configuration schemas defined in `contracts/`. Only the Composition Root (`dist/main/`) is authorized to parse environment variables.
- **Migrations Are Contracts:** SQL schema definitions and migrations (`contracts/migrations/*.sql`) are permanent, append-only assets. They must never be synthesized, wiped, or modified after commit.
- **Database Handle Injection:** Database cells in `dist/` must accept an active connection handle (`duckdb.DuckDBPyConnection`, `sqlite3.Connection`, or async connection pool) injected at invocation; hardcoded file paths or connection strings are banned.
- **HTTP Adapter Quarantine:** Pure domain cells in `dist/` must never perform network I/O. External API integrations must be quarantined into dedicated adapter cells capped at 150 LOC / 2,000 tokens, taking an injected transport port (`fetchFn` or `httpx.AsyncClient`).
- **Composition Root Exemption:** Only `dist/main/` (`--entrypoint`) is authorized to wire sibling cells (`from dist.<cell> import ...` or `import ... from '../<cell>'`) and read runtime environment variables. Cross-cell imports between sibling domain or adapter cells are strictly forbidden.

---

## 3. Quantitative Cell Boundaries & Budgets

Every cellular unit in `dist/` must remain small enough to be deterministically synthesized in a single LLM pass:

| Cell Classification | Seal Flag | Max Output Size | Max Inbound Context | Special Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Pure Domain Cell** | `seal <cell>` | 350 LOC / 4,500 tokens | 8,000 tokens | Zero I/O, zero env reads, requires property fuzzing (`@given` / `fc.assert`) |
| **I/O Adapter Cell** | `seal <cell> --adapter` | 150 LOC / 2,000 tokens | 8,000 tokens | Accepts injected DB handle or HTTP transport; zero domain logic |
| **Composition Root** | `seal main --entrypoint` | 200 LOC / 2,500 tokens | 8,000 tokens | Permitted to read `os.environ`/`process.env` and import sibling `dist/<cell>` APIs |

If a feature cannot fit within these ceilings, halt and decompose the specification into smaller cells connected by an explicit intermediate contract in `contracts/`.

---

## 4. Standard Regeneration Sequence

Execute in strict sequential order:

```bash
# 1. Prepare hermetic context & freeze upstream hash (wipes dist/<cell>/)
python3 scripts/regen_guard.py prepare <cell>

# 2. Synthesize dist/<cell>/ in a single pass reading ONLY scratch/context_<cell>.md

# 3. Verify static types and behavioral/property tests
# Python:
uv run ruff check . && uv run pyright && uv run pytest
# TypeScript:
bun x biome check . && bun x tsc --noEmit && bun test

# 4. Audit budgets, write .spec-lock.json, and lock permissions (0444)
python3 scripts/regen_guard.py seal <cell> [--adapter|--entrypoint]

# 5. Pre-commit and CI verification across all sealed cells
python3 scripts/regen_guard.py verify
```

---

## 5. Mandatory End-to-End Completion Gate (No Spec-Only Halting)

Never conclude a project generation or expansion request after only writing component specs. Every delivered system MUST include:

1. **Synthesized & Sealed Component Cells:** Every spec in `specs/<cell>.spec.md` must be compiled into `dist/<cell>/` and sealed via `python3 scripts/regen_guard.py seal <cell> [--adapter]`.
2. **Composition Root (`dist/main/`):** A dedicated entrypoint cell (`contracts/main_contract.*`, `specs/main.spec.md`, `dist/main/`) sealed with `python3 scripts/regen_guard.py seal main --entrypoint` that wires all adapters and domain cells into an executable CLI/service with a mandatory `--dry-run` flag.
3. **Deployment Manifests (`deploy/`):** A production `Dockerfile` and `docker-compose.yml` (plus cloud-specific event trigger setup scripts if targeting serverless).
4. **Operational Runbook (`README.md`):** Root documentation specifying:
   - Pipeline architecture and cell wiring diagram
   - Required environment variables and minimum IAM permissions
   - Exact commands to run tests, dry-run locally (`--dry-run --once`), regenerate a cell, and deploy to production

---

## 6. Prohibited Agent Behaviors

- **FORBIDDEN:** Modifying or weakening assertions in `tests/` or schemas in `contracts/` to make a failing `dist/` implementation pass during a repair loop.
- **FORBIDDEN:** Direct patching or editing of any file in `dist/` without executing `prepare` and `seal`.
- **FORBIDDEN:** Importing sibling cells from within domain or adapter cells (`dist/main` is the sole authorized wiring root).
- **FORBIDDEN:** Reading `os.environ` or `process.env` inside domain or adapter cells.
- **FORBIDDEN:** Leaving `dist/` unsealed or committing files without `.spec-lock.json`.
