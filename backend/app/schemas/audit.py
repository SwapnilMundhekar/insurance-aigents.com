from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class AuditRunSummary(BaseModel):
    trace_id: str
    created_at_utc: str
    query: str
    status: str
    domain: str
    intent: str
    llm_model: str
    embedding_model: str
    total_sources_used: int
    total_tool_calls: int
    risk_level: str
    human_review_required: bool

class AuditRunListResponse(BaseModel):
    total_runs: int
    runs: List[AuditRunSummary]

class AuditRunDetailResponse(BaseModel):
    trace_id: str
    created_at_utc: str
    workflow: Dict[str, Any]
    governance: Dict[str, Any]
    steps: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    reflection: Dict[str, Any]
