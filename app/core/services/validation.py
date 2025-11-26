# core/services/validation.py

from typing import List, TypedDict
from app.schemas.lms import LMSDocument, LMSLesson, LMSPage, LMSBlock, BlockType

class ValidationReport(TypedDict):
    valid: bool
    errors: List[str]
    warnings: List[str]

# ✅ Main validation function
def validate_lms(doc: LMSDocument) -> ValidationReport:
    errors = []
    warnings = []

    # 1. Course ID
    if not doc.courseId:
        errors.append("Missing courseId in LMSDocument")

    # 2. Lessons
    if not doc.lessons:
        errors.append("No lessons found in LMSDocument")

    for lesson in doc.lessons:
        if not lesson.lessonId:
            errors.append("Missing lessonId in one of the lessons")
        if not lesson.pages:
            errors.append(f"Lesson '{lesson.title}' has no pages")

        for page in lesson.pages:
            if not page.pageId:
                errors.append(f"Missing pageId in page of lesson '{lesson.title}'")
            if not page.blocks:
                warnings.append(f"Page '{page.title}' has no blocks")

            for block in page.blocks:
                if not block.blockId:
                    errors.append("Missing blockId in one of the blocks")
                if block.blockType not in ["text", "question", "image", "video", "embed", "instruction"]:
                    errors.append(f"Invalid blockType: {block.blockType}")
                if not block.content:
                    warnings.append(f"Block {block.blockId} has empty content")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
