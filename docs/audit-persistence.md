# Audit Persistence

The Agentic RAG workflow writes a structured audit record after each governed workflow run.

## Local development

The local MVP uses SQLite so the project can run without Docker or PostgreSQL.

Audit database path:

```text
data/audit/insurance_aigents_audit.db
```

This database is ignored by Git.

## Stored audit data

- workflow run summary
- governance decision
- agent steps
- tool calls
- retrieval sources
- reflection result
- final response status

## Endpoints

- `GET /audit/runs`
- `GET /audit/runs/{trace_id}`

## Production direction

In production, this layer should move to PostgreSQL. PostgreSQL provides durable queryable storage for audit records, workflow history, compliance review, and reporting.
