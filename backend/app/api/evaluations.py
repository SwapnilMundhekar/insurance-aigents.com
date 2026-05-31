from fastapi import APIRouter, HTTPException
from app.schemas.evaluations import EvaluationCase, EvaluationReportDetailResponse, EvaluationReportListResponse, EvaluationRunRequest, EvaluationRunResponse
from app.services.evaluation_service import all_cases, get_report, list_reports, run_evaluations

router = APIRouter(prefix="/evaluations", tags=["evaluations"])

@router.get("/cases", response_model=list[EvaluationCase])
def get_cases(include_agentic_cases: bool = False):
    return [EvaluationCase(**case) for case in all_cases(include_agentic_cases=include_agentic_cases)]

@router.post("/run", response_model=EvaluationRunResponse)
def run_evaluation_suite(request: EvaluationRunRequest):
    result = run_evaluations(
        include_agentic_cases=request.include_agentic_cases,
        document_id=request.document_id,
        top_k=request.top_k,
        max_loops=request.max_loops
    )
    return EvaluationRunResponse(**result)

@router.get("/reports", response_model=EvaluationReportListResponse)
def get_reports():
    reports = list_reports()
    return EvaluationReportListResponse(total_reports=len(reports), reports=reports)

@router.get("/reports/{report_id}", response_model=EvaluationReportDetailResponse)
def get_report_detail(report_id: str):
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Evaluation report not found.")
    return EvaluationReportDetailResponse(report_id=report_id, report=report)
