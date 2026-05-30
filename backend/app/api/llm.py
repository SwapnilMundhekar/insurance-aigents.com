from fastapi import APIRouter, HTTPException
from app.schemas.llm import LLMRequest, LLMResponse
from app.services.llm_service import generate_with_ollama

router = APIRouter(prefix="/llm", tags=["llm"])

@router.post("/test", response_model=LLMResponse)
def test_llm(request: LLMRequest):
    result = generate_with_ollama(request.prompt)

    if not result["ok"]:
        raise HTTPException(status_code=503, detail=result.get("error", "LLM service unavailable"))

    return LLMResponse(
        model=result["model"],
        prompt=result["prompt"],
        response=result["response"],
        input_characters=result["input_characters"],
        output_characters=result["output_characters"]
    )