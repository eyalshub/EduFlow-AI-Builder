# app/services/gemini_service.py
import httpx
from app.services.base import BaseLLMService
from app.core.config import settings

class GeminiService(BaseLLMService):
    async def chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                params={"key": settings.GOOGLE_API_KEY},
                json={
                    "contents": [{"parts": [{"text": m["content"]} for m in messages]}]
                }
            )
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
