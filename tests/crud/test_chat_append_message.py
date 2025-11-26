import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_chat_history as chat_history

@pytest.mark.asyncio
async def test_append_message_to_session():
    session_id = f"session_{uuid4()}"
    test_session = {
        "_id": session_id,
        "userId": "user_456",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": None,
        "messages": []
    }

    await chat_history.upsert_chat_session(session_id, test_session)

    message = {
        "sender": "user",
        "content": "Hello!",
    }

    await chat_history.append_message_to_session(session_id, message)
    result = await chat_history.get_chat_session(session_id)

    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0]["content"] == "Hello!"

    await chat_history.delete_chat_session(session_id)
