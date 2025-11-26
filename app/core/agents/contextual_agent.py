#app/core/agents/contextual_agent.py
# LangChain core imports: prompt templates and output parser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# OpenAI chat model integration
from langchain_openai import ChatOpenAI
# Input schema for Stage 1 agent
from app.schemas.input_model import Stage1Input
from app.services.prompt_manager import load_prompt
import json
import logging
# Load environment variables (e.g., OPENAI_API_KEY)

from dotenv import load_dotenv
logger = logging.getLogger(__name__)

load_dotenv()

# 1️⃣ Prompt Template
# This defines the role of the agent and the format it expects to receive input in.
# It includes a SYSTEM message with instructions and a USER message template that is dynamically filled.
prompt_data = load_prompt("data_agents/contextual_course_agent.yaml")

prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_data["system"]),
    ("user", prompt_data["user"])
])


# 2️⃣ Language Model Setup
# This uses GPT-4.1 with a slightly lower temperature for more deterministic, structured results.
llm = ChatOpenAI(model="gpt-4.1", temperature=0.6)



# 3️⃣ Chain Assembly
# The prompt is passed to the model, and the model's output is parsed into a plain string.
contextual_chain = (
    prompt
    | llm
    | StrOutputParser()
)


# 4️⃣ Agent Runner Function
# This function can be used from outside the module to run the agent with a Stage1Input instance.
# It only runs the chain if either `context` or `freePrompt` is provided.
async def run_contextual_agent(inputs: Stage1Input) -> dict:
    if not getattr(inputs, "context", None) and not getattr(inputs, "freePrompt", None):
        return {}  # No context to process
    prompt_inputs = {
        "subject": inputs.subject,
        "gradeLevel": inputs.gradeLevel,
        "bigIdea": inputs.bigIdea,
        "learningGate": inputs.learningGate,
        "skills": ", ".join(inputs.skills) if inputs.skills else "None",
        "context": inputs.context or "None",
        "freePrompt": inputs.freePrompt or "None"
    }

    raw_result = await contextual_chain.ainvoke(prompt_inputs)
    try:
        return json.loads(raw_result)
    except Exception as e:
        logger.warning(f"Contextual agent returned non-JSON: {raw_result} | Error: {e}")
        return {}




# 5️⃣ Exported Symbols
# This allows `run_contextual_agent` to be easily imported from this module
__all__ = ["run_contextual_agent"]
