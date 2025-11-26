import asyncio
from datetime import datetime
from mongoDB_project.config.connection import db
from app.models import chat_history

# 🔧 Sample document for testing
example_chat_session = {
    "_id": "session_abc_123",
    "userId": "user_xyz_789",
    "createdAt": datetime.utcnow().isoformat(),
    "updatedAt": datetime.utcnow().isoformat(),
    "messages": [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "sender": "User",
            "text": "I want to create a new course on the recent Israel-Iran war."
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "sender": "AI",
            "text": "Certainly! What specific aspects of the war would you like to cover?",
            "metadata": {
                "agentResponseTimeMs": 500,
                "relevantAgent": "CourseArchitectAgent"
            }
        }
    ],
    "sessionMetadata": {
        "courseTopic": "Israel-Iran War",
        "status": "active"
    }
}

async def run():
    print("🚀 Inserting test chat session...")
    await chat_history.upsert_chat_session(example_chat_session["_id"], example_chat_session)

    print("📨 Appending new user message...")
    await chat_history.append_message_to_session(
        "session_abc_123",
        {"sender": "User", "text": "Focus on the causes."}
    )

    print("🔍 Retrieving session...")
    session = await chat_history.get_chat_session("session_abc_123")
    print("✅ Retrieved:", session["sessionMetadata"])
    print("📄 Messages:", len(session["messages"]))

    print("🧹 Cleaning up test session...")
    deleted = await chat_history.delete_chat_session("session_abc_123")
    print("🗑️ Deleted:", deleted, "document(s)")

if __name__ == "__main__":
    asyncio.run(run())
