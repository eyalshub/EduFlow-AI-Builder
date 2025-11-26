# app/models/chat_history.py
from beanie import Document
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str  # "user" / "assistant"
    content: str
    timestamp: str


class ChatHistory(Document):
    userId: str
    messages: List[ChatMessage]
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chat_history"
