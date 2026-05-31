# Evaluation Framework

The evaluation framework measures whether the Agentic RAG system behaves correctly.

## What is evaluated

- input governance
- prompt injection blocking
- out-of-scope prompt blocking
- Personally Identifiable Information detection and redaction
- output guardrail behaviour
- optional end-to-end Agentic RAG execution

## Endpoints

- `GET /evaluations/cases`
- `POST /evaluations/run`
- `GET /evaluations/reports`
- `GET /evaluations/reports/{report_id}`

## Safe default

By default, `POST /evaluations/run` does not run full Agentic RAG cases. This avoids failing when Ollama, Qdrant, or a vector index is unavailable.

To run end-to-end cases, set:

```json
{
  "include_agentic_cases": true,
  "document_id": "your-document-id"
}
```

## Report storage

Reports are saved locally under:

```text
data/evaluations/
```

This folder is ignored by Git.
