# app/api/endpoints/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.factory import get_llm_service

router = APIRouter()

class ChatRequest(BaseModel):
    user_input: str
    provider: Optional[str] = None 

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    llm = get_llm_service(request.provider)
    messages = [
        {"role": "system", "content": "You are a helpful educational assistant."},
        {"role": "user", "content": request.user_input}
    ]
    reply = await llm.chat(messages)
    return {"response": reply}
