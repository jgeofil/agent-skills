---
name: event-sourcing-cqrs
description: >-
  Design and implement event-driven architectures using Event Sourcing, CQRS (Command Query Responsibility Segregation), projections, and distributed sagas. Use when designing append-only event stores, separating read/write models, building audit trails, or orchestrating cross-aggregate distributed transactions. Triggers: event sourcing, CQRS, event store, projection, saga, domain events.
license: MIT
metadata:
  version: "1.0"
  category: architecture-swe
---

# Event Sourcing & CQRS

Master event-driven data architectures combining Event Sourcing, CQRS, projections, and sagas for highly scalable, auditable distributed systems.

## When to Use This Skill

- Decoupling read performance from write throughput (CQRS)
- Implementing complete domain auditability with append-only logs (Event Sourcing)
- Materializing query-optimized views from event streams (Projections)
- Coordinating multi-step cross-service business transactions (Sagas)
- High-concurrency systems requiring conflict detection and replayability

## Architecture Overview

```text
Command -> Command Handler -> Aggregate Root -> Event Store
                                                    | (Event Bus / Stream)
                                                    v
                                         +------------------+
                                         |                  |
                                         v                  v
                                   Projection Worker   Saga Coordinator
                                         |                  |
                                         v                  v
                                    Read Database    Compensating Commands
```



## Core Principles

1. **Commands vs. Events**: Commands represent intent (may fail); Events represent immutable facts (already occurred).
2. **Aggregates as Consistency Boundaries**: Protect invariants; load state by replaying past events.
3. **Idempotent Projections**: Read models must handle out-of-order or duplicate events gracefully.
4. **Compensating Actions in Sagas**: Coordinate distributed workflows with explicit rollback/compensation logic.

## Reference Documentation

- [CQRS Implementation Guide](references/cqrs.md)
- [Event Store Design Patterns](references/event-store.md)
- [Projection Patterns & Read Models](references/projections.md)
- [Saga Orchestration & Compensation](references/sagas.md)
