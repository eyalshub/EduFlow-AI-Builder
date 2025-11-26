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
    assert result["content"] == "This is a test block."
    await blocks.delete_block_by_id(test_id)
