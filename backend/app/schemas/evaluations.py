from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class EvaluationRunRequest(BaseModel):
    include_agentic_cases: bool = False
    document_id: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)
    max_loops: int = Field(default=2, ge=1, le=3)

class EvaluationCase(BaseModel):
    case_id: str
    case_type: str
    name: str
    description: str
    input: Dict[str, Any]
    expected: Dict[str, Any]

class EvaluationCaseResult(BaseModel):
    case_id: str
    case_type: str
    name: str
    passed: bool
    score: float
    checks: List[Dict[str, Any]]
    error: Optional[str] = None

class EvaluationRunResponse(BaseModel):
    report_id: str
    created_at_utc: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    report_file: str
    results: List[EvaluationCaseResult]

class EvaluationReportListItem(BaseModel):
    report_id: str
    created_at_utc: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    report_file: str

class EvaluationReportListResponse(BaseModel):
    total_reports: int
    reports: List[EvaluationReportListItem]

class EvaluationReportDetailResponse(BaseModel):
    report_id: str
    report: Dict[str, Any]
