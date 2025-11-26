import datetime
import json
import logging
from typing import Optional, Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from app.services.prompt_manager import load_prompt, render_user_prompt
from app.services.fetchers.wikipedia_fetcher import fetch_wikipedia_summary
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Load prompt once at module level
PROMPT_PATH = "wiki/expand_article.yaml"
prompt_data = load_prompt(PROMPT_PATH)
system_tpl = prompt_data["system"]
user_tpl = prompt_data["user"]

# Setup LLM
llm = ChatOpenAI(model="gpt-4.1", temperature=0.3)
parser = StrOutputParser()


async def run_wiki_expand_pipeline(
    topic: str,
    subject: str,
    grade_level: str,
    lang: str = "he",
    learning_objective: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full pipeline: fetch Wikipedia summary → expand with LLM → return structured lesson module.
    """

    # Step 1 – Fetch summary
    wiki_summary = fetch_wikipedia_summary(topic, lang=lang)
    if not wiki_summary:
        raise ValueError(f"❌ Wikipedia summary not found for topic: '{topic}'")

    # Step 2 – Render prompt
    context = {
        "wiki_summary": wiki_summary,
        "subject": subject,
        "gradeLevel": grade_level,
        "lang": lang,
        "learningObjective": learning_objective or "",
    }

    messages = [
        SystemMessage(content=system_tpl),
        HumanMessage(content=render_user_prompt(user_tpl, context)),
    ]

    try:
        # Step 3 – Call LLM
        response = await llm.ainvoke(messages)
        response_str = response.content.strip()

        # Step 4 – Parse JSON response
        parsed = json.loads(response_str)

        if not isinstance(parsed, dict) or not parsed.get("coreExplanation"):
            raise ValueError("Missing expected keys in LLM response.")

        # Step 5 – Return result
        return {
            "status": "ok",
            "topic": topic,
            "subject": subject,
            "gradeLevel": grade_level,
            "language": lang,
            "sourceType": "Wikipedia",
            "sourceSummary": wiki_summary,
            "expandedContent": parsed,  # <- parsed JSON: explanation, vocab, questions, big idea
            "llmMetadata": {
                "model": "gpt-4.1",
                "promptPath": PROMPT_PATH,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            },
            "rawTextOutput": response_str,
        }

    except Exception as e:
        logger.exception("❌ Failed to run wiki expansion pipeline.")
        return {
            "status": "error",
            "reason": "llm_failure_or_invalid_json",
            "topic": topic,
            "exception": str(e),
            "rawTextOutput": response_str if "response_str" in locals() else None
        }
