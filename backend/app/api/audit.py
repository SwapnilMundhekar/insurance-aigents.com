from fastapi import APIRouter, HTTPException, Query
from app.schemas.audit import AuditRunDetailResponse, AuditRunListResponse
from app.services.audit_service import get_audit_run, list_audit_runs

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/runs", response_model=AuditRunListResponse)
def get_runs(limit: int = Query(default=20, ge=1, le=100)):
    runs = list_audit_runs(limit=limit)
    return AuditRunListResponse(total_runs=len(runs), runs=runs)

@router.get("/runs/{trace_id}", response_model=AuditRunDetailResponse)
def get_run(trace_id: str):
    result = get_audit_run(trace_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Audit run not found.")
    return AuditRunDetailResponse(**result)
