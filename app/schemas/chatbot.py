# app/schemas/chatbot.py
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.lms import LMSDocument

class ChatTurn(BaseModel):
    text: Optional[str] = None
    file: Optional[bytes] = None
    filename: Optional[str] = None
    courseId: Optional[str] = None
    lessonTitle: Optional[str] = None
    pageTitle: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    document: Optional[LMSDocument] = None
    errors: Optional[List[str]] = []
    warnings: Optional[List[str]] = []
