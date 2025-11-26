#app/api/v1/endpoints/final_pipeline.py
from fastapi import APIRouter
from app.schemas.lms import FullLessonInput
from app.core.pipeline.final_pipeline import generate_full_lesson_pipeline

router = APIRouter()

@router.post("/generate-full-lesson")
async def generate_full_lesson(input_data: FullLessonInput):
    result = await generate_full_lesson_pipeline(input_data)
    return result
