from pydantic import BaseModel
from typing import List, Dict, Any

class DocumentChunk(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    text: str
    token_estimate: int
    source_filename: str
    metadata: Dict[str, Any]

class DocumentIngestResponse(BaseModel):
    document_id: str
    source_filename: str
    total_characters: int
    total_token_estimate: int
    total_chunks: int
    chunks: List[DocumentChunk]