from beanie import Document
from pydantic import Field
from typing import List, Optional, Any
from datetime import datetime


class Outline(Document):
    title: str
    subject: str
    gradeLevel: str
    status: str = "Draft"
    lessons: List[dict]
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "outlines"
