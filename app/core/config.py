# app/core/config.py
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# === Load environment variables ===
load_dotenv()

class Settings:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GRAQ_API_KEY = os.getenv("GRAQ_API_KEY", "")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    DB_NAME = os.getenv("DB_NAME", "mongo_project_amit")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    COLLECTION_NAMES = [
        "content_corpus",
        "outlines",
        "blocks",
        "feedback_reports",
        "deployment_logs",
        "general_logs",
        "chat_history"
    ]

settings = Settings()

# === MongoDB client factory ===
def get_db():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    return client[settings.DB_NAME]

# === Beanie initialization ===
from app.models.content_corpus import ContentCorpus
from app.models.outlines import Outline
from app.models.blocks import Block
from app.models.feedback_reports import FeedbackReport
from app.models.deployment_logs import DeploymentLog
from app.models.general_logs import GeneralLog
from app.models.chat_history import ChatHistory

async def init_db():
    db = get_db()
    try:
        await init_beanie(
            database=db,
            document_models=[
                ContentCorpus,
                Outline,
                Block,
                FeedbackReport,
                DeploymentLog,
                GeneralLog,
                ChatHistory
            ]
        )
        print("✅ Beanie initialized successfully.")
    except Exception as e:
        print(f"❌ Beanie initialization failed: {e}")

# === Test connection ===
async def check_connection():
    db = get_db()
    try:
        await db.command("ping")
        print("✅ MongoDB connection is alive (ping successful).")
    except Exception as e:
        print(f"❌ MongoDB ping failed: {e}")

if __name__ == "__main__":
    import asyncio

    async def main():
        await check_connection()
        await init_db()

    asyncio.run(main())