# AGENTS.md - Spec-First, Disposable Code Governance

This repository operates under the **Spec-First, Disposable Code (Regenerative Architecture)** paradigm. All autonomous coding agents, IDE assistants, and human contributors must follow these structural mechanics without exception.

---

## 1. Artifact Authority Hierarchy

Files in this repository are strictly partitioned into **Permanent Authoritative Assets** and **Disposable Build Artifacts**:

| Directory | Status | Role | Modification Policy |
| :--- | :--- | :--- | :--- |
| `contracts/` | **PERMANENT** | Strict I/O schemas, interfaces, and error taxonomies | Edit deliberately; requires static type verification |
| `specs/` | **PERMANENT** | Module invariants, complexity ceilings, and anti-goals | Authoritative source of behavioral truth |
| `tests/` | **PERMANENT** | Black-box contract, property (fuzzer), and benchmark suites | Append/update assertions before regenerating `src/` |
| `src/` | **DISPOSABLE** | Compiled implementation logic satisfying `contracts/` & `tests/` | **Never patch iteratively.** Wipe and regenerate from spec |
| `scratch/` | **EPHEMERAL** | Timeboxed spikes and hypothesis falsification scripts | Must be deleted after extracting findings to `specs/` |

---

## 2. The Zero-Patch Mandate & Two-Patch Halt Rule

1. **No Tactical Band-Aids in `src/`:** When a bug, edge case, or architectural flaw is discovered in `src/<module>`, do **not** stack tactical code patches onto the implementation.
2. **The Two-Patch Halt Ceiling:** You are permitted at most **1 minor syntax/wiring correction** after a synthesis pass. If a module requires a second structural fix to pass tests, you must **HALT** implementation edits immediately.
3. **Root-Cause Escalation:** Every failure beyond syntax wiring indicates an incomplete specification (`specs/<module>.spec.md`), an under-constrained type boundary (`contracts/<module>`), or a missing test assertion (`tests/`). Fix the permanent layer first, run `rm -rf src/<module>`, and regenerate the implementation cleanly.

---

## 3. Cellular Module Boundaries & Cost Budgets

Every module under `src/<module>/` must remain small enough to be synthesized deterministically in a single LLM pass:

- **Maximum Implementation Size:** `<= 350 LOC` per module (excluding comments and blank lines). Target optimum: `120 - 250 LOC`.
- **Maximum Synthesis Cost:** `<= 4,500 output tokens` and `<= 45 seconds` generation latency per module.
- **Maximum Cyclomatic Complexity:** `<= 10` per function/method.
- **Zero Cross-Module Internal Imports:** `src/module_a` is strictly forbidden from importing directly from `src/module_b/internal`. Modules may only communicate through public types defined in `contracts/` and public module entry points (`src/<module>/index.ts` or `src/<module>/__init__.py`).

If a feature cannot fit within `350 LOC`, halt and decompose the specification into two sequential or orthogonal sub-modules connected by an explicit intermediate contract in `contracts/`.

---

## 4. Operational Workflows

### Workflow A: Forward Synthesis (`SPEC -> Implementation`)

Execute in strict sequential order:

1. **Verify Contract Compilation:** Validate `contracts/<module>` via static type checking (`mypy --strict` or `tsc --noEmit`).
2. **Verify Spec Completeness:** Confirm `specs/<module>.spec.md` defines all input/output invariants, error conditions, complexity limits, and explicit anti-goals.
3. **Verify Red Harness:** Confirm `tests/contract/` and `tests/property/` contain black-box assertions covering all spec invariants and fail prior to synthesis.
4. **Purge Target Directory:** Delete existing implementation artifacts (`rm -rf src/<module> && mkdir -p src/<module>`).
5. **Single-Pass Synthesis:** Generate `src/<module>` using only the module's contract, spec, and test suite as context.
6. **Audit & Gate:** Run the full test harness, static type checker, and `python3 scripts/audit_boundaries.py`.

### Workflow B: Reverse Ratcheting (`Implementation / Spike -> SPEC Update`)

When an exploratory script in `scratch/` succeeds or an uncaptured edge case is found during testing:

1. **Freeze Code Edits:** Do not promote `scratch/` code into `src/`, and do not refactor broken code in place.
2. **Extract Domain Constraints:** Identify every implicit data shape, boundary condition, timeout, or state invariant discovered in the code.
3. **Update Permanent Layers:**
   - Add missing types or field validators to `contracts/<module>`.
   - Document the edge case and resolution rule in `specs/<module>.spec.md`.
   - Write a deterministic test in `tests/contract/` and/or a property invariant in `tests/property/` that fails unless the edge case is handled.
4. **Destroy Specimen & Regenerate:** Delete the `scratch/` script and `rm -rf src/<module>`, then execute **Workflow A** to synthesize a clean implementation from the updated permanent assets.

---

## 5. Prohibited Agent Behaviors

- **FORBIDDEN:** Modifying or weakening assertions in `tests/` just to make a flawed `src/` implementation pass.
- **FORBIDDEN:** Mocking private internal functions of `src/<module>` inside `tests/`. All tests must treat `src/<module>` as an opaque black box.
- **FORBIDDEN:** Adding unapproved third-party dependencies in `src/<module>` that are not explicitly whitelisted in `specs/<module>.spec.md`.
- **FORBIDDEN:** Leaving TODO comments, fallback stubs, or uncaptured domain logic inside `src/` without a corresponding invariant in `specs/`.
