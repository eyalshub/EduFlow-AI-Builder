# test_fetchers/test_fetch_perplexity.py

import asyncio
from app.stage_1.fetchers.perplexity_fetcher import fetch_perplexity_summary

async def run_test():
    topic = "French Revolution"
    subject = "History"
    lang = "en"

    print("⏳ Testing fetch_perplexity_summary...")
    result = await fetch_perplexity_summary(topic=topic, subject=subject, lang=lang)

    assert isinstance(result, dict), "Result should be a dictionary"
    assert result.get("sourceType") == "Perplexity_Search", "Wrong source type"
    assert "summary" in result.get("processedContent", {}), "Missing summary in processedContent"
    assert len(result["processedContent"]["summary"]) > 30, "Summary too short"
    
    print("✅ Perplexity fetcher test passed.")
    print("\n📘 Summary Preview:\n")
    print(result["processedContent"]["summary"])

if __name__ == "__main__":
    asyncio.run(run_test())
