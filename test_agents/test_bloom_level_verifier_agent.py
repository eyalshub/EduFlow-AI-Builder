import pytest
from app.core.agents.bloom_level_verifier_agent import run_bloom_level_verifier_agent

DEBUG = True

@pytest.mark.asyncio
@pytest.mark.parametrize("input", [
    # --- Hebrew inputs ---
    {"question": "הסבר מדוע פרצה המהפכה הצרפתית.", "bloom_level": "הבנה ויישום"},
    {"question": "מנה את שלושת המרכיבים של מערכת הדם.", "bloom_level": "ידע ואיתור מידע"},
    {"question": "האם אתה מסכים עם טענת הכותב? נמק.", "bloom_level": "הסקת מסקנות והערכה"},

    # --- English inputs ---
    {"question": "List three causes of World War I.", "bloom_level": "ידע ואיתור מידע"},
    {"question": "Explain the impact of the printing press on European society.", "bloom_level": "הבנה ויישום"},
    {"question": "Do you agree with the author's claim? Justify your opinion.", "bloom_level": "הסקת מסקנות והערכה"},
])
async def test_bloom_level_verifier_valid(input):
    result = await run_bloom_level_verifier_agent(input)

    if DEBUG:
        print(f"\n🧠 Question: {input['question']}")
        print(f"🎯 Target Level: {input['bloom_level']}")
        print(f"🤖 Detected: {result.get('detected_level')} | Score: {result.get('match_score')} | Match? {result.get('matches_target')}")
        print(f"🔍 Justification: {result.get('justification')}")

    assert result["status"] == "ok"
    assert isinstance(result["match_score"], float)
    assert 0.0 <= result["match_score"] <= 1.0
    assert isinstance(result["matches_target"], bool)
    assert isinstance(result["justification"], str)


@pytest.mark.asyncio
@pytest.mark.parametrize("input", [
    # mismatched inputs
    {"question": "האם אתה מסכים עם טענת הכותב? נמק.", "bloom_level": "ידע ואיתור מידע"},
    {"question": "הסבר את השפעת המהפכה התעשייתית על החברה.", "bloom_level": "ידע ואיתור מידע"},
    {"question": "List the main steps of the scientific method.", "bloom_level": "הסקת מסקנות והערכה"},
])
async def test_bloom_level_verifier_mismatches(input):
    result = await run_bloom_level_verifier_agent(input)

    if DEBUG:
        print(f"\n🧠 Question: {input['question']}")
        print(f"🎯 Target Level: {input['bloom_level']}")
        print(f"🤖 Detected: {result.get('detected_level')} | Score: {result.get('match_score')} | Match? {result.get('matches_target')}")
        print(f"🔍 Justification: {result.get('justification')}")

    assert result["status"] == "ok"
    assert isinstance(result["match_score"], float)
    assert 0.0 <= result["match_score"] <= 1.0
    assert isinstance(result["matches_target"], bool)
    assert isinstance(result["justification"], str)
