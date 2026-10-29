# Stateful Subsystems & I/O Isolation Reference

Persisted data, database schemas, and external network endpoints cannot be wiped and regenerated like pure functions. When designing modules that interact with databases, external APIs, or runtime environments, enforce **Boundary Bifurcation**: quarantine all side-effects, connections, and external payloads to strict cellular interfaces.

---

## 1. Subsystem Isolation Matrix

| Subsystem | Layer 1 (`contracts/`) | Layer 2 (`specs/`) | Layer 3 (`tests/`) | Layer 4 / 5 (`dist/`) |
| :--- | :--- | :--- | :--- | :--- |
| **Schema & Migrations** | Append-only `contracts/migrations/NNNN_*.sql` + target table schemas | Idempotency rules, up/down migration invariants, rollback guarantees | Migration replay tests on disposable temporary database | Never synthesized; managed via migration runner CLI |
| **DuckDB / SQLite Queries** | Pydantic/Zod row models + `Protocol` signature taking a DB connection handle | Query complexity bounds, indexing strategy, transaction isolation | In-memory twin tests against `:memory:` DB using `@given` / `fc.assert` | Synthesized query functions accepting injected `conn` handle |
| **External HTTP / RPC** | Wire payload schema + internal domain schema + typed error union + `FetchLike` port | Retry policy, backoff with jitter, 429 budget, timeout ceilings | Wire fixture replay / VCR cassette tests mocking transport port | Micro-adapter cell (max 150 LOC) taking injected `fetchFn` or client |
| **Composition Root** | Application config schema (`RuntimeConfig` / `EnvConfig`) | Startup sequence, graceful shutdown timeout, CLI flag precedence | End-to-end dry-run smoke test (`--dry-run --once`) | `dist/main/` (`--entrypoint`, max 200 LOC) wiring adapters, domains, and config |

---

## 2. Pattern A: DuckDB / SQLite In-Memory Twin Verification

For embedded and analytical database workflows:

1. **Contract Definition:**
   Define table `SCHEMA_DDL` and strict row I/O models in `contracts/<cell>.contract.py`:
   ```python
   SCHEMA_DDL = """
   CREATE TABLE events (
       event_id VARCHAR PRIMARY KEY,
       user_id VARCHAR NOT NULL,
       amount DOUBLE NOT NULL,
       timestamp TIMESTAMP NOT NULL
   );
   """
   ```
2. **Handle Injection:**
   Require the synthesized entrypoint in `dist/<cell>/` to accept an active connection:
   ```python
   def query_user_totals(conn: duckdb.DuckDBPyConnection, user_id: str) -> list[UserTotal]:
       ...
   ```
   *Strictly forbidden:* Calling `duckdb.connect("path/to/file.db")` or `sqlite3.connect(...)` inside `dist/<cell>/`.
3. **Twin Fuzzing in Tests:**
   In `tests/property/test_<cell>.py`, instantiate an ephemeral in-memory database inside the property test runner:
   ```python
   @given(st.lists(event_strategy()))
   def test_aggregation_invariant(events: list[EventRecord]) -> None:
       with duckdb.connect(":memory:") as conn:
           conn.execute(SCHEMA_DDL)
           insert_events(conn, events)
           results = query_user_totals(conn, "user-123")
           assert sum(r.total for r in results) >= 0.0
   ```

---

## 3. Pattern B: Two-Schema HTTP Micro-Adapters

External third-party APIs frequently drift, add undocumented fields, or return unexpected types. Quarantine this volatility with two distinct schemas:

1. **Two-Schema Architecture in `contracts/<provider>.contract.ts`:**
   - **Wire Response Schema:** Validates raw upstream JSON (permissive, tolerates extraneous fields).
   - **Domain Output Schema:** Strict internal domain model (`z.object({...}).strict()` or `ConfigDict(extra="forbid")`).
2. **Transport Port Injection:**
   Require the adapter in `dist/<provider>_adapter/` to accept a transport function handle:
   ```typescript
   export async function fetchSpend(
     projectId: string,
     fetchFn: typeof fetch = fetch
   ): Promise<SpendSnapshot> { ... }
   ```
3. **Typed Error Taxonomy:**
   Map all transport failures, network timeouts, `429 Too Many Requests` (`Retry-After`), and JSON schema mismatches into a discrete domain error union defined in `contracts/`. Never leak raw HTTP errors into domain cells.

---

## 4. Lateral Stateful Architectures

When traditional relational database migrations introduce excessive regeneration friction, consider these three lateral alternatives:

- **Immutable Parquet Log + Disposable DuckDB Views (Zero-Migration State):**
  Persist state mutations as append-only Parquet chunks written to local disk or object storage. Define queries and views dynamically in DuckDB over the Parquet files. Schema changes simply redefine the analytical SQL view in `contracts/`, eliminating traditional database migrations entirely.
- **Declarative Schema Convergence (`sqldef` / Atlas):**
  Maintain a single declarative `contracts/schema.sql` defining the desired end-state schema. Use declarative diffing engines (`mysqldef`, `psqldef`, or Atlas) during deployment to converge database state instead of maintaining ordered sequential migration scripts.
- **VCR Wire-Cassette Ratcheting:**
  During exploratory spikes in `scratch/`, dump live HTTP request/response JSON fixtures into `tests/fixtures/`. Promote sanitized recordings into permanent contract replay tests before purging `scratch/`, allowing deterministic offline test execution.
