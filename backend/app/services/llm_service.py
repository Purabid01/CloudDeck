import httpx
import json
from typing import Type, TypeVar
from pydantic import BaseModel

from app.core.config import settings

T = TypeVar('T', bound=BaseModel)


class LLMService:

    async def complete(
        self,
        system: str,
        user: str,
        response_model: Type[T],
        max_retries: int = 3
    ) -> T:
        """
        Send a prompt to Ollama and parse response into a Pydantic model.
        Retries up to max_retries times if parsing fails.
        """
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{settings.ollama_url}/api/chat",
                        json={
                            "model": settings.ollama_model,
                            "messages": messages,
                            "stream": False    # wait for full response
                        }
                    )
                    response.raise_for_status()
                    data = response.json()

                    # extract the actual text content
                    content = data["message"]["content"]

                    # clean markdown code blocks if LLM wrapped JSON in ```
                    content = content.strip()
                    if content.startswith("```"):
                        lines = content.split("\n")
                        content = "\n".join(lines[1:-1])

                    # parse into Pydantic model
                    parsed = response_model.model_validate_json(content)
                    return parsed

            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"LLM failed after {max_retries} attempts: {str(e)}"
                    )
                # retry with a hint
                messages.append({
                    "role": "assistant",
                    "content": content if 'content' in locals() else ""
                })
                messages.append({
                    "role": "user",
                    "content": f"Your response was invalid. Return ONLY valid JSON matching the schema. Error: {str(e)}"
                })


# singleton
llm_service = LLMService()