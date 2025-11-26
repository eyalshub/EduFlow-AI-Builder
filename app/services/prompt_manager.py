# app/services/prompt_manager.py
from pathlib import Path
import yaml
from jinja2 import Template

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_DIR = BASE_DIR / "prompts" / "templates"

def load_prompt(file_path: str) -> dict:
    full_path = PROMPT_DIR / file_path
    print(f"📂 Loading prompt from: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        prompt = yaml.safe_load(f)

    if "system" not in prompt or "user" not in prompt:
        raise ValueError("❌ Prompt file must contain both 'system' and 'user' keys.")

    return prompt

def render_user_prompt(template_str: str, context: dict) -> str:
    """Render a Jinja user prompt template with the given context."""
    template = Template(template_str)
    return template.render(**context)