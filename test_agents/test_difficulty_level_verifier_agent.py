import pytest
from app.core.agents.difficulty_level_verifier_agent import (
    run_difficulty_level_verifier_agent,
)

# --- טסטים עם ובלי טקסט עבור כל רמת קושי ---
test_cases = [
    # ===================== התאמות =====================
    {
        "name": "Easy - factual question (no text)",
        "input": {
            "question": "מהי בירת ספרד?",
            "text": "",
            "difficulty_level": "נמוכה",
        },
        "expected": {"matches_target": True},
    },
    {
        "name": "Medium - explanation (with text)",
        "input": {
            "question": "הסבר כיצד פועלת מערכת העיכול.",
            "text": "מערכת העיכול כוללת את הפה, הקיבה, המעיים ואת פעולת הספיגה של המזון.",
            "difficulty_level": "בינונית",
        },
        "expected": {"matches_target": True},
    },
    {
        "name": "Hard - evaluation (with text)",
        "input": {
            "question": "הערך את תרומת מהפכת ההשכלה לעיצוב הדמוקרטיה המודרנית.",
            "text": "מהפכת ההשכלה הביאה להפצת רעיונות של חירות, שוויון וזכויות פרט, שהשפיעו על מבני השלטון.",
            "difficulty_level": "גבוהה",
        },
        "expected": {"matches_target": True},
    },

    # ===================== אי-התאמות =====================
    {
        "name": "Hard label - easy question (no text)",
        "input": {
            "question": "ציין שני צבעים בדגל צרפת.",
            "text": "",
            "difficulty_level": "גבוהה",
        },
        "expected": {"matches_target": False},
    },
    {
        "name": "Medium label - low-level recall (with text)",
        "input": {
            "question": "כמה יבשות יש בעולם?",
            "text": "ישנן שבע יבשות עיקריות בכדור הארץ.",
            "difficulty_level": "בינונית",
        },
        "expected": {"matches_target": False},
    },
    {
        "name": "Easy label - high cognitive task (with text)",
        "input": {
            "question": "השווה בין התנהלות שלטון האבסולוטיזם בצרפת ובאנגליה.",
            "text": "בצרפת, המלוכה האבסולוטית הגיעה לשיאה אצל לואי ה-14, בעוד שבאנגליה הייתה מגמה לחיזוק הפרלמנט.",
            "difficulty_level": "נמוכה",
        },
        "expected": {"matches_target": False},
    },
]

@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_cases, ids=[tc["name"] for tc in test_cases])
async def test_difficulty_level_verifier(case):
    result = await run_difficulty_level_verifier_agent(case["input"])
    print(
        f"\n🧠 Question: {case['input']['question']}\n"
        f"📚 Text: {case['input']['text']}\n"
        f"🎯 Target Level: {case['input']['difficulty_level']}\n"
        f"🤖 Detected: {result.get('detected_difficulty')} | "
        f"Score: {result.get('match_score')} | Match? {result.get('matches_target')}\n"
        f"🔍 Justification: {result.get('justification')}"
    )
    assert result["status"] == "ok", f"LLM failed: {result}"
    assert result["matches_target"] == case["expected"]["matches_target"], f"Wrong match decision.\nGot: {result}"
