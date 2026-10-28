from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    gcp_project_id: str = Field(min_length=1)
    monthly_budget_usd: float = Field(gt=0.0)
    hard_cap_usd: float = Field(gt=0.0)
    enforcement_mode: Literal["DRY_RUN", "SCALE_DOWN", "DISABLE_BILLING"] = "DRY_RUN"
    poll_interval_seconds: int = Field(default=300, ge=0)