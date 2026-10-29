---
name: workflow-orchestration
description: >-
  Design, implement, and test durable workflow orchestration systems (Temporal, Cadence, Step Functions). Use when building long-running business processes, human-in-the-loop workflows, distributed saga execution, or deterministic Python/TypeScript workflows. Triggers: Temporal, workflow orchestration, durable execution, activity retries.
license: MIT
metadata:
  version: "1.0"
  category: architecture-swe
---

# Workflow Orchestration

Design resilient, durable workflows and long-running distributed processes using modern orchestration frameworks (Temporal, Cadence, and cloud-native state machines).

## When to Use This Skill

- Building resilient multi-step workflows that must survive process restarts
- Managing asynchronous, multi-day, or human-in-the-loop business processes
- Coordinating distributed activities with automatic retries and exponential backoff
- Ensuring determinism and replay-testing safety in Python and TypeScript workflows

## Core Patterns

1. **Workflow Determinism**: Workflows must be deterministic; side-effects belong strictly in activities.
2. **Activity Retries & Timeouts**: Configure Schedule-to-Close, Start-to-Close, and Heartbeat timeouts.
3. **Replay & Compatibility Testing**: Verify that workflow definitions do not break in-flight histories.

## Reference Documentation

- [Workflow Orchestration Patterns](references/orchestration-patterns.md)
- [Temporal Python Testing & Replay Guide](references/temporal-resources/replay-testing.md)
- [Integration & Unit Testing](references/temporal-resources/unit-testing.md)
