# app/services/anthropic_service.py
import httpx
from app.services.base import BaseLLMService
from app.services.request_utils import format_messages_as_prompt
from app.core.config import settings

class AnthropicService(BaseLLMService):
    async def chat(self, messages: list[dict]) -> str:
        prompt = format_messages_as_prompt(messages, style="claude")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/complete",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-3-opus-20240229",
                    "prompt": prompt,
                    "max_tokens": 512,
                    "stop_sequences": ["\nHuman:"]
                }
            )
            return response.json()["completion"]