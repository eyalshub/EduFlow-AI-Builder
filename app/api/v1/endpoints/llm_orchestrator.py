# app/api/v1/endpoints/llm_orchestrator.py

from fastapi import APIRouter
from app.core.agents.main_llm_orchestrator_agent import (
    OrchestratorInput,
    OrchestratorResponse,
    run_main_orchestrator
)

router = APIRouter()

@router.post("/llm-orchestrator", response_model=OrchestratorResponse)
async def llm_orchestration(input: OrchestratorInput):
    return await run_main_orchestrator(input)
