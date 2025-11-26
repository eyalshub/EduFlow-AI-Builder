# tests/core/pipeline/test_stage_1_corpus_initial.py

import pytest
from app.core.pipeline.stage_1_corpus_initial import run_stage_1
from app.schemas.input_model import Stage1Input
from app.models.content_corpus import ContentCorpus
from beanie import init_beanie, PydanticObjectId


@pytest.mark.asyncio
async def test_run_stage_1_basic(test_db):
    print("\n🚀 Starting Stage 1 test (Single Lesson)...")
    await init_beanie(database=test_db, document_models=[ContentCorpus])

    inputs = Stage1Input(
        topicName="המהפכה הצרפתית",
        subject="History",
        gradeLevel="9",
        bigIdea="Revolution and Change",
        generationScope="Single Lesson",
        context=None,
        freePrompt=None,
        learningGate="Discovery Gate",
        skills=["Critical Thinking"]
    )

    print("🧠 Calling run_stage_1 with input:", inputs.model_dump())
    inserted_id = await run_stage_1(inputs)
    print("✅ Inserted document ID:", inserted_id)

    saved_doc = await ContentCorpus.get(PydanticObjectId(inserted_id))
    assert saved_doc is not None
    print("📦 Document retrieved from DB.")

    assert saved_doc.topicName == inputs.topicName
    assert saved_doc.subject == inputs.subject
    assert saved_doc.gradeLevel == inputs.gradeLevel

    content = saved_doc.content
    assert content is not None

    print("📝 finalSummary length:", len(content.finalSummary))
    print("📚 sourceChunks count:", len(content.sourceChunks))

    assert isinstance(content.finalSummary, str)
    assert len(content.finalSummary.strip()) > 20
    assert isinstance(content.sourceChunks, list)
    assert len(content.sourceChunks) >= 1

    if inputs.generationScope == "Single Lesson":
        print("📎 Skipping lessonContents check (Single Lesson mode).")
        assert not hasattr(content, "lessonContents") or content.lessonContents is None
    elif inputs.generationScope == "Full Course":
        assert hasattr(content, "lessonContents")
        assert isinstance(content.lessonContents, list)
        assert len(content.lessonContents) >= 1
        for lesson in content.lessonContents:
            assert "lessonTitle" in lesson
            assert "coreParagraphs" in lesson
            assert isinstance(lesson["coreParagraphs"], list)
            assert len(lesson["coreParagraphs"]) >= 2


@pytest.mark.asyncio
async def test_stage1_science_multiple_lessons(test_db):
    await init_beanie(database=test_db, document_models=[ContentCorpus])
    inputs = Stage1Input(
        topicName="The Water Cycle",
        subject="Science",
        gradeLevel="14",
        bigIdea="Systems in Nature",
        generationScope="Full Course",
        numLessons=3,
        context=None,
        freePrompt=None,
        learningGate="Discovery Gate",
        skills=["Observation", "Explanation"]
    )
    inserted_id = await run_stage_1(inputs)
    saved_doc = await ContentCorpus.get(PydanticObjectId(inserted_id))
    assert hasattr(saved_doc.content, "scopedLessons")
    assert isinstance(saved_doc.content.scopedLessons, list)
    assert len(saved_doc.content.scopedLessons) == 3

@pytest.mark.asyncio
async def test_stage1_literature_with_context(test_db):
    await init_beanie(database=test_db, document_models=[ContentCorpus])

    inputs = Stage1Input(
        topicName="Symbolism in 'The Little Prince'",
        subject="Literature",
        gradeLevel="10",
        bigIdea="Interpretation of Text",
        generationScope="Single Lesson",
        context="Focus on the symbolism of the rose and the fox.",
        freePrompt=None,
        learningGate="Independence Gate",
        skills=["Text Analysis", "Interpretation"]
    )

    inserted_id = await run_stage_1(inputs)
    saved_doc = await ContentCorpus.get(PydanticObjectId(inserted_id))

    assert saved_doc is not None
    summary = saved_doc.content.finalSummary.lower()
    assert any(term in summary for term in ["rose", "fox", "ורד", "שועל"])


@pytest.mark.asyncio
async def test_stage1_philosophy_free_prompt(test_db):
    await init_beanie(database=test_db, document_models=[ContentCorpus])

    inputs = Stage1Input(
        topicName="Existentialism",
        subject="Philosophy",
        gradeLevel="12",
        bigIdea="Meaning and Existence",
        generationScope="Full Course",     # ← VALID
        numLessons=2,                      # ← FIXED
        context=None,
        freePrompt="Create a lesson that explores Sartre’s concept of 'existence precedes essence'.",
        learningGate="Discovery Gate",
        skills=["Critical Thinking", "Argumentation"],courseLanguage="en"
    )

    inserted_id = await run_stage_1(inputs)
    saved_doc = await ContentCorpus.get(PydanticObjectId(inserted_id))

    assert saved_doc is not None
    lesson_titles = saved_doc.content.scopedLessons or []
    title_text = " ".join(lesson_titles).lower()
    assert isinstance(saved_doc.content.scopedLessons, list)
    assert len(saved_doc.content.scopedLessons) >= 2
