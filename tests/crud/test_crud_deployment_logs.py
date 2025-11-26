import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_deployment_logs as deployment_logs


@pytest.mark.asyncio
async def test_insert_and_get_all_deployment_logs():
    log_id = f"log_{uuid4()}"
    test_log = {
        "_id": log_id,
        "outlineId": "outline_123",
        "status": "Success",
        "timestamp": datetime.utcnow().isoformat(),
        "errorLog": None
    }

    await deployment_logs.insert_deployment_log(test_log)
    all_logs = await deployment_logs.get_all_deployment_logs()

    assert any(log["_id"] == log_id for log in all_logs)

    # Cleanup
    await db_cleanup(log_id)


@pytest.mark.asyncio
async def test_get_logs_by_status():
    log_id = f"log_{uuid4()}"
    test_log = {
        "_id": log_id,
        "outlineId": "outline_456",
        "status": "Failure",
        "timestamp": datetime.utcnow().isoformat(),
        "errorLog": "Connection timeout"
    }

    await deployment_logs.insert_deployment_log(test_log)
    failed_logs = await deployment_logs.get_logs_by_status("Failure")

    assert any(log["_id"] == log_id for log in failed_logs)

    # Cleanup
    await db_cleanup(log_id)


@pytest.mark.asyncio
async def test_get_logs_by_outline():
    log_id = f"log_{uuid4()}"
    outline_id = f"outline_{uuid4()}"
    test_log = {
        "_id": log_id,
        "outlineId": outline_id,
        "status": "Success",
        "timestamp": datetime.utcnow().isoformat(),
        "errorLog": None
    }

    await deployment_logs.insert_deployment_log(test_log)
    logs_by_outline = await deployment_logs.get_logs_by_outline(outline_id)

    assert any(log["_id"] == log_id for log in logs_by_outline)

    # Cleanup
    await db_cleanup(log_id)


@pytest.mark.asyncio
async def test_get_failed_deployments():
    log_id = f"log_{uuid4()}"
    test_log = {
        "_id": log_id,
        "outlineId": "outline_789",
        "status": "Failure",
        "timestamp": datetime.utcnow().isoformat(),
        "errorLog": "Something went wrong"
    }

    await deployment_logs.insert_deployment_log(test_log)
    failed_logs = await deployment_logs.get_failed_deployments()

    assert any(log["_id"] == log_id for log in failed_logs)

    # Cleanup
    await db_cleanup(log_id)


# 🧹 helper for cleanup
from app.core.config import db
async def db_cleanup(log_id: str):
    await db["deployment_logs"].delete_one({"_id": log_id})
