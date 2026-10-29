# Composition Root (`dist/main/`) & Operational Envelope Reference

The **Composition Root** is the sole architectural bridge between runtime environments (environment variables, CLI flags, host signals) and the isolated, machine-synthesized cells in `dist/`. It provides the operational envelope that transforms a set of cellular modules into an executable service or CLI.

---

## 1. Composition Root Invariants

| Attribute | Constraint | Enforcement |
| :--- | :--- | :--- |
| **Cell Path** | `dist/main/` (`__main__.py` or `index.ts`) | Sealed via `python3 scripts/regen_guard.py seal main --entrypoint` |
| **Max Size** | 200 LOC / 2,500 tokens | `regen_guard.py` aborts on size overflow |
| **Environment Reads** | Permitted to read `os.environ` / `process.env` | Only allowed under `--entrypoint` seal flag |
| **Cross-Cell Imports** | Permitted to import public entrypoints of sibling cells (`dist.<cell>`) | Only allowed under `--entrypoint` seal flag |
| **Domain Logic** | Zero internal business logic or complex data transformations | Must delegate to domain cells |
| **Mandatory CLI Flags** | `--dry-run` and `--once` (for polling engines/workers) | Verified during smoke test gate |

---

## 2. Anatomy of the Composition Root Cell

A complete Composition Root consists of four synchronized artifacts:

### 1. Configuration Contract (`contracts/main_contract.py` / `.ts`)
Strict validation schema for runtime options:
```python
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class RuntimeConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    project_id: str = Field(min_length=1)
    enforcement_mode: Literal["DRY_RUN", "ENFORCE"] = "DRY_RUN"
    poll_interval_seconds: int = Field(default=300, ge=0)
```

### 2. Composition Specification (`specs/main.spec.md`)
Declares wiring sequence, CLI flag precedence, and shutdown behavior:
```markdown
# SPEC: main (Composition Root & CLI Entrypoint)

## 1. Cell Metadata & Regeneration Budget
| Attribute | Constraint |
| :--- | :--- |
| **Cell ID** | `main` (`--entrypoint`) |
| **Contract Path** | `contracts/main_contract.py` |
| **Committed Artifact Path** | `dist/main/__main__.py` |
| **Max Implementation Size** | 200 LOC |

## 2. Pipeline Orchestration Sequence
1. Parse environment variables and CLI arguments into `RuntimeConfig`.
2. CLI `--dry-run` unconditionally overrides `enforcement_mode` to `"DRY_RUN"`.
3. Instantiate I/O transport handles and invoke ingestor/adapter cells.
4. Pass snapshots into pure domain cells to compute policy decisions.
5. If `enforcement_mode == "DRY_RUN"`, log actions to stdout as JSON and exit `0`.
6. Otherwise, execute approved actions via actuator cells.
```

### 3. Implementation (`dist/main/__main__.py` / `dist/main/index.ts`)
```python
from __future__ import annotations
import argparse
import json
import os
import sys
from contracts.main_contract import RuntimeConfig
from dist.billing_ingestor import fetch_spend_snapshot
from dist.policy_evaluator import evaluate_cost_policy
from dist.resource_actuator import execute_mitigations

def load_config(force_dry_run: bool) -> RuntimeConfig:
    mode = "DRY_RUN" if force_dry_run else os.environ.get("ENFORCEMENT_MODE", "DRY_RUN")
    return RuntimeConfig(
        project_id=os.environ["GCP_PROJECT_ID"],
        enforcement_mode=mode, # type: ignore[arg-type]
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Service Runner")
    parser.add_argument("--dry-run", action="store_true", help="Audit mode without mutations")
    parser.add_argument("--once", action="store_true", help="Execute single cycle and exit")
    args = parser.parse_args()

    cfg = load_config(force_dry_run=args.dry_run)
    snapshot = fetch_spend_snapshot(cfg.project_id)
    decision = evaluate_cost_policy(snapshot)

    if cfg.enforcement_mode == "DRY_RUN":
        print(json.dumps(decision.model_dump(), indent=2))
        return 0

    results = execute_mitigations(cfg.project_id, decision.actions)
    print(json.dumps([r.model_dump() for r in results], indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 3. Operational Envelope: `deploy/` & `README.md`

Every repository generated or governed by `spec-first-architect` must deliver production deployment manifests and an operational runbook:

### `deploy/Dockerfile`
```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY contracts/ ./contracts/
COPY dist/ ./dist/

USER 1000:1000
ENTRYPOINT ["uv", "run", "python", "-m", "dist.main"]
```

### `deploy/docker-compose.yml`
```yaml
services:
  service-name:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    restart: unless-stopped
    environment:
      ENFORCEMENT_MODE: "${ENFORCEMENT_MODE:-DRY_RUN}"
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: "0.25"
```

### `README.md` Runbook Requirements
Root documentation must provide:
1. **Pipeline Architecture Diagram:** ASCII or Mermaid diagram of data flow between cells.
2. **Environment Variable Table:** Name, type, default value, and IAM permission scope.
3. **Local Dry-Run Command:** Exact shell snippet to run a safe `--dry-run --once` evaluation.
4. **Cell Regeneration Command:** Exact `regen_guard.py` sequence for regenerating any component cell.
5. **Deployment Command:** Production `docker compose` or cloud deployment invocation.
