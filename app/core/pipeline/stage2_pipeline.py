# app/core/pipeline/stage2_pipeline.py
from typing import List
from types import SimpleNamespace

from app.schemas.stage2 import (
    Stage2Request,
    Stage2Result,
    EditTextResult,
    GeneratedQuestion,
    VerificationResult,
    BlockRef,
)
from app.core.agents.text_editor_agent import run_text_editor_agent, TextEditorInput
from app.core.agents.question_generator_agent import run_question_generator_agent, QuestionGenInput
from app.core.agents.bloom_level_verifier_agent import run_bloom_level_verifier_agent
from app.core.agents.difficulty_level_verifier_agent import run_difficulty_level_verifier_agent
from app.core.agents.grounding_verifier_agent import run_grounding_verifier_agent
from app.crud.crud_block import bulk_upsert_blocks  
from app.utils.idempotency import new_pipeline_run_id
from app.core.normalizers.question_normalizer import (
    normalize_mcq,
    shuffle_mcq_choices,
    is_dup_by_stem,
)


async def run_stage2(req: Stage2Request) -> Stage2Result:
    """
    Entry point for Stage 2. Adds a run-id if missing and routes by mode.
    """
    if req.pipeline_run_id is None:
        req.pipeline_run_id = new_pipeline_run_id()

    if req.mode == "edit_text":
        return await _run_edit_text(req)
    elif req.mode == "generate_questions":
        return await _run_generate_questions(req)
    else:
        raise ValueError("Invalid mode")


async def _run_edit_text(req: Stage2Request) -> Stage2Result:
    """
    Run the Text Editor Agent, optionally save a 'Paragraph' block, and return the result.
    """
    input_payload: TextEditorInput = {
        "stage1": req,  # carries topicName, subject, gradeLevel, etc.
        "raw_text": req.text,
        "audience": "students",
        "instructionStyle": "neutral",
        "outputFormat": "plain_text",
        "allowFormatting": False,
    }

    response = await run_text_editor_agent(input_payload)

    result = EditTextResult(
        edited_text=response.get("edited_text", ""),
        changes_summary=(response.get("justification", "") or "").split("\n")
        if response.get("justification")
        else [],
    )

    # Save to blocks if required
    saved_blocks: List[BlockRef] = []
    if req.save_to_blocks:
        block_dict = {
            "blockType": "Paragraph",
            "content": {"text": result.edited_text},
            "metadata": {"purpose": "Refined Text"},
            "courseOutlineId": req.courseOutlineId,
            "lessonId": req.lessonId,
            "sectionId": req.sectionId,
            "pageId": req.pageId,
            "pipeline_run_id": req.pipeline_run_id,
        }
        saved = await bulk_upsert_blocks([block_dict])
        saved_blocks = [{"_id": b["_id"], "blockType": b["blockType"]} for b in saved]

    return Stage2Result(
        mode=req.mode,
        edited_text=result.edited_text,
        saved_blocks=saved_blocks,
        summary={"chars": len(result.edited_text)},
    )



# async def _run_generate_questions(req: Stage2Request) -> Stage2Result:
#     """
#     Generate questions:
#       - Ensure 'num_questions' are collected using iterative calls.
#       - Validate/normalize MCQs, shuffle choices, and keep 'correct_index' accurate.
#       - De-duplicate by 'stem'.
#       - Optionally save all collected questions as blocks.
#     """
#     # Prepare chunk iterator; also support freePrompt fallback
#     chunks_iter = list(req.chunks) if req.chunks else []
#     if (not chunks_iter) and req.freePrompt and req.freePrompt.strip():
#         pseudo_text = f"Question topic: {req.freePrompt.strip()}"
#         pseudo = SimpleNamespace(chunk_id="free_prompt_ctx", text=pseudo_text)
#         chunks_iter = [pseudo]
#         req.chunks = [{"chunk_id": pseudo.chunk_id, "text": pseudo.text}]
#     if not chunks_iter:
#         return Stage2Result(
#             mode=req.mode,
#             generated=[],
#             saved_blocks=[],
#             summary={"num_chunks": 0, "total_questions": 0},
#         )

#     # Map enums to values (default to MCQ if not provided)
#     qtype_value = (
#         getattr(req.question_types[0], "value", str(req.question_types[0])).lower()
#         if req.question_types and len(req.question_types) > 0
#         else "mcq"
#     )

#     target_n = int(req.num_questions or 1)
#     collected: List[GeneratedQuestion] = []
#     attempts = 0
#     MAX_ATTEMPTS = max(3, target_n * 2)  # safety cap to avoid endless loops

#     # Outer loop: keep asking until we collect at least 'target_n' or hit attempt cap
#     while len(collected) < target_n and attempts < MAX_ATTEMPTS:
#         for chunk in chunks_iter:
#             remaining = target_n - len(collected)
#             if remaining <= 0:
#                 break

#             # Temporarily override 'req.chunks' and 'req.num_questions' to request only what's missing
#             original_chunks = req.chunks
#             original_num = req.num_questions
#             try:
#                 req.chunks = [{"chunk_id": getattr(chunk, "chunk_id"), "text": getattr(chunk, "text")}]
#                 req.num_questions = remaining
#                 response = await run_question_generator_agent(req)  # expected shape: {"questions": [...]}
#             finally:
#                 req.chunks = original_chunks
#                 req.num_questions = original_num

#             # Parse agent output
#             for q in response.get("questions", []):
#                 if not isinstance(q, dict):
#                     try:
#                         q = q.dict()
#                     except Exception:
#                         print("❌ Cannot convert to dict:", type(q))
#                         continue

             

#                 q["type"] = q.get("type", qtype_value).lower()
#                 print("🔍 Type detected:", q["type"])

#                 # Support both MCQ and open questions
#                 if q["type"] not in ["mcq", "open", "matching"]:
#                     print("⛔ Unsupported type:", q["type"])

#                     continue

#                 if q["type"] == "mcq":
#                     try:
#                         q = normalize_mcq(q)
#                         shuffle_mcq_choices(q)
#                     except Exception:
#                         print("⚠️ Malformed MCQ:", e)

#                         continue  # Skip malformed MCQ

#                 # Anti-dup by stem
#                 if any(is_dup_by_stem(q, gq.question) for gq in collected):
#                     print("🔁 Duplicate stem:", q["stem"])

#                     continue

#                 stem = q.get("stem", "")

#                 # Optional verifications
#                 cog_out = await run_bloom_level_verifier_agent({
#                     "question": stem,
#                     "bloom_level": getattr(req.cognitive_target, "value", str(req.cognitive_target)),
#                 }) if req.cognitive_target else {}

#                 diff_out = await run_difficulty_level_verifier_agent({
#                     "question": stem,
#                     "text": getattr(chunk, "text"),
#                     "difficulty_level": getattr(req.target_difficulty, "value", str(req.target_difficulty)),
#                 }) if req.target_difficulty else {}

#                 grounding_out = await run_grounding_verifier_agent({
#                     "question": stem,
#                     "answer": q.get("choices", [None])[q.get("correct_index", 0)] if q["type"] == "mcq" else "",
#                     "explanation": q.get("explanation", ""),
#                     "chunk": getattr(chunk, "text"),
#                 })

#                 collected.append(
#                     GeneratedQuestion(
#                         question=q,
#                         cognitive_verification=VerificationResult(
#                             detected=cog_out.get("detected_level"),
#                             match=cog_out.get("matches_target"),
#                             score=cog_out.get("match_score"),
#                             justification=cog_out.get("justification"),
#                         ) if cog_out else None,
#                         difficulty_verification=VerificationResult(
#                             detected=diff_out.get("detected_difficulty"),
#                             match=diff_out.get("matches_target"),
#                             score=diff_out.get("match_score"),
#                             justification=diff_out.get("justification"),
#                         ) if diff_out else None,
#                         grounding_verification={
#                             "grounded": grounding_out.get("grounded"),
#                             "quotes": grounding_out.get("evidence_spans"),
#                         } if grounding_out else None,
#                     )
#                 )

#                 if len(collected) >= target_n:
#                     break

#         attempts += 1

#     # Optionally save collected questions as blocks
#     saved_blocks: List[BlockRef] = []
#     if req.save_to_blocks and collected:
#         blocks = []
#         for gq in collected:
#             block = {
#                 "blockType": "question",
#                 "content": {
#                     "question": gq.question,
#                     "metadata": {
#                         "topic": req.topicName,
#                         "subject": req.subject,
#                         "grade_level": req.gradeLevel,
#                         "big_idea": req.bigIdea,
#                         "learning_gate": req.learningGate,
#                         "course_language": req.courseLanguage,
#                         "bloom_level": getattr(req.cognitive_target, "value", str(req.cognitive_target)) if req.cognitive_target else None,
#                         "difficulty": getattr(req.target_difficulty, "value", str(req.target_difficulty)) if req.target_difficulty else None,
#                         "chunk_ids": [c.chunk_id for c in chunks_iter] if chunks_iter else [],
#                     },
#                 },
#                 "metadata": {},
#                 "courseOutlineId": req.courseOutlineId,
#                 "lessonId": req.lessonId,
#                 "sectionId": req.sectionId,
#                 "pageId": req.pageId,
#                 "pipeline_run_id": req.pipeline_run_id,
#             }
#             blocks.append(block)

#         saved = await bulk_upsert_blocks(blocks)
#         saved_blocks = [
#             {"_id": saved[i]["_id"], "blockType": blocks[i]["blockType"]}
#             for i in range(len(blocks))
#         ]

#     return Stage2Result(
#         mode=req.mode,
#         generated=collected,
#         saved_blocks=saved_blocks,
#         summary={
#             "num_chunks": len(chunks_iter),
#             "total_questions": len(collected),
#             "requested": target_n,
#             "attempts": attempts,
#         },
#     )


async def _run_generate_questions(req: Stage2Request) -> Stage2Result:
    """
    Generate questions:
      - Ensure 'num_questions' are collected using iterative calls.
      - Validate/normalize MCQs, shuffle choices, and keep 'correct_index' accurate.
      - De-duplicate by 'stem'.
      - Run multi-agent verification (Bloom, difficulty, grounding).
      - Only accept questions that pass validation; optionally save as blocks.
    """
    # Prepare chunk iterator; also support freePrompt fallback
    chunks_iter = list(req.chunks) if req.chunks else []
    if (not chunks_iter) and req.freePrompt and req.freePrompt.strip():
        pseudo_text = f"Question topic: {req.freePrompt.strip()}"
        pseudo = SimpleNamespace(chunk_id="free_prompt_ctx", text=pseudo_text)
        chunks_iter = [pseudo]
        req.chunks = [{"chunk_id": pseudo.chunk_id, "text": pseudo.text}]
    if not chunks_iter:
        return Stage2Result(
            mode=req.mode,
            generated=[],
            saved_blocks=[],
            summary={"num_chunks": 0, "total_questions": 0},
        )

    # Map enums to values (default to MCQ if not provided)
    qtype_value = (
        getattr(req.question_types[0], "value", str(req.question_types[0])).lower()
        if req.question_types and len(req.question_types) > 0
        else "mcq"
    )

    target_n = int(req.num_questions or 1)
    collected: List[GeneratedQuestion] = []
    attempts = 0
    MAX_ATTEMPTS = max(3, target_n * 2)  # safety cap to avoid endless loops

    # Memory for rejected stems – avoid generating the same bad question again
    bad_stems = set()

    # Outer loop: keep asking until we collect at least 'target_n' or hit attempt cap
    while len(collected) < target_n and attempts < MAX_ATTEMPTS:
        for chunk in chunks_iter:
            remaining = target_n - len(collected)
            if remaining <= 0:
                break

            # Temporarily override 'req.chunks' and 'req.num_questions' to request only what's missing
            original_chunks = req.chunks
            original_num = req.num_questions
            try:
                req.chunks = [{"chunk_id": getattr(chunk, "chunk_id"), "text": getattr(chunk, "text")}]
                req.num_questions = remaining
                response = await run_question_generator_agent(req)  # expected shape: {"questions": [...]}
            finally:
                req.chunks = original_chunks
                req.num_questions = original_num

            # Parse agent output
            for q in response.get("questions", []):
                if not isinstance(q, dict):
                    try:
                        q = q.dict()
                    except Exception:
                        print("❌ Cannot convert to dict:", type(q))
                        continue

                q["type"] = q.get("type", qtype_value).lower()
                print("🔍 Type detected:", q["type"])

                # Support MCQ, open, matching
                if q["type"] not in ["mcq", "open", "matching"]:
                    print("⛔ Unsupported type:", q["type"])
                    continue

                if q["type"] == "mcq":
                    try:
                        q = normalize_mcq(q)
                        shuffle_mcq_choices(q)
                    except Exception as e:
                        print("⚠️ Malformed MCQ:", e)
                        continue  # Skip malformed MCQ

                stem = q.get("stem", "").strip()
                if not stem:
                    print("⚠️ Missing stem, skipping question")
                    continue

                # Anti-dup by stem vs. already accepted questions
                if any(is_dup_by_stem(q, gq.question) for gq in collected):
                    print("🔁 Duplicate stem vs collected:", stem)
                    continue

                # Also avoid stems that were previously rejected by validators
                if stem in bad_stems:
                    print("♻️ Previously rejected stem, skipping:", stem)
                    continue

                # Optional verifications
                cog_out = await run_bloom_level_verifier_agent({
                    "question": stem,
                    "bloom_level": getattr(req.cognitive_target, "value", str(req.cognitive_target)),
                }) if req.cognitive_target else {}

                diff_out = await run_difficulty_level_verifier_agent({
                    "question": stem,
                    "text": getattr(chunk, "text"),
                    "difficulty_level": getattr(req.target_difficulty, "value", str(req.target_difficulty)),
                }) if req.target_difficulty else {}

                grounding_out = await run_grounding_verifier_agent({
                    "question": stem,
                    "answer": q.get("choices", [None])[q.get("correct_index", 0)] if q["type"] == "mcq" else "",
                    "explanation": q.get("explanation", ""),
                    "chunk": getattr(chunk, "text"),
                })

                # Decide if this question passes the validation stack
                bloom_ok = True
                if req.cognitive_target and cog_out:
                    bloom_ok = bool(cog_out.get("matches_target", False))

                difficulty_ok = True
                if req.target_difficulty and diff_out:
                    difficulty_ok = bool(diff_out.get("matches_target", False))

                grounding_ok = True
                if grounding_out:
                    grounding_ok = bool(grounding_out.get("grounded", False))

                all_ok = bloom_ok and difficulty_ok and grounding_ok

                if not all_ok:
                    # This is where the reject-loop logic kicks in
                    bad_stems.add(stem)
                    print(
                        "❌ Rejected by validators:",
                        {
                            "stem": stem,
                            "bloom_ok": bloom_ok,
                            "difficulty_ok": difficulty_ok,
                            "grounding_ok": grounding_ok,
                        },
                    )
                    # Don't collect this question – let the loop request another one
                    continue

                # If all checks passed → accept question
                collected.append(
                    GeneratedQuestion(
                        question=q,
                        cognitive_verification=VerificationResult(
                            detected=cog_out.get("detected_level"),
                            match=cog_out.get("matches_target"),
                            score=cog_out.get("match_score"),
                            justification=cog_out.get("justification"),
                        ) if cog_out else None,
                        difficulty_verification=VerificationResult(
                            detected=diff_out.get("detected_difficulty"),
                            match=diff_out.get("matches_target"),
                            score=diff_out.get("match_score"),
                            justification=diff_out.get("justification"),
                        ) if diff_out else None,
                        grounding_verification={
                            "grounded": grounding_out.get("grounded"),
                            "quotes": grounding_out.get("evidence_spans"),
                        } if grounding_out else None,
                    )
                )

                if len(collected) >= target_n:
                    break

        attempts += 1

    # Optionally save collected questions as blocks
    saved_blocks: List[BlockRef] = []
    if req.save_to_blocks and collected:
        blocks = []
        for gq in collected:
            block = {
                "blockType": "question",
                "content": {
                    "question": gq.question,
                    "metadata": {
                        "topic": req.topicName,
                        "subject": req.subject,
                        "grade_level": req.gradeLevel,
                        "big_idea": req.bigIdea,
                        "learning_gate": req.learningGate,
                        "course_language": req.courseLanguage,
                        "bloom_level": getattr(req.cognitive_target, "value", str(req.cognitive_target)) if req.cognitive_target else None,
                        "difficulty": getattr(req.target_difficulty, "value", str(req.target_difficulty)) if req.target_difficulty else None,
                        "chunk_ids": [c.chunk_id for c in chunks_iter] if chunks_iter else [],
                    },
                },
                "metadata": {},
                "courseOutlineId": req.courseOutlineId,
                "lessonId": req.lessonId,
                "sectionId": req.sectionId,
                "pageId": req.pageId,
                "pipeline_run_id": req.pipeline_run_id,
            }
            blocks.append(block)

        saved = await bulk_upsert_blocks(blocks)
        saved_blocks = [
            {"_id": saved[i]["_id"], "blockType": blocks[i]["blockType"]}
            for i in range(len(blocks))
        ]

    return Stage2Result(
        mode=req.mode,
        generated=collected,
        saved_blocks=saved_blocks,
        summary={
            "num_chunks": len(chunks_iter),
            "total_questions": len(collected),
            "requested": target_n,
            "attempts": attempts,
        },
    )
