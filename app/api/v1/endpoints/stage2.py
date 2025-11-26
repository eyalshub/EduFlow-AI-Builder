#app/api/v1/endpoints/stage2.py
from fastapi import APIRouter, HTTPException
from app.schemas.stage2 import Stage2Request, Stage2Result
from app.core.pipeline.stage2_pipeline import run_stage2

router = APIRouter()

@router.post("/stage2/run", response_model=Stage2Result)
async def run_stage2_endpoint(req: Stage2Request):
    """
    Run Stage 2 pipeline for either text editing or question generation.
    """
    try:
        result = await run_stage2(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
