import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = PROJECT_ROOT / "data" / "audit"
AUDIT_DB_PATH = AUDIT_DIR / "insurance_aigents_audit.db"

def ensure_audit_database():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(AUDIT_DB_PATH))
    cursor = connection.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS workflow_runs ("
        "trace_id TEXT PRIMARY KEY, "
        "created_at_utc TEXT NOT NULL, "
        "query TEXT NOT NULL, "
        "status TEXT NOT NULL, "
        "domain TEXT, "
        "intent TEXT, "
        "route_to TEXT, "
        "llm_model TEXT, "
        "embedding_model TEXT, "
        "total_sources_used INTEGER, "
        "total_tool_calls INTEGER, "
        "risk_level TEXT, "
        "human_review_required INTEGER, "
        "trace_file TEXT, "
        "workflow_json TEXT NOT NULL"
        ")"
    )

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS agent_steps ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "trace_id TEXT NOT NULL, "
        "step_index INTEGER NOT NULL, "
        "agent_name TEXT NOT NULL, "
        "action TEXT NOT NULL, "
        "input_summary TEXT, "
        "output_summary TEXT, "
        "metadata_json TEXT, "
        "FOREIGN KEY(trace_id) REFERENCES workflow_runs(trace_id)"
        ")"
    )

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS tool_calls ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "trace_id TEXT NOT NULL, "
        "tool_name TEXT NOT NULL, "
        "ok INTEGER NOT NULL, "
        "input_json TEXT, "
        "result_json TEXT, "
        "error TEXT, "
        "FOREIGN KEY(trace_id) REFERENCES workflow_runs(trace_id)"
        ")"
    )

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS retrieval_sources ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "trace_id TEXT NOT NULL, "
        "document_id TEXT, "
        "chunk_id TEXT, "
        "chunk_index INTEGER, "
        "score REAL, "
        "source_filename TEXT, "
        "metadata_json TEXT, "
        "FOREIGN KEY(trace_id) REFERENCES workflow_runs(trace_id)"
        ")"
    )

    connection.commit()
    connection.close()

def as_json(value):
    return json.dumps(value, ensure_ascii=False)

def save_agentic_workflow_audit(response_payload):
    ensure_audit_database()
    trace_id = response_payload.get("trace_id", "")
    if not trace_id:
        return

    governance = response_payload.get("governance", {})
    reflection = response_payload.get("reflection", {})
    steps = response_payload.get("steps", [])
    tool_calls = response_payload.get("tool_calls", [])
    sources = response_payload.get("sources", [])

    created_at_utc = datetime.now(timezone.utc).isoformat()

    connection = sqlite3.connect(str(AUDIT_DB_PATH))
    cursor = connection.cursor()

    cursor.execute("DELETE FROM agent_steps WHERE trace_id = ?", (trace_id,))
    cursor.execute("DELETE FROM tool_calls WHERE trace_id = ?", (trace_id,))
    cursor.execute("DELETE FROM retrieval_sources WHERE trace_id = ?", (trace_id,))
    cursor.execute("DELETE FROM workflow_runs WHERE trace_id = ?", (trace_id,))

    cursor.execute(
        "INSERT INTO workflow_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            trace_id,
            created_at_utc,
            response_payload.get("query", ""),
            response_payload.get("status", ""),
            governance.get("domain", ""),
            governance.get("intent", ""),
            governance.get("route_to", ""),
            response_payload.get("llm_model", ""),
            response_payload.get("embedding_model", ""),
            int(response_payload.get("total_sources_used", 0)),
            len(tool_calls),
            reflection.get("risk_level", ""),
            1 if reflection.get("human_review_required", False) else 0,
            response_payload.get("trace_file", ""),
            as_json(response_payload)
        )
    )

    for step in steps:
        cursor.execute(
            "INSERT INTO agent_steps (trace_id, step_index, agent_name, action, input_summary, output_summary, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                trace_id,
                step.get("step_index", 0),
                step.get("agent_name", ""),
                step.get("action", ""),
                step.get("input_summary", ""),
                step.get("output_summary", ""),
                as_json(step.get("metadata", {}))
            )
        )

    for tool_call in tool_calls:
        cursor.execute(
            "INSERT INTO tool_calls (trace_id, tool_name, ok, input_json, result_json, error) VALUES (?, ?, ?, ?, ?, ?)",
            (
                trace_id,
                tool_call.get("tool_name", ""),
                1 if tool_call.get("ok", False) else 0,
                as_json(tool_call.get("input", {})),
                as_json(tool_call.get("result", {})),
                tool_call.get("error", None)
            )
        )

    for source in sources:
        cursor.execute(
            "INSERT INTO retrieval_sources (trace_id, document_id, chunk_id, chunk_index, score, source_filename, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                trace_id,
                source.get("document_id", ""),
                source.get("chunk_id", ""),
                source.get("chunk_index", 0),
                float(source.get("score", 0.0)),
                source.get("source_filename", ""),
                as_json(source.get("metadata", {}))
            )
        )

    connection.commit()
    connection.close()

def list_audit_runs(limit=20):
    ensure_audit_database()
    connection = sqlite3.connect(str(AUDIT_DB_PATH))
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(
        "SELECT trace_id, created_at_utc, query, status, domain, intent, llm_model, embedding_model, total_sources_used, total_tool_calls, risk_level, human_review_required "
        "FROM workflow_runs ORDER BY created_at_utc DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    connection.close()

    runs = []
    for row in rows:
        runs.append({
            "trace_id": row["trace_id"],
            "created_at_utc": row["created_at_utc"],
            "query": row["query"],
            "status": row["status"],
            "domain": row["domain"],
            "intent": row["intent"],
            "llm_model": row["llm_model"],
            "embedding_model": row["embedding_model"],
            "total_sources_used": row["total_sources_used"],
            "total_tool_calls": row["total_tool_calls"],
            "risk_level": row["risk_level"],
            "human_review_required": bool(row["human_review_required"])
        })
    return runs

def get_audit_run(trace_id):
    ensure_audit_database()
    connection = sqlite3.connect(str(AUDIT_DB_PATH))
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM workflow_runs WHERE trace_id = ?", (trace_id,))
    run = cursor.fetchone()
    connection.close()

    if not run:
        return None

    workflow = json.loads(run["workflow_json"])
    return {
        "trace_id": trace_id,
        "created_at_utc": run["created_at_utc"],
        "workflow": workflow,
        "governance": workflow.get("governance", {}),
        "steps": workflow.get("steps", []),
        "tool_calls": workflow.get("tool_calls", []),
        "sources": workflow.get("sources", []),
        "reflection": workflow.get("reflection", {})
    }
