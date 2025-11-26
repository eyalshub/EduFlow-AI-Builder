# test_agents/test_agent_lesson_content_full_flow.py

import asyncio
import pytest
from pprint import pprint

from app.core.agents.contextual_agent import run_contextual_agent
from app.core.agents.course_scoping_agent import run_course_scoping_agent
from app.core.agents.lesson_content_agent import run_lesson_content_agent
from app.schemas.input_model import Stage1Input, LessonContentAgentInput

@pytest.mark.asyncio
async def test_full_stage1_flow():
    # === Step 1: Input ===
    base_input = Stage1Input(
        topicName="The French Revolution",
        subject="History",
        gradeLevel="9",
        bigIdea="Revolutions challenge old systems and create new ones.",
        learningGate="Discovery Gate",
        skills=["critical thinking", "historical analysis"],
        numLessons=3
    )
    print("📥 Stage1Input:")
    pprint(base_input.model_dump())

    # === Step 2: Contextual Course Agent ===
    pedagogical_profile = await run_contextual_agent(base_input)
    print("\n🧠 Pedagogical Profile:")
    pprint(pedagogical_profile)

    # === Step 3: Course Scoping Agent ===
    lesson_titles = await run_course_scoping_agent(base_input)
    print("\n📚 Lesson Titles:")
    for i, title in enumerate(lesson_titles, 1):
        print(f"  {i}. {title}")

    # === Step 4: Lesson Content Agent ===
    for idx, lesson_title in enumerate(lesson_titles, start=1):
        lesson_input = LessonContentAgentInput(
            topicName=base_input.topicName,
            gradeLevel=base_input.gradeLevel,
            bigIdea=base_input.bigIdea,
            lessonTitle=lesson_title,
            lessonIndex=idx,
            pedagogicalProfile=pedagogical_profile
        )
        print(f"\n✏️ Generating content for Lesson {idx}: {lesson_title}")
        result = await run_lesson_content_agent(lesson_input)

        assert result.get("lessonTitle") == lesson_title
        assert "coreParagraphs" in result
        assert len(result["coreParagraphs"]) >= 2

        print(f"\n✅ Final Lesson Output [{lesson_title}]")
        pprint(result)


@pytest.mark.asyncio
async def test_lesson_content_agent_missing_fields():
    input_data = LessonContentAgentInput(
        topicName="Industrial Revolution",
        gradeLevel="8",
        bigIdea="Technological change reshapes society.",
        lessonTitle="Introduction to the Industrial Age",
        lessonIndex=1,
        pedagogicalProfile={}  # intentionally left blank
    )

    print("\n⚠️ Running lesson_content_agent with EMPTY pedagogical profile:")
    result = await run_lesson_content_agent(input_data)

    assert "lessonTitle" in result
    assert len(result.get("coreParagraphs", [])) >= 1  # Should still work, but less rich
    print("\n✅ Fallback Output with empty profile:")
    pprint(result)

@pytest.mark.asyncio
async def test_lesson_content_agent_basic():
    input_data = LessonContentAgentInput(
        topicName="The French Revolution",
        gradeLevel="9",
        bigIdea="Revolutions challenge old systems and create new ones.",
        lessonTitle="Key Turning Points in the French Revolution",
        lessonIndex=2,
        pedagogicalProfile={
            "themesToRevisit": ["social inequality", "monarchical rule"],
            "newConcepts": ["The Jacobins", "The Reign of Terror"],
            "skills": ["cause-effect analysis", "timeline interpretation"],
            "commonMisconceptions": ["The Revolution was quick", "Everyone supported it"],
            "pedagogicalNotes": "Encourage debate; use visual aids like timelines."
        }
    )

    print("\n✏️ Running lesson_content_agent with direct input:")
    result = await run_lesson_content_agent(input_data)

    assert result.get("lessonTitle") == input_data.lessonTitle
    assert "coreParagraphs" in result
    assert len(result["coreParagraphs"]) >= 2

    print("\n✅ Final Output:")
    pprint(result)


@pytest.mark.asyncio
async def test_full_stage1_flow_hebrew_history():
    base_input = Stage1Input(
        topicName="המהפכה הצרפתית",
        subject="היסטוריה",
        gradeLevel="16",
        bigIdea="מהפכות מאתגרות סדרים קיימים ויוצרות מציאות חדשה.",
        learningGate="Meeting Gate",
        skills=["חשיבה ביקורתית", "ניתוח סיבות ותוצאות"],
        numLessons=3
    )
    print("📥 קלט בעברית:")
    pprint(base_input.model_dump())

    pedagogical_profile = await run_contextual_agent(base_input)
    print("\n🧠 פרופיל פדגוגי:")
    pprint(pedagogical_profile)

    lesson_titles = await run_course_scoping_agent(base_input)
    print("\n📚 כותרות שיעורים:")
    for i, title in enumerate(lesson_titles, 1):
        print(f"  {i}. {title}")

    for idx, lesson_title in enumerate(lesson_titles, start=1):
        lesson_input = LessonContentAgentInput(
            topicName=base_input.topicName,
            gradeLevel=base_input.gradeLevel,
            bigIdea=base_input.bigIdea,
            lessonTitle=lesson_title,
            lessonIndex=idx,
            pedagogicalProfile=pedagogical_profile
        )
        print(f"\n✏️ מייצר שיעור {idx}: {lesson_title}")
        result = await run_lesson_content_agent(lesson_input)

        assert result.get("lessonTitle") == lesson_title
        assert "coreParagraphs" in result
        assert len(result["coreParagraphs"]) >= 2

        print(f"\n✅ תוצר סופי לשיעור [{lesson_title}]")
        pprint(result)



@pytest.mark.asyncio
async def test_full_stage1_flow_hebrew_social_science():
    base_input = Stage1Input(
        topicName="גלובליזציה",
        subject="מדעי החברה",
        gradeLevel="14",
        bigIdea="העולם המודרני הופך למקושר ומושפע זה מזה.",
        learningGate="Independence Gate",
        skills=["הבנה בין-תרבותית", "ניתוח תהליכים גלובליים"],
        numLessons=2
    )
    print("📥 קלט בעברית (גלובליזציה):")
    pprint(base_input.model_dump())

    pedagogical_profile = await run_contextual_agent(base_input)
    print("\n🧠 פרופיל פדגוגי:")
    pprint(pedagogical_profile)

    lesson_titles = await run_course_scoping_agent(base_input)
    print("\n📚 כותרות שיעורים:")
    for i, title in enumerate(lesson_titles, 1):
        print(f"  {i}. {title}")

    for idx, lesson_title in enumerate(lesson_titles, start=1):
        lesson_input = LessonContentAgentInput(
            topicName=base_input.topicName,
            gradeLevel=base_input.gradeLevel,
            bigIdea=base_input.bigIdea,
            lessonTitle=lesson_title,
            lessonIndex=idx,
            pedagogicalProfile=pedagogical_profile
        )
        print(f"\n✏️ מייצר שיעור {idx}: {lesson_title}")
        result = await run_lesson_content_agent(lesson_input)

        assert result.get("lessonTitle") == lesson_title
        assert "coreParagraphs" in result
        assert len(result["coreParagraphs"]) >= 2

        print(f"\n✅ תוצר סופי לשיעור [{lesson_title}]")
        pprint(result)
