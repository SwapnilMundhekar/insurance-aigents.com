import json
from pathlib import Path
from typing import Any, Dict
from app.services.tool_registry_service import execute_tool, list_tools

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = PROJECT_ROOT / "data" / "indexes"

MCP_TRANSPORT = "local_mcp_bridge"

def list_mcp_tools():
    tools = []
    for tool in list_tools():
        tools.append({
            "name": tool["name"],
            "description": tool["description"],
            "inputSchema": {
                "type": "object",
                "properties": {key: {"type": "string"} for key in tool.get("input_schema", {}).keys()},
                "required": list(tool.get("input_schema", {}).keys())
            }
        })
    return tools

def call_mcp_tool(name: str, arguments: Dict[str, Any]):
    result = execute_tool(name, arguments)
    return {
        "name": name,
        "ok": result.get("ok", False),
        "result": result.get("result", {}),
        "error": result.get("error"),
        "transport": MCP_TRANSPORT
    }

def list_mcp_resources():
    return [
        {
            "uri": "insurance://tools/catalog",
            "name": "Insurance Tool Catalog",
            "description": "Approved insurance tools exposed through the MCP bridge.",
            "mimeType": "application/json"
        },
        {
            "uri": "insurance://documents/latest-chunks",
            "name": "Latest Chunk Index Summary",
            "description": "Summary of the latest locally generated document chunk file.",
            "mimeType": "application/json"
        }
    ]

def latest_chunks_summary():
    files = sorted(INDEX_DIR.glob("*_chunks.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not files:
        return {
            "found": False,
            "message": "No chunk files found. Run document ingestion first."
        }

    latest_file = files[0]
    try:
        chunks = json.loads(latest_file.read_text(encoding="utf-8"))
    except Exception:
        chunks = []

    sample = []
    for chunk in chunks[:3]:
        sample.append({
            "document_id": chunk.get("document_id", ""),
            "chunk_id": chunk.get("chunk_id", ""),
            "chunk_index": chunk.get("chunk_index", 0),
            "source_filename": chunk.get("source_filename", ""),
            "token_estimate": chunk.get("token_estimate", 0),
            "metadata": chunk.get("metadata", {})
        })

    return {
        "found": True,
        "chunks_file": f"data/indexes/{latest_file.name}",
        "total_chunks": len(chunks),
        "sample_chunks": sample
    }

def read_mcp_resource(uri: str):
    if uri == "insurance://tools/catalog":
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps({"tools": list_mcp_tools()}, indent=2)
        }

    if uri == "insurance://documents/latest-chunks":
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(latest_chunks_summary(), indent=2)
        }

    raise ValueError(f"Unknown MCP resource URI: {uri}")

def list_mcp_prompts():
    return [
        {
            "name": "insurance_claim_triage",
            "description": "Prompt template for triaging an insurance claim using coverage, evidence, fraud, and human review checks.",
            "arguments": [
                {"name": "claim_summary", "description": "Short description of the claim", "required": True}
            ]
        },
        {
            "name": "governed_agentic_rag",
            "description": "Prompt template for governed Agentic RAG with retrieved sources and tool outputs.",
            "arguments": [
                {"name": "question", "description": "User question", "required": True}
            ]
        }
    ]

def get_mcp_prompt(prompt_name: str):
    if prompt_name == "insurance_claim_triage":
        return {
            "name": prompt_name,
            "description": "Prompt template for insurance claim triage.",
            "prompt": "Assess the insurance claim using policy coverage, required evidence, fraud indicators, and human review rules. Return a grounded decision-support summary, not a final claim decision."
        }

    if prompt_name == "governed_agentic_rag":
        return {
            "name": prompt_name,
            "description": "Prompt template for governed Agentic RAG.",
            "prompt": "Use input governance, retrieved context, approved tool outputs, reflection, and output guardrails before returning a final response."
        }

    raise ValueError(f"Unknown MCP prompt: {prompt_name}")

def json_rpc_success(request_id, result):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
        "error": None
    }

def json_rpc_error(request_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": None,
        "error": {
            "code": code,
            "message": message
        }
    }

def handle_mcp_json_rpc(payload: Dict[str, Any]):
    request_id = payload.get("id")
    method = payload.get("method", "")
    params = payload.get("params", {}) or {}

    try:
        if method == "tools/list":
            return json_rpc_success(request_id, {"tools": list_mcp_tools()})

        if method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            return json_rpc_success(request_id, call_mcp_tool(tool_name, arguments))

        if method == "resources/list":
            return json_rpc_success(request_id, {"resources": list_mcp_resources()})

        if method == "resources/read":
            uri = params.get("uri", "")
            return json_rpc_success(request_id, read_mcp_resource(uri))

        if method == "prompts/list":
            return json_rpc_success(request_id, {"prompts": list_mcp_prompts()})

        if method == "prompts/get":
            prompt_name = params.get("name", "")
            return json_rpc_success(request_id, get_mcp_prompt(prompt_name))

        return json_rpc_error(request_id, -32601, f"Method not found: {method}")
    except Exception as error:
        return json_rpc_error(request_id, -32000, str(error))
