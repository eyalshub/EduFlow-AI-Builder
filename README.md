# 📘 Amit AI Content Builder

Amit AI Builder is a production-grade multi-agent GenAI system that automatically generates curriculum-aligned lessons, questions, and LMS-ready instructional content.
Built end-to-end using FastAPI, MongoDB, multi-agent LLM orchestration, and YAML-driven prompt pipelines.

---
## 📑 Table of Contents
- [Executive Overview](#executive-overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Pipeline Overview](#pipeline-overview)
  - [Stage 1 – Corpus Acquisition](#stage-1--content-corpus-acquisition)
  - [Stage 2 – Text Editing & Question Generation](#stage-2--text-editing--question-generation)
  - [Final Pipeline](#final-pipeline)
- [Agents](#agents)
- [Normalizers & Validators](#normalizers--validators)
- [Database Schema](#database-schema)
- [UI Screens](#ui-screens)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Roadmap](#roadmap)

---
# 📌 Executive Overview

Amit AI Content Builder is a **production-grade multi-agent GenAI platform** for generating curriculum-aligned lessons, questions, and structured instructional materials.  
It enables teachers and pedagogical teams to rapidly produce high-quality educational content that is automatically normalized into LMS-ready formats.

Designed and implemented **end-to-end by a single engineer**, the system uses a modular orchestration architecture that coordinates multiple LLM-based agents across the full workflow: content acquisition, text refinement, question generation, grounding verification, difficulty scoring, and structured LMS output formatting.  
Each agent exposes a clear contract, allowing the pipeline to maintain pedagogical consistency, reduce LLM hallucination risks, and ensure deterministic and repeatable outputs.

A robust **MongoDB persistence layer**, strict schema validation, and resilient error-handling mechanisms ensure operational reliability at scale.  
The system is in full production use and provides the core technical foundation for future **adaptive-learning engines**, supporting metadata-driven personalization and dynamic content expansion.
---
# 🚀 Key Features
1. Multi-Agent GenAI Architecture

Modular orchestration of specialized LLM agents (generation, editing, validation), each with strict I/O contracts for deterministic, reliable execution.

2. Two-Stage Content Pipeline

Stage 1: Source acquisition, contextual expansion, pedagogical processing.

Stage 2: Text refinement & question generation with validation loops.
Stages isolated, API-driven, and idempotent.

3. Validation Stack for Question Quality

Tri-layer verification:

Bloom level

Difficulty alignment

Grounding & evidence
Ensures pedagogical and factual correctness.

4. Intelligent Reject-Loop

Adaptive regeneration cycle with memory (bad_stems) that avoids repeating weak or invalid questions.

5. LMS-Ready Structured Output

All paragraphs and questions normalize into a strict LMS schema with hierarchy metadata (courseOutlineId → lessonId → pageId) and pedagogical fields.

6. Pluggable LLM Providers

Unified interface for OpenAI, Perplexity, and local models (Ollama/GGUF).
Automatic retries, fallbacks, and consistent output formatting.

7. Production-Grade MongoDB Layer

Idempotent upserts, schema enforcement, structured collections (content_corpus, blocks, outlines, etc.), and metadata-driven traceability.

8. YAML-Driven Prompt Templates

Versioned prompts with declared input/output sections for reproducible agent behavior and easy iteration.

9. Developer-Friendly FastAPI + UI

Typed REST endpoints plus lightweight HTML tools for Stage 1, Stage 2, orchestrator testing, and lesson viewing.

10. Comprehensive Test Coverage

Unit tests, pipeline tests, normalization tests, and CRUD validation ensuring stability and regression safety.

---
## System Architecture

🗂️ Project Structure

```bash


project_amit_ai_builder/
├── app/
│ ├── api/v1/endpoints/
│ │ ├── chatbot.py # ✅ New – chatbot endpoint
│ │ ├── llm_orchestrator.py # ✅ New – orchestrator endpoint
│ │ ├── free_chat.py # ✅ New – free-form chat endpoint
│ │ └── content_corpus.py # Stage 1 API
│ │
│ ├── core/
│ │ ├── agents/
│ │ │ ├── text_editor_agent.py
│ │ │ ├── question_generator_agent.py
│ │ │ ├── bloom_level_verifier_agent.py
│ │ │ ├── difficulty_level_verifier_agent.py
│ │ │ ├── grounding_verifier_agent.py
│ │ │ ├── lesson_content_agent.py # ✅ New – Stage 1 lesson agent
│ │ │ └── main_llm_orchestrator_agent.py # ✅ New – master LLM orchestrator
│ │ │
│ │ ├── normalizers/
│ │ │ ├── lms_normalizer.py # ✅ New – LMS structure normalizer
│ │ │ └── question_normalizer.py # ✅ New – Question structure normalizer
│ │ │
│ │ ├── orchestrator/
│ │ │ └── chat_orchestrator.py # ✅ New – central chat orchestrator
│ │ │
│ │ ├── pipeline/
│ │ │ ├── stage_1_corpus_initial.py
│ │ │ └── wiki_expand_pipeline.py # ✅ New – wiki content expansion
│ │ │
│ │ ├── services/
│ │ │ ├── file_ingest.py # ✅ New – file ingestion service
│ │ │ ├── validation.py # ✅ New – LMS document validation
│ │ │ ├── openai_service.py
│ │ │ ├── perplexity_service.py
│ │ │ ├── request_utils.py
│ │ │ └── prompt_manager.py
│ │ │
│ │ └── config.py
│ │
│ ├── crud/
│ │ ├── crud_content_corpus.py # Stage 1 CRUD
│ │ └── ... # Other collections CRUD (blocks, logs, etc.)
│ │
│ ├── models/
│ ├── schemas/
│ │ ├── stage2.py
│ │ ├── chatbot.py # ✅ New – chatbot schemas
│ │ └── lms.py # ✅ New – LMS validation schemas
│ │
│ ├── services/
│ │ ├── openai_service.py
│ │ ├── perplexity_service.py
│ │ ├── request_utils.py
│ │ └── prompt_manager.py
│ │
│ ├── utils/
│ │ ├── file_helpers.py
│ │ ├── hash.py
│ │ └── time.py
│ │
│ └── worker/
│ └── main.py
│
├── prompts/
│ └── templates/
│ ├── text_editor_prompt.yaml
│ ├── question_generator_prompt.yaml
│ ├── cognitive_level_verifier_prompt.yaml
│ ├── difficulty_level_verifier_prompt.yaml
│ ├── grounding_verifier_prompt.yaml
│ ├── data_agents/
│ │ └── lesson_content_agent.yaml # ✅ New
│ └── wiki/
│ └── expand_article.yaml # ✅ New
│
├── static/
│ ├── generate_corpus.html # Stage 1 UI
│ ├── generate_stage2.html # Stage 2 UI
│ ├── orchestrator_test.html # ✅ New – test UI for orchestrator
│ └── view_lesson.html # ✅ New – lesson view UI
│
├── tests/
│ ├── api/
│ ├── crud/
│ ├── core/
│ │ ├── pipeline/
│ │ │ ├── test_stage2_pipeline.py
│ │ │ └── test_wiki_expand_pipeline.py # ✅ New
│ │ ├── normalizers/
│ │ │ └── test_question_normalizer.py # ✅ New
│ │ ├── services/
│ │ │ └── test_validation.py # ✅ New
│ │ └── test_stage1_pipeline.py
│ │
│ ├── test_agents/
│ │ └── test_lesson_content_agent.py # ✅ New
│ │
│ └── conftest.py
│
├── input.json # ✅ New – sample input
├── input_text_editr.json # ✅ New – text editor input example
├── result.json # ✅ New – sample output
├── requirements.txt
└── README.md


## Pipeline Overview

---
### Stage 1 – Content Corpus Acquisition

```text
┌──────────────────────────────────────────────────────────────┐
│                        API Request                            │
│ Inputs: topicName, subject, gradeLevel, bigIdea, files...     │
└──────────────────────────────────────────────────────────────┘
                                │
                                ▼
              ┌──────────────────────────────────────┐
              │  run_stage_1() Pipeline Controller   │
              └──────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────┐
        │ [STEP 1] Course Scoping Agent (conditional)            │
        │ run_course_scoping_agent → lesson_titles[]             │
        └────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    [STEP 2–4] Content Acquisition Layer                       │
│ Wiki → Perplexity (linear chain)    ||    Uploaded Files (parallel branch)    │
└──────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌──────────────────────────────┬──────────────────────────────────────┐
        │                              │                                      │
        ▼                              ▼                                      ▼
┌──────────────────────────┐   ┌──────────────────────────┐        ┌─────────────────────────────┐
│ [2] Wikipedia Fetcher     │   │ [3] Perplexity Fetcher    │        │ [4] Uploaded File Parser     │
│ fetch_wikipedia(topic)    │   │ fetch_perplexity(...)     │        │ process_uploaded_file(path)  │
└──────────────────────────┘   └──────────────────────────┘        └─────────────────────────────┘
        │                              │                                      │
        ▼                              ▼                                      ▼
┌──────────────────────────┐   ┌──────────────────────────┐        ┌─────────────────────────────┐
│ normalize_chunk(wiki)     │   │ normalize_chunk(perp)     │        │ normalize_chunk(uploaded)   │
└──────────────────────────┘   └──────────────────────────┘        └─────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│ [STEP 5] ContextualCourseAgent                                │
│ run_contextual_agent(inputs) → contextual_data                │
│ normalize_chunk()                                             │
└──────────────────────────────────────────────────────────────┘
                                │
                                ▼
      ┌──────────────────────────────────────────────────────────┐
      │ [STEP 5.5] LessonContentAgent (only if lesson_titles[])  │
      │ run_lesson_content_agent() → lesson_contents[]           │
      └──────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────┐
        │ [STEP 6] Final Summary Builder                         │
        │ Combine: wiki + perplexity + uploads + context         │
        └────────────────────────────────────────────────────────┘
                                │
                                ▼
     ┌────────────────────────────────────────────────────────────┐
     │ [STEP 7] Assemble Source Chunks                            │
     │ ensure_sections() + add_chunk_ids()                        │
     └────────────────────────────────────────────────────────────┘
                                │
                                ▼
     ┌────────────────────────────────────────────────────────────┐
     │ [STEP 8] Pedagogical Analysis                              │
     │ build_pedagogical_analysis(chunks)                         │
     └────────────────────────────────────────────────────────────┘
                                │
                                ▼
     ┌────────────────────────────────────────────────────────────┐
     │ [STEP 9] Quality Gate                                      │
     │ topic_alignment + warnings                                 │
     └────────────────────────────────────────────────────────────┘
                                │
                                ▼
     ┌────────────────────────────────────────────────────────────┐
     │ [STEP 10] Final Document Assembly                          │
     │ finalSummary + chunks + lessons + meta                     │
     └────────────────────────────────────────────────────────────┘
                                │
                                ▼
      ┌────────────────────────────────────────────────────────┐
      │ [STEP 11] MongoDB Upsert (ContentCorpus)               │
      │ Upsert by cacheKey                                     │
      └────────────────────────────────────────────────────────┘


---


### Stage 2 – Question + Text Pipeline

┌──────────────────────────────────────────────────────────────┐
│                    API Request → Stage 2                      │
│   Inputs: mode, chunks/freePrompt, num_questions, targets…    │
└──────────────────────────────────────────────────────────────┘
                                │
                                ▼
                ┌──────────────────────────────────────┐
                │        run_stage_2() Controller      │
                └──────────────────────────────────────┘
                         │                 │
            ┌────────────┘                 └──────────────┐
            ▼                                              ▼


====================================================================
                         MODE: EDIT TEXT
====================================================================

        ┌────────────────────────────────────────────────────────────┐
        │ [1] TextEditorAgent                                        │
        │  • Cleans & restructures text                              │
        │  • Removes redundancy & noise                              │
        │  • Returns {edited_text, justification[]}                  │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │ [2] Optional Save-to-Blocks                                │
        │  blockType = "Paragraph"                                   │
        │  metadata = {"purpose": "Refined Text"}                    │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │                 Stage2Result (edit_text)                   │
        └────────────────────────────────────────────────────────────┘


====================================================================
                     MODE: GENERATE QUESTIONS
====================================================================

                    Chunks (Stage 1) OR freePrompt
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │ [0] Chunk Preparation                                      │
        │  • Build chunks_iter                                       │
        │  • If no chunks → wrap freePrompt into pseudo-chunk        │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼

────────────────────────────── MAIN LOOP ───────────────────────────────
Loop until:
    ✔ collected >= target_n
    OR
    ✔ attempts >= MAX_ATTEMPTS
────────────────────────────────────────────────────────────────────────


        ┌────────────────────────────────────────────────────────────┐
        │ [1] QuestionGeneratorAgent                                 │
        │  • Generates the *remaining* missing questions             │
        │  • req.num_questions and req.chunks change dynamically     │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │ [2] Normalization Layer                                    │
        │  • normalize_mcq                                           │
        │  • shuffle choices                                         │
        │  • extract & validate stem                                 │
        │  • skip malformed questions                                │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │ [3] Duplicate Filtering                                    │
        │  • Skip if stem matches an already-accepted question       │
        │  • Skip if stem exists in bad_stems (previous rejections) │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼
────────────────────────── VALIDATION STACK ───────────────────────────

    ┌──────────────────────────────────────────────────────────────┐
    │ [4] BloomLevelVerifierAgent                                  │
    │   → matches target cognitive level?                          │
    └──────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────┐
    │ [5] DifficultyLevelVerifierAgent                              │
    │   → Is question difficulty aligned with source chunk?         │
    └──────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────┐
    │ [6] GroundingVerifierAgent                                   │
    │   → Is answer grounded in actual evidence from chunk?         │
    └──────────────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────────────────


                      ┌───────────────┬────────────────────────────┐
                      ▼               │                            ▼
        ┌──────────────────────┐      │          ┌────────────────────────┐
        │   VALID → ACCEPT     │      │          │  INVALID → REJECT       │
        │  Add to collected[]  │      │          │  Add stem → bad_stems   │
        └──────────────────────┘      │          └────────────────────────┘
                                      │
                                      ▼
                      (Loop continues with new requests)


──────────────────────────── END MAIN LOOP ─────────────────────────────


                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │ [7] Optional Save-to-DB                                    │
        │   blockType = "question"                                   │
        │   metadata includes:                                       │
        │     • topic / subject / grade                              │
        │     • bigIdea / learningGate                               │
        │     • bloom_level / difficulty                             │
        │     • originating chunk_ids                                │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │                 Stage2Result (questions)                   │
        │  • collected questions                                     │
        │  • per-agent validation data                               │
        │  • # attempts                                              │
        │  • DB block references                                     │
        └────────────────────────────────────────────────────────────┘
---

### Final Pipeline
┌───────────────────────────────────────────────────────────────────┐
│                     API Request → Full Pipeline                   │
│   Input: FullLessonInput                                          │
│   mode ∈ { "stage1", "stage2" }                                   │
│   Contains all metadata needed for both stages                    │
└───────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                ┌──────────────────────────────────────┐
                │  generate_full_lesson_pipeline()      │
                │              Controller               │
                └──────────────────────────────────────┘
                                │
            ┌───────────────────┴───────────────────┐
            ▼                                       ▼

═════════════════════════════════════════════════════════════════════
                           MODE: STAGE 1
═════════════════════════════════════════════════════════════════════

        ┌────────────────────────────────────────────────────────────┐
        │ [1] run_stage_1(data)                                      │
        │  • Wikipedia + Perplexity + Files + Context Agent          │
        │  • Course Scoping Agent                                    │
        │  • Lesson Content Agent                                    │
        │  • Merge + Summaries + Pedagogy + Quality Gate             │
        │  • Upsert to MongoDB (ContentCorpus)                       │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │   Return:                                                 │
        │     { success: True, mode: "stage1", document: <ID> }     │
        └────────────────────────────────────────────────────────────┘


═════════════════════════════════════════════════════════════════════
                           MODE: STAGE 2
═════════════════════════════════════════════════════════════════════

                    ┌────────────────────────────────┐
                    │  [0] Build Stage2Request        │
                    │   (mapping FullLessonInput →    │
                    │    Stage2Request model)         │
                    └────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │ [1] run_stage2(stage2_request)                             │
        │   ┌────────────────────────────────────────────────────┐   │
        │   │ MODE: "edit_text"                                  │   │
        │   │  → TextEditorAgent                                 │   │
        │   │  → Optional DB block save                          │   │
        │   └────────────────────────────────────────────────────┘   │
        │                                                            │
        │   ┌────────────────────────────────────────────────────┐   │
        │   │ MODE: "generate_questions"                         │   │
        │   │   → Chunk prep (Stage 1 chunks or freePrompt)      │   │
        │   │   → Main Loop:                                     │   │
        │   │         QuestionGeneratorAgent                     │   │
        │   │         Normalization + Duplicate Filtering        │   │
        │   │         Validation Stack (Bloom + Difficulty +     │   │
        │   │                                 Grounding)         │   │
        │   │         Reject-loop via bad_stems memory           │   │
        │   │   → Optional DB block save                         │   │
        │   └────────────────────────────────────────────────────┘   │
        └────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────────────────┐
        │   Return:                                                 │
        │     {                                                     │
        │       success: True,                                      │
        │       mode: "stage2",                                     │
        │       blocks: result.blocks,                              │
        │       errors: result.errors,                              │
        │       message: result.message                             │
        │     }                                                     │
        └────────────────────────────────────────────────────────────┘


═════════════════════════════════════════════════════════════════════
                           INVALID MODE
═════════════════════════════════════════════════════════════════════

        ┌────────────────────────────────────────────────────────────┐
        │ { success: False, error: "Invalid mode",                   │
        │   message: "Mode must be stage1 or stage2" }               │
        └────────────────────────────────────────────────────────────┘

---
## 🧠 Agents

Amit AI Content Builder is powered by a modular suite of specialized LLM agents.  
Each agent follows a **strict input/output contract**, uses a **dedicated YAML prompt**,  
and is orchestrated through a central controller to ensure deterministic and pedagogically aligned outputs.

---

### **1. TextEditorAgent**
- Refines and restructures raw text for student-facing materials.  
- **Responsibilities:** cleanup, simplification, tone alignment, LMS-ready formatting  
- **File:** `text_editor_agent.py`

---

### **2. QuestionGeneratorAgent**
- Generates high-quality assessment items (MCQ, open-ended, matching) directly from content chunks.  
- **Responsibilities:** question construction, distractor generation, alignment with learning objectives  
- **File:** `question_generator_agent.py`

---

### **3. BloomLevelVerifierAgent**
- Evaluates whether a generated question matches the required Bloom’s Taxonomy level.  
- **Responsibilities:** cognitive classification, match scoring  
- **File:** `bloom_level_verifier_agent.py`

---

### **4. DifficultyLevelVerifierAgent**
- Assesses the pedagogical difficulty of a question relative to the source text and grade level.  
- **Responsibilities:** difficulty scoring, alignment checks  
- **File:** `difficulty_level_verifier_agent.py`

---

### **5. GroundingVerifierAgent**
- Ensures that every question is factually grounded in evidence from the original chunk.  
- **Responsibilities:** grounding validation, evidence extraction, justification  
- **File:** `grounding_verifier_agent.py`

---

### **6. LessonContentAgent**
- Stage 1 agent that generates full lesson content:  
  introduction, structured paragraphs, summary, and discussion questions.  
- **Responsibilities:** pedagogical content creation, hierarchical structuring  
- **File:** `lesson_content_agent.py`

---

### **7. MainLLMOrchestratorAgent**
- High-level controller coordinating agent execution and workflow consistency.  
- **Responsibilities:** dynamic routing, agent selection, context propagation, quality assurance  
- **File:** `main_llm_orchestrator_agent.py`

---
---
## 🔧 Normalizers & Validators

Amit AI Content Builder includes a robust normalization and validation layer designed to enforce structure, correctness, and consistency across all generated content.
These components ensure that LLM outputs become deterministic, schema-safe, and LMS-ready.

1. Question Normalizer

Standardizes question objects across all agents and modes.
Responsibilities:

Normalize MCQ structure (stem, choices, correct_index)

Shuffle distractors while preserving answer correctness

Enforce consistent field naming

Detect duplicate questions via semantic stem matching

File: question_normalizer.py

2. LMS Structure Normalizer

Transforms raw agent outputs (chat messages, text blocks, question arrays) into strict LMS-compliant JSON objects.
Responsibilities:

Convert free-text into LMS block structures

Inject hierarchy metadata (courseOutlineId → lessonId → sectionId → pageId)

Apply content-type specific formatting (Paragraph / Question / Matching / Open)

Validate completeness and required fields

File: lms_normalizer.py

3. Document Validator

Validates full-lesson JSON documents before saving or returning to clients.
Responsibilities:

Schema enforcement for LMS lessons and pages

Block-level validation (question formats, metadata correctness)

Detection of missing or malformed sections

Severity-tagged error reporting

File: validation.py

4. Pedagogical Validators (Stage 2)

A specialized validation stack used during question generation to guarantee instructional quality.
Includes:

BloomLevelVerifierAgent → Cognitive level accuracy

DifficultyLevelVerifierAgent → Difficulty alignment

GroundingVerifierAgent → Evidence-based correctness

These validators work together to enforce pedagogical soundness before questions are accepted into the final output.
---
## 📚 Database Schema
Amit AI Content Builder uses a structured, production-grade MongoDB design, optimized for traceability, versioning, and multi-agent pipelines.

Core Collections
1. content_corpus

Stores the full output of Stage 1.
Fields include:

topicName, subject, gradeLevel

sourceChunks[] (wiki/perplexity/uploads)

contextualSummary, lessonSummaries

pedagogicalAnalysis

pipeline_run_id

2. blocks

Atomic LMS units created in Stage 2.
Examples:

Paragraph blocks

MCQ / Open / Matching questions

Edited text blocks

Each block contains:

blockType

content (typed structure)

metadata (difficulty, bloom, source chunk IDs, etc.)

courseOutlineId → lessonId → sectionId → pageId

3. outlines

Hierarchical course → lesson → page tree.
Generated independently & referenced by blocks.

4. general_logs / deployment_logs / chat_history

Operational logging collections to support debugging, pipeline audits, and user interaction tracking.
---
#🖥️ UI Screens
The project includes lightweight HTML tools under /static, enabling rapid development and debugging.

Screen	Path	Purpose
Stage 1 Generator	/static/generate_corpus.html	Kick off content corpus creation
Stage 2 Generator	/static/generate_stage2.html	Edit text / generate questions
Orchestrator Tester	/static/orchestrator_test.html	Debug multi-agent chat and pipeline flow
Lesson Viewer	/static/view_lesson.html	Render final LMS-style lesson with blocks

Designed for developers, QA, and instructional teams to interact with the system without needing Postman or code.
---
# ⚙️ Setup & Installation
1. Clone the repository

git clone https://github.com/eyalshub/amit-ai-builder.git
cd amit-ai-builder

2. Install dependencies
pip install -r requirements.txt

3. Environment variables
OPENAI_API_KEY=...
PERPLEXITY_API_KEY=...
MONGODB_URI=...

4. Run the server
uvicorn app.main:app --reload

5. Access UI screens

Stage 1 UI → http://localhost:8000/static/generate_corpus.html

Stage 2 UI → http://localhost:8000/static/generate_stage2.html

Orchestrator UI → http://localhost:8000/static/orchestrator_test.html
---
# 🔌 API Endpoints
Stage 1 – Content Corpus
POST /api/v1/content_corpus/generate
Generates the full pedagogical corpus (wiki, perplexity, lesson content, context, summaries).

Stage 2 – Text Editing
POST /api/v1/stage2/edit_text

Stage 2 – Question Generation
POST /api/v1/stage2/generate_questions

Chat-Orchestrator
POST /api/v1/orchestrator/chat

Free Chat
POST /api/v1/chat/free

Full OpenAPI docs:
http://localhost:8000/docs

---
#🧪 Testing
The project includes comprehensive tests:
Test Types

* Pipeline tests: Stage 1 & Stage 2 end-to-end

* Agent tests: LessonContentAgent, normalization, validators

* CRUD tests: ContentCorpus, Blocks, Outlines, Logs

* Schema validation tests

Run all tests
pytest -q

Run a specific suite
pytest tests/core/pipeline/test_stage2_pipeline.py


#🗺️ Roadmap
Planned enhancements to expand the system into a next-generation adaptive learning engine:

## Near-Term

* Add per-question rationale generation

* Add semantic search over content corpus

* Expand difficulty model using embeddings

* Integration with pgvector for chunk indexing

## Mid-Term

* Adaptive learning loop based on student performance

* Lesson auto-revision using drift detection

* Multi-language output with automatic translation agents

## Long-Term

* Full AI Curriculum Engine

* Automated personalization per student

* ML model to predict best question type per topic
## 🔍 Current Functionality

### Stage 1 – Initial Content Corpus Creation
- Receives user input: `topic`, `subject`, `grade level`, etc.
- Uses LLM agents (Perplexity, OpenAI, etc.) to fetch and process raw content.
- Saves the processed content in the `content_corpus` collection in MongoDB.
- Offers a simple **HTML UI** for triggering the generation.
- Orchestrates the entire logic via a single pipeline controller.

**File:**  
app/core/pipeline/stage_1_corpus_initial.py
---

**Responsibilities:**
- Coordinates calls to LLM agents
- Manages processing logic
- Stores the final result in MongoDB (`content_corpus`)



This module:
- Coordinates calls to LLM agents
- Manages processing logic
- Stores the final result in MongoDB (`content_corpus`)


**UI:**  
[http://localhost:8000/static/generate_corpus.html](http://localhost:8000/static/generate_corpus.html)






---

## ✏️ Stage 2 – Text Editing & Question Generation

This stage enhances the raw educational content from Stage 1 by generating LMS-ready blocks.  

### Supported Modes
- `edit_text` → Edits and refines paragraphs.  
- `generate_questions` → Generates questions (MCQ, open, matching) based on a chunk.

### Agents Involved
1. **TextEditorAgent**  
   - Refines text for students.  
   - Prompt: `prompts/templates/text_editor_prompt.yaml`

2. **QuestionGeneratorAgent**  
   - Generates questions based on input chunk.  
   - Prompt: `prompts/templates/question_generator_prompt.yaml`

3. **BloomLevelVerifierAgent**  
   - Verifies match with Bloom taxonomy.  
   - Prompt: `prompts/templates/cognitive_level_verifier_prompt.yaml`

4. **DifficultyLevelVerifierAgent**  
   - Scores question difficulty.  
   - Prompt: `prompts/templates/difficulty_level_verifier_prompt.yaml`

5. **GroundingVerifierAgent**  
   - Validates that question is grounded in source text.  
   - Prompt: `prompts/templates/grounding_verifier_prompt.yaml`

### Output & Storage
- Saved to the `blocks` MongoDB collection.  
- Includes metadata like:
  - `blockType`, `question`, `bloomLevel`, `difficulty`, `pipeline_run_id`
  - Hierarchical course fields (`courseId`, `lessonId`, `pageId`)

**UI:**  
[http://localhost:8000/static/generate_stage2.html](http://localhost:8000/static/generate_stage2.html)

#### 💾 Output & Storage

- Saved to the `blocks` MongoDB collection.
- Includes metadata like:
  - `blockType`, `question`, `bloomLevel`, `difficulty`, `pipeline_run_id`, and hierarchical course fields.

---
---

## 🧠 New Components Added

### Agents
- `lesson_content_agent.py` → Writes lesson-level content (introduction, paragraphs, summary, questions).  
- `main_llm_orchestrator_agent.py` → The "brain" agent that manages other agents dynamically.

### Normalizers
- `lms_normalizer.py` → Normalizes raw chat/file inputs into LMS JSON format.  
- `question_normalizer.py` → Ensures question objects are standardized across pipelines.

### Orchestrator
- `chat_orchestrator.py` → Routes incoming chat/file/user requests to the correct agents.

### Services
- `file_ingest.py` → Reads and parses uploaded files into text for the pipeline.  
- `validation.py` → Validates generated documents against LMS schema.

### Pipelines
- `wiki_expand_pipeline.py` → Expands Wikipedia-style content into structured lessons.

### Schemas
- `chatbot.py` → Schemas for chatbot interactions.  
- `lms.py` → Schemas & validation models for LMS-compatible JSON.

### UI (Static)
- `orchestrator_test.html` → Debug/test UI for orchestrator flow.  
- `view_lesson.html` → UI to preview a full lesson (pages + blocks).

### Tests
- `test_lesson_content_agent.py` → Unit tests for lesson agent.  
- `test_question_normalizer.py` → Tests normalization logic.  
- `test_wiki_expand_pipeline.py` → Tests wiki expansion pipeline.  
- `test_validation.py` → Tests schema validation logic.

---
## 🎥 Demo
![Demo Screenshot](static/demo_screenshot.png)





-----

