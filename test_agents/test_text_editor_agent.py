import pytest
from app.schemas.input_model import Stage1Input
from app.core.agents.text_editor_agent import run_text_editor_agent, TextEditorInput


def print_agent_output(name: str, raw: str, edited: str, justification: str):
    print(f"\n========== TEST CASE: {name} ==========")
    print("✏️ Original Text:\n", raw)
    print("\n✅ Edited Text:\n", edited)
    print("\n📝 Justification:\n", justification)
    print("=" * 45)


@pytest.mark.asyncio
async def test_text_editor_agent_basic_hebrew():
    raw_text = "המהפכה הצרפתית הייתה מאוד מאוד חשובה, ממש ממש שינתה הכל."

    stage1 = Stage1Input(
        topicName="המהפכה הצרפתית",
        subject="היסטוריה",
        gradeLevel="ט'",
        bigIdea="מהפכה ושינוי חברתי",
        learningGate="Discovery Gate",
        skills=["הבנת הנקרא", "חשיבה ביקורתית"],
        courseLanguage="he"
    )

    agent_input: TextEditorInput = {
        "stage1": stage1,
        "raw_text": raw_text,
        "audience": "תלמידי כיתה ט'",
        "instructionStyle": "friendly",
        "outputFormat": "paragraphs",
        "allowFormatting": False
    }

    result = await run_text_editor_agent(agent_input)
    assert result["status"] == "ok"
    print_agent_output("Hebrew Basic", raw_text, result["edited_text"], result["justification"])


@pytest.mark.asyncio
async def test_text_editor_agent_english_science_advanced():
    raw_text = "Plants use sunlight to make food. It's called photosynthesis. It's very important."

    stage1 = Stage1Input(
        topicName="Photosynthesis",
        subject="Science",
        gradeLevel="6",
        bigIdea="Energy in Nature",
        learningGate="Discovery Gate",
        skills=["Scientific explanation", "Critical thinking"],
        courseLanguage="en"
    )

    agent_input: TextEditorInput = {
        "stage1": stage1,
        "raw_text": raw_text,
        "audience": "Middle school science students",
        "instructionStyle": "formal",
        "outputFormat": "paragraphs",
        "allowFormatting": True
    }

    result = await run_text_editor_agent(agent_input)
    assert result["status"] == "ok"
    print_agent_output("English Science", raw_text, result["edited_text"], result["justification"])


@pytest.mark.asyncio
async def test_text_editor_agent_english_history_friendly():
    raw_text = "The American Revolution happened because people were mad. They didn’t like taxes. So they fought."

    stage1 = Stage1Input(
        topicName="American Revolution",
        subject="History",
        gradeLevel="8",
        bigIdea="Struggle for Independence",
        learningGate="Meeting Gate",
        skills=["Argumentation", "Historical empathy"],
        courseLanguage="en"
    )

    agent_input: TextEditorInput = {
        "stage1": stage1,
        "raw_text": raw_text,
        "audience": "Teen history learners",
        "instructionStyle": "friendly",
        "outputFormat": "paragraphs",
        "allowFormatting": False
    }

    result = await run_text_editor_agent(agent_input)
    assert result["status"] == "ok"
    print_agent_output("English History", raw_text, result["edited_text"], result["justification"])


@pytest.mark.asyncio
async def test_text_editor_agent_hebrew_literature_advanced():
    raw_text = "הסיפור עוסק בילד שהולך לבית ספר ומפחד מהמורה שלו. זה היה לו קשה מאוד כי הוא ביישן."

    stage1 = Stage1Input(
        topicName="יחסי מורה-תלמיד",
        subject="ספרות",
        gradeLevel="י'",
        bigIdea="זהות וביטוי עצמי",
        learningGate="Independence Gate",
        skills=["ניתוח ספרותי", "הבעת רגשות בכתב"],
        courseLanguage="he"
    )

    agent_input: TextEditorInput = {
        "stage1": stage1,
        "raw_text": raw_text,
        "audience": "תלמידי תיכון בספרות",
        "instructionStyle": "formal",
        "outputFormat": "paragraphs",
        "allowFormatting": False
    }

    result = await run_text_editor_agent(agent_input)
    assert result["status"] == "ok"
    print_agent_output("Hebrew Literature", raw_text, result["edited_text"], result["justification"])
