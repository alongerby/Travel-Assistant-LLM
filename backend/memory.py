from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any
import time

@dataclass
class SessionState:
    memory_note: str = ""
    geo_location: str = ""
    updated_at: float = field(default_factory=time.time)

_SESSIONS: Dict[str, SessionState] = {}

def get_session(session_id: str) -> SessionState:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = SessionState()
    return _SESSIONS[session_id]

def reset_session(session_id: str):
    if session_id in _SESSIONS:
        _SESSIONS[session_id] = SessionState()