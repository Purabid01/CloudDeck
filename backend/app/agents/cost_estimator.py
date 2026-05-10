from pydantic import BaseModel
from typing import Optional
from app.services.llm_service import llm_service


class CostItem(BaseModel):
    service: str
    monthly_usd: float


class CostOutput(BaseModel):
    total_monthly_usd: float
    breakdown: list[CostItem]
    sizing_tier: str
    tip: str


SYSTEM_PROMPT = """You are a cloud cost estimator.
Given a blueprint and workload size, estimate the monthly cost.
Respond ONLY with valid JSON. No explanation, no markdown, just JSON.

JSON schema:
{
  "total_monthly_usd": float,
  "breakdown": [{"service": "name", "monthly_usd": float}],
  "sizing_tier": "xs or s or m or l",
  "tip": "one cost saving tip"
}"""


async def run_cost_estimator(task, context: dict) -> dict:
    intake = context.get("intake", {})
    blueprint = context.get("blueprint_finder", {})

    user_message = f"""
Blueprint: {blueprint.get('blueprint_name')}
Estimated users: {intake.get('estimated_users', 'unknown')}
Needs database: {intake.get('needs_database')}
Needs auth: {intake.get('needs_auth')}

Estimate monthly Azure costs for a small deployment.
"""
    result = await llm_service.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        response_model=CostOutput
    )
    return result.model_dump()