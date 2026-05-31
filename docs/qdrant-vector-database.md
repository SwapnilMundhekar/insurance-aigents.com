# Qdrant Vector Database Migration

Qdrant is used as the vector database layer for the Agentic RAG platform.

## Why Qdrant

The early MVP used local JSON vector indexes. That works for small testing, but a real Agentic RAG system needs a vector database that supports fast similarity search and metadata filtering.

## Flow

```text
chunks
    ↓
embedding model
    ↓
Qdrant collection
    ↓
semantic search
    ↓
retrieved chunks for Agentic RAG
```

## Endpoints

- `POST /rag/qdrant/index`
- `POST /rag/qdrant/search`

## Local Qdrant

Start Qdrant with Docker:

```bash
docker run --name insurance-aigents-qdrant -p 6333:6333 -p 6334:6334 -v "%USERPROFILE%\qdrant_storage:/qdrant/storage" qdrant/qdrant
```

Open:

```text
http://localhost:6333
```
