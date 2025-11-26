#tests/core/pipeline/test_stage2_pipeline.py
import pytest
from app.schemas.stage2 import (
    Stage2Request,
    Stage2Mode,
    QuestionType,
    Difficulty,
    CognitiveTarget
)
from app.core.pipeline.stage2_pipeline import run_stage2

base_common_kwargs = dict(
    topicName="המהפכה הצרפתית",
    subject="היסטוריה",
    gradeLevel="9",
    bigIdea="שינוי מהפכני",
    generationScope="Single Topic",
    skills=["הבנה", "ניתוח"],
    learningGate="זיהוי והבנה",
    context="המהפכה הצרפתית הייתה תהליך מהותי לשינוי חברתי ופוליטי בצרפת.",
    freePrompt=None,
    courseLanguage="he"
)

@pytest.mark.asyncio
async def test_stage2_text_edit_with_save():
    req = Stage2Request(
        **base_common_kwargs,
        text="המהפכה הייתה מאוד חשובה וזהו.",
        mode=Stage2Mode.edit_text,
        language="he",
        save_to_blocks=True
    )
    result = await run_stage2(req)
    assert result.edited_text
    assert len(result.saved_blocks) > 0

@pytest.mark.asyncio
async def test_stage2_generate_open_question():
    req = Stage2Request(
        **base_common_kwargs,
        mode=Stage2Mode.generate_questions,
        question_types=[QuestionType.OPEN],
        num_questions=1,
        save_to_blocks=False,
        cognitive_target=CognitiveTarget.comprehension_application,
        target_difficulty=Difficulty.medium,
        chunks=[{
            "chunk_id": "chunk_002",
            "text": "המהפכה הצרפתית סימנה שינוי עמוק במבנה החברתי והפוליטי בצרפת."
        }]
    )
    result = await run_stage2(req)
    assert len(result.generated) == 1

@pytest.mark.asyncio
async def test_stage2_generate_matching_question():
    req = Stage2Request(
        **base_common_kwargs,
        mode=Stage2Mode.generate_questions,
        question_types=[QuestionType.MATCHING],
        num_questions=1,
        save_to_blocks=False,
        cognitive_target=CognitiveTarget.knowledge,
        target_difficulty=Difficulty.hard,
        chunks=[{
            "chunk_id": "chunk_003",
            "text": "במהלך המהפכה הצרפתית, התרחשו שינויים משמעותיים במערכת השלטונית."
        }]
    )
    result = await run_stage2(req)
    assert len(result.generated) == 1

@pytest.mark.asyncio
async def test_stage2_generate_multiple_types():
    req = Stage2Request(
        **base_common_kwargs,
        mode=Stage2Mode.generate_questions,
        question_types=[QuestionType.MCQ, QuestionType.OPEN],
        num_questions=2,
        save_to_blocks=False,
        cognitive_target=CognitiveTarget.inference_evaluation,
        target_difficulty=Difficulty.medium,
        chunks=[{
            "chunk_id": "chunk_004",
            "text": "המהפכה הצרפתית עודדה רעיונות חדשים על שלטון העם וזכויות האדם."
        }]
    )
    result = await run_stage2(req)
    assert len(result.generated) >= 1

@pytest.mark.asyncio
async def test_stage2_empty_chunk_should_fail_gracefully():
    req = Stage2Request(
        **base_common_kwargs,
        mode=Stage2Mode.generate_questions,
        question_types=[QuestionType.MCQ],
        num_questions=1,
        save_to_blocks=False,
        cognitive_target=CognitiveTarget.knowledge,
        target_difficulty=Difficulty.easy,
        chunks=[{
            "chunk_id": "chunk_empty",
            "text": ""
        }]
    )
    result = await run_stage2(req)
    assert len(result.generated) == 0

@pytest.mark.asyncio
async def test_stage2_with_free_prompt_only():
    print("🧪 Starting: test_stage2_with_free_prompt_only")

    req = Stage2Request(
        **{
            **base_common_kwargs,
            "freePrompt": "כתוב שאלה פתוחה על חשיבות זכויות האדם.",
            "context": "זכויות האדם הן עקרונות מוסריים המבטאים את הזכות של כל אדם לחיות בכבוד, בביטחון ובשוויון.",
            "chunks": []  # בכוונה ריק
        },
        mode=Stage2Mode.generate_questions,
        question_types=[QuestionType.OPEN],
        num_questions=1,
        save_to_blocks=False,
        cognitive_target=CognitiveTarget.comprehension_application,
        target_difficulty=Difficulty.medium,
    )

    print("📥 Request:", req.model_dump())
    result = await run_stage2(req)
    print("📤 Result object:", result)
    print("📊 Generated questions count:", len(result.generated))

    if not result.generated:
        print("❌ No questions generated.")
        assert False, f"Expected at least one question, but got: {result}"

    for i, q in enumerate(result.generated):
        print(f"🔹 Question {i+1}: {q.question}")
        print(f"   🔸 Bloom match: {q.cognitive_verification.match}")
        print(f"   🔸 Difficulty match: {q.difficulty_verification.match}")
        print(f"   🔸 Grounded: {q.grounding_verification.get('grounded')}")

    assert len(result.generated) >= 1


@pytest.mark.asyncio
async def test_stage2_generate_question_and_save_to_blocks():
    print("🧪 Starting: test_stage2_generate_question_and_save_to_blocks")
    req = Stage2Request(
        **base_common_kwargs,
        mode=Stage2Mode.generate_questions,
        question_types=[QuestionType.MCQ],
        num_questions=1,
        save_to_blocks=True,
        cognitive_target=CognitiveTarget.knowledge,
        target_difficulty=Difficulty.easy,
        chunks=[{
            "chunk_id": "chunk_save_001",
            "text": "המהפכה הצרפתית סימנה את סיום השלטון המלוכני בצרפת והולדת הדמוקרטיה המודרנית."
        }]
    )
    result = await run_stage2(req)

    print("📊 Generated:", len(result.generated), " | Saved:", len(result.saved_blocks))
    for i, blk in enumerate(result.saved_blocks):
        print(f"🧱 Block {i+1}: {blk}")
        assert hasattr(blk, "blockType")
        assert blk.blockType == "question"

    assert len(result.saved_blocks) >= 1

    # אפשרות לבדוק את תוכן השאלה מתוך result.generated ולא מתוך saved_blocks
    for q in result.generated:
        print("🧠 Generated Question:", q.question)
        assert q.question["question"].get("stem")
        if q.question.get("choices"):
            assert isinstance(q.question["question"]["choices"], list)


def test_shuffle_mcq_preserves_correct_answer():
    from app.core.normalizers.question_normalizer import shuffle_mcq_choices

    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "choices": ["מדריד", "ברצלונה", "סביליה", "ולנסיה"],
        "correct_index": 0  # מדריד
    }

    shuffle_mcq_choices(q, seed=42)

    assert q["choices"] != ["מדריד", "ברצלונה", "סביליה", "ולנסיה"]

    assert q["choices"][q["correct_index"]] == "מדריד"

@pytest.mark.asyncio
async def test_stage2_generate_multiple_questions_count_matches():
    req = Stage2Request(
        **base_common_kwargs,
        mode=Stage2Mode.generate_questions,
        question_types=[QuestionType.MCQ],
        num_questions=3,
        save_to_blocks=False,
        cognitive_target=CognitiveTarget.knowledge,
        target_difficulty=Difficulty.easy,
        chunks=[{
            "chunk_id": "chunk_count_test",
            "text": "המהפכה הצרפתית סימנה שינוי עמוק בצרפת והשפיעה על מבנה השלטון."
        }]
    )
    result = await run_stage2(req)
    print("📊 Generated questions:", len(result.generated))
    assert len(result.generated) >= 3
