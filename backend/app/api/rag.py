from fastapi import APIRouter, HTTPException
from app.schemas.rag import RagAnswerRequest, RagAnswerResponse, RagIndexRequest, RagIndexResponse, RagSearchRequest, RagSearchResponse
from app.services.rag_answer_service import answer_with_rag
from app.services.vector_search_service import build_vector_index, search_vector_index

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/index", response_model=RagIndexResponse)
def index_document(request: RagIndexRequest):
    try:
        result = build_vector_index(request.document_id)
        return RagIndexResponse(**result)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.post("/search", response_model=RagSearchResponse)
def search_documents(request: RagSearchRequest):
    try:
        result = search_vector_index(request.query, request.document_id, request.top_k)
        return RagSearchResponse(**result)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.post("/answer", response_model=RagAnswerResponse)
def answer_question(request: RagAnswerRequest):
    try:
        result = answer_with_rag(request.query, request.document_id, request.top_k)
        return RagAnswerResponse(**result)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))