# app/schemas/lms.py

from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from uuid import uuid4

from app.schemas.stage2 import (
    CognitiveTarget,
    Difficulty,
    QuestionType,
    Chunk,
)


# LMS STRUCTURE OUTPUT

BlockType = Literal["text", "question", "image", "video", "embed", "instruction"]

class LMSBlock(BaseModel):
    blockId: str = Field(default_factory=lambda: f"block_{uuid4().hex}")
    pageId: str
    lessonId: str
    blockType: BlockType
    content: dict
    metadata: Optional[dict] = None


class LMSPage(BaseModel):
    pageId: str = Field(default_factory=lambda: f"page_{uuid4().hex}")
    lessonId: str
    title: str
    blocks: List[LMSBlock] = Field(default_factory=list)


class LMSLesson(BaseModel):
    lessonId: str = Field(default_factory=lambda: f"lesson_{uuid4().hex}")
    courseId: str
    title: str
    pages: List[LMSPage] = Field(default_factory=list)


class LMSDocument(BaseModel):
    courseId: str
    lessons: List[LMSLesson]
    version: str = "1.0"


# ✅ FULL INPUT FOR FINAL PIPELINE (Stage1 + Stage2 Compatible)

class FullLessonInput(BaseModel):
    # ---- Mode Selection ----
    mode: Literal["stage1", "stage2"]
    stage2_mode: Optional[Literal["edit_text", "generate_questions"]] = None

    # ---- Common Fields ----
    topicName: str
    subject: str
    gradeLevel: str
    bigIdea: str
    learningGate: Literal["Meeting Gate", "Independence Gate", "Discovery Gate"]
    generationScope: Literal["Single Lesson", "Full Course"] = "Single Lesson"
    courseLanguage: Optional[str] = "he"
    skills: List[str] = Field(default_factory=list)

    context: Optional[str] = None
    freePrompt: Optional[str] = None

    # ---- Stage 1 specific ----
    numLessons: Optional[int] = None
    usePerplexity: Optional[bool] = False

    # ---- Stage 2 specific ----
    question_types: Optional[List[QuestionType]] = None
    num_questions: Optional[int] = None
    save_to_blocks: Optional[bool] = False
    cognitive_target: Optional[CognitiveTarget] = None
    target_difficulty: Optional[Difficulty] = None
    chunks: Optional[List[Chunk]] = Field(default_factory=list)
    text: Optional[str] = None  # only for edit_text
    language: Optional[str] = None
    max_length: Optional[int] = None

    courseOutlineId: Optional[str] = None
    lessonId: Optional[str] = None
    sectionId: Optional[str] = None
    pageId: Optional[str] = None
    pipeline_run_id: Optional[str] = None
