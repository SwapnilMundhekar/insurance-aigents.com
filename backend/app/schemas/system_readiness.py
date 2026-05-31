from pydantic import BaseModel
from typing import List

class SystemReadinessResponse(BaseModel):
    ready_for_agentic_rag: bool
    ollama_available: bool
    indexed_documents_available: bool
    chunks_files_found: int
    latest_chunks_file: str
    required_models: List[str]
    detected_models: List[str]
    missing_models: List[str]
    recommendations: List[str]
