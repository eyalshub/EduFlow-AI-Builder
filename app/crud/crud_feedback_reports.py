from datetime import datetime
from app.core.config import get_db

# ➕ Insert / Upsert

async def insert_feedback_report_if_not_exists(report_doc: dict):
    db = get_db()
    existing = await db["feedback_reports"].find_one({"_id": report_doc["_id"]})
    if not existing:
        await db["feedback_reports"].insert_one(report_doc)
        print("📥 Feedback report inserted.")
    else:
        print("📄 Feedback report already exists.")

async def upsert_feedback_report(report_doc: dict):
    db = get_db()
    result = await db["feedback_reports"].replace_one(
        {"_id": report_doc["_id"]},
        report_doc,
        upsert=True
    )
    return result.upserted_id or report_doc["_id"]

# 🔍 Reads

async def get_feedback_report_by_id(report_id: str):
    db = get_db()
    return await db["feedback_reports"].find_one({"_id": report_id})

async def get_feedback_reports_by_outline(outline_id: str):
    db = get_db()
    cursor = db["feedback_reports"].find({"outlineId": outline_id})
    return [doc async for doc in cursor]

async def get_feedback_reports_by_block(block_id: str):
    db = get_db()
    cursor = db["feedback_reports"].find({"blockId": block_id})
    return [doc async for doc in cursor]

# 🧠 Analysis Helpers

async def get_blocks_needing_revision(outline_id: str = None):
    db = get_db()
    query = {"overallStatus": "Needs_Revision"}
    if outline_id:
        query["outlineId"] = outline_id
    cursor = db["feedback_reports"].find(query)
    return [doc async for doc in cursor]

# ❌ Delete

async def delete_feedback_report(report_id: str):
    db = get_db()
    result = await db["feedback_reports"].delete_one({"_id": report_id})
    return result.deleted_count
