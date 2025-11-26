import pytest
from app.core.pipeline.final_pipeline import generate_full_lesson_pipeline
from app.schemas.stage2 import CognitiveTarget, Difficulty, QuestionType
from app.schemas.lms import FullLessonInput


@pytest.mark.asyncio
async def test_pipeline_stage1_only():
    print("🚀 Running test: stage1 only")
    input_data = FullLessonInput(
        mode="stage1",
        topicName="המהפכה הצרפתית",
        subject="היסטוריה",
        gradeLevel="10",
        bigIdea="מהפכות משנות את פני החברה",
        courseLanguage="he",
        learningGate="Meeting Gate",
        generation_scope="Single Lesson",
        cognitive_target=CognitiveTarget.comprehension_application,
        target_difficulty=Difficulty.medium,
        question_types=[QuestionType.MCQ],
        num_questions=3,
        save_to_blocks=False,
        skills=["חשיבה ביקורתית"],
    )

    result = await generate_full_lesson_pipeline(input_data)
    print("🧪 Result (stage1):", result)

    assert result["success"] is True
    assert result["mode"] == "stage1"
    assert "content" in result
    assert "pipelineMeta" in result
    assert isinstance(result["content"], dict)
    assert isinstance(result["pipelineMeta"], dict)


@pytest.mark.asyncio
async def test_pipeline_stage2_only():
    print("🚀 Running test: stage2 only")

    input_data = FullLessonInput(
        mode="stage2",
        stage2_mode="generate_questions",
        topicName="המהפכה הצרפתית",
        subject="היסטוריה",
        gradeLevel="9",
        bigIdea="שינוי מהפכני",
        generation_scope="Single Lesson",
        skills=["הבנה", "ניתוח"],
        learning_gate="Discovery Gate",
        course_language="he",
        question_types=[QuestionType.MATCHING],
        num_questions=1,
        save_to_blocks=False,
        cognitive_target=CognitiveTarget.comprehension_application,
        target_difficulty=Difficulty.hard,
    )

    # הוספת השדה `chunks` נדרשת ידנית (hack זמני), כי `FullLessonInput` לא כולל אותו לפי הסכימה:
    input_data_dict = input_data.dict(by_alias=True)
    input_data_dict["chunks"] = [
        {
            "chunk_id": "chunk_001",
            "text": "ב-1789 קרסה הסמכות המלוכנית בצרפת. ההמון כבש את הבסטיליה, והוכרזה הצהרת זכויות האדם."
        }
    ]

    result = await generate_full_lesson_pipeline(FullLessonInput(**input_data_dict))
    print("🧪 Result (stage2):", result)

    assert result["success"] is True
    assert result["mode"] == "stage2"
    assert "blocks" in result
    assert isinstance(result["blocks"], list)
    assert len(result["blocks"]) > 0
    for blk in result["blocks"]:
        assert "blockId" in blk
        assert "blockType" in blk
