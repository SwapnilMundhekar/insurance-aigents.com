# InsuranceAIGents

Enterprise Agentic Insurance Operations Platform.

This project demonstrates local-first enterprise AI architecture for insurance operations, including:

- Multi-agent orchestration
- Retrieval Augmented Generation
- Vector database memory
- Short-term state memory
- Audit logging
- Evaluation pipelines
- Observability
- Human approval workflows

## Part 1

Part 1 creates the local platform foundation:

- FastAPI API Gateway
- PostgreSQL
- Redis
- Qdrant
- Docker Compose

## Run

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8000/health
```