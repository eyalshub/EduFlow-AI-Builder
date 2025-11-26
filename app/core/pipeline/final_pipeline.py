# app/core/pipeline/final_pipeline.py

import logging
from typing import Dict, Any
from app.schemas.lms import FullLessonInput
from app.core.pipeline.stage_1_corpus_initial import run_stage_1
from app.core.pipeline.stage2_pipeline import run_stage2
from app.schemas.stage2 import Stage2Request

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def generate_full_lesson_pipeline(data: FullLessonInput) -> Dict[str, Any]:
    logger.info(f"🌀 Starting pipeline – Mode: {data.mode}")

    if data.mode == "stage1":
        logger.info("🔧 Running Stage 1...")
        try:
            document = await run_stage_1(data)
            logger.info("✅ Stage 1 completed")
            return {
                "success": True,
                "mode": "stage1",
                "document": document
            }
        except Exception as e:
            logger.exception("❌ Error in Stage 1")
            return {
                "success": False,
                "mode": "stage1",
                "error": str(e),
                "message": "Failed to generate full lesson pipeline"
            }

    elif data.mode == "stage2":
        logger.info("🔧 Running Stage 2...")

        try:
            stage2_input = Stage2Request(
                mode=data.stage2_mode,  # must be "generate_questions" or "edit_text"
                topicName=data.topicName,
                subject=data.subject,
                gradeLevel=data.gradeLevel,
                bigIdea=data.bigIdea,
                courseLanguage=data.courseLanguage,
                learningGate=data.learningGate,
                generationScope=data.generationScope,
                skills=data.skills,
                question_types=data.question_types,
                num_questions=data.num_questions,
                save_to_blocks=data.save_to_blocks,
                cognitive_target=data.cognitive_target,
                target_difficulty=data.target_difficulty,
                chunks=data.chunks,
                text=data.text,
                language=data.language,
                max_length=data.max_length,
                context=data.context,
                freePrompt=data.freePrompt,
                courseOutlineId=data.courseOutlineId,
                lessonId=data.lessonId,
                sectionId=data.sectionId,
                pageId=data.pageId,
                pipeline_run_id=data.pipeline_run_id
            )

            logger.debug("📥 Stage2Request ready: %s", stage2_input.model_dump())

            result = await run_stage2(stage2_input)
            logger.info("✅ Stage 2 completed")

            return {
    "success": True,
    "mode": "stage2",
    "blocks": result.blocks,
    "errors": result.errors,
    "message": result.message,
}

        except Exception as e:
            logger.exception("❌ Error in Stage 2")
            return {
                "success": False,
                "mode": "stage2",
                "error": str(e),
                "message": "Failed to generate full lesson pipeline"
            }

    else:
        logger.warning("❗ Invalid mode specified: %s", data.mode)
        return {
            "success": False,
            "error": f"Invalid mode: {data.mode}",
            "message": "Mode must be either 'stage1' or 'stage2'"
        }
