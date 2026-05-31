from pydantic import BaseModel, Field
from typing import Any, Dict, List

class OutputGuardrailValidateRequest(BaseModel):
    answer: str = Field(..., min_length=1)
    sources: List[Dict[str, Any]] = []
    tool_calls: List[Dict[str, Any]] = []
    governance: Dict[str, Any] = {}
    reflection: Dict[str, Any] = {}

class OutputGuardrailValidateResponse(BaseModel):
    allowed_to_return: bool
    final_status: str
    risk_flags: List[str]
    blocked_reasons: List[str]
    required_actions: List[str]
    safe_answer: str
    summary: str
    metadata: Dict[str, Any]
