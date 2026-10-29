---
name: deployment-strategies
description: >-
  Implement zero-downtime deployment strategies including Blue-Green, Canary releases, Rolling updates, GitOps automation (ArgoCD, Flux), and progressive delivery. Use when designing deployment pipelines, configuring release rollouts, or establishing GitOps workflows. Triggers: blue-green deployment, canary release, rolling update, GitOps, progressive delivery.
license: MIT
metadata:
  version: "1.0"
  category: ci-cd-swe
---

# Deployment Strategies

Master modern deployment patterns and progressive delivery workflows to achieve zero-downtime releases and automated rollouts.

## When to Use This Skill

- Designing release pipelines requiring zero-downtime cutovers
- Implementing canary deployments with metric-based progressive promotion
- Setting up GitOps continuous delivery with ArgoCD or Flux
- Configuring rolling updates with health checks and graceful termination
- Establishing automated promotion and emergency abort mechanisms

## Strategy Comparison

| Strategy | Downtime | Resource Cost | Rollback Speed | Complexity | Best For |
|---|---|---|---|---|---|
| **Recreate** | Yes | Low | Slow | Low | Dev / Non-critical |
| **Rolling** | Zero | Medium | Medium | Medium | General microservices |
| **Blue-Green** | Zero | High (2x) | Instant | Medium | Monoliths, stateful apps |
| **Canary** | Zero | Medium | Fast | High | High-traffic services |
| **GitOps** | Zero | Medium | Fast (git revert) | Medium | Kubernetes clusters |

## Core Principles

1. **Traffic Shifting**: Shift traffic gradually (e.g. 5% -> 25% -> 50% -> 100%) while observing error rates and latency.
2. **Automated Rollback Criteria**: Define explicit SLO thresholds (e.g. error rate > 0.5% for 2 mins) that immediately trigger rollback.
3. **Graceful Connection Draining**: Always allow in-flight HTTP and WebSocket connections to terminate cleanly.

## Reference Documentation

- [Deployment Engineering & GitOps Patterns](references/deployment-engineer.md)
- [Infrastructure as Code Deployment Guidelines](references/terraform-specialist.md)
