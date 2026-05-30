from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas.documents import DocumentIngestResponse
from app.services.document_service import ingest_document

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/ingest", response_model=DocumentIngestResponse)
def ingest(upload_file: UploadFile = File(...)):
    try:
        return ingest_document(upload_file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))