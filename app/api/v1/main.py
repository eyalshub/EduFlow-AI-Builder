# app/api/main.py
from fastapi import APIRouter
from app.api.v1.endpoints import generate, content_corpus, stage2

api_router = APIRouter()

api_router.include_router(generate.router, prefix="/api/v1", tags=["Content Corpus"])
api_router.include_router(content_corpus.router, prefix="/api/v1", tags=["Content Corpus"])
api_router.include_router(stage2.router, prefix="/api/v1", tags=["Stage 2"])
