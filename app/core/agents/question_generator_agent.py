# app/core/agents/question_generator_agent.py
# -*- coding: utf-8 -*-
import logging
from typing import List, Optional, TypedDict, Literal, Union, Tuple

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.schemas.input_model import Stage1Input
from app.schemas.stage2 import Stage2Request
from app.services.prompt_manager import load_prompt, render_user_prompt
import json

load_dotenv()
logger = logging.getLogger(__name__)

# ---- Load prompt from YAML ----
prompt_data = load_prompt("data_agents/question_generator_prompt.yaml")
system_tpl = prompt_data["system"]
user_tpl = prompt_data["user"]

# ---- LLM config ----
llm = ChatOpenAI(model="gpt-4.1", temperature=0.8)

# ---- Pydantic Output Schema (discriminated union) ----
class MCQQuestion(BaseModel):
    type: Literal["mcq"]
    stem: str
    choices: List[str]
    correct_index: int
    explanation: Optional[str] = None

class OpenQuestion(BaseModel):
    type: Literal["open"]
    stem: str
    expected_answer: str
    guidance: Optional[str] = None

class MatchingQuestion(BaseModel):
    type: Literal["matching"]
    instructions: str
    pairs: List[Tuple[str, str]]
    distractors: List[str]

QuestionUnion = Union[MCQQuestion, OpenQuestion, MatchingQuestion]

class QuestionGenResponse(BaseModel):
    questions: List[QuestionUnion]

parser = PydanticOutputParser(pydantic_object=QuestionGenResponse)

# ---- Data Types ----
class Chunk(TypedDict):
    chunk_id: str
    text: str

class QuestionGenInput(TypedDict):
    question_type: Literal["mcq", "open", "matching"]
    bloom_level: str
    difficulty: float
    chunks: List[Chunk]
    stage1: Stage1Input

# ---- Optional: normalize legacy keys before parsing ----
def _normalize_legacy(text: str) -> str:
    try:
        obj = json.loads(text)
    except Exception:
        return text
    if isinstance(obj, dict) and "questions" in obj and isinstance(obj["questions"], list):
        for q in obj["questions"]:
            if isinstance(q, dict):
                # open: prompt -> stem, ideal_answer -> expected_answer
                if q.get("type") == "open":
                    if "prompt" in q and "stem" not in q:
                        q["stem"] = q.pop("prompt")
                    if "ideal_answer" in q and "expected_answer" not in q:
                        q["expected_answer"] = q.pop("ideal_answer")
                # matching: if missing type but structure indicates matching
                if "instructions" in q and "pairs" in q and "type" not in q:
                    q["type"] = "matching"
        return json.dumps(obj, ensure_ascii=False)
    return text


def questions_to_blocks(questions: list) -> list:
    blocks = []
    for q in questions:
        qtype = q.get("type")
        if qtype == "mcq":
            blk = {
                "blockType": "question",
                "content": {
                    "question": {
                        "stem": q["stem"],
                        "choices": q["choices"],
                        "correct_index": q["correct_index"],
                        "explanation": q.get("explanation", "")
                    }
                },
                "metadata": None
            }
            blocks.append(blk)

        elif qtype == "open":
            blk = {
                "blockType": "question",
                "content": {
                    "question": {
                        "stem": q["stem"],
                        "expected_answer": q["expected_answer"],
                        "guidance": q.get("guidance", "")
                    }
                },
                "metadata": None
            }
            blocks.append(blk)

        elif qtype == "matching":
            blk = {
                # אפשר לשקול blockType ייעודי "matching" אם יש לך רנדרר כזה ב-LMS
                "blockType": "question",
                "content": {
                    "matching": {
                        "instructions": q["instructions"],
                        "pairs": q["pairs"],
                        "distractors": q.get("distractors", [])
                    }
                },
                "metadata": None
            }
            blocks.append(blk)

        else:
            # סוג לא נתמך כרגע – דלג
            continue

    return blocks

# ---- Agent Function ----
async def run_question_generator_agent(input: Stage2Request) -> dict:
    try:
        context = {
            "topicName": input.topicName,
            "subject": input.subject,
            "gradeLevel": input.gradeLevel,
            "bigIdea": input.bigIdea,
            "learningGate": input.learningGate,
            "skills": input.skills,
            "context": input.context,
            "freePrompt": input.freePrompt,
            "courseLanguage": input.courseLanguage,
            "question_type": input.question_types[0].value,
            "bloom_level": input.cognitive_target.value,
            "difficulty": input.target_difficulty.value,
            "chunks": input.chunks,
        }

        rendered_user = render_user_prompt(user_tpl, context) + "\n\n" + parser.get_format_instructions()

        messages = [
            SystemMessage(content=system_tpl),
            HumanMessage(content=rendered_user),
        ]

        raw_response = await llm.ainvoke(messages)
        print("🧠 Raw LLM Response:\n", raw_response)

        clean_text = _normalize_legacy(raw_response.content)
        print("🧼 Cleaned Text:\n", clean_text)
        parsed = parser.parse(clean_text)
        parsed_questions = parsed.questions
        return {
            "success": True,
            "questions": parsed_questions,
            "blocks": questions_to_blocks([q.dict() for q in parsed_questions])
        }


    except Exception as e:
        logger.exception("❌ Failed to parse LLM response into QuestionGenResponse.")
        return {
            "status": "error",
            "reason": "invalid_format_or_llm_error",
            "exception": str(e),
        }

__all__ = ["run_question_generator_agent", "QuestionGenInput"]
