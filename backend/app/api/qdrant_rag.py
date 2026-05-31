from fastapi import APIRouter, HTTPException
from app.schemas.qdrant_rag import QdrantIndexRequest, QdrantIndexResponse, QdrantSearchRequest, QdrantSearchResponse
from app.services.qdrant_vector_service import qdrant_index_document, qdrant_search

router = APIRouter(prefix="/rag/qdrant", tags=["qdrant-rag"])

@router.post("/index", response_model=QdrantIndexResponse)
def index_document_in_qdrant(request: QdrantIndexRequest):
    try:
        result = qdrant_index_document(request.document_id)
        return QdrantIndexResponse(**result)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Qdrant indexing failed: {str(error)}")

@router.post("/search", response_model=QdrantSearchResponse)
def search_qdrant(request: QdrantSearchRequest):
    try:
        result = qdrant_search(request.query, request.document_id, request.top_k)
        return QdrantSearchResponse(**result)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Qdrant search failed: {str(error)}")
