from typing import Any, Dict
from app.services.mcp_bridge_service import call_mcp_tool

def execute_mcp_tool(tool_name: str, tool_input: Dict[str, Any]):
    result = call_mcp_tool(tool_name, tool_input)
    return {
        "tool_name": tool_name,
        "ok": result.get("ok", False),
        "result": result.get("result", {}),
        "error": result.get("error"),
        "transport": result.get("transport", "local_mcp_bridge")
    }
