from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas.pdf_ocr import PdfOcrIngestResponse
from app.services.pdf_ocr_service import ingest_pdf_with_ocr

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/pdf-ingest-with-ocr", response_model=PdfOcrIngestResponse)
def pdf_ingest_with_ocr(upload_file: UploadFile = File(...)):
    try:
        if not upload_file.filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported for OCR ingestion.")
        result = ingest_pdf_with_ocr(upload_file)
        return PdfOcrIngestResponse(**result)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
