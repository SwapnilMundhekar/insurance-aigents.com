from pydantic import BaseModel
from typing import List

class PdfTestPageReport(BaseModel):
    page_number: int
    character_count: int
    word_count: int
    readability_status: str
    recommendation: str

class PdfTestChunkSample(BaseModel):
    chunk_id: str
    chunk_index: int
    token_estimate: int
    preview: str

class PdfIngestionTestResponse(BaseModel):
    document_id: str
    source_filename: str
    total_pages: int
    readable_pages: int
    weak_extraction_pages: int
    ocr_required_pages: int
    overall_quality: str
    recommendation: str
    total_extracted_characters: int
    total_token_estimate: int
    total_chunks_created: int
    chunks_file: str
    page_reports: List[PdfTestPageReport]
    chunk_samples: List[PdfTestChunkSample]
