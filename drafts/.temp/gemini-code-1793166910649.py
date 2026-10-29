from __future__ import annotations
from typing import Protocol
from pydantic import BaseModel, ConfigDict, Field


class SpendSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    project_id: str = Field(min_length=1)
    current_spend_usd: float = Field(ge=0.0)
    projected_spend_usd: float = Field(ge=0.0)
    active_gce_instances: int = Field(ge=0)
    active_gpu_count: int = Field(ge=0)


class CostIngestor(Protocol):
    def fetch_spend(self, project_id: str) -> SpendSnapshot:
        ...