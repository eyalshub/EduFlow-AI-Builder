# app/crud/crud_chat_history.py
from datetime import datetime
from app.core.config import get_db

# 📝 Insert or Update a Full Chat Session
async def upsert_chat_session(session_id: str, session_data: dict):
    db = get_db()
    session_data["updatedAt"] = datetime.utcnow().isoformat()
    await db["chat_history"].replace_one(
        {"_id": session_id},
        session_data,
        upsert=True
    )

# 📩 Append a Message to an Existing Session
async def append_message_to_session(session_id: str, message: dict):
    db = get_db()
    message["timestamp"] = datetime.utcnow().isoformat()
    await db["chat_history"].update_one(
        {"_id": session_id},
        {
            "$push": {"messages": message},
            "$set": {"updatedAt": datetime.utcnow().isoformat()}
        }
    )

# 🔍 Get a Full Chat Session
async def get_chat_session(session_id: str):
    db = get_db()
    return await db["chat_history"].find_one({"_id": session_id})

# 🔍 Get All Sessions for a User
async def get_sessions_by_user(user_id: str):
    db = get_db()
    cursor = db["chat_history"].find({"userId": user_id})
    return [doc async for doc in cursor]

# 🧼 Delete a Session
async def delete_chat_session(session_id: str):
    db = get_db()
    result = await db["chat_history"].delete_one({"_id": session_id})
    return result.deleted_count


# ✅ Simple helper to add a single message as a standalone chat (for free-form LLM chat)
async def save_chat_message(user_id: str, user_input: str, llm_response: str):
    session_id = f"session_{user_id}"  # Or create unique session IDs if needed
    message = {
        "sender": "user",
        "text": user_input
    }
    response = {
        "sender": "llm",
        "text": llm_response
    }
    existing = await get_chat_session(session_id)
    if not existing:
        session_data = {
            "_id": session_id,
            "userId": user_id,
            "createdAt": datetime.utcnow().isoformat(),
            "messages": [message, response]
        }
        await upsert_chat_session(session_id, session_data)
    else:
        await append_message_to_session(session_id, message)
        await append_message_to_session(session_id, response)
