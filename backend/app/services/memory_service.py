import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import redis

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MEMORY_DIR = PROJECT_ROOT / "data" / "memory"
SESSION_DIR = MEMORY_DIR / "sessions"
CACHE_DIR = MEMORY_DIR / "cache"

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def ensure_memory_dirs():
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_redis_client():
    return redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=1)

def is_redis_available():
    try:
        client = get_redis_client()
        client.ping()
        return True
    except Exception:
        return False

def active_backend():
    if is_redis_available():
        return "redis"
    return "file_fallback"

def safe_key(value):
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return digest

def session_file_path(session_id):
    ensure_memory_dirs()
    return SESSION_DIR / f"{safe_key(session_id)}.json"

def cache_file_path(cache_key):
    ensure_memory_dirs()
    return CACHE_DIR / f"{safe_key(cache_key)}.json"

def read_json_file(path, default_value):
    if not path.exists():
        return default_value
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default_value

def write_json_file(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")

def preview_answer(answer, limit=300):
    cleaned = " ".join(str(answer).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."

def build_turn_from_response(response_payload):
    governance = response_payload.get("governance", {})
    reflection = response_payload.get("reflection", {})
    return {
        "trace_id": response_payload.get("trace_id", ""),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "query": response_payload.get("query", ""),
        "answer_preview": preview_answer(response_payload.get("answer", "")),
        "status": response_payload.get("status", ""),
        "intent": governance.get("intent", ""),
        "risk_level": reflection.get("risk_level", "")
    }

def save_agentic_session_memory(session_id: Optional[str], response_payload: Dict[str, Any]):
    if not session_id:
        return {"saved": False, "reason": "No session_id provided."}

    turn = build_turn_from_response(response_payload)

    if is_redis_available():
        client = get_redis_client()
        redis_key = f"session:{session_id}:turns"
        client.rpush(redis_key, json.dumps(turn))
        client.ltrim(redis_key, -20, -1)
        client.expire(redis_key, 86400)
        return {"saved": True, "backend": "redis", "session_id": session_id}

    path = session_file_path(session_id)
    turns = read_json_file(path, [])
    turns.append(turn)
    turns = turns[-20:]
    write_json_file(path, turns)
    return {"saved": True, "backend": "file_fallback", "session_id": session_id}

def get_session_turns(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    if is_redis_available():
        client = get_redis_client()
        redis_key = f"session:{session_id}:turns"
        raw_items = client.lrange(redis_key, -limit, -1)
        return [json.loads(item) for item in raw_items]

    path = session_file_path(session_id)
    turns = read_json_file(path, [])
    return turns[-limit:]

def delete_session(session_id: str) -> bool:
    deleted = False
    if is_redis_available():
        client = get_redis_client()
        redis_key = f"session:{session_id}:turns"
        deleted = client.delete(redis_key) > 0

    path = session_file_path(session_id)
    if path.exists():
        path.unlink()
        deleted = True
    return deleted

def build_memory_snapshot(session_id: Optional[str]):
    if not session_id:
        return {
            "enabled": False,
            "backend": active_backend(),
            "session_id": None,
            "recent_turns": [],
            "summary": "No session_id provided, so session memory was not loaded."
        }

    turns = get_session_turns(session_id, limit=5)
    return {
        "enabled": True,
        "backend": active_backend(),
        "session_id": session_id,
        "recent_turns": turns,
        "summary": f"Loaded {len(turns)} recent turn(s) for this session."
    }

def set_cache_value(cache_key: str, value: Dict[str, Any], ttl_seconds: int = 3600):
    if is_redis_available():
        client = get_redis_client()
        redis_key = f"cache:{cache_key}"
        client.set(redis_key, json.dumps(value), ex=ttl_seconds)
        return {"backend": "redis", "cache_key": cache_key, "saved": True}

    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "ttl_seconds": ttl_seconds,
        "value": value
    }
    write_json_file(cache_file_path(cache_key), payload)
    return {"backend": "file_fallback", "cache_key": cache_key, "saved": True}

def get_cache_value(cache_key: str):
    if is_redis_available():
        client = get_redis_client()
        redis_key = f"cache:{cache_key}"
        value = client.get(redis_key)
        if value is None:
            return None
        return json.loads(value)

    payload = read_json_file(cache_file_path(cache_key), None)
    if not payload:
        return None
    return payload.get("value")

def delete_cache_value(cache_key: str):
    deleted = False
    if is_redis_available():
        client = get_redis_client()
        deleted = client.delete(f"cache:{cache_key}") > 0

    path = cache_file_path(cache_key)
    if path.exists():
        path.unlink()
        deleted = True
    return deleted

def memory_status():
    return {
        "backend": active_backend(),
        "redis_available": is_redis_available(),
        "redis_url": REDIS_URL,
        "fallback_path": "data/memory"
    }
