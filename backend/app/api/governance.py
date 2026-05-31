from fastapi import APIRouter
from app.schemas.governance import GovernanceAnalyzeRequest, GovernanceAnalyzeResponse
from app.services.governance_service import analyze_prompt

router = APIRouter(prefix="/governance", tags=["governance"])

@router.post("/analyze", response_model=GovernanceAnalyzeResponse)
def analyze(request: GovernanceAnalyzeRequest):
    result = analyze_prompt(request.query)
    return GovernanceAnalyzeResponse(**result)