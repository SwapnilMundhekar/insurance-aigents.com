# Observability

Observability means being able to inspect, measure, and debug system behaviour.

For an Agentic RAG system, observability includes agent steps, tool calls, governance decisions, retrieved sources, output guardrail results, human review flags, and final workflow status.

## Endpoints

- `GET /observability/summary`
- `GET /observability/traces`
- `GET /observability/traces/{trace_id}`
- `GET /observability/tools`
- `GET /observability/risks`
- `GET /observability/agents`

## What this helps answer

- How many workflows were approved, blocked, or marked as needs review?
- Which tools are being called most often?
- Which agents are active in the workflow?
- Which risk flags appear most often?
- Which trace IDs need debugging?

## Local development

The current observability layer reads local trace files from:

```text
data/logs/
```

Generated trace logs are ignored by Git.

## Production direction

In production, this should evolve into OpenTelemetry traces, metrics, dashboards, and alerts. OpenTelemetry is an observability standard for collecting traces, metrics, and logs across services.
