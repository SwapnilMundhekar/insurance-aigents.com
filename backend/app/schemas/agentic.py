from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class AgenticRagRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)
    max_loops: int = Field(default=2, ge=1, le=3)

class AgenticRagSource(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    score: float
    source_filename: str
    text: str

class AgenticToolCall(BaseModel):
    tool_name: str
    ok: bool
    input: Dict[str, Any]
    result: Dict[str, Any]
    error: Optional[str] = None

class AgenticTraceStep(BaseModel):
    step_index: int
    agent_name: str
    action: str
    input_summary: str
    output_summary: str
    metadata: Dict[str, Any]

class AgenticRagResponse(BaseModel):
    query: str
    rewritten_query: str
    answer: str
    status: str
    llm_model: str
    embedding_model: str
    total_sources_used: int
    sources: List[AgenticRagSource]
    tool_calls: List[AgenticToolCall]
    governance: Dict[str, Any]
    trace_id: str
    trace_file: str
    loop_count: int
    reflection: Dict[str, Any]
    steps: List[AgenticTraceStep]