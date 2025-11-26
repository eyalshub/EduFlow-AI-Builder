# app/crud/crud_block.py
from pymongo import UpdateOne
from datetime import datetime, timedelta
from app.core.config import get_db

# ➕ Insert / Upsert
async def insert_block_if_not_exists(block_doc: dict):
    db = get_db()
    existing = await db["blocks"].find_one({"_id": block_doc["_id"]})
    if not existing:
        await db["blocks"].insert_one(block_doc)
        print("📥 Block inserted.")
    else:
        print("📄 Block already exists.")

async def upsert_block(block_doc: dict):
    db = get_db()
    result = await db["blocks"].replace_one(
        {"_id": block_doc["_id"]},
        block_doc,
        upsert=True
    )
    return result.upserted_id or block_doc["_id"]

# 🔍 Reads
async def get_block_by_id(block_id: str):
    db = get_db()
    return await db["blocks"].find_one({"_id": block_id})

async def get_all_blocks():
    db = get_db()
    cursor = db["blocks"].find()
    return [doc async for doc in cursor]

async def find_blocks_by_page(page_id: str):
    db = get_db()
    cursor = db["blocks"].find({"pageId": page_id})
    return [doc async for doc in cursor]

async def find_blocks_by_outline(outline_id: str):
    db = get_db()
    cursor = db["blocks"].find({"courseOutlineId": outline_id})
    return [doc async for doc in cursor]

async def find_recent_blocks(days_back: int = 7):
    db = get_db()
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    cursor = db["blocks"].find({"createdAt": {"$gte": cutoff.isoformat()}})
    return [doc async for doc in cursor]

# 🛠️ Update
async def update_block_text(block_id: str, new_text: str):
    db = get_db()
    result = await db["blocks"].update_one(
        {"_id": block_id},
        {"$set": {"content.text": new_text}}
    )
    return result.modified_count

async def add_evaluation_rubric(block_id: str, rubric: dict):
    db = get_db()
    result = await db["blocks"].update_one(
        {"_id": block_id},
        {"$set": {"evaluationRubric": rubric}}
    )
    return result.modified_count

# ❌ Delete
async def delete_block_by_id(block_id: str):
    db = get_db()
    result = await db["blocks"].delete_one({"_id": block_id})
    return result.deleted_count

# 📘 Question-type blocks
async def get_question_blocks_by_outline(outline_id: str):
    db = get_db()
    question_types = ["Multiple_Choice_Question", "Open_Ended_Question", "True_False_Question"]
    cursor = db["blocks"].find({
        "courseOutlineId": outline_id,
        "blockType": {"$in": question_types}
    })
    return [doc async for doc in cursor]

async def get_question_blocks_by_corpus(corpus_id: str):
    db = get_db()
    outlines_cursor = db["outlines"].find({
        "lessons.corpusId": corpus_id
    })
    outline_ids = [outline["_id"] async for outline in outlines_cursor]

    question_types = ["Multiple_Choice_Question", "Open_Ended_Question", "True_False_Question"]
    cursor = db["blocks"].find({
        "courseOutlineId": {"$in": outline_ids},
        "blockType": {"$in": question_types}
    })
    return [doc async for doc in cursor]


async def bulk_upsert_blocks(blocks: list[dict]):
    """
    Efficiently upserts a list of blocks using bulk_write.
    Assumes each block has a unique _id or deterministic key.
    """
    db = get_db()

    ops = []
    for block in blocks:
        block["updatedAt"] = datetime.utcnow().isoformat()
        if "createdAt" not in block:
            block["createdAt"] = block["updatedAt"]

        filter_key = {
            "_id": block.get("_id")
        } if "_id" in block else {
            "pipeline_run_id": block["pipeline_run_id"],
            "blockType": block["blockType"],
            "content.questionText": block["content"].get("questionText", "")
        }

        ops.append(UpdateOne(
            filter_key,
            {"$set": block},
            upsert=True
        ))

    if ops:
        result = await db["blocks"].bulk_write(ops)
        print(f"✅ Bulk upsert complete. Inserted: {result.upserted_count}, Modified: {result.modified_count}")

    # Read back saved docs 
    return [block async for block in db["blocks"].find({
        "pipeline_run_id": blocks[0]["pipeline_run_id"]
    })]