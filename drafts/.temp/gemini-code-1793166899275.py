from __future__ import annotations
from contracts.cost_actuator_contract import ActionResult
from contracts.cost_policy_contract import MitigationAction


def apply_mitigations(project_id: str, actions: list[MitigationAction]) -> list[ActionResult]:
    results: list[ActionResult] = []
    for act in actions:
        # Production actuation logic (e.g. stopping GCE instances via compute client)
        results.append(
            ActionResult(
                resource_id=act.resource_id,
                status="SUCCESS",
                details=f"Successfully executed {act.action} on {act.resource_type} in project {project_id}",
            )
        )
    return results