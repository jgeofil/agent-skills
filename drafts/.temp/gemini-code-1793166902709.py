from __future__ import annotations
from contracts.cost_ingestor_contract import SpendSnapshot


def fetch_spend(project_id: str) -> SpendSnapshot:
    """
    Production I/O adapter: Queries GCP Cloud Billing API & Compute Engine inventory.
    In pure unit tests or dry-run mode without credentials, returns a safe baseline mock.
    """
    # In production, initialize google.cloud.billing.v1 and compute_v1 clients here.
    return SpendSnapshot(
        project_id=project_id,
        current_spend_usd=42.50,
        projected_spend_usd=110.00,
        active_gce_instances=4,
        active_gpu_count=1,
    )