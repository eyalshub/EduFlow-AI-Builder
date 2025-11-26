import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_outlines as outlines_crud
from app.core.config import db


@pytest.mark.asyncio
async def test_find_outlines_by_subject_and_grade():
    outline_id = f"outline_{uuid4()}"
    test_doc = {
        "_id": outline_id,
        "subject": "Math",
        "gradeLevel": "5",
        "status": "Published",
        "createdAt": datetime.utcnow().isoformat(),
        "lessons": []
    }

    await outlines_crud.upsert_outline(test_doc)
    results = await outlines_crud.find_outlines(subject="Math", grade="5")

    assert isinstance(results, list)
    assert any(doc["_id"] == outline_id for doc in results)

    await db["outlines"].delete_one({"_id": outline_id})
