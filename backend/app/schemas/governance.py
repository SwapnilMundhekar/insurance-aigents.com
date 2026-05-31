from pydantic import BaseModel, Field
from typing import Any, Dict, List

class GovernanceAnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=8000)

class GovernanceAnalyzeResponse(BaseModel):
    allowed: bool
    route_to: str
    domain: str
    intent: str
    risk_flags: List[str]
    blocked_reasons: List[str]
    decomposed_tasks: List[str]
    allowed_tool_names: List[str]
    requires_human_review: bool
    original_character_count: int
    redacted_query: str
    governance_summary: str
    metadata: Dict[str, Any]