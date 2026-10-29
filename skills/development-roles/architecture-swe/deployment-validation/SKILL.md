---
name: deployment-validation
description: >-
  Validates application configurations, environment variables, multi-cloud infrastructure schemas, and deployment readiness before release. Use when auditing deployment configs, checking environment consistency across stages, or establishing automated configuration validation. Triggers: config validate, deployment validation, env check, cloud architecture audit.
license: MIT
metadata:
  version: "1.0"
  category: architecture-swe
---

# Deployment & Configuration Validation

Ensure zero-defect deployments through schema-driven configuration validation, environment drift detection, and multi-cloud infrastructure compliance.

## When to Use This Skill

- Validating environment variables and secret injection across staging and production
- Enforcing typed schema validation (Zod, Pydantic, JSON Schema) on runtime configs
- Verifying infrastructure readiness prior to traffic shifting or canary release
- Preventing application startup crashes caused by misconfigured environment variables

## Validation Checklist

1. **Schema Integrity**: Validate all keys against typed schemas with strict type and format constraints.
2. **Environment Separation**: Ensure production secrets and URLs are never present in test/staging manifests.
3. **Fail-Fast Startup**: Crash immediately on boot if any required variable or external dependency is unreachable.
4. **Drift Detection**: Detect discrepancies between desired infrastructure state and live configuration.

## Reference Documentation

- [Configuration Validation Framework & Schemas](references/config-validation.md)
- [Multi-Cloud Architecture Guidelines](references/cloud-architecture.md)
