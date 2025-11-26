import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_outlines as outlines_crud
from app.core.config import db


@pytest.mark.asyncio
async def test_update_outline_status():
    outline_id = f"outline_{uuid4()}"
    test_doc = {
        "_id": outline_id,
        "subject": "English",
        "gradeLevel": "10",
        "status": "Draft",
        "createdAt": datetime.utcnow().isoformat(),
        "lessons": []
    }

    await outlines_crud.upsert_outline(test_doc)
    await outlines_crud.update_outline_status(outline_id, "Finalized")

    result = await outlines_crud.get_outline_by_id(outline_id)
    assert result["status"] == "Finalized"

    await db["outlines"].delete_one({"_id": outline_id})
