---
name: frontend-refactor-planner
description: >-
  Creates safe, phased refactor plans for complex or legacy frontend codebases. Covers component splitting strategies, state simplification, performance profiling, accessibility auditing, and incremental migration plans. Use when refactoring "legacy code", "messy components", "performance issues", or "large files".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Frontend Refactor Planner

Structure, prioritize, and execute safe refactoring of complex frontend components and legacy UI code without regressions.

## When to Use This Skill

- Decomposing monolithic components (>300 lines) into clean composable units
- Untangling deeply nested prop drilling and consolidating fragmented state
- Eliminating excessive re-renders, bundle bloat, or UI lag
- Modernizing legacy class components or outdated patterns to modern hooks/RSC

## The 4-Phase Refactoring Protocol

```text
Phase 1: Characterize & Stabilize (Zero Behavioral Change)
                  |
                  v
Phase 2: Extract & Decouple (Isolate Pure Logic & Types)
                  |
                  v
Phase 3: Restructure & Simplify (Compound Components & State)
                  |
                  v
Phase 4: Optimize & Verify (Perf Benchmarking & Accessibility)
```

### Phase 1: Characterize & Stabilize
- **Baseline Test Coverage**: Write characterization tests verifying current behavior before touching implementation code.
- **Visual Baseline**: Snapshot current UI states (Storybook or Cypress/Playwright visual regression).
- **Metric Anchor**: Record baseline bundle size, render duration, and lighthouse accessibility score.

### Phase 2: Extract & Decouple
- Extract pure business logic and calculation routines into standalone, testable utility functions.
- Move TypeScript interface declarations to dedicated domain type modules.
- Separate data-fetching logic into custom hooks (`useUserData`, `useInventoryQuery`).

### Phase 3: Restructure & Simplify
- **Compound Component Pattern**: Replace mega-components with compound child components (`Table.Header`, `Table.Row`, `Table.Cell`).
- **State Colocation**: Push state as close as possible to where it is consumed; move shared state to Zustand or React Context.
- **Eliminate Prop Drilling**: Replace 4+ layer prop pass-throughs with composition (`children` or scoped context).

### Phase 4: Optimize & Verify
- Profile re-renders using React DevTools Profiler; wrap heavy compute in `useMemo`.
- Enforce accessibility compliance: keyboard focus trapping, ARIA roles, contrast check.
- Confirm zero test regressions and verify bundle size delta.

## Done Criteria Checklist

- [ ] All unit and integration tests passing with >=80% coverage on refactored modules
- [ ] No regression in Core Web Vitals (INP, LCP, CLS)
- [ ] Accessibility score >= 95 with zero critical AXE violations
- [ ] TypeScript strict mode passes with zero `any` casts

## Spec-First Alignment (Reverse Ratcheting)

> [!TIP]
> In **Spec-First codebases (`spec-first-architect-v2`)**, legacy frontend decomposition avoids endless in-place patching. Instead, use **Reverse Ratcheting**:
> 1. Prototype component interactions in a timeboxed `scratch/` spike.
> 2. Extract types into Layer 1 `contracts/` and interaction invariants into Layer 2 `specs/`.
> 3. Freeze visual/behavioral fixtures in Layer 3 `tests/`.
> 4. Synthesize clean, disposable UI cells into `dist/` and lock them via `regen_guard.py seal`.

## Related Skills

- `spec-first-architect-v2` — Cellular disposable code generation and reverse ratcheting workflow
- `component-scaffold-generator` — Scaffolding standardized frontend components
- `page-layout-builder` — Structuring page-level UI hierarchies
