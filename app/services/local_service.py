# app/services/local_service.py
import httpx
from app.services.base import BaseLLMService
from app.core.config import settings

class LocalService(BaseLLMService):
    async def chat(self, messages: list[dict]) -> str:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages]) + "\nassistant:"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_HOST}/api/generate",
                json={"model": "mistral", "prompt": prompt, "stream": False}
            )
            return response.json()["response"]
