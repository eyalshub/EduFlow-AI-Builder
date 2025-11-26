# app/core/agents/course_scoping_agent.py
# -*- coding: utf-8 -*-

import logging
import re
from typing import List, Optional, Union  

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from app.schemas.input_model import Stage1Input
from app.services.prompt_manager import load_prompt

load_dotenv()
logger = logging.getLogger(__name__)

# ---- Load prompt from YAML ----
prompt_data = load_prompt("data_agents/course_scoping_agent.yaml")
system_tpl = prompt_data["system"]
user_tpl   = prompt_data["user"]

prompt = ChatPromptTemplate.from_messages([
    ("system", system_tpl),
    ("user",   user_tpl),
])

# ---- LLM config ----
llm = ChatOpenAI(model="gpt-4.1", temperature=0.5)

# ---- Post-processing helpers ----
_BULLET_PREFIX = r"^\s*(?:[-*•·]+|\d+[\.)]|[a-zA-Z]\)|\([a-zA-Z0-9]\))\s*"
_WS_ONLY = re.compile(r"^\s*$")

def _clamp_num_lessons(n: Optional[int], default: int = 3, min_n: int = 1, max_n: int = 12) -> int:
    if not isinstance(n, int):
        return default
    return max(min_n, min(max_n, n))

def _truncate_words(line: str, max_words: int = 10) -> str:
    words = line.split()
    if len(words) <= max_words:
        return line
    return " ".join(words[:max_words]).rstrip(" -–—·•")

def _clean_lines(raw: str, max_len: int = 120, max_words: int = 10) -> List[str]:
    if not raw:
        return []
    raw = raw.strip()
    lines = raw.splitlines()

    cleaned: List[str] = []
    seen = set()
    for line in lines:
        if _WS_ONLY.match(line):
            continue
        line = re.sub(_BULLET_PREFIX, "", line).strip()
        if not line:
            continue
        line = line.strip(' "\'`-–—·•\t')
        if len(line) > max_len:
            line = line[:max_len].rstrip(" -–—·•")
        line = _truncate_words(line, max_words=max_words)
        key = line.lower()
        if key and key not in seen:
            seen.add(key)
            cleaned.append(line)

    # fallback: comma/semicolon separated
    if len(cleaned) <= 1 and ("," in raw or ";" in raw):
        alt = re.split(r"[;,]", raw)
        tmp, seen2 = [], set()
        for a in alt:
            a = re.sub(_BULLET_PREFIX, "", a).strip(' "\'`-–—·•\t')
            if not a:
                continue
            if len(a) > max_len:
                a = a[:max_len].rstrip(" -–—·•")
            a = _truncate_words(a, max_words=max_words)
            k2 = a.lower()
            if k2 and k2 not in seen2:
                seen2.add(k2)
                tmp.append(a)
        if len(tmp) > len(cleaned):
            cleaned = tmp

    return cleaned

def _fallback_titles(topic: str, grade: Union[str, int], k: int = 3) -> List[str]:
    topic = (topic or "הנושא").strip()
    heb = re.search(r"[\u0590-\u05FF]", topic) is not None
    if heb:
        base = [
            f"היכרות עם {topic}",
            f"אבני דרך ב{topic}",
            f"{topic}: רעיונות והשפעות",
            f"{topic} בהקשר עולמי",
            f"מורשת ומשמעויות של {topic}",
        ]
    else:
        base = [
            f"Introduction to {topic}",
            f"Key Turning Points in {topic}",
            f"{topic}: Ideas and Impact",
            f"{topic} in Global Context",
            f"Legacy and Lessons of {topic}",
        ]
    return base[: max(1, k)]

# ---- Chain: prompt → llm → string ----
chain = prompt | llm | JsonOutputParser()

async def run_course_scoping_agent(inputs: Stage1Input) -> List[str]:
    """
    Returns a clean, deduped list of lesson titles with length control and fallback.
    Uses YAML at prompts/templates/data_agents/course_scoping_agent.yaml (via load_prompt).
    """
    num: int = _clamp_num_lessons(getattr(inputs, "numLessons", None))
    big: str = getattr(inputs, "bigIdea", "") or ""
    topic: str = (getattr(inputs, "topicName", "") or "").strip()
    grade: Union[str, int] = getattr(inputs, "gradeLevel", "") or ""
    pedagogy: str = getattr(inputs, "pedagogicalProfileJson", "") or ""

    try:
        result = await chain.ainvoke({
            "topicName": topic,
            "gradeLevel": grade,
            "bigIdea": big,
            "numLessons": num,
            "pedagogical_json_from_contextual_agent": pedagogy,
        })

        raw_lessons = result.get("lessons", [])

        if all(isinstance(x, dict) and "title" in x for x in raw_lessons):
                raw_titles = [x["title"] for x in raw_lessons]
        elif all(isinstance(x, str) for x in raw_lessons):
                raw_titles = raw_lessons
        else:
                raise ValueError("Unexpected format in 'lessons' — expected list of str or list of dict with 'title'")

    except Exception:
        logger.exception("Course scoping LLM call failed; using fallback titles.")
        return _fallback_titles(topic, grade, k=num)

    titles = _clean_lines("\n".join(raw_titles), max_len=120, max_words=10)
    if not titles:
        return _fallback_titles(topic, grade, k=num)

    if len(titles) > num:
        titles = titles[:num]

    titles = [t for t in titles if re.search(r"[A-Za-z\u0590-\u05FF0-9]", t)]
    return titles or _fallback_titles(topic, grade, k=num)

__all__ = ["run_course_scoping_agent"]
