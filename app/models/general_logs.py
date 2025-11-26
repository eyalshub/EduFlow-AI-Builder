# app/models/general_logs.py
from beanie import Document
from typing import Optional, Dict
from datetime import datetime

class GeneralLog(Document):
    level: str                     # e.g., "INFO", "WARNING", "ERROR"
    source: str                    # e.g., "fetcher", "deployment"
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = datetime.utcnow()

    class Settings:
        name = "general_logs"
