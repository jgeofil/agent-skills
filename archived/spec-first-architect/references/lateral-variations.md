# Lateral Variations on Spec-First, Disposable Code

When standard prose-plus-contract specifications create friction for a specific problem domain, apply one of these four lateral variations. Each preserves the core principle that **implementation code is disposable**, while adapting the permanent source of truth to fit the task's uncertainty profile.

---

## Comparison Matrix Across Lateral Variations

| Variation | Authoritative Source of Truth | Best Domain Fit | Setup Overhead | Primary Failure Mode | Escape Hatch |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Property-Driven Synthesis (Tests-as-Spec)** | Strict I/O schemas (`contracts/`) + generative property fuzzers (`tests/property/`) | Algorithmic kernels, parsers, compilers, state machines, mathematical transforms | Low (skip `specs/*.md` prose) | Under-constrained properties allow trivial or degenerate solutions | Add concrete input/output anchor examples alongside invariants |
| **2. Shadow-Spec Extraction (Reverse Ratcheting)** | Timeboxed exploratory spike in `scratch/` extracted into formal Spec + Contract | Unfamiliar third-party APIs, undocumented protocols, ambiguous domain workflows | Minimal upfront; structured extraction post-spike | Temptation to copy-paste spike code directly into `dist/` | Enforce automated deletion of `scratch/` before synthesis begins |
| **3. Multi-Target Tournament Compilation** | Single shared `contracts/` + `specs/` + `tests/benchmarks/` compiled into N parallel `dist/` variants | High-throughput data pipelines, storage engines, latency-critical bottlenecks | Moderate (1x Spec, Nx cheap parallel synthesis passes) | Benchmark harness fails to test realistic adversarial data distributions | Augment benchmark suite with skewed, high-cardinality production fixtures |
| **4. Mutation-Locked Verification** | Standard 5-Layer stack + automated mutation testing (`mutmut` / `Stryker`) | High-assurance financial, cryptographic, or safety-critical state transitions | High verification compute cost | Equivalent mutants create noisy false alarms | Restrict mutation operators to boundary conditions and state branches |

---

## Variation 1: Property-Driven Synthesis (Tests-as-Spec)

When a cell's behavior is mathematically or structurally self-evident from its invariants, omit the natural-language `specs/<cell>.spec.md` file entirely. Treat the synthesis engine as a constraint solver whose sole objective is producing an implementation in `dist/<cell>` that survives an adversarial fuzzer.

### Execution Protocol
1. Define strict input/output types in `contracts/<cell>`.
2. Write 3 to 6 property-based invariants using `Hypothesis` (Python) or `fast-check` (TypeScript) in `tests/property/`:
   - **Round-trip / Invertibility:** `decode(encode(x)) == x`
   - **Idempotency:** `f(f(x)) == f(x)`
   - **Metamorphic Relations:** Transforming input `x` by known factor `k` changes output `f(x)` predictably.
   - **Oracle Equivalence:** Output matches a naive, slow, 15-line reference oracle function embedded inside the test file.
3. Synthesize `dist/<cell>` directly from `contracts/` and `tests/property/` running at `1,000+` generated examples per property. Seal with `python3 scripts/regen_guard.py seal <cell>`.

---

## Variation 2: Shadow-Spec Extraction (Reverse Ratcheting)

When requirements cannot be specified upfront because the external system or domain behavior is unknown, attempting to write `specs/` first leads to speculative fiction. Instead, quarantine open-ended exploration and use Reverse Ratcheting to harvest the spec.

### Execution Protocol
1. **Quarantined Spike:** Create a single throwaway script in `scratch/spike_<topic>.(py|ts)` with a strict timebox (e.g., 45 minutes) and falsification criteria.
2. **Chaotic Discovery:** Iterate rapidly in `scratch/` until the API handshake, data transformation, or algorithm works against real inputs.
3. **Automated Extraction Prompt:** Pass `scratch/spike_<topic>` to the agent with the instruction:
   > *"Analyze this exploratory script. Extract (1) all data schemas and error types into `contracts/<cell>`, (2) all discovered edge cases, rate limits, and state invariants into `specs/<cell>.spec.md`, and (3) black-box test assertions into `tests/`. Do not copy any implementation code."*
4. **Purge & Synthesize:** Delete `scratch/spike_<topic>` and synthesize `dist/<cell>` cleanly from the extracted artifacts using `prepare` and `seal`.

---

## Variation 3: Multi-Target Tournament Compilation

Because implementation code is cheap and decoupled from the specification, you do not need to guess which architectural library or algorithm will perform best before coding. Compile the same specification into competing implementations and let empirical telemetry select the winner.

### Execution Protocol
1. Lock a single `contracts/<cell>`, `specs/<cell>.spec.md`, and `tests/benchmarks/<cell>.bench.(py|ts)`.
2. Prompt parallel synthesis runs targeting distinct architectural strategies into isolated sibling directories:
   - `dist/<cell>_candidate_a/` (e.g., in-memory streaming generator)
   - `dist/<cell>_candidate_b/` (e.g., vectorized columnar batching via Polars/DuckDB)
   - `dist/<cell>_candidate_c/` (e.g., lookup-table state machine)
3. Execute the functional test suite and benchmark harness across all candidates simultaneously, measuring p99 latency, peak RSS memory, and LOC count.
4. Promote the winning candidate to `dist/<cell>/`, record the benchmark metrics in `specs/<cell>.spec.md`, delete all losing candidates, and seal with `python3 scripts/regen_guard.py seal <cell>`.

---

## Variation 4: Mutation-Locked Verification

LLMs can satisfy weak test suites by generating brittle happy-path shortcuts. Mutation-Locked Verification proves the test harness is airtight before allowing a regenerated cell to be accepted.

### Execution Protocol
1. After synthesizing `dist/<cell>` and passing all tests in `tests/`, run an automated mutation tool (`mutmut` for Python, `Stryker` for TypeScript) targeting `dist/<cell>`.
2. The mutation engine injects synthetic defects into `dist/<cell>` (flipping `<` to `<=`, removing error raises, mutating constants).
3. If any mutant survives (tests still pass despite mutated implementation code), the verification harness in `tests/` has a blind spot.
4. Add a new test assertion in `tests/` to kill the surviving mutant, update `specs/<cell>.spec.md` if the mutant exposed an ambiguous boundary condition, and re-seal the cell.
