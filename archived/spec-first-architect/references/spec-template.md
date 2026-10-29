# Cellular Behavioral Specification Template

Use these templates for specifications in `specs/<cell>.spec.md`. Keep all specifications clinical, declarative, and tabular. Omit narrative prose.

---

## 1. Domain / Adapter Cell Specification Template (`specs/<cell>.spec.md`)

```markdown
# SPEC: <cell_name>

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `<cell_name>` |
| **Cell Classification** | `<Pure Domain Cell | I/O Adapter Cell>` |
| **Contract Path** | `contracts/<cell_name>_contract.(py|ts)` |
| **Committed Artifact Path** | `dist/<cell_name>/` (Sealed via `.spec-lock.json`) |
| **Max Implementation Size** | `<350 LOC (Domain) | 150 LOC (Adapter)>` |
| **Max Inbound Context** | 8,000 Tokens (Enforced via `regen_guard.py prepare`) |
| **Permitted Dependencies** | `<explicit list, e.g., pydantic, polars | zod> (Zero unlisted packages)` |
| **State / I/O Quarantine** | `<Zero I/O (Pure Domain) | Injected DB Handle | Injected HTTP Transport>` |

## 2. Responsibility & Boundary Scope
- **Primary Function:** Single-sentence clinical statement of the transformation or side-effect performed by this cell.
- **Inbound Boundary:** Exact types accepted from `contracts/<cell_name>`.
- **Outbound Boundary:** Exact return types and domain errors emitted from `contracts/<cell_name>`.

## 3. Core Invariants (Must Hold Across All Inputs)
1. **Determinism:** Given identical input payloads and injected clock/seed, output must be bit-for-bit identical.
2. **Conservation / Idempotency:** <Specify structural invariants tested by property fuzzers (`@given` / `fc.assert`), e.g., output count == input count, sum of allocations == 1.0>.
3. **Immutability:** Input structures passed into the cell must never be mutated in place.

## 4. Edge-Case & Failure Resolution Matrix
| Condition / Trigger | Expected Behavior | Emitted Error / Return |
| :--- | :--- | :--- |
| Empty collection / zero-length payload | Return empty validated result without invoking downstream I/O | `Ok([])` |
| Malformed schema / out-of-range numeric | Reject immediately at boundary before business logic | `ContractValidationError` |
| Upstream timeout or transient I/O failure | Abort within timeout ceiling; do not retry internally unless specified | `UpstreamTimeoutError` |
| Numerical overflow / NaN / null key | Halt computation and return domain error with offending key | `DomainInvariantError` |

## 5. Explicit Anti-Goals (Forbidden Patterns)
- **DO NOT** read environment variables (`os.environ` or `process.env`). All configuration must be passed via `contracts/`.
- **DO NOT** import directly from sibling cells in `dist/`. Only `dist/main` (--entrypoint) may wire cells.
- **DO NOT** instantiate global database connections, HTTP clients, or background daemon threads.
- **DO NOT** catch generic exceptions silently (`except Exception: pass` or empty `catch {}`).
```

---

## 2. Composition Root Specification Template (`specs/main.spec.md`)

```markdown
# SPEC: main (Composition Root & CLI Entrypoint)

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `main` (`--entrypoint`) |
| **Contract Path** | `contracts/main_contract.(py|ts)` |
| **Committed Artifact Path** | `dist/main/__main__.py` (or `dist/main/index.ts`) |
| **Max Implementation Size** | 200 LOC / 2,500 Tokens |
| **Max Inbound Context** | 8,000 Tokens |

## 2. Pipeline Orchestration Sequence
1. Parse environment variables and CLI arguments into validated `RuntimeConfig`.
2. The `--dry-run` flag unconditionally forces evaluation mode to `"DRY_RUN"`.
3. Instantiate I/O client handles and invoke read adapters.
4. Pass snapshots into pure domain cells to compute policy decisions.
5. If in `"DRY_RUN"` mode, emit structured JSON plan to stdout and exit `0` without mutations.
6. If in active enforcement mode, invoke actuator cells and emit execution audit log.

## 3. Exit Code Matrix
| Exit Code | Condition |
| :--- | :--- |
| `0` | Successful execution (dry-run or completed enforcement) |
| `1` | Configuration error / missing environment variable |
| `2` | Upstream API timeout or unrecoverable infrastructure failure |
```
