import pytest
from datetime import datetime
from uuid import uuid4
import app.crud.crud_chat_history as chat_history

@pytest.mark.asyncio
async def test_get_sessions_by_user():
    user_id = f"user_{uuid4()}"
    session_id_1 = f"session_{uuid4()}"
    session_id_2 = f"session_{uuid4()}"

    session1 = {
        "_id": session_id_1,
        "userId": user_id,
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": None,
        "messages": []
    }
    session2 = {
        "_id": session_id_2,
        "userId": user_id,
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": None,
        "messages": []
    }

    await chat_history.upsert_chat_session(session_id_1, session1)
    await chat_history.upsert_chat_session(session_id_2, session2)

    result = await chat_history.get_sessions_by_user(user_id)
    session_ids = [doc["_id"] for doc in result]

    assert session_id_1 in session_ids
    assert session_id_2 in session_ids

    await chat_history.delete_chat_session(session_id_1)
    await chat_history.delete_chat_session(session_id_2)
