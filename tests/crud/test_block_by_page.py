import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_block as blocks

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
    assert any(doc["_id"] == test_id for doc in result_list)
    await blocks.delete_block_by_id(test_id)
