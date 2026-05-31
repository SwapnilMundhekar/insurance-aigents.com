from fastapi import APIRouter
from app.schemas.output_guardrails import OutputGuardrailValidateRequest, OutputGuardrailValidateResponse
from app.services.output_guardrail_service import validate_agentic_output

router = APIRouter(prefix="/guardrails/output", tags=["guardrails"])

@router.post("/validate", response_model=OutputGuardrailValidateResponse)
def validate_output(request: OutputGuardrailValidateRequest):
    result = validate_agentic_output(
        answer=request.answer,
        sources=request.sources,
        tool_calls=request.tool_calls,
        governance=request.governance,
        reflection=request.reflection
    )
    return OutputGuardrailValidateResponse(**result)
