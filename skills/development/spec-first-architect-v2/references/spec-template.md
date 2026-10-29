# Cell Behavioral Specification Template

Use this template for every cell specification in `specs/<cell_name>.spec.md`. Keep all specifications clinical, declarative, and tabular. Omit narrative prose.

```markdown
# SPEC: <cell_name>

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `<cell_name>` |
| **Cell Classification** | `<domain \| adapter (--adapter) \| entrypoint (--entrypoint)>` |
| **Contract Path** | `contracts/<cell_name>_contract.(py\|ts)` |
| **Transitive Contract Deps** | `<explicit list of shared contracts, e.g., contracts/common_contract.py>` |
| **Committed Artifact Path** | `dist/<cell_name>/` (Sealed via `dist/<cell_name>/.spec-lock.json`) |
| **Max Implementation Size** | `<350 LOC (domain) \| 150 LOC (adapter) \| 200 LOC (entrypoint)>` |
| **Max Regeneration Budget** | `<4,500 \| 2,000 \| 2,500> Output Tokens / <= 30s Wall-Clock` |
| **Permitted External Deps** | `<explicit list, e.g., pydantic, polars / zod>` (Zero unlisted packages) |

## 2. Responsibility & Boundary Scope
- **Primary Function:** Single-sentence clinical statement of the transformation or I/O boundary performed by this cell.
- **Inbound Boundary:** Exact types and injected ports (DB connection handle, `FetchLike`, config) accepted from `contracts/<cell_name>_contract`.
- **Outbound Boundary:** Exact return types and discriminated domain error unions emitted from `contracts/<cell_name>_contract`.

## 3. Core Invariants (Must Hold Across All Inputs)
1. **Determinism:** Given identical input payloads and injected clock/seed/port, output must be bit-for-bit identical.
2. **Conservation / Metamorphic Relation:** <Specify structural invariants verified by `Hypothesis` `@given` or `fast-check` `fc.assert`, e.g., output row count <= input row count, sum of allocations == 1.0>.
3. **Immutability:** Input structures passed into the cell must never be mutated in place.

## 4. Edge-Case & Failure Resolution Matrix
| Condition / Trigger | Expected Deterministic Behavior | Emitted Error / Return |
| :--- | :--- | :--- |
| Empty collection / zero-length payload | Return empty validated result without invoking downstream I/O | `Ok([])` |
| Malformed schema / out-of-range numeric | Reject immediately at boundary before domain logic | `ContractValidationError` |
| Upstream timeout or HTTP 429 rate-limit | Abort within timeout ceiling; map `Retry-After` header into error union | `RateLimitedError(retry_after_ms)` |
| Numerical overflow / NaN / null key | Halt computation and return domain error with offending key | `DomainInvariantError` |

## 5. Performance & Complexity Ceilings
- **Time Complexity:** `O(N log N)` worst-case with respect to input batch size `N`.
- **Space Complexity:** `O(N)` peak heap allocation; no unbounded in-memory buffering.
- **Latency Target:** `< 15ms` p99 for standard in-memory payload (`N = 1,000`).

## 6. Explicit Anti-Goals (Forbidden Patterns)
- **DO NOT** read `os.environ`, `process.env`, or `Bun.env` inside this cell (unless classified as `--entrypoint`).
- **DO NOT** open hardcoded database paths (`duckdb.connect("file.ddb")`) or instantiate global HTTP clients.
- **DO NOT** catch generic exceptions silently (`except Exception: pass` or empty `catch {}`).
- **DO NOT** import internal files from sibling cells under `dist/`.
```
