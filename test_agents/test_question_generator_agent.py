# test_agents/test_question_generator_variation.py

import pytest
import json
import hashlib
from app.core.agents.question_generator_agent import run_question_generator_agent, QuestionGenInput
from app.schemas.input_model import Stage1Input


def hash_text(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


@pytest.mark.asyncio
async def test_question_generator_variation_mcq():
    base_input: QuestionGenInput = {
        "question_type": "mcq",
        "bloom_level": "understand",
        "difficulty": 0.5,
        "chunks": [{
            "chunk_id": "chunk_repeat",
            "text": (
                "The Reign of Terror was a radical phase of the French Revolution, "
                "where thousands were executed. It was led by Robespierre and the Jacobins. "
                "This period is debated for its ethics and consequences."
            )
        }],
        "stage1": Stage1Input(
            topicName="The French Revolution",
            subject="History",
            gradeLevel="9",
            bigIdea="Power and Resistance",
            learningGate="Discovery Gate",
            skills=["analyzing causes", "evaluating consequences"],
            context=None,
            freePrompt=None,
            courseLanguage="he"
        )
    }

    results = set()
    hashes = set()

    print("\n🧪 MCQ Stems Generated:")
    for i in range(3):
        input_data = base_input.copy()
        input_data["chunks"][0]["text"] += f" [variant {i+1}]"
        input_data["stage1"].freePrompt = f"אנא נסח שאלת ברירה חדשה בנושא זה. נסיון {i+1}"

        result = await run_question_generator_agent(input_data)
        assert result["status"] == "ok", f"❌ Status was not ok: {result}"

        stem = result["content"]["stem"].strip()
        result_hash = hash_text(stem)
        hashes.add(result_hash)
        results.add(stem)

        print(f"\n🔹 MCQ {i+1} (Hash: {result_hash}):")
        print("Q:", stem)
        for j, choice in enumerate(result["content"]["choices"]):
            prefix = "✅" if j == result["content"]["correct_index"] else "-"
            print(f"{prefix} Choice {j+1}:", choice)
        print("Explanation:", result["content"]["explanation"])

    assert len(results) == 3, "❌ Expected 3 different MCQ stems, but some are identical."


@pytest.mark.asyncio
async def test_question_generator_variation_open():
    base_input: QuestionGenInput = {
        "question_type": "open",
        "bloom_level": "analyze",
        "difficulty": 0.7,
        "chunks": [{
            "chunk_id": "chunk_repeat",
            "text": (
                "The Reign of Terror was a radical phase of the French Revolution, "
                "where thousands were executed. It was led by Robespierre and the Jacobins. "
                "This period is debated for its ethics and consequences."
            )
        }],
        "stage1": Stage1Input(
            topicName="The French Revolution",
            subject="History",
            gradeLevel="9",
            bigIdea="Power and Resistance",
            learningGate="Discovery Gate",
            skills=["critical thinking"],
            context=None,
            freePrompt=None,
            courseLanguage="he"
        )
    }

    results = set()
    hashes = set()

    print("\n🧪 Open Prompts Generated:")
    for i in range(3):
        input_data = base_input.copy()
        input_data["chunks"][0]["text"] += f" [variant {i+1}]"
        input_data["stage1"].freePrompt = f"הפק שאלה פתוחה חדשה לנסיון {i+1} בהקשר מוסרי או פוליטי."

        result = await run_question_generator_agent(input_data)
        assert result["status"] == "ok", f"❌ Status was not ok: {result}"

        prompt = result["content"]["prompt"].strip()
        result_hash = hash_text(prompt)
        hashes.add(result_hash)
        results.add(prompt)

        print(f"\n🔹 Open {i+1} (Hash: {result_hash}):")
        print("Prompt:", prompt)
        print("Ideal Answer:", result["content"]["ideal_answer"])
        print("Guidance:", result["content"]["guidance"])

    assert len(results) == 3, "❌ Expected 3 different open prompts, but some are identical."


@pytest.mark.asyncio
async def test_question_generator_variation_matching():
    base_input: QuestionGenInput = {
        "question_type": "matching",
        "bloom_level": "remember",
        "difficulty": 0.3,
        "chunks": [{
            "chunk_id": "chunk_repeat",
            "text": (
                "The Reign of Terror was a radical phase of the French Revolution, "
                "where thousands were executed. It was led by Robespierre and the Jacobins. "
                "This period is debated for its ethics and consequences."
            )
        }],
        "stage1": Stage1Input(
            topicName="The French Revolution",
            subject="History",
            gradeLevel="9",
            bigIdea="People and Movements",
            learningGate="Discovery Gate",
            skills=["recall", "categorization"],
            context=None,
            freePrompt=None,
            courseLanguage="he"
        )
    }

    results = set()
    hashes = set()

    print("\n🧪 Matching Pairs Generated:")
    for i in range(3):
        input_data = base_input.copy()
        input_data["chunks"][0]["text"] += f" [variant {i+1}]"
        input_data["stage1"].freePrompt = f"נא ליצור שאלת התאמה שונה בכל ריצה. גרסה {i+1}"

        result = await run_question_generator_agent(input_data)
        assert result["status"] == "ok", f"❌ Status was not ok: {result}"

        result_json = json.dumps(result["content"]["pairs"], ensure_ascii=False)
        result_hash = hash_text(result_json)
        hashes.add(result_hash)
        results.add(result_json)

        print(f"\n🔹 Matching {i+1} (Hash: {result_hash}):")
        print("Instructions:", result["content"]["instructions"])
        for left, right in result["content"]["pairs"]:
            print(f"- {left} ⇨ {right}")
        print("Distractors:", result["content"]["distractors"])

    assert len(results) == 3, "❌ Expected 3 different matching sets, but some are identical."
