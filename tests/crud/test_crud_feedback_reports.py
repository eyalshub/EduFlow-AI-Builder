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
    assert result["overallStatus"] == "Approved"

    await cleanup_feedback_report(report_id)


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

    await cleanup_feedback_report(report_id)


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

    assert any(doc["_id"] == report_id for doc in results)

    await cleanup_feedback_report(report_id)


@pytest.mark.asyncio
async def test_get_blocks_needing_revision():
    outline_id = f"outline_{uuid4()}"
    report_id = f"report_{uuid4()}"
    test_doc = {
        "_id": report_id,
        "outlineId": outline_id,
        "blockId": "block_rev",
        "createdAt": datetime.utcnow().isoformat(),
        "overallStatus": "Needs_Revision",
        "revisionPrompt": "Clarify the concept."
    }

    await feedback_crud.upsert_feedback_report(test_doc)
    results = await feedback_crud.get_blocks_needing_revision(outline_id)

    assert any(doc["_id"] == report_id for doc in results)

    await cleanup_feedback_report(report_id)


# 🧹 Helper cleanup
async def cleanup_feedback_report(report_id: str):
    await db["feedback_reports"].delete_one({"_id": report_id})
