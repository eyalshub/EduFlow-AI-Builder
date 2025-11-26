from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DeploymentLog(Document):
    outlineId: str
    status: str  # e.g., "Success" or "Failure"
    errorLog: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "deployment_logs"
