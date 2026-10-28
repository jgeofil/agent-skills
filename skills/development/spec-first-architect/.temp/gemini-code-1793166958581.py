from __future__ import annotations
import argparse
import json
import os
import sys
import time
from contracts.main_contract import RuntimeConfig
# Import public entrypoints of your generated component cells:
from dist.billing_ingestor import fetch_spend_snapshot
from dist.policy_evaluator import evaluate_cost_policy
from dist.resource_actuator import execute_mitigations


def load_config(force_dry_run: bool) -> RuntimeConfig:
    mode = "DRY_RUN" if force_dry_run else os.environ.get("ENFORCEMENT_MODE", "DRY_RUN")
    return RuntimeConfig(
        gcp_project_id=os.environ["GCP_PROJECT_ID"],
        monthly_budget_usd=float(os.environ.get("MONTHLY_BUDGET_USD", "100.0")),
        hard_cap_usd=float(os.environ.get("HARD_CAP_USD", "150.0")),
        enforcement_mode=mode,  # type: ignore[arg-type]
        poll_interval_seconds=int(os.environ.get("POLL_INTERVAL_SECONDS", "300")),
    )


def run_cycle(cfg: RuntimeConfig) -> int:
    snapshot = fetch_spend_snapshot(project_id=cfg.gcp_project_id)
    decision = evaluate_cost_policy(
        snapshot=snapshot,
        soft_budget_usd=cfg.monthly_budget_usd,
        hard_cap_usd=cfg.hard_cap_usd,
    )

    if cfg.enforcement_mode == "DRY_RUN" or not decision.actions:
        print(json.dumps({
            "mode": cfg.enforcement_mode,
            "current_spend_usd": snapshot.current_spend_usd,
            "planned_actions": [a.model_dump() for a in decision.actions],
        }))
        return 0

    results = execute_mitigations(project_id=cfg.gcp_project_id, actions=decision.actions)
    print(json.dumps({"mode": cfg.enforcement_mode, "executed": [r.model_dump() for r in results]}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="GCP Cloud Cost Control Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Log mitigation plan without mutating GCP resources")
    parser.add_argument("--once", action="store_true", help="Execute a single evaluation pass and exit")
    args = parser.parse_args()

    cfg = load_config(force_dry_run=args.dry_run)
    if args.once or cfg.poll_interval_seconds == 0:
        return run_cycle(cfg)

    while True:
        run_cycle(cfg)
        time.sleep(cfg.poll_interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())