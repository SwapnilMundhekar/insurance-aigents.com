from fastapi import APIRouter, HTTPException, Query
from app.schemas.observability import AgentStepStatsResponse, ObservabilitySummaryResponse, RiskSummaryResponse, ToolUsageResponse, TraceDetailResponse, TraceListResponse
from app.services.observability_service import build_agent_stats, build_observability_summary, build_risk_summary, build_tool_usage, get_trace_detail, list_trace_summaries

router = APIRouter(prefix="/observability", tags=["observability"])

@router.get("/summary", response_model=ObservabilitySummaryResponse)
def get_summary(limit: int = Query(default=10, ge=1, le=50)):
    return ObservabilitySummaryResponse(**build_observability_summary(limit=limit))

@router.get("/traces", response_model=TraceListResponse)
def get_traces(limit: int = Query(default=20, ge=1, le=100)):
    traces = list_trace_summaries(limit=limit)
    return TraceListResponse(total_traces=len(traces), traces=traces)

@router.get("/traces/{trace_id}", response_model=TraceDetailResponse)
def get_trace(trace_id: str):
    result = get_trace_detail(trace_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return TraceDetailResponse(**result)

@router.get("/tools", response_model=ToolUsageResponse)
def get_tools():
    return ToolUsageResponse(**build_tool_usage())

@router.get("/risks", response_model=RiskSummaryResponse)
def get_risks():
    return RiskSummaryResponse(**build_risk_summary())

@router.get("/agents", response_model=AgentStepStatsResponse)
def get_agents():
    return AgentStepStatsResponse(**build_agent_stats())
