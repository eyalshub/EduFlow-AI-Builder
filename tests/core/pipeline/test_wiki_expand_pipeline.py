import pytest
import asyncio
import json

from app.core.pipeline.wiki_expand_pipeline import run_wiki_expand_pipeline


@pytest.mark.asyncio
async def test_run_wiki_expand_pipeline_basic():
    result = await run_wiki_expand_pipeline(
        topic="המהפכה הצרפתית",
        subject="History",
        grade_level="9",
        lang="he",
        learning_objective="התלמידים יבינו את הסיבות המרכזיות למהפכה"
    )

    assert result["status"] == "ok"
    assert "expandedContent" in result
    expanded = result["expandedContent"]

    # Check required fields in expanded content
    assert isinstance(expanded, dict)
    assert "coreExplanation" in expanded
    assert isinstance(expanded["coreExplanation"], str) and len(expanded["coreExplanation"]) > 100

    assert "keyVocabulary" in expanded
    assert isinstance(expanded["keyVocabulary"], list)
    assert len(expanded["keyVocabulary"]) >= 2

    assert "discussionQuestions" in expanded
    assert isinstance(expanded["discussionQuestions"], list)
    assert len(expanded["discussionQuestions"]) >= 1

    assert "bigIdea" in expanded
    assert isinstance(expanded["bigIdea"], str)

    print("\n✅ Test passed: Wiki expansion produced valid educational structure.")
    print("\n📘 Core Explanation preview:")
    print(expanded["coreExplanation"][:300])
