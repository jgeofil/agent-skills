from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class MitigationAction(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    resource_type: Literal["GCE_INSTANCE", "VERTEX_NOTEBOOK", "GKE_NODE_POOL"]
    resource_id: str = Field(min_length=1)
    action: Literal["STOP", "SCALE_DOWN", "DELETE"]


class PolicyDecision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    project_id: str
    triggered_tier: Literal["NORMAL", "SOFT_BUDGET_EXCEEDED", "HARD_CAP_BREACHED"]
    actions: list[MitigationAction] = Field(default_factory=list)