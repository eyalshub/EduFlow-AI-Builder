# app/crud/crud_content_corpus.py
from datetime import datetime, timedelta
from app.core.config import get_db
from bson import ObjectId

# ➕ Upsert
async def upsert_document(doc: dict):
    db = get_db()
    result = await db["content_corpus"].replace_one(
        {"_id": doc["_id"]},
        doc,
        upsert=True
    )
    return result.upserted_id or doc["_id"]

# 🔍 Read
async def find_by_filters(subject: str = None, grade: str = None):
    db = get_db()
    query = {}
    if subject:
        query["subject"] = subject
    if grade:
        query["gradeLevel"] = grade
    cursor = db["content_corpus"].find(query)
    return [doc async for doc in cursor]

async def get_document_by_id(corpus_id: str):
    db = get_db()
    try:
        doc = await db["content_corpus"].find_one({"_id": ObjectId(corpus_id)})
        return doc
    except Exception:
        return None

async def get_all_documents():
    db = get_db()
    cursor = db["content_corpus"].find()
    return [doc async for doc in cursor]

# ❌ Delete
async def delete_document_by_id(doc_id: str):
    db = get_db()
    result = await db["content_corpus"].delete_one({"_id": doc_id})
    return result.deleted_count

# 📆 Recent
async def find_recent_documents(days_back: int = 7):
    db = get_db()
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    cursor = db["content_corpus"].find({"createdAt": {"$gte": cutoff.isoformat()}})
    return [doc async for doc in cursor]

# 🛠️ Update
async def update_summary(doc_id: str, new_summary: str):
    db = get_db()
    result = await db["content_corpus"].update_one(
        {"_id": doc_id},
        {"$set": {"content.finalSummary": new_summary}}
    )
    return result.modified_count

# 📊 Count
async def count_documents():
    db = get_db()
    return await db["content_corpus"].count_documents({})
