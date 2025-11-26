#app/core/agents/grounding_verifier_agent.py
# -*- coding: utf-8 -*-
import json
import logging
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from app.services.prompt_manager import load_prompt, render_user_prompt

load_dotenv()
logger = logging.getLogger(__name__)

# ---- Load YAML prompt ----
prompt_data = load_prompt("data_agents/cognitive_level_verifier_prompt.yaml")
system_tpl = prompt_data["system"]
user_tpl = prompt_data["user"]

# ---- LLM Config ----
llm = ChatOpenAI(model="gpt-4.1", temperature=0.3)
parser = StrOutputParser()

# ---- Input type ----
class BloomLevelVerifierInput(TypedDict):
    question: str
    bloom_level: str  # Hebrew input, e.g. "הבנה ויישום"

# ---- Agent Function ----
async def run_bloom_level_verifier_agent(input: BloomLevelVerifierInput) -> dict:
    """
    Checks whether the question matches the intended Bloom level (in Hebrew).
    Returns a JSON with detected_level, match_score, matches_target, and justification.
    """
    try:
        context = {
            "question": input["question"],
            "bloom_level": input["bloom_level"]
        }

        rendered_user = render_user_prompt(user_tpl, context)

        messages = [
            SystemMessage(content=system_tpl),
            HumanMessage(content=rendered_user)
        ]

        response = await llm.ainvoke(messages)
        response_str = response.content

    except Exception as e:
        logger.exception("LLM call failed in Bloom Level Verifier.")
        return {"status": "error", "reason": "llm_call_failed", "exception": str(e)}

    try:
        parsed = json.loads(response_str)
        if parsed.get("status") != "ok":
            raise ValueError("LLM returned non-ok status.")
        return parsed

    except Exception as e:
        logger.warning("Invalid JSON or malformed response: %s", response_str)
        return {
            "status": "error",
            "reason": "invalid_json_response",
            "raw_output": response_str,
            "exception": str(e)
        }

__all__ = ["run_bloom_level_verifier_agent", "BloomLevelVerifierInput"]
