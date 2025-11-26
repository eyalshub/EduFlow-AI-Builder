# app/models/content_corpus.py
from __future__ import annotations

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from beanie import Document, Indexed
from pymongo import IndexModel


# -------- Source chunk internals --------

class ProcessedSection(BaseModel):
    title: str
    text: str


class ProcessedContent(BaseModel):
    summary: str
    sections: List[ProcessedSection] = Field(default_factory=list)


SourceType = Literal[
    "Wikipedia",
    "Uploaded_PDF",
    "Perplexity_Search",
    "ContextualCourseAgent",
    "Course_Scoping_Agent",
    "Webpage",
    "Other",
]


class SourceChunk(BaseModel):
    # trace/id for cross-references (e.g., in pedagogicalAnalysis)
    chunkId: Optional[str] = None

    sourceType: SourceType
    sourceURI: Optional[str] = None
    sourceName: Optional[str] = None
    sourceQuery: Optional[str] = None

    # timestamps as ISO8601 strings with trailing 'Z' (to match pipeline output)
    retrievedAt: str
    processedContent: ProcessedContent


# -------- Root content --------

class Content(BaseModel):
    finalSummary: str
    sourceChunks: List[SourceChunk] = Field(default_factory=list)
    # Stage 2 may use this; ok to persist from Stage 1 when present
    scopedLessons: Optional[List[str]] = None


# -------- Pedagogical analysis --------

class PedagogicalTerm(BaseModel):
    term: str
    definition: str


class BigIdeaAlignmentItem(BaseModel):
    bigIdea: str
    supportingEvidenceSnippet: str
    # reference a chunkId from sourceChunks (e.g., "ch_01")
    sourceChunkReference: str


class PedagogicalAnalysis(BaseModel):
    masterGlossary: List[PedagogicalTerm] = Field(default_factory=list)
    bigIdeaAlignment: List[BigIdeaAlignmentItem] = Field(default_factory=list)


# -------- Mongo document --------

class ContentCorpus(Document):
    # unique (sparse) index to enforce idempotent upserts
    cacheKey: Optional[str] = Indexed(str, unique=True)  # Optional → sparse

    topicName: str
    subject: str
    gradeLevel: str
    createdAt: str  # ISO8601 UTC with trailing 'Z'
    version: float = 1.1

    content: Content
    pedagogicalAnalysis: Optional[PedagogicalAnalysis] = None
    pipelineMeta: Optional[Dict[str, Any]] = None

    class Settings:
        name = "content_corpus"
        # Define index explicitly as well (safe if duplicated with `Indexed`)
        indexes = [
            IndexModel([("cacheKey", 1)], unique=True, sparse=True),
        ]
