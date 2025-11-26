# app/utils/lms_block_converter.py
from typing import Dict
from app.utils.lms_structures import (
    build_mcq_question,
    build_open_question,
    build_matching_question,
    build_rich_text_paragraph_block
)

def build_lms_block(block_data: Dict) -> Dict:
    """
    Converts a normalized block dictionary into a fully structured LMS-compatible JSON block.
    Supports: Multiple Choice, Open-ended, Matching, and Rich Text blocks.
    """
    block_type = block_data.get("blockType")

    # 🔹 Question block: could be MCQ, open-ended, or matching
    if block_type == "question":
        question = block_data.get("question", {})
        q_type = question.get("type")

        if q_type == "mcq":
            return build_mcq_question(
                stem=question["stem"],
                options=question["choices"],
                correct_index=question["correct_index"]
            )

        elif q_type == "open":
            return build_open_question(
                stem=question["stem"]
            )

        elif q_type == "matching":
            return build_matching_question(
                pairs=question["pairs"],
                distractors=question.get("distractors", [])
            )

    # 🔹 Text editing block (rich text paragraph)
    elif block_type == "edit":
        return build_rich_text_paragraph_block(
            text=block_data["text"]
        )

    # 🔺 Unsupported block type or missing content
    raise ValueError(f"Unsupported block type or content: {block_data}")
