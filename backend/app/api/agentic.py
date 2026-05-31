from fastapi import APIRouter, HTTPException
from app.schemas.agentic import AgenticRagRequest, AgenticRagResponse
from app.services.agentic_rag_service import run_agentic_rag

router = APIRouter(prefix="/agentic", tags=["agentic"])

@router.post("/rag-answer", response_model=AgenticRagResponse)
def agentic_rag_answer(request: AgenticRagRequest):
    try:
        result = run_agentic_rag(
            query=request.query,
            document_id=request.document_id,
            top_k=request.top_k,
            max_loops=request.max_loops,
            session_id=request.session_id
        )
        return AgenticRagResponse(**result)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))