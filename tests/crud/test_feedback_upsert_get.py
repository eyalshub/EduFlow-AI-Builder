import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_feedback_reports as feedback_crud
from app.core.config import db

@pytest.mark.asyncio
async def test_upsert_and_get_feedback_report():
    report_id = f"report_{uuid4()}"
    test_doc = {
        "_id": report_id,
        "outlineId": "outline_abc",
        "blockId": "block_xyz",
        "createdAt": datetime.utcnow().isoformat(),
        "overallStatus": "Approved",
        "revisionPrompt": "Looks good overall."
    }

    await feedback_crud.upsert_feedback_report(test_doc)
    result = await feedback_crud.get_feedback_report_by_id(report_id)

    assert result is not None
    assert result["_id"] == report_id

    await db["feedback_reports"].delete_one({"_id": report_id})
