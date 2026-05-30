<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=230&color=0:0f172a,50:1e40af,100:06b6d4&text=InsuranceAIGents.com&fontColor=ffffff&fontSize=48&fontAlignY=38&desc=Enterprise%20Agentic%20Insurance%20Operations%20Platform&descAlignY=58&animation=fadeIn" alt="InsuranceAIGents animated banner" />

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=26&duration=2800&pause=700&color=38BDF8&center=true&vCenter=true&width=850&lines=Multi-Agent+Insurance+Decision+Systems;Agentic+RAG+with+Tool+Calling;Local-First+AI+Architecture;Traceable%2C+Auditable%2C+Human-Governed+AI" alt="Animated typing headline" />

<br/>

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API%20Gateway-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-111827?style=for-the-badge)
![RAG](https://img.shields.io/badge/RAG-Retrieval%20Augmented%20Generation-7C3AED?style=for-the-badge)
![Agentic AI](https://img.shields.io/badge/Agentic%20AI-Supervisor%20Workflow-06B6D4?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Local%20MVP%20Build-22C55E?style=for-the-badge)

</div>

---

# InsuranceAIGents.com

**InsuranceAIGents.com** is a local-first enterprise AI engineering showcase project for building **agentic insurance operations workflows** using multi-agent orchestration, Retrieval Augmented Generation, controlled tool calling, trace logging, and human review decision patterns.

This project is designed to demonstrate how an insurance organisation could move beyond a simple chatbot and toward a safer, more observable, and more governable AI decision-support platform.

---

## Why This Project Exists

Insurance workflows are complex. Claims, policy interpretation, fraud signals, evidence requirements, compliance checks, and human review decisions cannot be handled safely by a single free-form chatbot.

This project uses a more enterprise-ready pattern:

```text
User question
    ↓
Input validation
    ↓
Supervisor Agent
    ↓
Query rewriting
    ↓
Document retrieval
    ↓
Insurance tool calling
    ↓
Grounded answer generation
    ↓
Reflection and review
    ↓
Traceable final response
```

---

## Core Capabilities

| Capability               | Description                                                     |
| ------------------------ | --------------------------------------------------------------- |
| **Agentic RAG**          | Retrieves relevant policy context before generating an answer   |
| **Supervisor Agent**     | Controls the workflow and coordinates specialist steps          |
| **Query Rewrite Agent**  | Converts user questions into better retrieval queries           |
| **Retrieval Agent**      | Searches indexed insurance document chunks                      |
| **Tool Calling Agent**   | Calls approved insurance tools through a controlled registry    |
| **Reflection Agent**     | Reviews answer quality, grounding, and risk                     |
| **Trace Logging**        | Records each agent step for auditability and debugging          |
| **Human Review Logic**   | Escalates uncertain or risky cases instead of blindly approving |
| **Local LLM Serving**    | Uses local model serving through Ollama during development      |
| **Token-Aware Chunking** | Splits documents into manageable chunks with overlap            |

---

## Architecture

```mermaid
flowchart TD
    A[User Prompt] --> B[FastAPI API Gateway]
    B --> C[Input Validation]
    C --> D[Supervisor Agent]

    D --> E[Query Rewrite Agent]
    E --> F[Retrieval Agent]

    F --> G[Vector Search Layer]
    G --> H[Retrieved Policy Chunks]

    D --> I[Tool Calling Agent]
    I --> J[Coverage Check Tool]
    I --> K[Evidence Check Tool]
    I --> L[Fraud Signal Tool]
    I --> M[Human Review Tool]

    H --> N[Answer Agent]
    J --> N
    K --> N
    L --> N
    M --> N

    N --> O[Reflection Agent]
    O --> P[Trace Logger]
    P --> Q[Final Response]

    subgraph Local AI Runtime
        R[Ollama LLM]
        S[Embedding Model]
    end

    E --> R
    N --> R
    O --> R
    G --> S
```

---

## Current Local Workflow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant Supervisor
    participant RAG as Retrieval Layer
    participant Tools as Tool Registry
    participant LLM as Local LLM
    participant Trace as Trace Logger

    User->>API: Ask insurance question
    API->>Supervisor: Start agentic workflow
    Supervisor->>LLM: Rewrite query
    Supervisor->>RAG: Retrieve relevant chunks
    Supervisor->>Tools: Run insurance tools
    Tools-->>Supervisor: Structured tool results
    Supervisor->>LLM: Generate grounded answer
    Supervisor->>LLM: Reflect on answer
    Supervisor->>Trace: Save workflow trace
    Supervisor-->>API: Final answer with sources and tool calls
    API-->>User: JSON response
```

---

## Tool Calling Design

The project uses a **controlled tool registry**.

A tool registry is a catalogue of approved backend functions the agent is allowed to call. This prevents the model from taking uncontrolled actions.

Current tools:

| Tool                  | Purpose                                                                  |
| --------------------- | ------------------------------------------------------------------------ |
| `coverage_check_tool` | Checks whether the claim appears related to covered events or exclusions |
| `evidence_check_tool` | Identifies likely claim evidence requirements                            |
| `fraud_signal_tool`   | Detects simple fraud indicators from claim wording                       |
| `human_review_tool`   | Decides whether the case should be escalated                             |

Each tool has:

```text
name
description
input schema
execution function
structured output
trace log entry
```

---

## Retrieval Augmented Generation Pipeline

```mermaid
flowchart LR
    A[Upload Document] --> B[Extract Text]
    B --> C[Clean Text]
    C --> D[Chunk Text]
    D --> E[Estimate Tokens]
    E --> F[Attach Metadata]
    F --> G[Create Embeddings]
    G --> H[Vector Index]
    H --> I[Semantic Search]
    I --> J[Grounded Answer]
```

The current RAG pipeline supports:

* Document ingestion
* Text extraction
* Text cleaning
* Token estimation
* Chunking with overlap
* Metadata tracking
* Local embedding generation
* Semantic vector search
* Grounded answer generation

---

## API Endpoints

| Endpoint                   | Purpose                                    |
| -------------------------- | ------------------------------------------ |
| `GET /`                    | Basic API status                           |
| `GET /health`              | Dependency health check                    |
| `POST /llm/test`           | Test local Large Language Model generation |
| `POST /documents/ingest`   | Upload and chunk a document                |
| `POST /rag/index`          | Convert chunks into embeddings             |
| `POST /rag/search`         | Search indexed document chunks             |
| `POST /rag/answer`         | Generate a grounded RAG answer             |
| `GET /tools/list`          | List available tools                       |
| `POST /tools/execute`      | Execute a registered tool                  |
| `POST /agentic/rag-answer` | Run the full agentic RAG workflow          |

---

## Technology Stack

| Layer                    | Technology                            |
| ------------------------ | ------------------------------------- |
| Backend API              | FastAPI                               |
| Local model serving      | Ollama                                |
| Language model interface | Local HTTP API                        |
| Embeddings               | Local embedding model                 |
| Vector search            | Local vector index for MVP            |
| Future vector database   | Qdrant                                |
| Short-term memory        | Redis planned                         |
| Persistent storage       | PostgreSQL planned                    |
| Containerisation         | Docker Compose planned                |
| Observability            | Trace logs now, OpenTelemetry planned |
| Frontend                 | Planned                               |

---

## Project Structure

```text
insurance-aigents.com/
    backend/
        app/
            api/
            agents/
            core/
            memory/
            models/
            observability/
            rag/
            schemas/
            services/
        requirements.txt
        run_local_api.py

    data/
        uploads/
        indexes/
        logs/

    docs/
    docker-compose.yml
    README.md
```

---

## Example Agentic Response Shape

```json
{
  "query": "The customer has windscreen damage after a storm. Is it covered and what evidence is required?",
  "rewritten_query": "windscreen storm damage insurance coverage evidence requirements",
  "status": "approved",
  "llm_model": "llama3.1:8b",
  "embedding_model": "nomic-embed-text",
  "total_sources_used": 1,
  "tool_calls": [
    {
      "tool_name": "coverage_check_tool",
      "ok": true,
      "result": {
        "coverage_status": "potentially_covered"
      }
    },
    {
      "tool_name": "evidence_check_tool",
      "ok": true,
      "result": {
        "required_evidence": [
          "incident description",
          "photographs of damage",
          "repair invoice or quote"
        ]
      }
    }
  ],
  "reflection": {
    "approved": true,
    "risk_level": "low",
    "human_review_required": false
  }
}
```

---

## What Makes This Different From A Chatbot

| Chatbot                   | InsuranceAIGents.com                    |
| ------------------------- | --------------------------------------- |
| Answers directly          | Retrieves evidence first                |
| No controlled tools       | Uses an approved tool registry          |
| Hard to audit             | Saves trace logs                        |
| May hallucinate           | Uses grounded context and reflection    |
| One model does everything | Supervisor coordinates specialist steps |
| No escalation logic       | Supports human review decisioning       |

---

## Local Development Status

```text
Completed:
    ✓ FastAPI backend foundation
    ✓ Local LLM endpoint
    ✓ Document ingestion
    ✓ Token-aware chunking
    ✓ Local vector indexing
    ✓ Semantic search
    ✓ Basic RAG answer generation
    ✓ Agentic RAG supervisor workflow
    ✓ Controlled insurance tool registry
    ✓ Tool calling inside supervisor workflow
    ✓ Trace logging

Next:
    → Input guardrails
    → Business domain classifier
    → Intent classifier
    → Prompt decomposition
    → Redis memory
    → PostgreSQL audit persistence
    → Qdrant vector database migration
    → Frontend dashboard
    → Observability dashboards
```

---

## Planned Enterprise Enhancements

```mermaid
mindmap
  root((InsuranceAIGents Roadmap))
    Governance
      Input guardrails
      Output validation
      Human approval workflows
      Audit events
    Memory
      Redis working memory
      PostgreSQL workflow memory
      Vector semantic memory
      Episodic agent memory
    Observability
      Agent traces
      Token metrics
      Latency tracking
      Tool failure monitoring
      Retrieval quality metrics
    Deployment
      Docker Compose
      Cloudflare front door
      Secure public demo
      Cloud migration path
    AI Engineering
      Model selection
      Prompt versioning
      Evaluation datasets
      Reflection scoring
```

---

## Local Setup

> This project is currently designed as a local-first MVP.

Install backend dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run_local_api.py
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

---

## Security Notes

This repository intentionally avoids committing:

```text
environment files
local virtual environments
uploaded documents
generated indexes
agent trace logs
API keys
tokens
passwords
local machine paths
Cloudflare tunnel credentials
private customer data
```

The public repository should contain source code, documentation, configuration templates, and safe example material only.

---

## Interview Positioning

This project demonstrates hands-on capability across:

* Agentic AI system design
* Multi-step orchestration
* Retrieval Augmented Generation
* Context engineering
* Tool calling
* Local model serving
* Controlled AI workflows
* Human review patterns
* Traceability and auditability
* Insurance-domain AI decision support
* Production-minded AI engineering

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=130&color=0:06b6d4,50:1e40af,100:0f172a&section=footer" alt="Animated footer" />

</div>
