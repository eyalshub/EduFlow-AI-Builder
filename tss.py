# test_prompt_loader.py
from app.services.prompt_manager import load_prompt

if __name__ == "__main__":
    prompt = load_prompt("data_agents/course_scoping_agent.yaml")
    print("✅ Prompt loaded successfully!")
    print("System Prompt:", prompt["system"][:80], "...")
    print("User Prompt:", prompt["user"][:80], "...")
