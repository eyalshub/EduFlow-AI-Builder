from app.core.config import get_db

# ✅ Always pull the collection from the inside
def get_collection():
    db = get_db()
    return db["general_logs"]

# ➕ Insert
async def insert_general_log(log_doc: dict):
    collection = get_collection()
    await collection.insert_one(log_doc)
    print(f"📥 Inserted log entry {log_doc['_id']}")

# 🔍 Read
async def get_all_logs():
    collection = get_collection()
    cursor = collection.find()
    return [doc async for doc in cursor]

async def get_logs_by_level(level: str):
    collection = get_collection()
    cursor = collection.find({"level": level})
    return [doc async for doc in cursor]

async def get_logs_by_source(source: str):
    collection = get_collection()
    cursor = collection.find({"source": source})
    return [doc async for doc in cursor]

async def get_logs_by_corpus_id(corpus_id: str):
    collection = get_collection()
    cursor = collection.find({"details.corpusId": corpus_id})
    return [doc async for doc in cursor]

# ❌ Delete
async def delete_log_by_id(log_id: str):
    collection = get_collection()
    result = await collection.delete_one({"_id": log_id})
    return result.deleted_count

async def delete_all_logs():
    collection = get_collection()
    result = await collection.delete_many({})
    print(f"🗑️ Deleted {result.deleted_count} log entries.")

# ✅ Init
async def init_general_logs_collection():
    db = get_db()
    existing_collections = await db.list_collection_names()
    if "general_logs" not in existing_collections:
        await db.create_collection("general_logs")
        print("✅ 'general_logs' collection created.")
    else:
        print("ℹ️ 'general_logs' collection already exists.")
