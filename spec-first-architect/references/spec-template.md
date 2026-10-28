# Module Behavioral Specification Template

Use this template for every module specification in `specs/<module>.spec.md`. Keep all specifications clinical, declarative, and tabular. Omit narrative prose.

```markdown
# SPEC: <module_name>

## 1. Module Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Module ID** | `<module_name>` |
| **Contract Path** | `contracts/<module_name>.contract.(py\|ts)` |
| **Implementation Path** | `src/<module_name>/` |
| **Max Implementation Size** | 300 LOC (Hard Ceiling: 350 LOC) |
| **Max Regeneration Budget** | 3,000 Output Tokens / 30s Wall-Clock |
| **Permitted External Deps** | `<explicit list, e.g., pydantic, polars / zod>` (Zero unlisted packages) |
| **Statefulness** | `<Pure Stateless Function \| Bounded In-Memory State \| External I/O Adapter>` |

## 2. Responsibility & Boundary Scope
- **Primary Function:** Single-sentence clinical statement of the transformation or side-effect performed by this module.
- **Inbound Boundary:** Exact types accepted from `contracts/<module_name>`.
- **Outbound Boundary:** Exact return types and domain errors emitted from `contracts/<module_name>`.

## 3. Core Invariants (Must Hold Across All Inputs)
1. **Determinism:** Given identical input payloads and injected clock/seed, output must be bit-for-bit identical.
2. **Conservation / Idempotency:** <Specify structural invariants tested by property-based fuzzers, e.g., output row count <= input row count, sum of allocations == 1.0>.
3. **Immutability:** Input structures passed into the module must never be mutated in place.

## 4. Edge-Case & Failure Resolution Matrix
| Condition / Trigger | Expected Behavior | Emitted Error / Return |
| :--- | :--- | :--- |
| Empty collection / zero-length payload | Return empty validated result without invoking downstream I/O | `Ok([])` |
| Malformed schema / out-of-range numeric | Reject immediately at boundary before business logic | `ContractValidationError` |
| Upstream timeout or transient I/O failure | Abort within timeout ceiling; do not retry internally unless specified | `UpstreamTimeoutError` |
| Numerical overflow / NaN / null key | Halt computation and return domain error with offending key | `DomainInvariantError` |

## 5. Performance & Complexity Ceilings
- **Time Complexity:** `O(N log N)` worst-case with respect to input batch size `N`.
- **Space Complexity:** `O(N)` peak heap allocation; no unbounded buffering.
- **Latency Target:** `< 15ms` p99 for standard payload (`N = 1,000`).

## 6. Explicit Anti-Goals (Forbidden Patterns)
- **DO NOT** implement internal caching, memoization, or background worker threads inside this module.
- **DO NOT** catch generic exceptions silently (`except Exception: pass` or empty `catch {}`).
- **DO NOT** perform network, filesystem, or environment variable reads unless injected via the explicit config contract.
- **DO NOT** import internal files from sibling modules under `src/`.
```
