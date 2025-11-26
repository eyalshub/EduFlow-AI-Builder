from datetime import datetime, timedelta
from app.core.config import get_db

# === Utility
def get_collection():
    db = get_db()
    return db["outlines"]

# ➕ Insert / Upsert

async def insert_outline_if_not_exists(outline_doc: dict):
    db = get_db()
    existing = await db["outlines"].find_one({"_id": outline_doc["_id"]})
    if not existing:
        await db["outlines"].insert_one(outline_doc)
        print("📥 Inserted example outline document.")
    else:
        print("📄 Outline document already exists.")

async def upsert_outline(outline_doc: dict):
    db = get_db()
    result = await db["outlines"].replace_one(
        {"_id": outline_doc["_id"]},
        outline_doc,
        upsert=True
    )
    return result.upserted_id or outline_doc["_id"]

# 🔍 Reads

async def get_outline_by_id(outline_id: str):
    db = get_db()
    return await db["outlines"].find_one({"_id": outline_id})

async def get_all_outlines():
    collection = get_collection()
    cursor = collection.find()
    return [doc async for doc in cursor]

async def find_outlines(subject: str = None, grade: str = None):
    db = get_db()
    query = {}
    if subject:
        query["subject"] = subject
    if grade:
        query["gradeLevel"] = grade
    cursor = db["outlines"].find(query)
    return [doc async for doc in cursor]

async def find_recent_outlines(days_back: int = 7):
    db = get_db()
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    cursor = db["outlines"].find({"createdAt": {"$gte": cutoff.isoformat()}})
    return [doc async for doc in cursor]

# 🛠️ Updates

async def update_outline_status(outline_id: str, new_status: str):
    db = get_db()
    result = await db["outlines"].update_one(
        {"_id": outline_id},
        {"$set": {"status": new_status}}
    )
    return result.modified_count

async def append_block_to_page(outline_id: str, page_id: str, block_id: str):
    db = get_db()
    result = await db["outlines"].update_one(
        {
            "_id": outline_id,
            "lessons.sections.pages.pageId": page_id
        },
        {
            "$push": {
                "lessons.$[].sections.$[].pages.$[page].blocks": block_id
            }
        },
        array_filters=[{"page.pageId": page_id}]
    )
    return result.modified_count

# 🔗 Relations

async def get_corpus_for_outline(outline_id: str):
    db = get_db()
    outline = await db["outlines"].find_one({"_id": outline_id})
    if not outline:
        return None
    corpus_id = outline["lessons"][0]["corpusId"]
    return await db["content_corpus"].find_one({"_id": corpus_id})

async def validate_outline_dependencies(outline_doc: dict):
    db = get_db()
    missing_corpus = []
    missing_blocks = []

    for lesson in outline_doc.get("lessons", []):
        corpus_id = lesson.get("corpusId")
        if not await db["content_corpus"].find_one({"_id": corpus_id}):
            missing_corpus.append(corpus_id)

        for section in lesson.get("sections", []):
            for page in section.get("pages", []):
                for block_id in page.get("blocks", []):
                    if not await db["blocks"].find_one({"_id": block_id}):
                        missing_blocks.append(block_id)

    return {
        "missingCorpus": missing_corpus,
        "missingBlocks": missing_blocks
    }

# ❌ Delete

async def delete_outline_by_id(outline_id: str):
    db = get_db()
    result = await db["outlines"].delete_one({"_id": outline_id})
    return result.deleted_count
