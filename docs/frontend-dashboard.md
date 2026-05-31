# Frontend Dashboard

The project includes a local FastAPI-served dashboard.

Open:

```text
http://127.0.0.1:8000/dashboard
```

## Current capabilities

- API health check
- memory status
- governance testing
- governed Agentic RAG question runner
- MCP tool catalogue
- observability summary
- trace list and trace detail viewer
- safe evaluation runner

## Why this approach

This local dashboard avoids adding a Node.js build system too early. It gives a visible end-to-end demo while keeping the project simple and stable.

## Future direction

The dashboard can later be migrated to a full Next.js frontend with authentication, document upload pages, human review queues, and production deployment.
