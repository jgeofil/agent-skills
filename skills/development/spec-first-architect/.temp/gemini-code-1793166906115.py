from __future__ import annotations
from typing import Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field
from contracts.cost_policy_contract import MitigationAction


class ActionResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    resource_id: str
    status: Literal["SUCCESS", "FAILED", "DRY_RUN"]
    details: str


class CostActuator(Protocol):
    def apply_mitigations(self, project_id: str, actions: list[MitigationAction]) -> list[ActionResult]:
        ...