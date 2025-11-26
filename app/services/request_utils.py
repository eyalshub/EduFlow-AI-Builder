# app/services/request_utils.py
def format_messages_as_prompt(messages: list[dict], style: str = "default") -> str:
    if style == "claude":
        prompt = "\n".join([
            f"Human: {m['content']}" if m['role'] == 'user' else f"Assistant: {m['content']}"
            for m in messages
        ]) + "\nAssistant:"
        return prompt
    else:
        # default style (OpenAI, others)
        return messages
