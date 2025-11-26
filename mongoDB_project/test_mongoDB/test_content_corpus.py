import asyncio
from datetime import datetime
from mongoDB_project.config.connection import db 

async def insert_example_document():
    example_doc = {
        "_id": "corpus_unique_id_789",
        "topicName": "The French Revolution",
        "subject": "History",
        "gradeLevel": "9",
        "createdAt": datetime.utcnow().isoformat(),
        "version": 1.1,
        "content": {
            "finalSummary": "...",
            "sourceChunks": [
                {
                    "sourceType": "Wikipedia",
                    "sourceURI": "https://en.wikipedia.org/wiki/French_Revolution",
                    "retrievedAt": datetime.utcnow().isoformat(),
                    "processedContent": {
                        "summary": "...",
                        "sections": [
                            {"title": "Causes", "text": "..."}
                        ]
                    }
                }
            ]
        },
        "pedagogicalAnalysis": {
            "masterGlossary": [
                {"term": "Estates-General", "definition": "..."}
            ],
            "bigIdeaAlignment": [
                {
                    "bigIdea": "Revolutions devour their own children.",
                    "supportingEvidenceSnippet": "...",
                    "sourceChunkReference": "Wikipedia"
                }
            ]
        }
    }

    existing = await db["content_corpus"].find_one({"_id": example_doc["_id"]})
    if not existing:
        await db["content_corpus"].insert_one(example_doc)
        print("📥 Example document inserted into 'content_corpus'.")
    else:
        print("📄 Example document already exists.")

if __name__ == "__main__":
    asyncio.run(insert_example_document())
