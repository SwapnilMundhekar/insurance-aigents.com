from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.llm import router as llm_router
from app.api.documents import router as documents_router
from app.api.rag import router as rag_router
from app.api.tools import router as tools_router
from app.api.agentic import router as agentic_router
from app.api.governance import router as governance_router
from app.api.pdf_quality import router as pdf_quality_router
from app.api.pdf_test import router as pdf_test_router
from app.api.pdf_ocr import router as pdf_ocr_router
from app.api.semantic_ingestion import router as semantic_ingestion_router
from app.api.qdrant_rag import router as qdrant_rag_router
from app.api.audit import router as audit_router
from app.api.memory import router as memory_router
from app.api.output_guardrails import router as output_guardrails_router
from app.api.evaluations import router as evaluations_router
from app.api.observability import router as observability_router

app = FastAPI(
    title="InsuranceAIGents API",
    description="Local-first Agentic RAG insurance operations platform with governance, tool calling, reflection, and trace logging.",
    version="0.1.0"
)

app.include_router(health_router)
app.include_router(llm_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(tools_router)
app.include_router(agentic_router)
app.include_router(governance_router)
app.include_router(pdf_quality_router)
app.include_router(pdf_test_router)
app.include_router(pdf_ocr_router)
app.include_router(semantic_ingestion_router)
app.include_router(qdrant_rag_router)
app.include_router(audit_router)
app.include_router(memory_router)
app.include_router(output_guardrails_router)
app.include_router(evaluations_router)
app.include_router(observability_router)

@app.get("/")
def root():
    return {
        "name": "InsuranceAIGents",
        "status": "running",
        "architecture": "Governed Agentic RAG with tool calling, reflection, and trace logging",
        "version": "0.1.0"
    }