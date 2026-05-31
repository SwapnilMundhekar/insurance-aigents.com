from pydantic import BaseModel
from typing import List

class PdfOcrPageReport(BaseModel):
    page_number: int
    extraction_method: str
    readability_status: str
    normal_text_characters: int
    ocr_text_characters: int
    final_text_characters: int
    word_count: int
    recommendation: str

class PdfOcrChunkSample(BaseModel):
    chunk_id: str
    chunk_index: int
    token_estimate: int
    preview: str

class PdfOcrIngestResponse(BaseModel):
    document_id: str
    source_filename: str
    total_pages: int
    pages_using_pdf_text: int
    pages_using_ocr: int
    pages_with_no_text: int
    total_extracted_characters: int
    total_token_estimate: int
    total_chunks_created: int
    chunks_file: str
    ocr_engine_available: bool
    page_reports: List[PdfOcrPageReport]
    chunk_samples: List[PdfOcrChunkSample]
