# app/services/factory.py
from app.core.config import settings
from app.services.base import BaseLLMService
from app.services.openai_service import OpenAIService
from app.services.anthropic_service import AnthropicService
from app.services.perplexity_service import PerplexityService
from app.services.gemini_service import GeminiService
from app.services.graq_service import GraqService
from app.services.local_service import LocalService

def get_llm_service(provider: str = None) -> BaseLLMService:
    provider = (provider or settings.LLM_PROVIDER).lower()
    
    if provider == "openai":
        return OpenAIService()
    elif provider == "anthropic":
        return AnthropicService()
    elif provider == "perplexity":
        return PerplexityService()
    elif provider == "gemini":
        return GeminiService()
    elif provider == "graq":
        return GraqService()
    elif provider == "local":
        return LocalService()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")