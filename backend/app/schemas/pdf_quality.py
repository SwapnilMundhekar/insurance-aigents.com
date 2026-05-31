from pydantic import BaseModel
from typing import List

class PdfPageQuality(BaseModel):
    page_number: int
    character_count: int
    word_count: int
    readable_character_ratio: float
    garbled_character_ratio: float
    whitespace_ratio: float
    readability_status: str
    recommendation: str

class PdfQualityResponse(BaseModel):
    source_filename: str
    total_pages: int
    readable_pages: int
    weak_extraction_pages: int
    ocr_required_pages: int
    overall_quality: str
    recommendation: str
    pages: List[PdfPageQuality]