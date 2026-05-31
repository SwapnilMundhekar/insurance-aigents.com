from pydantic import BaseModel
from typing import Any, Dict, List

class TraceSummary(BaseModel):
    trace_id: str
    created_at_utc: str
    query_preview: str
    status: str
    domain: str
    intent: str
    total_steps: int
    total_tool_calls: int
    total_sources_used: int
    risk_level: str
    human_review_required: bool
    trace_file: str

class ObservabilitySummaryResponse(BaseModel):
    total_traces: int
    status_counts: Dict[str, int]
    risk_level_counts: Dict[str, int]
    total_tool_calls: int
    total_sources_used: int
    average_sources_per_trace: float
    human_review_required_count: int
    unique_agents_seen: List[str]
    unique_tools_seen: List[str]
    latest_traces: List[TraceSummary]

class TraceListResponse(BaseModel):
    total_traces: int
    traces: List[TraceSummary]

class TraceDetailResponse(BaseModel):
    trace_id: str
    trace_file: str
    trace: Dict[str, Any]

class ToolUsageItem(BaseModel):
    tool_name: str
    total_calls: int
    successful_calls: int
    failed_calls: int

class ToolUsageResponse(BaseModel):
    total_tool_calls: int
    tools: List[ToolUsageItem]

class RiskSummaryResponse(BaseModel):
    governance_risk_flags: Dict[str, int]
    output_guardrail_risk_flags: Dict[str, int]
    reflection_risk_levels: Dict[str, int]
    human_review_required_count: int

class AgentStepStatsItem(BaseModel):
    agent_name: str
    total_steps: int
    actions: Dict[str, int]

class AgentStepStatsResponse(BaseModel):
    total_steps: int
    agents: List[AgentStepStatsItem]
