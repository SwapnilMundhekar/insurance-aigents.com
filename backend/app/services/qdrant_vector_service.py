import json
import os
from pathlib import Path
from uuid import NAMESPACE_DNS, uuid5
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.services.embedding_service import OLLAMA_EMBED_MODEL, embed_text

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = PROJECT_ROOT / "data" / "indexes"

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "insurance_aigents_chunks")

def get_qdrant_client():
    return QdrantClient(url=QDRANT_URL, timeout=30)

def ensure_qdrant_available():
    client = get_qdrant_client()
    client.get_collections()
    return client

def find_latest_chunks_file():
    files = sorted(INDEX_DIR.glob("*_chunks.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError("No chunk files found. Run document ingestion first.")
    return files[0]

def find_chunks_file(document_id):
    if document_id:
        path = INDEX_DIR / f"{document_id}_chunks.json"
        if not path.exists():
            raise FileNotFoundError(f"No chunks found for document_id {document_id}.")
        return path
    return find_latest_chunks_file()

def extract_document_id_from_chunks_file(chunks_file):
    return chunks_file.name.replace("_chunks.json", "")

def ensure_collection(client, vector_size):
    try:
        client.get_collection(collection_name=QDRANT_COLLECTION)
        return
    except Exception:
        pass

    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE
        )
    )

def build_payload(chunk):
    metadata = chunk.get("metadata", {})
    return {
        "document_id": chunk.get("document_id", ""),
        "chunk_id": chunk.get("chunk_id", ""),
        "chunk_index": chunk.get("chunk_index", 0),
        "text": chunk.get("text", ""),
        "source_filename": chunk.get("source_filename", ""),
        "metadata": metadata,
        "section_title": metadata.get("section_title", ""),
        "page_start": metadata.get("page_start", 0),
        "page_end": metadata.get("page_end", 0),
        "embedding_model": OLLAMA_EMBED_MODEL
    }

def qdrant_index_document(document_id=None):
    client = ensure_qdrant_available()
    chunks_file = find_chunks_file(document_id)
    actual_document_id = extract_document_id_from_chunks_file(chunks_file)
    chunks = json.loads(chunks_file.read_text(encoding="utf-8"))

    if not chunks:
        raise ValueError("Chunk file exists but contains no chunks.")

    first_embedding = embed_text(chunks[0]["text"], prefix="search_document: ")
    embedding_dimensions = len(first_embedding)
    ensure_collection(client, embedding_dimensions)

    points = []

    first_point_id = str(uuid5(NAMESPACE_DNS, chunks[0]["chunk_id"]))
    points.append(models.PointStruct(
        id=first_point_id,
        vector=first_embedding,
        payload=build_payload(chunks[0])
    ))

    for chunk in chunks[1:]:
        embedding = embed_text(chunk["text"], prefix="search_document: ")
        point_id = str(uuid5(NAMESPACE_DNS, chunk["chunk_id"]))
        points.append(models.PointStruct(
            id=point_id,
            vector=embedding,
            payload=build_payload(chunk)
        ))

    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points
    )

    return {
        "document_id": actual_document_id,
        "collection_name": QDRANT_COLLECTION,
        "source_chunks_file": f"data/indexes/{chunks_file.name}",
        "total_chunks_indexed": len(points),
        "embedding_model": OLLAMA_EMBED_MODEL,
        "embedding_dimensions": embedding_dimensions,
        "qdrant_url": QDRANT_URL
    }

def build_document_filter(document_id):
    if not document_id:
        return None
    return models.Filter(
        must=[
            models.FieldCondition(
                key="document_id",
                match=models.MatchValue(value=document_id)
            )
        ]
    )

def qdrant_search(query, document_id=None, top_k=3):
    client = ensure_qdrant_available()
    query_embedding = embed_text(query, prefix="search_query: ")
    query_filter = build_document_filter(document_id)

    search_results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_embedding,
        query_filter=query_filter,
        limit=top_k
    )

    results = []
    for item in search_results:
        payload = item.payload or {}
        results.append({
            "document_id": payload.get("document_id", ""),
            "chunk_id": payload.get("chunk_id", ""),
            "chunk_index": payload.get("chunk_index", 0),
            "score": round(float(item.score), 6),
            "text": payload.get("text", ""),
            "source_filename": payload.get("source_filename", ""),
            "metadata": payload.get("metadata", {})
        })

    return {
        "query": query,
        "collection_name": QDRANT_COLLECTION,
        "embedding_model": OLLAMA_EMBED_MODEL,
        "total_results": len(results),
        "results": results
    }
