from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class MemoryStatusResponse(BaseModel):
    backend: str
    redis_available: bool
    redis_url: str
    fallback_path: str

class MemoryTurn(BaseModel):
    trace_id: str
    created_at_utc: str
    query: str
    answer_preview: str
    status: str
    intent: str
    risk_level: str

class SessionMemoryResponse(BaseModel):
    session_id: str
    total_turns: int
    turns: List[MemoryTurn]

class CacheSetRequest(BaseModel):
    cache_key: str = Field(..., min_length=1, max_length=300)
    value: Dict[str, Any]
    ttl_seconds: Optional[int] = Field(default=3600, ge=60, le=86400)

class CacheGetResponse(BaseModel):
    cache_key: str
    found: bool
    value: Optional[Dict[str, Any]] = None

class DeleteResponse(BaseModel):
    key: str
    deleted: bool
