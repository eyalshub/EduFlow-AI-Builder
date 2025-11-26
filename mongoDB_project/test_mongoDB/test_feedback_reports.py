# mongoDB_project/test_mongoDB/test_feedback_reports.py

import asyncio
from datetime import datetime
from mongoDB_project.config.connection import db
from app.models.feedback_reports import insert_feedback_report_if_not_exists

example_feedback = {
    "_id": "feedback_report_xyz",
    "timestamp": datetime.utcnow().isoformat(),
    "outlineId": "bp_uniqueLessonId_MeetingGate_FINAL",
    "blockId": "block_id_001",
    "reviewResults": [
        {
            "principle": "עומק הלמידה",
            "status": "Pass",
            "comment": "The question requires analysis and justification."
        },
        {
            "principle": "חיבור ללמידה",
            "status": "Fail",
            "comment": "The question is too abstract. It needs to be linked to the student's experience."
        },
        {
            "principle": "מעורבות בלמידה",
            "status": "Pass",
            "comment": "The block is an active task."
        }
    ],
    "overallStatus": "Needs_Revision",
    "revisionPrompt": "Rewrite this question to be more open-ended and connect to the student's personal experience by asking them to recall a similar situation."
}


async def run():
    await insert_feedback_report_if_not_exists(example_feedback)
    doc = await db["feedback_reports"].find_one({"_id": example_feedback["_id"]})
    print("✅ Inserted and fetched:" if doc else "❌ Insert failed.")

if __name__ == "__main__":
    asyncio.run(run())
