from pydantic import BaseModel
from app.services.llm_service import llm_service


class ClassifierOutput(BaseModel):
    pattern: str
    confidence: float
    reasoning: str


SYSTEM_PROMPT = """You are an infrastructure workload classifier.
Given a workload description and keywords, classify it into one pattern.
Respond ONLY with valid JSON. No explanation, no markdown, just JSON.

Patterns: web-portal, data-pipeline, ml-inference, api-service, etl, batch

JSON schema:
{
  "pattern": "the pattern name",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence why"
}"""


async def run_classifier(task, context: dict) -> dict:
    intake = context.get("intake", {})
    user_message = f"""
Workload: {intake.get('workload_description')}
Keywords: {intake.get('keywords')}
Type hint: {intake.get('workload_type')}
"""
    result = await llm_service.complete(
        system=SYSTEM_PROMPT,
        user=user_message,
        response_model=ClassifierOutput
    )
    return result.model_dump()