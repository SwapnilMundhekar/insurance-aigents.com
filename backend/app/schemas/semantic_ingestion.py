from pydantic import BaseModel
from typing import List

class SemanticPageReport(BaseModel):
    page_number: int
    character_count: int
    detected_headings: List[str]

class SemanticChunkSample(BaseModel):
    chunk_id: str
    chunk_index: int
    section_title: str
    page_start: int
    page_end: int
    token_estimate: int
    preview: str

class SemanticIngestResponse(BaseModel):
    document_id: str
    source_filename: str
    total_pages: int
    total_sections_detected: int
    total_chunks_created: int
    total_token_estimate: int
    chunks_file: str
    page_reports: List[SemanticPageReport]
    chunk_samples: List[SemanticChunkSample]
