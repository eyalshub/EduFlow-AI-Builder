from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FeedbackReport(Document):
    blockId: str
    outlineId: str
    overallStatus: str  # e.g., "Approved", "Needs_Revision"
    revisionPrompt: Optional[str]
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "feedback_reports"
