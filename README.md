# 📘 Amit AI Content Builder

An AI-powered system for generating high-quality educational content based on pedagogical standards.  
Built with **FastAPI**, **MongoDB**, and modular **GPT-based agents** for each stage of the pipeline.


# 📌 Executive Overview

Amit AI Content Builder is a **production-grade multi-agent GenAI platform** for generating curriculum-aligned lessons, questions, and structured instructional materials.  
It enables teachers and pedagogical teams to rapidly produce high-quality educational content that is automatically normalized into LMS-ready formats.

Designed and implemented **end-to-end by a single engineer**, the system uses a modular orchestration architecture that coordinates multiple LLM-based agents across the full workflow: content acquisition, text refinement, question generation, grounding verification, difficulty scoring, and structured LMS output formatting.  
Each agent exposes a clear contract, allowing the pipeline to maintain pedagogical consistency, reduce LLM hallucination risks, and ensure deterministic and repeatable outputs.

A robust **MongoDB persistence layer**, strict schema validation, and resilient error-handling mechanisms ensure operational reliability at scale.  
The system is in full production use and provides the core technical foundation for future **adaptive-learning engines**, supporting metadata-driven personalization and dynamic content expansion.


---

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





-----




# 🧩 Stage 1 — Exact Pipeline Flow (Code-Accurate)

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
