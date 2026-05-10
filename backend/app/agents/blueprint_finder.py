from pydantic import BaseModel
from typing import Optional
from app.services.llm_service import llm_service


# Local blueprint catalog — in production this comes from DB + vector search
BLUEPRINTS = [
    {
        "id": "bp-001",
        "name": "Azure Internal Web Portal",
        "description": "Simple web app with database and SSO. Ideal for internal tools.",
        "services": ["App Service", "Azure SQL", "VNet"],
        "base_cost": 177
    },
    {
        "id": "bp-002",
        "name": "Azure Data Pipeline",
        "description": "Batch ETL pipeline for data processing and transformation.",
        "services": ["Data Factory", "Azure SQL", "Storage"],
        "base_cost": 250
    },
    {
        "id": "bp-003",
        "name": "Azure ML Inference",
        "description": "Deploy ML models as REST API endpoints with auto-scaling.",
        "services": ["AKS", "Container Registry", "Azure ML"],
        "base_cost": 400
    }
]


class BlueprintOutput(BaseModel):
    blueprint_id: str
    blueprint_name: str
    confidence: float
    reasoning: str


SYSTEM_PROMPT = """You are an infrastructure blueprint specialist.
Given a workload description and pattern, pick the best blueprint from the catalog.
Respond ONLY with valid JSON. No explanation, no markdown, just JSON.

JSON schema:
{
  "blueprint_id": "the blueprint id",
  "blueprint_name": "the blueprint name",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence why this blueprint fits"
}"""


async def run_blueprint_finder(task, context: dict) -> dict:
    intake = context.get("intake", {})
    classifier = context.get("classifier", {})

    catalog_text = "\n".join([
        f"ID: {bp['id']} | Name: {bp['name']} | Description: {bp['description']}"
        for bp in BLUEPRINTS
    ])

    user_message = f"""
Workload: {intake.get('workload_description')}
Pattern: {classifier.get('pattern')}
Cloud preference: {intake.get('inferred_cloud')}

Available blueprints:
{catalog_text}
"""
    result = await llm_service.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        response_model=BlueprintOutput
    )
    return result.model_dump()