# Lateral Variations on Spec-First, Disposable Code

When standard prose-plus-contract specifications create friction for a specific problem domain, apply one of these four lateral variations. Each preserves the core rule that **implementation code in `dist/` is disposable and cryptographically sealed**, while adapting the upstream source of truth to fit the task's uncertainty profile.

---

## Comparison Matrix Across Lateral Variations

| Variation | Authoritative Source of Truth | Best Domain Fit | Setup Overhead | Primary Failure Mode | Escape Hatch |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Property-Driven Synthesis (Tests-as-Spec)** | Strict I/O schemas (`contracts/`) + generative property fuzzers (`tests/property/`) | Algorithmic kernels, parsers, compilers, state machines, scoring transforms | Low (minimal `specs/*.md` prose) | Under-constrained properties allow trivial or degenerate solutions | Add concrete input/output anchor examples alongside invariants |
| **2. Shadow-Spec Extraction (Reverse Ratcheting)** | Timeboxed exploratory spike in `scratch/` extracted into formal Spec + Contract | Unfamiliar third-party APIs, undocumented protocols, ambiguous domain workflows | Minimal upfront; structured extraction post-spike | Temptation to copy-paste spike code directly into `dist/` | Enforce pre-commit block on `scratch/` and require `regen_guard.py prepare` & `seal` |
| **3. Multi-Target Tournament Compilation** | Single shared `contracts/` + `specs/` + `tests/benchmarks/` compiled into N candidate cells | High-throughput data pipelines, storage engines, latency-critical bottlenecks | Moderate (1x Spec, Nx cheap parallel synthesis passes) | Benchmark harness fails to test realistic adversarial data distributions | Augment benchmark suite with skewed, high-cardinality production fixtures |
| **4. Mutation-Locked Verification** | Standard 5-Layer stack + automated mutation testing (`mutmut` / `Stryker`) | High-assurance financial, cryptographic, or safety-critical state transitions | High verification compute cost | Equivalent mutants create noisy false alarms | Restrict mutation operators to boundary conditions and state branches |

---

## Variation 1: Property-Driven Synthesis (Tests-as-Spec)

When a cell's behavior is mathematically or structurally self-evident from its invariants, keep `specs/<cell>.spec.md` as a minimal metadata stub and let `tests/property/` drive synthesis.

### Execution Protocol
1. Define strict input/output types in `contracts/<cell>_contract.(py|ts)`.
2. Write 3 to 6 property-based invariants using `Hypothesis` (`@given`) or `fast-check` (`fc.assert`) in `tests/property/`:
   - **Round-trip / Invertibility:** `decode(encode(x)) == x`
   - **Idempotency:** `f(f(x)) == f(x)`
   - **Metamorphic Relations:** Transforming input `x` by known factor `k` changes output `f(x)` predictably.
   - **Oracle Equivalence:** Output matches a naive, slow, 15-line reference oracle function embedded inside the test file.
3. Run `python3 scripts/regen_guard.py prepare <cell>`, synthesize `dist/<cell>/` directly from `scratch/context_<cell>.md`, and seal with `python3 scripts/regen_guard.py seal <cell>`.

---

## Variation 2: Shadow-Spec Extraction (Reverse Ratcheting)

When requirements cannot be specified upfront because the external system or domain behavior is unknown, quarantine open-ended exploration in `scratch/` and use Reverse Ratcheting to harvest the spec.

### Execution Protocol
1. **Quarantined Spike:** Create a throwaway script in `scratch/spike_<topic>.(py|ts)` with a strict 45-minute timebox and falsification criteria.
2. **Chaotic Discovery:** Iterate rapidly in `scratch/` until the API handshake or algorithm works against live inputs (optionally dumping wire fixtures to `tests/fixtures/`).
3. **Automated Extraction Prompt:** Pass `scratch/spike_<topic>` to the agent:
   > *"Analyze this exploratory script. Extract (1) all data schemas and error types into `contracts/<cell>_contract`, (2) all discovered edge cases, rate limits, and state invariants into `specs/<cell>.spec.md`, and (3) black-box and property test assertions into `tests/`. Do not copy any implementation code."*
4. **Purge, Prepare, Synthesize & Seal:** Delete `scratch/spike_<topic>`, run `python3 scripts/regen_guard.py prepare <cell>`, synthesize `dist/<cell>/` from `scratch/context_<cell>.md`, and seal via `python3 scripts/regen_guard.py seal <cell>`.

---

## Variation 3: Multi-Target Tournament Compilation

Compile the same specification into competing architectural implementations and let empirical telemetry select the winner.

### Execution Protocol
1. Lock `contracts/<cell>_contract`, `specs/<cell>.spec.md`, and `tests/benchmarks/`.
2. Synthesize competing strategies into temporary directories (`scratch/cand_polars/`, `scratch/cand_duckdb/`, `scratch/cand_pure/`).
3. Benchmark all candidates against p99 latency, peak RSS memory, and LOC count.
4. Promote the winner to `dist/<cell>/`, delete `scratch/cand_*`, and seal with `python3 scripts/regen_guard.py seal <cell>`.
