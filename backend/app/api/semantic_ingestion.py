from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas.semantic_ingestion import SemanticIngestResponse
from app.services.semantic_chunking_service import semantic_ingest_document

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/semantic-ingest", response_model=SemanticIngestResponse)
def semantic_ingest(upload_file: UploadFile = File(...)):
    try:
        result = semantic_ingest_document(upload_file)
        return SemanticIngestResponse(**result)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
