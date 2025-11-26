# app/services/base.py
from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        pass