# app/crud/crud_deployment_logs.py
from app.core.config import get_db

# ✅ Insert log
async def insert_deployment_log(log_doc: dict):
    db = get_db()
    await db["deployment_logs"].insert_one(log_doc)
    print("📤 Deployment log inserted.")

# 🔍 Retrieve logs
async def get_all_deployment_logs():
    db = get_db()
    cursor = db["deployment_logs"].find()
    return [doc async for doc in cursor]

async def get_logs_by_status(status: str):
    db = get_db()
    cursor = db["deployment_logs"].find({"status": status})
    return [doc async for doc in cursor]

async def get_logs_by_outline(outline_id: str):
    db = get_db()
    cursor = db["deployment_logs"].find({"outlineId": outline_id})
    return [doc async for doc in cursor]

# 🧪 Error logs only
async def get_failed_deployments():
    db = get_db()
    cursor = db["deployment_logs"].find({
        "status": "Failure",
        "errorLog": {"$ne": None}
    })
    return [doc async for doc in cursor]
