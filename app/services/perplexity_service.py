# app/services/perplexity_service.py
import httpx
from app.services.base import BaseLLMService
from app.core.config import settings

class PerplexityService(BaseLLMService):
    async def chat(self, messages: list[dict]) -> str:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar",  # Specify the model you want to use
            "messages": messages,
            "stream": False
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        data = response.json()
        print("Perplexity Response:", data)  

        if "choices" in data and "message" in data["choices"][0]:
            return data["choices"][0]["message"]["content"]
        elif "text" in data:
            return data["text"]
        else:
            return f"Unexpected response format: {data}"
