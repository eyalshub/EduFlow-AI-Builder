# app/api/v1/endpoints/chatbot.py

from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.chatbot import ChatTurn, ChatResponse
from app.core.orchestrator.chat_orchestrator import run_chat_turn

router = APIRouter()

# 📨 POST /chat – text-based interaction
@router.post("/chat", response_model=ChatResponse)
async def chat_with_text(
    text: str = Form(...),
    courseId: str = Form(default="course_123"),
    lessonTitle: str = Form(default="Lesson 1"),
    pageTitle: str = Form(default="Page 1")
):
    chat_input = ChatTurn(
        text=text,
        courseId=courseId,
        lessonTitle=lessonTitle,
        pageTitle=pageTitle
    )
    return await run_chat_turn(chat_input)

# 📂 POST /chat/upload – file-based interaction
@router.post("/chat/upload", response_model=ChatResponse)
async def chat_with_file(
    file: UploadFile = File(...),
    courseId: str = Form(default="course_123"),
    lessonTitle: str = Form(default="Lesson 1"),
    pageTitle: str = Form(default="Page 1")
):
    file_bytes = await file.read()

    chat_input = ChatTurn(
        file=file_bytes,
        filename=file.filename,
        courseId=courseId,
        lessonTitle=lessonTitle,
        pageTitle=pageTitle
    )
    return await run_chat_turn(chat_input)
