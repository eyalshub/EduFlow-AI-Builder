# app/core/agents/main_llm_orchestrator_agent.py

from typing import Optional, List, Literal
from pydantic import BaseModel
from app.schemas.lms import LMSBlock, LMSDocument
from app.core.agents.text_editor_agent import run_text_editor_agent
from app.core.pipeline.stage_1_corpus_initial import run_stage_1
from app.core.agents.question_generator_agent import run_question_generator_agent
from app.schemas.input_model import Stage1Input
from app.core.pipeline.stage2_pipeline import run_stage2
from app.schemas.stage2 import Stage2Request
from app.services.factory import get_llm_service
from app.crud.crud_chat_history import save_chat_message
from typing import Union

# Input to the main agent
class OrchestratorInput(BaseModel):
    task: Literal["stage1_full_course", "edit_text", "generate_questions", "chat"]
    userInput: Union[str, Stage1Input, Stage2Request]
    courseId: Optional[str] = None
    gradeLevel: Optional[str] = None
    subject: Optional[str] = None
    fileContent: Optional[str] = None
    lmsJson: Optional[dict] = None

# Agent output
class OrchestratorResponse(BaseModel):
    success: bool
    document: Optional[LMSDocument] = None
    blocks: Optional[List[LMSBlock]] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None


# Main function of the agent
async def run_main_orchestrator(input: OrchestratorInput) -> OrchestratorResponse:
    try:
        if input.task == "stage1_full_course":
            corpus_doc = await run_stage_1(input.userInput, input.subject, input.gradeLevel)
            return OrchestratorResponse(
                success=True,
                document=corpus_doc,
                message="Stage 1 completed: course structure and content generated."
            )
        elif input.task == "chat":
            llm = get_llm_service() 
            response_text = await llm.run(str(input.userInput))
            await save_chat_message(input.courseId or "anon", str(input.userInput), response_text)

            return OrchestratorResponse(
                success=True,
                message="Chat response generated.",
                blocks=[LMSBlock(
                    blockType="text",
                    content={"text": response_text},
                    pageId="page_1",
                    lessonId="lesson_1"
                )]
            )
        elif input.task == "edit_text":
                try:
                    stage1_data = input.lmsJson or {}
                    stage1_input = Stage1Input(**stage1_data)
                except Exception as e:
                    return OrchestratorResponse(
                        success=False,
                        message="Failed to parse Stage1Input from lmsJson",
                        errors=[str(e)]
                    )
                result = await run_text_editor_agent({
                    "stage1": stage1_input,
                    "raw_text": input.userInput,
                    "audience": "תלמידי תיכון",
                    "instructionStyle": "הסבר פשוט ובהיר",
                    "outputFormat": "פסקה טקסטואלית",
                    "allowFormatting": False
                })
                if result.get("status") != "ok":
                    return OrchestratorResponse(
                        success=False,
                        message="Text editing failed",
                        errors=[result.get("reason", "Unknown error")]
                    )
                block = LMSBlock(
                blockType="text",
                content={"text": result.get("edited_text", "")},
                pageId="page_1",
                lessonId="lesson_1"
            )
                return OrchestratorResponse(
                        success=True,
                        blocks=[block],
                        message="Text edited successfully."
                    )
        elif input.task == "generate_questions":
            try:
                data = dict(input.lmsJson or {})

                data.pop("mode", None)
                stage2_req = Stage2Request(
                    **data,
                    mode="generate_questions",
                    text=input.userInput if isinstance(input.userInput, str) else "",  # 🛠
                    freePrompt=input.userInput if isinstance(input.userInput, str) else "",  # 🛠
                    courseOutlineId=input.courseId or "outline_1",
                    lessonId="lesson_1",
                    sectionId="section_1",
                    pageId="page_1"
                )
            except Exception as e:
                return OrchestratorResponse(
                    success=False,
                    message="Failed to create Stage2Request from orchestrator input.",
                    errors=[str(e)]
                )

            stage2_result = await run_stage2(stage2_req)

            blocks = []
            if stage2_result.generated:
                for gq in stage2_result.generated:
                    blocks.append(LMSBlock(
                        blockType="question",
                        content=gq.question,
                        pageId="page_1",
                        lessonId="lesson_1"
                    ))

            return OrchestratorResponse(
                success=True,
                blocks=blocks,
                message=f"Generated {len(blocks)} questions successfully." if blocks else "No questions generated."
            )

        else:
            return OrchestratorResponse(success=False, message="Unknown task")

    except Exception as e:
        return OrchestratorResponse(success=False, errors=[str(e)], message="Exception occurred")
