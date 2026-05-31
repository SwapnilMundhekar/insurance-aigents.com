from fastapi import APIRouter, File, HTTPException, UploadFile
from app.schemas.pdf_quality import PdfQualityResponse
from app.services.pdf_quality_service import analyze_pdf_quality

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/pdf-quality", response_model=PdfQualityResponse)
def pdf_quality(upload_file: UploadFile = File(...)):
    try:
        if not upload_file.filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported for PDF quality analysis.")
        result = analyze_pdf_quality(upload_file)
        return PdfQualityResponse(**result)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))