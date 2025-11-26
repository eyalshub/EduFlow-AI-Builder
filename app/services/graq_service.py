# app/services/graq_service.py
import httpx
from app.services.base import BaseLLMService
from app.core.config import settings

class GraqService(BaseLLMService):
    async def chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.graq.cloud/chat",
                headers={
                    "Authorization": f"Bearer {settings.GRAQ_API_KEY}"
                },
                json={
                    "model": "mixtral-8x7b",
                    "messages": messages
                }
            )
            return response.json()["choices"][0]["message"]["content"]

