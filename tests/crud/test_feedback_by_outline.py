import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_feedback_reports as feedback_crud
from app.core.config import db

@pytest.mark.asyncio
async def test_get_feedback_reports_by_outline():
    outline_id = f"outline_{uuid4()}"
    report_id = f"report_{uuid4()}"
    test_doc = {
        "_id": report_id,
        "outlineId": outline_id,
        "blockId": "block_1",
        "createdAt": datetime.utcnow().isoformat(),
        "overallStatus": "Needs_Revision",
        "revisionPrompt": "Add more examples."
    }

    await feedback_crud.upsert_feedback_report(test_doc)
    results = await feedback_crud.get_feedback_reports_by_outline(outline_id)

    assert any(doc["_id"] == report_id for doc in results)
    await db["feedback_reports"].delete_one({"_id": report_id})
