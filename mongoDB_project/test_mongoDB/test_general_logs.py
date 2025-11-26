import asyncio
from datetime import datetime
from mongoDB_project.config.connection import db
from app.models import general_logs

example_log_entry = {
    "_id": "log_entry_id_123",
    "timestamp": datetime.utcnow().isoformat(),
    "level": "INFO",
    "source": "Stage1_ContentAcquisition",
    "message": "Content corpus generated successfully for topic 'The French Revolution'.",
    "details": {
        "corpusId": "corpus_unique_id_789",
        "durationMs": 1500,
        "additionalInfo": "Cache miss, new generation performed.",
        "filePath": "content_sources/server.py"
    }
}


async def run():
    await general_logs.insert_log_entry(example_log_entry)

    logs_by_level = await general_logs.get_logs_by_level("INFO")
    print(f"\n🔎 Logs with level 'INFO': {len(logs_by_level)} entries")

    logs_by_source = await general_logs.get_logs_by_source("Stage1_ContentAcquisition")
    print(f"\n📦 Logs from Stage1_ContentAcquisition: {len(logs_by_source)} entries")

    recent_logs = await general_logs.get_recent_logs(minutes=10)
    print(f"\n🕒 Logs from last 10 minutes: {len(recent_logs)} entries")


if __name__ == "__main__":
    asyncio.run(run())
