from pydantic import BaseModel
from typing import Optional
from app.services.llm_service import llm_service


class IntakeOutput(BaseModel):
    workload_description: str
    inferred_cloud: str
    estimated_users: Optional[int] = None
    needs_database: bool
    needs_auth: bool
    workload_type: str
    keywords: list[str]


SYSTEM_PROMPT = """You are an infrastructure requirements analyst.
Extract structured requirements from the user's request.
Respond ONLY with valid JSON. No explanation, no markdown, just JSON.

JSON schema:
{
  "workload_description": "short clean description",
  "inferred_cloud": "azure or aws or gcp or any",
  "estimated_users": null or integer,
  "needs_database": true or false,
  "needs_auth": true or false,
  "workload_type": "web-portal or data-pipeline or ml-inference or api-service",
  "keywords": ["list", "of", "key", "terms"]
}"""


async def run_intake(task, context: dict) -> dict:
    result = await llm_service.complete(
        system=SYSTEM_PROMPT,
        user=task.description,
        response_model=IntakeOutput
    )
    return result.model_dump()