from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas.pdf_test import PdfIngestionTestResponse
from app.services.pdf_test_service import run_pdf_ingestion_test

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/pdf-ingestion-test", response_model=PdfIngestionTestResponse)
def pdf_ingestion_test(upload_file: UploadFile = File(...)):
    try:
        if not upload_file.filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported for this ingestion test.")
        result = run_pdf_ingestion_test(upload_file)
        return PdfIngestionTestResponse(**result)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
