# app/stage_1/fetchers/perplexity_fetcher.py

import datetime
from typing import Optional

from app.services.fetchers.wikipedia_fetcher import fetch_wikipedia_summary
from app.services.factory import get_llm_service


def build_perplexity_prompt(topic: str, subject: str, lang: str, wiki_summary: Optional[str] = None) -> str:
    base_prompt = f"""
You are an educational AI researcher.
Your task is to generate a high-quality, concise summary about the topic below,
suitable for a middle/high school lesson in the subject of {subject}.
Language: {lang.upper()}

Topic: {topic}
"""
    if wiki_summary:
        base_prompt += f"\nHere is some background information from Wikipedia to help you start:\n\n{wiki_summary}\n"
    base_prompt += "\nPlease return a coherent summary suitable for educational use."
    return base_prompt.strip()


async def fetch_perplexity_summary(topic: str, subject: str = "General", lang: str = "he") -> dict:
    """
    Simulates Perplexity.ai fast content acquisition for Stage 1.
    Returns a sourceChunk-formatted dictionary.
    """
    # Optional: Try to get Wikipedia summary to support LLM
    wiki_summary = fetch_wikipedia_summary(topic, lang=lang)

    prompt = build_perplexity_prompt(topic, subject, lang, wiki_summary)

    # Get LLM (simulating perplexity behavior)
    llm = get_llm_service(provider="openai")
    result = await llm.ainvoke(prompt)

    return {
        "sourceType": "Perplexity_Search",
        "sourceQuery": topic,
        "sourceURI": "https://www.perplexity.ai/search/mock",  # Replace if needed
        "retrievedAt": datetime.datetime.utcnow().isoformat() + "Z",
        "processedContent": {
            "summary": result,
            "sections": []  # Sections will be added later in stage 4
        }
    }


__all__ = ["fetch_perplexity_summary"]
