import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_chat_history as chat_history

@pytest.mark.asyncio
async def test_upsert_and_get_chat_session():
    session_id = f"session_{uuid4()}"
    test_session = {
        "_id": session_id,
        "userId": "user_123",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": None,
        "messages": []
    }

    await chat_history.upsert_chat_session(session_id, test_session)
    result = await chat_history.get_chat_session(session_id)

    assert result is not None
    assert result["_id"] == session_id
    assert result["userId"] == "user_123"

    await chat_history.delete_chat_session(session_id)
