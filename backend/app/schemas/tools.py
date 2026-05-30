from pydantic import BaseModel, Field
from typing import Any, Dict, List

class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

class ToolListResponse(BaseModel):
    tools: List[ToolDefinition]

class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(..., min_length=1)
    tool_input: Dict[str, Any]

class ToolExecuteResponse(BaseModel):
    tool_name: str
    ok: bool
    result: Dict[str, Any]
    error: str | None = None