---
name: data-pipeline-architecture
description: >-
  Design and implement end-to-end batch and streaming data pipeline architectures including ingestion, orchestration, dbt transformations, data quality contracts, and lakehouse storage. Use when designing data pipelines, planning analytics infrastructure, or establishing data platform architecture. Triggers: data pipeline, batch pipeline, streaming pipeline, data architecture, ETL pipeline.
license: MIT
metadata:
  version: "1.0"
  category: data-scientist
---

# Data Pipeline Architecture

Architect reliable, performant, and cost-effective data pipelines across batch and streaming workloads using the modern data stack.

## When to Use This Skill

- Designing end-to-end data ingestion and transformation pipelines
- Selecting appropriate storage layers (Data Lake, Delta Lake, Iceberg, Snowflake, BigQuery)
- Structuring multi-stage data pipelines (Bronze -> Silver -> Gold / Medallion Architecture)
- Integrating orchestration (Airflow/Dagster), transformations (dbt), and processing (Spark)
- Enforcing end-to-end data quality checks, observability, and alerting

## Pipeline Architecture (Medallion Pattern)

```text
Raw Sources (APIs, DBs, Kafka)
              |
              v
[ Bronze Layer ] Raw ingestion, schema-on-read, append-only
              |
              v (Spark / dbt / SQL)
[ Silver Layer ] Cleaned, deduplicated, validated, normalized
              |
              v (Aggregations & Business Logic)
[ Gold Layer ]   Dimensional models (Star schema), feature stores, BI cubes
```

## Core Principles

1. **Idempotency**: Every pipeline run or backfill must produce identical results regardless of execution count.
2. **Schema Evolution**: Handle schema drift using versioned schemas and explicit migration protocols.
3. **Data Quality Gates**: Fail fast on contract violations before corrupting downstream Gold tables.
4. **Partitioning & Pruning**: Partition by query access patterns (e.g. `event_date`, `tenant_id`) to minimize compute cost.

## Reference Documentation

- [Data Pipeline Design & Specification](references/data-pipeline-design.md)
- [Data-Driven Feature Development Guide](references/data-driven-features.md)
- [Data Engineering Best Practices & Architecture](references/data-engineer-guide.md)
