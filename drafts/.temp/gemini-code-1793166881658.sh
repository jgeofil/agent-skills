export GCP_PROJECT_ID="my-gcp-project-123"
export MONTHLY_BUDGET_USD="50.0"
export HARD_CAP_USD="80.0"
uv run python -m dist.main --dry-run --once