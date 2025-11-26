# core/normalizers/lms_normalizer.py

from uuid import uuid4
from typing import List, Dict
from app.schemas.lms import LMSBlock, LMSPage, LMSLesson, LMSDocument, BlockType

# 🟦 Normalize raw block dictionaries into structured LMSBlock objects
def normalize_blocks(raw_blocks: List[Dict], lesson_id: str, page_id: str) -> List[LMSBlock]:
    normalized = []
    for raw in raw_blocks:
        block_type = raw.get("blockType", "text")
        content = raw.get("content", {})
        metadata = raw.get("metadata", {})

        block = LMSBlock(
            pageId=page_id,
            lessonId=lesson_id,
            blockType=block_type,
            content=content,
            metadata=metadata
        )
        normalized.append(block)
    return normalized

# 🟦 Wrap blocks into a single LMSPage
def create_page(title: str, blocks: List[LMSBlock], lesson_id: str) -> LMSPage:
    return LMSPage(
        title=title,
        lessonId=lesson_id,
        blocks=blocks
    )

# 🟦 Wrap pages into a single LMSLesson
def create_lesson(title: str, pages: List[LMSPage], course_id: str) -> LMSLesson:
    return LMSLesson(
        title=title,
        courseId=course_id,
        pages=pages
    )

# 🟦 Build a complete LMSDocument from a list of raw blocks
def normalize_from_raw_content(
    raw: List[Dict], 
    course_id: str, 
    lesson_title: str = "Lesson 1", 
    page_title: str = "Main Page"
) -> LMSDocument:
    lesson_id = f"lesson_{uuid4().hex}"
    page_id = f"page_{uuid4().hex}"

    blocks = normalize_blocks(raw_blocks=raw, lesson_id=lesson_id, page_id=page_id)
    page = create_page(title=page_title, blocks=blocks, lesson_id=lesson_id)
    lesson = create_lesson(title=lesson_title, pages=[page], course_id=course_id)

    return LMSDocument(
        courseId=course_id,
        lessons=[lesson]
    )
