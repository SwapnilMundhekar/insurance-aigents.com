from app.services.insurance_tools_service import coverage_check_tool, evidence_check_tool, fraud_signal_tool, human_review_tool

TOOL_REGISTRY = {
    "coverage_check_tool": {
        "description": "Checks whether claim wording appears related to covered events or exclusions.",
        "input_schema": {"query": "string"},
        "function": coverage_check_tool
    },
    "evidence_check_tool": {
        "description": "Returns likely evidence required for claim assessment.",
        "input_schema": {"query": "string"},
        "function": evidence_check_tool
    },
    "fraud_signal_tool": {
        "description": "Detects simple fraud risk indicators from claim wording.",
        "input_schema": {"query": "string"},
        "function": fraud_signal_tool
    },
    "human_review_tool": {
        "description": "Decides whether a claim should be escalated to human review.",
        "input_schema": {
            "coverage_status": "string",
            "fraud_risk_level": "string",
            "missing_evidence_count": "integer"
        },
        "function": human_review_tool
    }
}

def list_tools():
    tools = []
    for name, definition in TOOL_REGISTRY.items():
        tools.append({
            "name": name,
            "description": definition["description"],
            "input_schema": definition["input_schema"]
        })
    return tools

def execute_tool(tool_name, tool_input):
    if tool_name not in TOOL_REGISTRY:
        return {
            "tool_name": tool_name,
            "ok": False,
            "result": {},
            "error": f"Unknown tool: {tool_name}"
        }

    try:
        tool_function = TOOL_REGISTRY[tool_name]["function"]
        result = tool_function(tool_input)
        return {
            "tool_name": tool_name,
            "ok": True,
            "result": result,
            "error": None
        }
    except Exception as error:
        return {
            "tool_name": tool_name,
            "ok": False,
            "result": {},
            "error": str(error)
        }