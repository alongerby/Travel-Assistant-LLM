import os, json
import httpx
from dotenv import load_dotenv
from memory import SessionState
import json
import re
from typing import Any

load_dotenv()

OPENROUTER_BASE = os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    **({"Authorization": f"Bearer {OPENROUTER_API_KEY}"} if OPENROUTER_API_KEY else {}),
    # Optional, but nice to include:
    "X-Title": os.getenv("APP_TITLE", "Travel Assistant (Dev)"),
}

async def chat(messages: list[dict], temperature: float = 0.6, max_tokens: int = 800) -> str:
    url = f"{OPENROUTER_BASE}/chat/completions"
    payload = {"model": OPENROUTER_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    async with httpx.AsyncClient(timeout=50) as client:
        r = await client.post(url, headers=HEADERS, json=payload)
        r.raise_for_status()
        return _extract_text(r.json()) or "(no content)"
    

def _extract_text(data: dict) -> str:
    choice = data.get("choices", [{}])[0]
    msg = choice.get("message", {}) or {}
    return (msg.get("content") or msg.get("reasoning") or choice.get("content") or "").strip()
    

async def rewrite_memory(session: SessionState, user_message: str) -> str:
    from prompts import MEMORY_UPDATER_SYSTEM
    url = f"{OPENROUTER_BASE}/chat/completions"
    payload = {
        "model": OPENROUTER_MODEL,
        "temperature": 0.1,                 
        "max_tokens": 400,
        "messages": [
            {"role": "system", "content": MEMORY_UPDATER_SYSTEM},
            {"role": "user", "content": f"Previous memory:\n{session.memory_note.strip() or '(empty)'}"},
            {"role": "user", "content": f"Latest user message:\n{user_message.strip()}"},
        ],
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=HEADERS, json=payload)
        if r.status_code >= 400:
            return session  # non-fatal: keep old memory
        raw = r.json()['choices']
        print(raw[0]['message']['content'])
        data = ensure_json(raw[0]['message']['content'])
        # try:
        #     data = json.loads(raw)
        # except Exception:
        #     data = {"memory_note": session.memory_note, "geo_location": ""}
        # Update session
        session.memory_note = data.get("memory_note", session.memory_note)
        if data.get("geo_location"):  # only overwrite if non-empty
            session.geo_location = data["geo_location"]
        return session
    

JSON_OBJECT_RE = re.compile(r"\{[\s\S]*\}")

def ensure_json(obj: Any) -> dict[str, Any]:
    """
    Ensure we return a Python dict from either:
    - already parsed dict
    - raw JSON string
    - string containing extra text with JSON embedded
    """
    if isinstance(obj, dict):
        return obj

    if isinstance(obj, str):
        # Try direct JSON load
        try:
            return json.loads(obj)
        except json.JSONDecodeError:
            pass

        # Try extracting first {...} block
        m = JSON_OBJECT_RE.search(obj)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass

    # Fallback: return empty structure
    return {"memory_note": "", "geo_location": ""}