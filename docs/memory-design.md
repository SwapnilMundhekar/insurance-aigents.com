# Memory Design

The Agentic RAG system uses memory in multiple layers.

## Memory types

| Memory type | Purpose | Current implementation | Future implementation |
|---|---|---|---|
| Working memory | Recent session state | Redis if available, file fallback otherwise | Redis |
| Audit memory | Durable workflow history | SQLite | PostgreSQL |
| Semantic memory | Document knowledge | Local JSON or Qdrant | Qdrant |
| Retrieval cache | Reusable search or tool results | Redis/file cache | Redis |

## Why working memory matters

Working memory lets the agent remember recent workflow runs in the same session. This supports follow-up questions, debugging, and trace continuity.

## Local-first behaviour

If Redis is running, the system stores working memory in Redis. If Redis is unavailable, the system automatically uses local file fallback under:

```text
data/memory/
```

This folder is ignored by Git.

## Agentic RAG integration

`POST /agentic/rag-answer` now accepts `session_id`. When a session ID is provided, the workflow loads recent session memory and saves the new run after completion.

## Example request

```json
{
  "query": "Is windscreen damage covered?",
  "document_id": null,
  "top_k": 3,
  "max_loops": 2,
  "session_id": "demo-session-1"
}
```
