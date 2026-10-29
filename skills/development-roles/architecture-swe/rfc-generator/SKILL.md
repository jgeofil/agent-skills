---
name: rfc-generator
description: >-
  Generates Request for Comments documents for technical proposals including problem statement, solution design, alternatives, risks, and rollout plans. Use for "RFC", "technical proposals", "design docs", or "architecture proposals".
license: MIT
metadata:
  version: "1.0"
  category: architecture-swe
---

# RFC Generator

Create comprehensive technical proposals with RFCs.

## RFC Template

```markdown
# RFC-042: Implement Read Replicas for Analytics

**Status:** Draft | In Review | Accepted | Rejected | Implemented
**Author:** Alice (alice@example.com)
**Reviewers:** Bob, Charlie, David
**Created:** 2024-01-15
**Updated:** 2024-01-20
**Target Date:** Q1 2024

## Summary

Add PostgreSQL read replicas to separate analytical queries from transactional workload, improving database performance and enabling new analytics features.

## Problem Statement

### Current Situation

Our PostgreSQL database serves both transactional (OLTP) and analytical (OLAP) workloads:

- 1000 writes/min (checkout, orders, inventory)
- 5000 reads/min (user browsing, search)
- 500 analytics queries/min (dashboards, reports)

### Issues

1. **Performance degradation**: Analytics queries slow down transactions
2. **Resource contention**: Complex reports consume CPU/memory
3. **Blocking features**: Can't add more dashboards without impacting users
4. **Peak hour problems**: Analytics scheduled during business hours

### Impact

- Checkout p95 latency: 800ms (target: <300ms)
- Database CPU: 75% average, 95% peak
- Customer complaints about slow pages
- Product team blocked on analytics features

### Success Criteria

- Checkout latency <300ms p95
- Database CPU <50%
- Support 2x more analytics queries
- Zero impact on transactional performance

## Proposed Solution

### High-Level Design
```

┌─────────────┐
│ Primary │────────────────┐
│ (Write) │ │
└─────────────┘ │
▼
┌─────────────┐
│ Replica 1 │
│ (Read) │
└─────────────┘
▼
┌─────────────┐
│ Replica 2 │
│ (Analytics)│
└─────────────┘

````

### Architecture
1. **Primary database**: Handles all writes and critical reads
2. **Read Replica 1**: Serves user-facing read queries
3. **Read Replica 2**: Dedicated to analytics/reporting

### Routing Strategy
```typescript
const db = {
  primary: primaryConnection,
  read: replicaConnection,
  analytics: analyticsConnection,
};

// Write
await db.primary.users.create(data);

// Critical read (always fresh)
await db.primary.users.findById(id);

// Non-critical read (can be slightly stale)
await db.read.products.search(query);

// Analytics
await db.analytics.orders.aggregate(pipeline);
````

### Replication

- **Type:** Streaming replication
- **Lag:** <1 second for read replica, <5 seconds acceptable for analytics
- **Monitoring:** Alert if lag >5 seconds


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

