import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_outlines as outlines_crud
from app.core.config import db


@pytest.mark.asyncio
async def test_upsert_and_get_outline():
    outline_id = f"outline_{uuid4()}"
    test_doc = {
        "_id": outline_id,
        "subject": "History",
        "gradeLevel": "9",
        "status": "Draft",
        "createdAt": datetime.utcnow().isoformat(),
        "lessons": []
    }

    await outlines_crud.upsert_outline(test_doc)
    result = await outlines_crud.get_outline_by_id(outline_id)

    assert result is not None
    assert result["_id"] == outline_id
    assert result["status"] == "Draft"

    await db["outlines"].delete_one({"_id": outline_id})
