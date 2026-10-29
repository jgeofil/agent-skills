# Stateful Subsystems, I/O Adapters & Composition Root Reference

Persisted data, external network APIs, and application startup wiring cannot be treated identically to stateless functions. Enforce **Boundary Bifurcation** to keep `dist/` cells 100% disposable and cryptographically sealed without risking data corruption or flaky network tests.

---

## 1. Subsystem Isolation Matrix

| Subsystem | Layer 1 (`contracts/`) | Layer 2 (`specs/`) | Layer 3 (`tests/`) | Layer 4 (`dist/`) | Seal Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Schema & Migrations** | Append-only `contracts/migrations/NNNN_*.sql` + target DDL schemas | Idempotency, lock-timeout ceilings, index invariants | Ephemeral DB boot test applying all `.sql` files + schema inspection | Stateless migration runner (`dist/migrator/`); zero synthesized DDL | `seal migrator --adapter` |
| **DuckDB / SQLite State** | Pydantic/Zod row models + `Protocol` signature taking a DB connection handle | Query complexity ceiling, transaction rollback rules, NaN/NULL semantics | `Hypothesis` / `fast-check` fuzzing against `:memory:` DB per test iteration | Stateless SQL execution & hydration module (`dist/<store>_cell/`) | `seal <store>_cell --adapter` |
| **External HTTP / RPC** | Wire payload schema + internal domain schema + typed error union + `FetchLike` port | Timeout budget, HTTP status mapping table, rate-limit header parsing | Replay tests using mocked transport (`httpx.MockTransport` or mock `fetch`) | Pure wire-to-domain adapter (`dist/<api>_adapter/`) | `seal <api>_adapter --adapter` (150 LOC max) |
| **Composition Root** | `contracts/main_contract.(py\|ts)` (`RuntimeConfig` schema) | CLI flags (`--dry-run`, `--once`), polling lifecycle, wiring order | CLI smoke test wiring `:memory:` DB + mock transport | Thin entrypoint (`dist/main/`) reading env vars & wiring sibling `dist/*` cells | `seal main --entrypoint` (200 LOC max) |

---

## 2. Database Migrations & DuckDB/SQLite In-Memory Twins

1. **Migrations Live in `contracts/migrations/`:** Historical DDL scripts (`0001_init.sql`, `0002_add_index.sql`) are permanent Layer 1 contracts. Never allow an LLM to regenerate or overwrite committed migration files.
2. **Mandatory Connection Handle Injection:** Cells in `dist/` are mechanically blocked by `regen_guard.py` from calling `duckdb.connect("file.ddb")` or `sqlite3.connect("file.db")`. Always inject an active `duckdb.DuckDBPyConnection` or `sqlite3.Connection` handle.
3. **In-Memory Twin Fuzzing:** Inside `tests/property/test_<cell>.py`, instantiate `with duckdb.connect(":memory:") as conn:` inside the `@given(...)` property loop so every fuzzing case executes against a fresh, zero-artifact in-memory database.

---

## 3. Two-Schema HTTP Transport Micro-Adapters (`--adapter`)

Never allow a `domain` cell to perform network I/O. Isolate every third-party integration into a dedicated `adapter` cell capped at **150 LOC**:
1. **Wire vs. Domain Schema Split:** In `contracts/<provider>_contract.ts` (or `.py`), define both a lenient `WireResponseSchema` (tolerating extra upstream fields) and a strict `DomainModelSchema` (`extra="forbid"` / `.strict()`).
2. **Transport Port Injection:** Accept `fetchFn: FetchLike` (TypeScript) or `client: httpx.Client` (Python) as an explicit parameter.
3. **Total Error Mapping:** Catch timeouts, HTTP `429` (`Retry-After`), and wire schema errors inside the adapter and return a discriminated union (`Result[DomainModel, AdapterError]`). Never let raw transport exceptions cross into domain cells.

---

## 4. Composition Root (`dist/main/` with `--entrypoint`) & Deployment Envelope

To prevent the **Orphan Cell Trap**, every project must include a Composition Root (`dist/main/`), `deploy/` manifests, and an operational `README.md`.

### Composition Root Rules (`dist/main/`)
- Sealed with `python3 scripts/regen_guard.py seal main --entrypoint` (capped at **200 LOC**).
- Exempt from the pure-cell ban on `os.environ` / `process.env` / `Bun.env` and sibling `dist.<cell>` imports.
- Must implement a `--dry-run` CLI flag (and `--once` for polling services) that runs the full ingestion and domain policy evaluation pipeline and prints planned mutations as structured JSON without executing external writes.

### Zero-Inference `deploy/Dockerfile` (Python `uv` Example)
```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY contracts/ ./contracts/
COPY dist/ ./dist/

USER 1000:1000
ENTRYPOINT ["uv", "run", "python", "-m", "dist.main"]
```

---

## 5. Lateral Stateful Architectures

- **Immutable Parquet Log + Disposable DuckDB Views (Zero-Migration State):** Persist state events as append-only Parquet segments on disk. Define relational projections in `contracts/views.sql` via `CREATE OR REPLACE VIEW`. Both the views and `dist/` query cells remain 100% disposable with zero schema-migration risk.
- **Declarative Schema Convergence (`sqldef` / Atlas):** Maintain a single declarative `contracts/schema.sql` file instead of sequential migrations and apply diffs deterministically via `sqlite3def` or `psqldef`.
- **VCR Wire-Cassette Ratcheting:** Record live HTTP request/response pairs during `scratch/` spikes into `tests/fixtures/<cell>_cassettes.json`, delete `scratch/`, and replay those fixtures in `tests/contract/` to synthesize `dist/<cell>_adapter/`.
