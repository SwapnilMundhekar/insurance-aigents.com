import json
import math
import os
from pathlib import Path
from app.services.embedding_service import embed_text, OLLAMA_EMBED_MODEL

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = PROJECT_ROOT / "data" / "indexes"

def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)

def find_latest_chunks_file():
    files = sorted(INDEX_DIR.glob("*_chunks.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError("No chunk files found. Run /documents/ingest first.")
    return files[0]

def find_chunks_file(document_id):
    if document_id:
        path = INDEX_DIR / f"{document_id}_chunks.json"
        if not path.exists():
            raise FileNotFoundError(f"No chunks found for document_id {document_id}.")
        return path
    return find_latest_chunks_file()

def extract_document_id_from_chunks_file(chunks_file):
    name = chunks_file.name
    return name.replace("_chunks.json", "")

def build_vector_index(document_id=None):
    chunks_file = find_chunks_file(document_id)
    actual_document_id = extract_document_id_from_chunks_file(chunks_file)
    chunks = json.loads(chunks_file.read_text(encoding="utf-8"))

    vector_records = []
    embedding_dimensions = 0

    for chunk in chunks:
        embedding = embed_text(chunk["text"], prefix="search_document: ")
        embedding_dimensions = len(embedding)
        vector_records.append({
            "document_id": chunk["document_id"],
            "chunk_id": chunk["chunk_id"],
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "source_filename": chunk["source_filename"],
            "metadata": chunk["metadata"],
            "embedding_model": OLLAMA_EMBED_MODEL,
            "embedding": embedding
        })

    vector_index_file = INDEX_DIR / f"{actual_document_id}_vectors.json"
    vector_index_file.write_text(json.dumps(vector_records, indent=2), encoding="utf-8")

    return {
        "document_id": actual_document_id,
        "source_chunks_file": str(chunks_file),
        "vector_index_file": str(vector_index_file),
        "total_chunks_indexed": len(vector_records),
        "embedding_model": OLLAMA_EMBED_MODEL,
        "embedding_dimensions": embedding_dimensions
    }

def find_latest_vector_file():
    files = sorted(INDEX_DIR.glob("*_vectors.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError("No vector index found. Run /rag/index first.")
    return files[0]

def find_vector_file(document_id):
    if document_id:
        path = INDEX_DIR / f"{document_id}_vectors.json"
        if not path.exists():
            raise FileNotFoundError(f"No vector index found for document_id {document_id}.")
        return path
    return find_latest_vector_file()

def search_vector_index(query, document_id=None, top_k=3):
    vector_file = find_vector_file(document_id)
    records = json.loads(vector_file.read_text(encoding="utf-8"))
    query_embedding = embed_text(query, prefix="search_query: ")

    scored_results = []
    for record in records:
        score = cosine_similarity(query_embedding, record["embedding"])
        scored_results.append({
            "document_id": record["document_id"],
            "chunk_id": record["chunk_id"],
            "chunk_index": record["chunk_index"],
            "score": round(float(score), 6),
            "text": record["text"],
            "source_filename": record["source_filename"]
        })

    scored_results.sort(key=lambda item: item["score"], reverse=True)
    return {
        "query": query,
        "embedding_model": OLLAMA_EMBED_MODEL,
        "total_results": min(top_k, len(scored_results)),
        "results": scored_results[:top_k]
    }