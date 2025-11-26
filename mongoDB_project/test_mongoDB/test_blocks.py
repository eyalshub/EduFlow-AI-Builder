import asyncio
from datetime import datetime
from mongoDB_project.config.connection import db
from app.models.blocks import (
    insert_block_if_not_exists,
    get_block_by_id,
    get_question_blocks_by_outline,
    get_question_blocks_by_corpus
)

# Example paragraph block
example_block = {
    "_id": "block_mongo_id_abc1",
    "courseOutlineId": "course_outline_456",
    "lessonId": "lesson_01",
    "sectionId": "sec_01_01",
    "pageId": "page_01_01_01",
    "blockType": "Paragraph",
    "metadata": {"purpose": "Context Setting"},
    "content": {
        "text": "The social structure of pre-revolutionary France was divided into Three Estates..."
    }
}

# Example multiple choice question block
example_question_block = {
    "_id": "block_mongo_id_abc2",
    "courseOutlineId": "course_outline_456",
    "lessonId": "lesson_01",
    "sectionId": "sec_01_01",
    "pageId": "page_01_01_01",
    "blockType": "Multiple_Choice_Question",
    "metadata": {"cognitiveLevel": "Knowledge", "difficulty": "Easy"},
    "content": {
        "questionText": "Which group made up the Third Estate?",
        "options": ["The Clergy", "The Nobility", "The Commoners"],
        "correctAnswerIndex": 2
    },
    "sourceContext": {
        "sourceType": "Wikipedia",
        "sourceURI": "https://en.wikipedia.org/wiki/French_Revolution",
        "textSnippet": "The Third Estate was comprised of the commoners of France..."
    },
    "evaluationRubric": {
        "criteria": [
            "Student identifies the correct group as 'The Commoners'.",
            "Student explains the distinction between the Three Estates."
        ],
        "levels": [
            {"level": "Excellent", "description": "Fully correct and well-explained."},
            {"level": "Partial", "description": "Correct group but incomplete explanation."},
            {"level": "Incorrect", "description": "Incorrect group or no explanation."}
        ]
    }
}

async def test_blocks():
    # Insert example blocks if they don't exist
    await insert_block_if_not_exists(example_block)
    await insert_block_if_not_exists(example_question_block)

    # Test getting block by ID
    block = await get_block_by_id("block_mongo_id_abc2")
    if block:
        print("✅ Block fetched by ID:", block["blockType"])
    else:
        print("❌ Block not found by ID.")

    # Test getting question blocks by outline
    questions_by_outline = await get_question_blocks_by_outline("course_outline_456")
    print(f"📚 Found {len(questions_by_outline)} question block(s) by outline.")

    # Test getting question blocks by corpus
    questions_by_corpus = await get_question_blocks_by_corpus("corpus_unique_id_789")
    print(f"🔍 Found {len(questions_by_corpus)} question block(s) by corpus.")

if __name__ == "__main__":
    asyncio.run(test_blocks())
