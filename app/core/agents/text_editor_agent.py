# app/core/agents/text_editor_agent.py
# -*- coding: utf-8 -*-
import logging
from typing import Literal, Optional, TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from app.schemas.input_model import Stage1Input
from app.services.prompt_manager import load_prompt, render_user_prompt

load_dotenv()
logger = logging.getLogger(__name__)

# ---- Load prompt from YAML ----
prompt_data = load_prompt("data_agents/text_editor_prompt.yaml")
system_tpl = prompt_data["system"]
user_tpl = prompt_data["user"]


# ---- Pydantic schema ----
class TextEditResult(BaseModel):
    status: Literal["ok"]
    edited_text: str = Field(..., description="The revised LMS-ready text")
    justification: str = Field(..., description="Why edits were made (or 'No changes needed')")


# ---- LLM config ----
llm = ChatOpenAI(model="gpt-4.1", temperature=0.7)
parser = PydanticOutputParser(pydantic_object=TextEditResult)
format_instructions = parser.get_format_instructions()

# ---- Input format ----
class TextEditorInput(TypedDict):
    stage1: Stage1Input
    raw_text: str
    audience: str
    instructionStyle: str
    outputFormat: str
    allowFormatting: bool


# ---- Agent function ----
async def run_text_editor_agent(input: TextEditorInput) -> dict:
    """
    Edits a given Hebrew/English text according to LMS course parameters.
    Returns a structured JSON with edited_text + justification.
    """
    try:
        context = {
            "topicName": input["stage1"].topicName,
            "subject": input["stage1"].subject,
            "gradeLevel": input["stage1"].gradeLevel,
            "bigIdea": input["stage1"].bigIdea,
            "learningGate": input["stage1"].learningGate,
            "skills": input["stage1"].skills,
            "courseLanguage": input["stage1"].courseLanguage,
            "courseLanguageLabel": normalize_language_label(input["stage1"].courseLanguage),
            "raw_text": input["raw_text"],
            "audience": input["audience"],
            "instructionStyle": input["instructionStyle"],
            "outputFormat": input["outputFormat"],
            "allowFormatting": str(input["allowFormatting"]).lower()
        }

        rendered_user = render_user_prompt(user_tpl, context)
        messages = [
            SystemMessage(content=system_tpl),
            HumanMessage(content=f"{rendered_user}\n\n{format_instructions}")
        ]

        response = await llm.ainvoke(messages)
        print("🧠 Raw LLM response:", response.content) 
        parsed = parser.parse(response.content)
        return parsed.dict()

    except Exception as e:
        logger.exception("Text editing failed.")
        return {
            "status": "error",
            "reason": "parser_or_llm_error",
            "exception": str(e)
        }



# ---- Helper ----
def normalize_language_label(lang: Optional[str]) -> str:
    if not lang:
        return "Hebrew"
    lang = lang.lower()
    if lang.startswith("he") or "עברית" in lang:
        return "Hebrew"
    elif lang.startswith("en") or "english" in lang or "אנגלית" in lang:
        return "English"
    return lang.capitalize()


__all__ = ["run_text_editor_agent", "TextEditorInput"]
