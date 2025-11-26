# app/models/block.py

from beanie import Document
from datetime import datetime
from pydantic import Field
from typing import Optional

class Block(Document):
    pageId: str
    content: dict
    blockType: str
    courseOutlineId: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    evaluationRubric: Optional[dict] = None

    class Settings:
        name = "blocks"
