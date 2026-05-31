from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class QdrantIndexRequest(BaseModel):
    document_id: Optional[str] = None

class QdrantIndexResponse(BaseModel):
    document_id: str
    collection_name: str
    source_chunks_file: str
    total_chunks_indexed: int
    embedding_model: str
    embedding_dimensions: int
    qdrant_url: str

class QdrantSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)

class QdrantSearchResult(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    score: float
    text: str
    source_filename: str
    metadata: Dict[str, Any]

class QdrantSearchResponse(BaseModel):
    query: str
    collection_name: str
    embedding_model: str
    total_results: int
    results: List[QdrantSearchResult]
