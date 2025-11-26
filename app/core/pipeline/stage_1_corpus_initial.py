# app/core/pipeline/stage_1_corpus_initial.py
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from pymongo.errors import DuplicateKeyError

from app.schemas.input_model import Stage1Input
from app.utils import generate_cache_key, current_timestamp
from app.services.fetchers.wikipedia_fetcher import fetch_wikipedia_summary
from app.services.fetchers.perplexity_fetcher import fetch_perplexity_summary
from app.services.fetchers.file_processor import process_uploaded_file
from app.core.agents.contextual_agent import run_contextual_agent
from app.core.agents.course_scoping_agent import run_course_scoping_agent
from app.models.content_corpus import ContentCorpus
from app.core.agents.lesson_content_agent import run_lesson_content_agent
from app.schemas.input_model import LessonContentAgentInput
logger = logging.getLogger(__name__)

# ---------- helpers ----------
def ensure_utc_iso_z(ts: Optional[str] = None) -> str:
    try:
        if ts:
            s = ts.replace("Z", "")
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
        else:
            dt = datetime.now(timezone.utc)
    except Exception:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def normalize_chunk(chunk: Dict[str, Any], default_source_type: Optional[str] = None) -> Dict[str, Any]:
    c = dict(chunk or {})
    if default_source_type and not c.get("sourceType"):
        c["sourceType"] = default_source_type
    pc = dict(c.get("processedContent") or {})
    pc["summary"] = (pc.get("summary") or "").strip()
    if "sections" not in pc or pc["sections"] is None:
        pc["sections"] = []
    c["processedContent"] = pc
    c["retrievedAt"] = ensure_utc_iso_z(c.get("retrievedAt") or current_timestamp())
    return c

def ensure_sections(chunk: Dict[str, Any]) -> Dict[str, Any]:
    pc = chunk.get("processedContent", {})
    if pc and pc.get("summary") and not pc.get("sections"):
        pc["sections"] = [{"title": "Overview", "text": pc["summary"]}]
        chunk["processedContent"] = pc
    return chunk

def add_chunk_ids(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for i, ch in enumerate(chunks, start=1):
        ch["chunkId"] = f"ch_{i:02d}"
    return chunks

def topic_keywords(topic: str) -> List[str]:
    return [w.lower() for w in topic.replace("-", " ").split() if len(w.strip()) >= 3]

def compute_topic_alignment(topic: str, texts: str) -> float:
    kws = topic_keywords(topic)
    if not kws:
        return 1.0
    text_lc = texts.lower()
    hits = sum(1 for k in kws if k in text_lc)
    return hits / len(kws)

def build_pedagogical_analysis(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    ref_id = None
    for c in chunks:
        if c.get("sourceType") == "Wikipedia":
            ref_id = c.get("chunkId")
            break
    if not ref_id and chunks:
        ref_id = chunks[0].get("chunkId", "ch_01")

    glossary = [
        {"term": "Estates-General", "definition": "Synthesized definition from all sources."},
        {"term": "Sans-culottes",   "definition": "Synthesized definition from all sources."}
    ]
    big_ideas = [{
        "bigIdea": "Revolutions devour their own children.",
        "supportingEvidenceSnippet": "The Reign of Terror saw early leaders executed, illustrating internal radicalization.",
        "sourceChunkReference": ref_id
    }]
    return {"masterGlossary": glossary, "bigIdeaAlignment": big_ideas}
# -------------------------------------


async def run_stage_1(inputs: Stage1Input, uploaded_files: Optional[List[str]] = None) -> str:
    logger.info("🚀 Starting Stage 1: Initial Content Corpus Acquisition")

    # Step 1: Course Scoping (lesson titles)
    lesson_titles: List[str] = []
    should_scope = (inputs.generationScope in ("Full Course", "Single Topic")) and (inputs.numLessons or 0) >= 1
    if should_scope:
        try:
            logger.info("📚 [CourseScopingAgent] Proposing lesson titles...")
            lesson_titles = await run_course_scoping_agent(inputs)
            lesson_titles = [t.strip() for t in (lesson_titles or []) if t and t.strip()]
            logger.info(f"✅ Lesson titles ({len(lesson_titles)}): {lesson_titles}")
        except Exception:
            logger.exception("❌ Failed to generate lesson titles")
            lesson_titles = []

    # Step 2: Wikipedia
    topic_clean = inputs.topicName.strip()
    wiki_slug  = quote(topic_clean.replace(" ", "_"))
    wiki_url   = f"https://he.wikipedia.org/wiki/{wiki_slug}"
    try:
        logger.info("🌐 Fetching from Wikipedia...")
        wiki_summary = fetch_wikipedia_summary(topic_clean) or "No Wikipedia summary found."
        wiki_data = normalize_chunk({
            "sourceType": "Wikipedia",
            "sourceQuery": topic_clean,
            "sourceURI": wiki_url,
            "retrievedAt": current_timestamp(),
            "processedContent": {"summary": wiki_summary, "sections": []}
        }, default_source_type="Wikipedia")
    except Exception:
        logger.exception("❌ Failed to fetch Wikipedia data")
        wiki_data = normalize_chunk({
            "sourceType": "Wikipedia",
            "sourceQuery": topic_clean,
            "sourceURI": wiki_url,
            "retrievedAt": current_timestamp(),
            "processedContent": {"summary": "Failed to fetch Wikipedia", "sections": []}
        }, default_source_type="Wikipedia")

    # Step 3: Perplexity
    perplexity_data: Optional[Dict[str, Any]] = None
    if inputs.usePerplexity or not uploaded_files:
        try:
            logger.info("🔎 [PerplexityAgent] Generating summary via LLM...")
            raw = await fetch_perplexity_summary(topic=inputs.topicName, subject=inputs.subject, lang="he")
            if isinstance(raw, dict):
                perplexity_data = normalize_chunk(raw, default_source_type="Perplexity_Search")
                if perplexity_data.get("sourceType") in (None, "", "Perplexity"):
                    perplexity_data["sourceType"] = "Perplexity_Search"
                if "sourceURI" not in perplexity_data:
                    perplexity_data["sourceURI"] = "https://www.perplexity.ai/search/mock"
            else:
                perplexity_data = normalize_chunk({
                    "sourceType": "Perplexity_Search",
                    "sourceURI": "https://www.perplexity.ai/search/mock",
                    "retrievedAt": current_timestamp(),
                    "processedContent": {"summary": str(raw), "sections": []}
                }, default_source_type="Perplexity_Search")
        except Exception:
            logger.exception("❌ Failed to fetch Perplexity summary")
            perplexity_data = normalize_chunk({
                "sourceType": "Perplexity_Search",
                "retrievedAt": current_timestamp(),
                "processedContent": {"summary": "Failed to fetch Perplexity summary", "sections": []}
            }, default_source_type="Perplexity_Search")

    # Step 4: Uploaded files
    uploaded_data: List[Dict[str, Any]] = []
    if uploaded_files:
        try:
            logger.info("📂 Processing uploaded files...")
            tasks = [asyncio.to_thread(process_uploaded_file, path) for path in uploaded_files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    logger.exception("❌ Failed processing file", exc_info=r)
                    continue
                uploaded_data.append(normalize_chunk(r, default_source_type="Uploaded_PDF"))
            logger.info(f"✅ Processed {len(uploaded_data)} files")
        except Exception:
            logger.exception("❌ Failed to process uploaded files")

    # Step 5: Contextual Agent
    contextual_data: Optional[Dict[str, Any]] = None
    context_result = ""
    try:
        logger.info("🧠 [ContextualAgent] Adapting content to context...")
        context_result = await run_contextual_agent(inputs)
        contextual_data = normalize_chunk({
            "sourceType": "ContextualCourseAgent",
            "retrievedAt": current_timestamp(),
            "processedContent": {
                "summary": context_result.get("summary", "").strip() if isinstance(context_result, dict) else str(context_result).strip(),
                "sections": [{"title": "Guiding Elements", "text": (context_result or "").strip()}]
            }
        }, default_source_type="ContextualCourseAgent")
        logger.info("✅ Contextual data integrated")
    except Exception:
        logger.exception("❌ Failed to generate contextual data")
        contextual_data = None
        context_result = ""

    # Step 5.5: Lesson Content Agent
    lesson_contents: List[Dict[str, Any]] = []
    if lesson_titles:
        logger.info("✏️ [LessonContentAgent] Generating lesson content for each title...")
        for idx, title in enumerate(lesson_titles, start=1):
            try:
                lesson_input = LessonContentAgentInput(
                    topicName=inputs.topicName,
                    gradeLevel=inputs.gradeLevel,
                    bigIdea=inputs.bigIdea,
                    lessonTitle=title,
                    lessonIndex=idx,
                    pedagogicalProfile=context_result or {}
                )
                result = await run_lesson_content_agent(lesson_input)
                if isinstance(result, dict):
                    lesson_contents.append(result)
                    logger.info(f"✅ Lesson {idx} generated: {title}")
            except Exception:
                logger.exception(f"❌ Failed to generate lesson {idx}: {title}")

    # Step 6: Final Summary
    logger.info("📝 Building final summary...")
    parts: List[str] = []
    if context_result: parts.append(context_result)
    if perplexity_data and "summary" in perplexity_data.get("processedContent", {}):
        parts.append(perplexity_data["processedContent"]["summary"])
    if "summary" in wiki_data.get("processedContent", {}):
        parts.append(wiki_data["processedContent"]["summary"])
    for d in uploaded_data:
        if "processedContent" in d and "summary" in d["processedContent"]:
            parts.append(d["processedContent"]["summary"])
    final_summary = "\n\n".join([p for p in parts if p and p.strip()]).strip()

    # Step 7: Assemble sources
    source_chunks: List[Dict[str, Any]] = [wiki_data]
    if perplexity_data: source_chunks.append(perplexity_data)
    source_chunks.extend(uploaded_data)
    if contextual_data: source_chunks.append(contextual_data)

    if lesson_titles:
        source_chunks.append(normalize_chunk({
            "sourceType": "Course_Scoping_Agent",
            "retrievedAt": current_timestamp(),
            "processedContent": {
                "summary": "Auto-generated lesson titles by Course Scoping Agent.",
                "sections": [{"title": "Lesson Titles", "text": "\n".join(lesson_titles)}]
            }
        }, default_source_type="Course_Scoping_Agent"))

    source_chunks = [ensure_sections(c) for c in source_chunks]
    source_chunks = add_chunk_ids(source_chunks)

    # Step 8: Pedagogical analysis
    pedagogical = build_pedagogical_analysis(source_chunks)

    # Step 9: Quality Gate
    texts_for_alignment = " ".join(
        [final_summary] + [c["processedContent"]["summary"] for c in source_chunks if c.get("processedContent")]
    )
    topic_alignment = compute_topic_alignment(inputs.topicName, texts_for_alignment)
    quality_warnings = []
    if topic_alignment < 0.4:
        quality_warnings.append("topic_mismatch_low_alignment")

    # Step 10: Save to DB
    content_payload: Dict[str, Any] = {
        "finalSummary": final_summary,
        "sourceChunks": source_chunks
    }
    if lesson_titles:
        content_payload["scopedLessons"] = lesson_titles
    if lesson_contents:
        content_payload["lessons"] = lesson_contents


    document: Dict[str, Any] = {
        "topicName": inputs.topicName,
        "subject": inputs.subject,
        "gradeLevel": inputs.gradeLevel,
        "createdAt": ensure_utc_iso_z(current_timestamp()),
        "version": 1.1,
        "cacheKey": generate_cache_key(
            inputs.topicName, inputs.subject, inputs.gradeLevel, inputs.bigIdea
        ),
        "content": content_payload,
        "pedagogicalAnalysis": pedagogical,
        "pipelineMeta": {
            "agentsUsed": [a for a, used in [
                ("Course_Scoping_Agent", bool(lesson_titles)),
                ("LessonContentAgent", bool(lesson_contents)),
                ("ContextualCourseAgent", bool(context_result)),
                ("Perplexity_Search", bool(perplexity_data)),
                ("Wikipedia", True)
            ] if used],
            "quality": {"topicAlignment": round(topic_alignment, 3), "warnings": quality_warnings}
        }
    }

    try:
        logger.info("💾 Upsert by cacheKey (idempotent)...")
        existing = await ContentCorpus.find_one(
            ContentCorpus.cacheKey == document.get("cacheKey", "")
        )
        doc = ContentCorpus(**document)

        if existing:
            doc.id = existing.id
            await doc.replace()
        else:
            try:
                await doc.insert()
            except DuplicateKeyError:
                existing = await ContentCorpus.find_one(
                    ContentCorpus.cacheKey == document["cacheKey"]
                )
                if existing:
                    doc.id = existing.id
                    await doc.replace()
                else:
                    raise

        logger.info(f"✅ Document upserted with _id: {doc.id}")
        return str(doc.id)

    except Exception:
        logger.exception("❌ Failed to upsert document to MongoDB")
        raise RuntimeError("Stage 1 failed during document save.")
