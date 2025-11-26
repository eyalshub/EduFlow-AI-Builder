import pytest
from uuid import uuid4
from datetime import datetime
from app.crud import crud_general_logs as general_logs

@pytest.mark.anyio
async def test_insert_and_get_log_by_level():
    log_id = f"log_{uuid4()}"
    log_doc = {
        "_id": log_id,
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "source": "test_logger",
        "message": "This is a test log",
        "details": {"corpusId": "corpus_123"}
    }

    await general_logs.insert_general_log(log_doc)
    results = await general_logs.get_logs_by_level("INFO")
    assert any(log["_id"] == log_id for log in results)

@pytest.mark.anyio
async def test_get_logs_by_source():
    log_id = f"log_{uuid4()}"
    log_doc = {
        "_id": log_id,
        "timestamp": datetime.utcnow().isoformat(),
        "level": "WARNING",
        "source": "unit_test",
        "message": "Testing source filter",
        "details": {}
    }

    await general_logs.insert_general_log(log_doc)
    results = await general_logs.get_logs_by_source("unit_test")
    assert any(log["_id"] == log_id for log in results)

@pytest.mark.anyio
async def test_get_logs_by_corpus_id():
    log_id = f"log_{uuid4()}"
    corpus_id = f"corpus_{uuid4()}"
    log_doc = {
        "_id": log_id,
        "timestamp": datetime.utcnow().isoformat(),
        "level": "DEBUG",
        "source": "corpus_module",
        "message": "Linked to corpus",
        "details": {"corpusId": corpus_id}
    }

    await general_logs.insert_general_log(log_doc)
    results = await general_logs.get_logs_by_corpus_id(corpus_id)
    assert any(log["_id"] == log_id for log in results)

@pytest.mark.anyio
async def test_delete_log_by_id():
    log_id = f"log_{uuid4()}"
    log_doc = {
        "_id": log_id,
        "timestamp": datetime.utcnow().isoformat(),
        "level": "ERROR",
        "source": "deletion_test",
        "message": "Should be deleted",
        "details": {}
    }

    await general_logs.insert_general_log(log_doc)
    deleted = await general_logs.delete_log_by_id(log_id)
    assert deleted == 1

@pytest.mark.anyio
async def test_delete_all_logs():
    for i in range(3):
        log_doc = {
            "_id": f"log_bulk_{uuid4()}",
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "source": "bulk_test",
            "message": f"Bulk message {i}",
            "details": {}
        }
        await general_logs.insert_general_log(log_doc)

    await general_logs.delete_all_logs()
    logs = await general_logs.get_all_logs()
    assert len(logs) == 0
