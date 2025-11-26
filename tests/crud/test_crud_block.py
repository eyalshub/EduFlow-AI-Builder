# tests/crud/test_crud_block.py

import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_block as blocks


@pytest.mark.asyncio
async def test_upsert_and_get_block():
    test_id = f"block_{uuid4()}"
    test_doc = {
        "_id": test_id,
        "courseOutlineId": "outline_123",
        "lessonId": "lesson_1",
        "sectionId": "section_1",
        "pageId": "page_1",
        "blockType": "text",
        "metadata": {},
        "content": "This is a test block.",
        "createdAt": datetime.utcnow().isoformat()
    }

    await blocks.upsert_block(test_doc)
    result = await blocks.get_block_by_id(test_id)

    assert result is not None
    assert result["content"] == test_doc["content"]

    await blocks.delete_block_by_id(test_id)


@pytest.mark.asyncio
async def test_get_blocks_by_page():
    page_id = f"page_{uuid4()}"
    test_id = f"block_{uuid4()}"
    test_doc = {
        "_id": test_id,
        "courseOutlineId": "outline_456",
        "lessonId": "lesson_2",
        "sectionId": "section_2",
        "pageId": page_id,
        "blockType": "question",
        "metadata": {},
        "content": "Question content",
        "createdAt": datetime.utcnow().isoformat()
    }

    await blocks.upsert_block(test_doc)
    result_list = await blocks.find_blocks_by_page(page_id)

    assert isinstance(result_list, list), "Expected a list of documents"
    assert any(doc["_id"] == test_id for doc in result_list), "Inserted block not found in page"

    await blocks.delete_block_by_id(test_id)
