# app/schemas/stage2.py
# This file defines the schemas for Stage 2 of the application, including request and result models.
from enum import Enum
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


# --- Enums ---

class Stage2Mode(str, Enum):
    edit_text = "edit_text"
    generate_questions = "generate_questions"

class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class CognitiveTarget(str, Enum):
    knowledge = "knowledge"
    comprehension_application = "comprehension_application"
    inference_evaluation = "inference_evaluation"

class QuestionType(str, Enum):
    MCQ = "mcq"
    OPEN = "open"
    MATCHING = "matching"

# --- Request Models ---

class Chunk(BaseModel):
    chunk_id: str
    text: str
    scope: Optional[dict] = None  # optional: lessonId, sectionId, pageId...

class Stage2Request(BaseModel):
    # Common input from Stage 1
    topicName: str
    subject: str
    gradeLevel: str
    bigIdea: str
    generationScope: str
    skills: List[str]
    learningGate: str
    context: Optional[str] = None
    freePrompt: Optional[str] = None
    courseLanguage: Optional[str] = "he"  
    # Either chunks (for question gen) or raw text (for edit)
    chunks: Optional[List[Chunk]] = None
    text: Optional[str] = None

    mode: Stage2Mode

    # Text editing options
    language: Optional[str] = None
    max_length: Optional[int] = None

    # Question generation options
    question_types: Optional[List[QuestionType]] = None
    num_questions: Optional[int] = Field(default=None, ge=1, le=20)
    cognitive_target: Optional[CognitiveTarget] = None
    target_difficulty: Optional[Difficulty] = None

    # Saving options
    save_to_blocks: bool = True
    courseOutlineId: Optional[str] = None
    lessonId: Optional[str] = None
    sectionId: Optional[str] = None
    pageId: Optional[str] = None

    pipeline_run_id: Optional[str] = None
    @model_validator(mode="after")
    def _validate_mode_dependencies(self) -> "Stage2Request":
        """
        Enforce required fields based on mode, and provide sensible defaults.
        """
        if self.mode == Stage2Mode.generate_questions:
            # num_questions is required in this mode
            if self.num_questions is None:
                raise ValueError("num_questions is required when mode=generate_questions")

            # chunks are strongly recommended/expected for question generation
            if not self.chunks or len(self.chunks) == 0:
                raise ValueError("chunks must be provided (non-empty) when mode=generate_questions")

            # default question type to MCQ if not provided
            if not self.question_types or len(self.question_types) == 0:
                self.question_types = [QuestionType.MCQ]

        if self.mode == Stage2Mode.edit_text:
            # text is expected in edit mode
            if not self.text:
                raise ValueError("text must be provided when mode=edit_text")

        return self

# --- Result Models ---

class VerificationResult(BaseModel):
    detected: Optional[str] = None
    match: Optional[bool] = None
    score: Optional[float] = None
    justification: Optional[str] = None


class GroundingEvidence(BaseModel):
    chunk_id: str
    quote: str


class GeneratedQuestion(BaseModel):
    """
    We keep 'question' as a dict for flexibility, but validate MCQ shape when applicable.
    Expected MCQ keys: stem (str), choices (List[str]), correct_index (int in range), explanation (opt).
    """
    question: Dict[str, Any]
    cognitive_verification: Optional[VerificationResult] = None
    difficulty_verification: Optional[VerificationResult] = None
    grounding_verification: Optional[Dict[str, Any]] = None  # e.g., {"grounded": True, "quotes": [...]}

    @model_validator(mode="after")
    def _validate_mcq_shape(self) -> "GeneratedQuestion":
        q = self.question or {}
        qtype = (q.get("type") or q.get("question_type") or "").lower()

        # If it's explicitly an MCQ OR looks like MCQ (has choices)
        looks_like_mcq = isinstance(q.get("choices"), list)
        if qtype == "mcq" or looks_like_mcq:
            # Ensure required keys exist
            if "stem" not in q or "choices" not in q:
                raise ValueError("MCQ question must include 'stem' and 'choices'")

            # Validate correct_index presence (support both snake/camel)
            if "correct_index" not in q and "correctIndex" not in q:
                raise ValueError("MCQ question must include 'correct_index' (or 'correctIndex')")

            # Normalize correct_index to int and validate range
            idx = q.get("correct_index", q.get("correctIndex"))
            try:
                idx = int(idx)
            except Exception as e:
                raise ValueError(f"MCQ 'correct_index' must be an integer: {e}")

            if not isinstance(q["choices"], list) or len(q["choices"]) == 0:
                raise ValueError("MCQ 'choices' must be a non-empty list")

            if idx < 0 or idx >= len(q["choices"]):
                raise ValueError("MCQ 'correct_index' is out of range for given 'choices'")

            # Write-back normalized key to snake_case (internal canonical form)
            q["correct_index"] = idx
            if "correctIndex" in q:
                # keep internal canonical schema; external mapping can convert later
                del q["correctIndex"]

            self.question = q

        return self

class EditTextResult(BaseModel):
    edited_text: str
    changes_summary: Optional[List[str]] = Field(default_factory=list)

class BlockRef(BaseModel):
    _id: str
    blockType: str

class Stage2Result(BaseModel):
    mode: Stage2Mode
    edited_text: Optional[str] = None
    generated: Optional[List[GeneratedQuestion]] = Field(default=None)
    saved_blocks: List[BlockRef] = Field(default_factory=list)
    summary: Optional[dict] = None
