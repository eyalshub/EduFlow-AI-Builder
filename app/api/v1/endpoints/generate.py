#app/api/v1/endpoints/generate.py
from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from app.schemas.input_model import Stage1Input
from app.core.pipeline.stage_1_corpus_initial import run_stage_1

router = APIRouter()

@router.post("/generate-corpus")
async def generate_corpus(
    topicName: str = Form(...),
    subject: str = Form(...),
    gradeLevel: str = Form(...),
    bigIdea: str = Form(...),
    learningGate: str = Form(...),
    skills: str = Form(...),  # comma-separated string from form
    context: Optional[str] = Form(None),
    freePrompt: Optional[str] = Form(None),
    courseLanguage: Optional[str] = Form("he"),
    generationScope: Optional[str] = Form("Single Lesson"),
    numLessons: Optional[int] = Form(None),
    usePerplexity: Optional[bool] = Form(False),
):
    try:
        input_data = Stage1Input(
            topicName=topicName,
            subject=subject,
            gradeLevel=gradeLevel,
            bigIdea=bigIdea,
            learningGate=learningGate,
            skills=[s.strip() for s in skills.split(",") if s.strip()],
            context=context,
            freePrompt=freePrompt,
            courseLanguage=courseLanguage,
            generationScope=generationScope,
            numLessons=numLessons,
            usePerplexity=usePerplexity
        )
        result = await run_stage_1(input_data)
        return JSONResponse(
    status_code=200,
    content={"_id": str(result)}
)

    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "error", "detail": str(e)})
