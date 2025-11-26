import asyncio
from datetime import datetime
from mongoDB_project.config.connection import db

async def insert_example_outline():
    example_outline_doc = {
        "_id": "course_outline_456",
        "courseTitle": "World History: Age of Revolutions",
        "courseDescription": "This course explores the major political and social upheavals from the 18th to the 19th century...",
        "subject": "History",
        "gradeLevel": "9",
        "language": "en",
        "status": "Approved",
        "createdAt": datetime.utcnow().isoformat(),
        "approvedAt": datetime.utcnow().isoformat(),
        "version": 2,
        "lessons": [
            {
                "lessonId": "lesson_01",
                "lessonTitle": "The French Revolution: A Double-Edged Sword",
                "lessonDescription": "We will explore...",
                "corpusId": "corpus_unique_id_789",
                "bigIdea": "Revolutions devour their own children.",
                "learningGate": "שער מפגש",
                "skillObjectives": ["Develop teamwork skills", "Practice respectful debate"],
                "sections": [
                    {
                        "sectionId": "sec_01_01",
                        "sectionTitle": "The Causes of the Revolution",
                        "pages": [
                            {
                                "pageId": "page_01_01_01",
                                "pageTitle": "The Three Estates",
                                "blocks": [
                                    "block_mongo_id_abc1",
                                    "block_mongo_id_abc2"
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    existing = await db["outlines"].find_one({"_id": example_outline_doc["_id"]})
    if not existing:
        await db["outlines"].insert_one(example_outline_doc)
        print("📥 Example document inserted into 'outlines'.")
    else:
        print("📄 Example outline already exists.")

if __name__ == "__main__":
    asyncio.run(insert_example_outline())
