from __future__ import annotations
from contracts.cost_ingestor_contract import SpendSnapshot
from contracts.cost_policy_contract import MitigationAction, PolicyDecision


def evaluate_policy(snapshot: SpendSnapshot, soft_budget_usd: float, hard_cap_usd: float) -> PolicyDecision:
    if snapshot.projected_spend_usd >= hard_cap_usd:
        actions = [
            MitigationAction(resource_type="GCE_INSTANCE", resource_id="heavy-worker-gpu-0", action="STOP"),
            MitigationAction(resource_type="VERTEX_NOTEBOOK", resource_id="jupyter-dev-instance", action="STOP"),
        ]
        return PolicyDecision(
            project_id=snapshot.project_id,
            triggered_tier="HARD_CAP_BREACHED",
            actions=actions,
        )
    elif snapshot.current_spend_usd >= soft_budget_usd:
        return PolicyDecision(
            project_id=snapshot.project_id,
            triggered_tier="SOFT_BUDGET_EXCEEDED",
            actions=[MitigationAction(resource_type="GCE_INSTANCE", resource_id="staging-runner-1", action="SCALE_DOWN")],
        )
    return PolicyDecision(project_id=snapshot.project_id, triggered_tier="NORMAL", actions=[])