import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_feedback_reports as feedback_crud
from app.core.config import db


@pytest.mark.asyncio
async def test_get_feedback_reports_by_block():
    block_id = f"block_{uuid4()}"
    report_id = f"report_{uuid4()}"
    test_doc = {
        "_id": report_id,
        "outlineId": "outline_1",
        "blockId": block_id,
        "createdAt": datetime.utcnow().isoformat(),
        "overallStatus": "Approved",
        "revisionPrompt": "✅ Well done"
    }

    await feedback_crud.upsert_feedback_report(test_doc)

    results = await feedback_crud.get_feedback_reports_by_block(block_id)

    assert isinstance(results, list)
    assert any(doc["_id"] == report_id for doc in results)

    # Cleanup
    await db["feedback_reports"].delete_one({"_id": report_id})
