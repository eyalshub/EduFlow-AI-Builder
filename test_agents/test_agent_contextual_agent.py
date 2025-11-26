# test_agents/test_agent_contextual_agent.py

import pytest
import json
from app.core.agents.contextual_agent import run_contextual_agent
from app.schemas.input_model import Stage1Input

# 🔍 Pretty print helper for inspection
def print_result(title: str, raw: str):
    print(f"\n🧪 TEST CASE: {title}")
    print("📘 RAW OUTPUT:")
    print(raw)
    try:
        parsed = json.loads(raw)
        print("✅ PARSED JSON:")
        for key, value in parsed.items():
            print(f"- {key}: {value}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON PARSE ERROR: {e}")

# 🧪 Executes a single test case
async def run_test_case(title: str, **kwargs):
    inputs = Stage1Input(**kwargs)
    output = await run_contextual_agent(inputs)
    print_result(title, output)

    # Check JSON format
    assert output.strip().startswith("{") and output.strip().endswith("}")
    parsed = json.loads(output)

    # Required keys
    expected_keys = {
        "themes_to_revisit",
        "new_concepts_to_introduce",
        "skills_to_practice",
        "common_misconceptions_to_address",
        "pedagogical_notes"
    }
    assert expected_keys.issubset(parsed.keys()), f"Missing keys: {expected_keys - set(parsed.keys())}"

# 🚀 Full test suite for contextual agent
@pytest.mark.asyncio
async def test_contextual_agent_multiple_cases():
    await run_test_case(
        title="🇮🇱 Hebrew / History",
        topicName="המהפכה הצרפתית",
        subject="היסטוריה",
        gradeLevel="9",
        bigIdea="מהפכות משנות סדרי עולם",
        learningGate="Discovery Gate",
        skills=["הבנה ביקורתית", "ניתוח השוואתי"],
        context="בשיעור הקודם התלמידים למדו על עקרונות הנאורות והשפעתם על המחשבה המדינית.",
        freePrompt="התמקד בתפקיד של הפילוסופיה בנפילת המלוכה."
    )

    await run_test_case(
        title="🇬🇧 English / French Revolution",
        topicName="The French Revolution",
        subject="History",
        gradeLevel="9",
        bigIdea="Revolutions devour their own children.",
        learningGate="Discovery Gate",
        skills=["critical thinking", "historical analysis"],
        context="Students explored the Enlightenment and key philosophers like Rousseau and Locke.",
        freePrompt="Focus on how Enlightenment ideals influenced revolutionary leaders."
    )

    await run_test_case(
        title="🌍 Geography / Climate Change",
        topicName="Climate Systems",
        subject="Geography",
        gradeLevel="10",
        bigIdea="Climate shapes civilization.",
        learningGate="Meeting Gate",
        skills=["data interpretation", "comparison", "causal reasoning"],
        context="Students studied types of climate zones and examples from different continents.",
        freePrompt="Prepare for a lesson that introduces the effects of human activity on climate stability."
    )

    await run_test_case(
        title="🧬 Biology / Genetics",
        topicName="Genetic Inheritance",
        subject="Biology",
        gradeLevel="11",
        bigIdea="Traits are transmitted through patterns.",
        learningGate="Independence Gate",
        skills=["pattern recognition", "application", "prediction"],
        context="Last lesson introduced Mendel’s laws using pea plant examples.",
        freePrompt="Create a bridge to real-world genetic disorders using similar principles."
    )

    await run_test_case(
        title="📖 Literature / Macbeth",
        topicName="Macbeth",
        subject="Literature",
        gradeLevel="10",
        bigIdea="Ambition and power corrupt.",
        learningGate="Discovery Gate",
        skills=["literary analysis", "textual inference"],
        context="Students read Act 1 and discussed Macbeth’s initial motivations.",
        freePrompt="Encourage reflection on internal vs external conflict in Act 2."
    )
