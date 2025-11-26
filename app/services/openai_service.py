# app/services/openai_service.py
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.base import BaseLLMService

class OpenAIService(BaseLLMService):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(self, messages: list[dict]) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4.1",
            messages=messages
        )
        return response.choices[0].message.content


    async def ainvoke(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        return await self.chat(messages)
    
    async def run(self, prompt: str) -> str:
        return await self.ainvoke(prompt)