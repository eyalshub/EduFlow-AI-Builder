# app/core/orchestrator/chat_orchestrator.py

from app.schemas.chatbot import ChatTurn, ChatResponse
from app.core.services.file_ingest import ingest_upload
from app.core.normalizers.lms_normalizer import normalize_from_raw_content
from app.core.services.validation import validate_lms
from app.schemas.lms import LMSDocument

# 🎯 Central orchestrator: receives input, returns structured LMS JSON or errors
async def run_chat_turn(input: ChatTurn) -> ChatResponse:
    try:
        # 1. Ingest input (file or text)
        if input.file:
            ingest_result = await ingest_upload(file_bytes=input.file, filename=input.filename)
        elif input.text:
            ingest_result = {"kind": "text", "content": input.text}
        else:
            return ChatResponse(success=False, errors=["No input provided."], document=None)

        # 2. Normalize to LMSDocument
        if ingest_result["kind"] == "json":
            raw_blocks = ingest_result["content"].get("blocks", [])
        else:  # text
            raw_blocks = [{"blockType": "text", "content": {"text": ingest_result["content"]}}]

        lms_doc: LMSDocument = normalize_from_raw_content(
            raw=raw_blocks,
            course_id=input.courseId or "course_default",
            lesson_title=input.lessonTitle or "Lesson",
            page_title=input.pageTitle or "Page"
        )

        # 3. Validate LMSDocument
        validation = validate_lms(lms_doc)

        if not validation["valid"]:
            return ChatResponse(
                success=False,
                errors=validation["errors"],
                warnings=validation["warnings"],
                document=lms_doc
            )

        # 4. Return success response with LMS JSON
        return ChatResponse(
            success=True,
            document=lms_doc,
            warnings=validation["warnings"]
        )

    except Exception as e:
        return ChatResponse(success=False, errors=[str(e)], document=None)
