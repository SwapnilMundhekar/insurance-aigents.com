from fastapi import APIRouter, HTTPException, Query
from app.schemas.memory import CacheGetResponse, CacheSetRequest, DeleteResponse, MemoryStatusResponse, SessionMemoryResponse
from app.services.memory_service import delete_cache_value, delete_session, get_cache_value, get_session_turns, memory_status, set_cache_value

router = APIRouter(prefix="/memory", tags=["memory"])

@router.get("/status", response_model=MemoryStatusResponse)
def get_memory_status():
    return MemoryStatusResponse(**memory_status())

@router.get("/session/{session_id}", response_model=SessionMemoryResponse)
def get_session_memory(session_id: str, limit: int = Query(default=10, ge=1, le=20)):
    turns = get_session_turns(session_id, limit=limit)
    return SessionMemoryResponse(session_id=session_id, total_turns=len(turns), turns=turns)

@router.delete("/session/{session_id}", response_model=DeleteResponse)
def clear_session_memory(session_id: str):
    deleted = delete_session(session_id)
    return DeleteResponse(key=session_id, deleted=deleted)

@router.post("/cache", response_model=CacheGetResponse)
def set_cache(request: CacheSetRequest):
    set_cache_value(request.cache_key, request.value, request.ttl_seconds or 3600)
    return CacheGetResponse(cache_key=request.cache_key, found=True, value=request.value)

@router.get("/cache/{cache_key}", response_model=CacheGetResponse)
def get_cache(cache_key: str):
    value = get_cache_value(cache_key)
    return CacheGetResponse(cache_key=cache_key, found=value is not None, value=value)

@router.delete("/cache/{cache_key}", response_model=DeleteResponse)
def clear_cache(cache_key: str):
    deleted = delete_cache_value(cache_key)
    return DeleteResponse(key=cache_key, deleted=deleted)
