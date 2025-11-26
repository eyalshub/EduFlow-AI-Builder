import pytest
from datetime import datetime, timedelta
from uuid import uuid4
import app.crud.crud_outlines as outlines_crud
from app.core.config import db


@pytest.mark.asyncio
async def test_find_recent_outlines():
    outline_id = f"outline_{uuid4()}"
    test_doc = {
        "_id": outline_id,
        "subject": "Science",
        "gradeLevel": "8",
        "status": "Published",
        "createdAt": datetime.utcnow().isoformat(),
        "lessons": []
    }

    await outlines_crud.upsert_outline(test_doc)
    results = await outlines_crud.find_recent_outlines(days_back=2)

    assert isinstance(results, list)
    assert any(doc["_id"] == outline_id for doc in results)

    await db["outlines"].delete_one({"_id": outline_id})
