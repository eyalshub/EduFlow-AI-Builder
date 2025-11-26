# test_agents/test_agent_course_scoping_agent.py

import asyncio
import pytest
from app.core.agents.course_scoping_agent import run_course_scoping_agent
from app.schemas.input_model import Stage1Input


@pytest.mark.asyncio
async def test_course_scoping_agent_basic():
    """Test the course scoping agent with a standard English topic."""
    inputs = Stage1Input(
        topicName="The French Revolution",
        subject="History",
        gradeLevel="9",
        bigIdea="Revolutions devour their own children.",
        learningGate="Discovery Gate",
        skills=["critical thinking", "historical analysis"],
        numLessons=4
    )
    result = await run_course_scoping_agent(inputs)
    print("\n📘 Lesson Titles:")
    for r in result:
        print("-", r)
    assert len(result) == 4


@pytest.mark.asyncio
async def test_course_scoping_agent_with_contextual_profile():
    """Simulates the use of contextual_course_agent output passed downstream."""
    pedagogical_json = {
        "themes_to_revisit": [
            "Inequality between social classes",
            "Abuse of power and monarchy",
            "Desire for democratic reform"
        ],
        "new_concepts_to_introduce": [
            "The Reign of Terror",
            "The Declaration of the Rights of Man",
            "Rise of Napoleon"
        ],
        "skills_to_practice": [
            "critical thinking",
            "historical analysis",
            "inference"
        ],
        "common_misconceptions_to_address": [
            "All revolutionaries supported democracy",
            "The French Revolution ended quickly"
        ],
        "pedagogical_notes": "Use storytelling and visual timelines to engage students. Begin with real-world connections to injustice. Encourage questioning and debate."
    }

    inputs = Stage1Input(
        topicName="The French Revolution",
        subject="History",
        gradeLevel="9",
        bigIdea="Revolutions devour their own children.",
        learningGate="Discovery Gate",
        skills=pedagogical_json["skills_to_practice"],
        numLessons=5
    )

    result = await run_course_scoping_agent(inputs)
    print("\n📘 Lesson Titles (with context):")
    for r in result:
        print("-", r)
    assert len(result) == 5


@pytest.mark.asyncio
async def test_course_scoping_agent_hebrew_topic():
    """Test with a Hebrew topic to ensure Hebrew fallback logic works."""
    inputs = Stage1Input(
        topicName="המהפכה התעשייתית",
        subject="היסטוריה",
        gradeLevel="10",
        bigIdea="שינויים טכנולוגיים יוצרים מהפכות חברתיות",
        learningGate="Independence Gate",
        skills=["ניתוח היסטורי", "השוואה בין תקופות"],
        numLessons=5
    )
    result = await run_course_scoping_agent(inputs)
    print("\n📘 כותרות שיעור (בעברית):")
    for r in result:
        print("-", r)
    assert len(result) == 5
