# app/api/v1/free_chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

router = APIRouter()

class FreeChatRequest(BaseModel):
    text: str

# אפשר להגדיר פעם אחת ולהשתמש מחדש
llm = ChatOpenAI(model="gpt-4.1", temperature=0.7)

@router.post("/free-chat")
async def free_chat(req: FreeChatRequest):
    try:
        msgs = [
            SystemMessage(content="You are a helpful assistant. Answer in Hebrew when the user writes Hebrew."),
            HumanMessage(content=req.text),
        ]
        res = await llm.ainvoke(msgs)
        return {"reply": res.content}
    except Exception as e:
        print(f"[free-chat] error: {e}")
        raise HTTPException(status_code=500, detail="LLM call failed")
