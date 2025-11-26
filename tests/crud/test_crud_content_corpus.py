# tests/crud/test_content_corpus.py

import pytest
from datetime import datetime
from uuid import uuid4

import app.crud.crud_content_corpus as content_corpus

@pytest.mark.asyncio
async def test_upsert_and_fetch_document():
    # Arrange
    test_id = f"test_doc_{uuid4()}"
    test_doc = {
        "_id": test_id,
        "topicName": "Test Topic",
        "subject": "Science",
        "gradeLevel": "10",
        "createdAt": datetime.utcnow().isoformat(),
        "version": 1.0,
        "content": {
            "finalSummary": "This is a test summary.",
            "sourceChunks": []
        }
    }

    # Act
    await content_corpus.upsert_document(test_doc)
    result = await content_corpus.get_document_by_id(test_id)

    # Assert
    assert result is not None
    assert result["topicName"] == "Test Topic"

    # Cleanup
    await content_corpus.delete_document_by_id(test_id)
