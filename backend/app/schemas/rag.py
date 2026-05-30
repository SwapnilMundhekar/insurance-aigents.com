from pydantic import BaseModel, Field
from typing import List, Optional

class RagIndexRequest(BaseModel):
    document_id: Optional[str] = None

class RagIndexResponse(BaseModel):
    document_id: str
    source_chunks_file: str
    vector_index_file: str
    total_chunks_indexed: int
    embedding_model: str
    embedding_dimensions: int

class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)

class RagSearchResult(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    score: float
    text: str
    source_filename: str

class RagSearchResponse(BaseModel):
    query: str
    embedding_model: str
    total_results: int
    results: List[RagSearchResult]

class RagAnswerRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=10)

class RagAnswerSource(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    score: float
    source_filename: str
    text: str

class RagAnswerResponse(BaseModel):
    query: str
    answer: str
    llm_model: str
    embedding_model: str
    total_sources_used: int
    sources: List[RagAnswerSource]
    prompt_character_count: int