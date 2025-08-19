import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import re
from typing import Any, Dict
from datetime import datetime
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from prompts import SYSTEM_PROMPT, REASONING_NUDGE, MEMORY_UPDATER_SYSTEM
from memory import get_session, reset_session
from llm import chat as llm_chat, rewrite_memory

from external import country_info

load_dotenv()
app = FastAPI(title=os.getenv("APP_TITLE", "Travel Assistant (Dev)"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=False,
    allow_methods=["*"],          
    allow_headers=["*"],          
)

# ---------- Schemas
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str = "default"
    input: str

class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
def health(): return {"ok": True}

@app.post("/reset")
async def reset(payload: dict):
    sid = payload.get("session_id")
    if not sid:
        raise HTTPException(400, "Missing session_id")
    reset_session(sid)
    return {"status": "reset", "session_id": sid}


# ---------- Chat
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    ss = get_session(req.session_id)
    print(req.session_id)
    try:
        ss = await rewrite_memory(ss, req.input)
    except Exception as e:
        # non-fatal; keep previous memory
        print("[MEMORY] rewrite failed:", e)
    up_to_date_info = None
    if ss.geo_location:
        try:
            up_to_date_info = await country_info(ss.geo_location)
        except:
            pass
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": REASONING_NUDGE},
        {"role": "system", "content": f"destination location information (for your use only if any relevant information) {up_to_date_info}"},
        {"role": "system", "content": f"Session memory (for your use only):\n{ss.memory_note + ' trip location: ' + ss.geo_location  or '(empty)'}"},
        {"role": "user", "content": req.input},
    ]

    try:
        reply = await llm_chat(messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    return ChatResponse(reply=reply)


@app.get("/memory")
def get_memory(session_id: str = Query("default")):
    return {"memory_note": get_session(session_id)}
