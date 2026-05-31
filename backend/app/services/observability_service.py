import json
import re
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = PROJECT_ROOT / "data" / "logs"

LOCAL_PATH_PATTERNS = [
    r"[A-Za-z]:\\\\Users\\\\[^\s\"']+",
    r"C:\\\\Users\\\\[^\s\"']+",
    r"/Users/[^\s\"']+",
    r"/home/[^\s\"']+"
]

def ensure_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def safe_relative_trace_path(path):
    return f"data/logs/{path.name}"

def preview_text(text, limit=180):
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."

def sanitize_string(value):
    sanitized = value
    for pattern in LOCAL_PATH_PATTERNS:
        sanitized = re.sub(pattern, "[REDACTED_LOCAL_PATH]", sanitized)
    return sanitized

def sanitize_value(value):
    if isinstance(value, str):
        return sanitize_string(value)
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_value(item) for key, item in value.items()}
    return value

def trace_files():
    ensure_log_dir()
    return sorted(LOG_DIR.glob("agentic_trace_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)

def load_trace_file(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return sanitize_value(data)
    except Exception:
        return None

def response_from_trace(trace):
    if not trace:
        return {}
    if isinstance(trace, dict) and "response" in trace:
        return trace.get("response", {}) or {}
    return trace

def trace_id_from_file(path):
    name = path.name
    return name.replace("agentic_trace_", "").replace(".json", "")

def make_trace_summary(path):
    trace = load_trace_file(path)
    response = response_from_trace(trace)
    governance = response.get("governance", {})
    reflection = response.get("reflection", {})
    steps = response.get("steps", [])
    tool_calls = response.get("tool_calls", [])
    sources = response.get("sources", [])

    trace_id = response.get("trace_id") or trace.get("trace_id") if isinstance(trace, dict) else None
    if not trace_id:
        trace_id = trace_id_from_file(path)

    created_at = ""
    if isinstance(trace, dict):
        created_at = trace.get("created_at_utc", "")

    return {
        "trace_id": trace_id,
        "created_at_utc": created_at,
        "query_preview": preview_text(response.get("query", "")),
        "status": response.get("status", "unknown"),
        "domain": governance.get("domain", "unknown"),
        "intent": governance.get("intent", "unknown"),
        "total_steps": len(steps),
        "total_tool_calls": len(tool_calls),
        "total_sources_used": len(sources),
        "risk_level": reflection.get("risk_level", "unknown"),
        "human_review_required": bool(reflection.get("human_review_required", False)),
        "trace_file": safe_relative_trace_path(path)
    }

def list_trace_summaries(limit=20):
    summaries = []
    for path in trace_files()[:limit]:
        summary = make_trace_summary(path)
        summaries.append(summary)
    return summaries

def get_trace_detail(trace_id):
    expected_file = LOG_DIR / f"agentic_trace_{trace_id}.json"
    if expected_file.exists():
        trace = load_trace_file(expected_file)
        return {
            "trace_id": trace_id,
            "trace_file": safe_relative_trace_path(expected_file),
            "trace": trace or {}
        }

    for path in trace_files():
        trace = load_trace_file(path)
        response = response_from_trace(trace)
        current_trace_id = response.get("trace_id") or trace_id_from_file(path)
        if current_trace_id == trace_id:
            return {
                "trace_id": trace_id,
                "trace_file": safe_relative_trace_path(path),
                "trace": trace or {}
            }

    return None

def increment_counter(counter, key):
    if not key:
        key = "unknown"
    counter[key] = counter.get(key, 0) + 1

def all_trace_responses():
    responses = []
    for path in trace_files():
        trace = load_trace_file(path)
        response = response_from_trace(trace)
        if response:
            responses.append(response)
    return responses

def build_observability_summary(limit=10):
    responses = all_trace_responses()
    status_counts = {}
    risk_level_counts = {}
    agent_names = set()
    tool_names = set()
    total_tool_calls = 0
    total_sources_used = 0
    human_review_required_count = 0

    for response in responses:
        increment_counter(status_counts, response.get("status", "unknown"))
        reflection = response.get("reflection", {})
        increment_counter(risk_level_counts, reflection.get("risk_level", "unknown"))

        if reflection.get("human_review_required", False):
            human_review_required_count += 1

        tool_calls = response.get("tool_calls", [])
        sources = response.get("sources", [])
        steps = response.get("steps", [])
        total_tool_calls += len(tool_calls)
        total_sources_used += len(sources)

        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name")
            if tool_name:
                tool_names.add(tool_name)

        for step in steps:
            agent_name = step.get("agent_name")
            if agent_name:
                agent_names.add(agent_name)

    total_traces = len(responses)
    average_sources = round(total_sources_used / total_traces, 4) if total_traces else 0.0

    return {
        "total_traces": total_traces,
        "status_counts": status_counts,
        "risk_level_counts": risk_level_counts,
        "total_tool_calls": total_tool_calls,
        "total_sources_used": total_sources_used,
        "average_sources_per_trace": average_sources,
        "human_review_required_count": human_review_required_count,
        "unique_agents_seen": sorted(list(agent_names)),
        "unique_tools_seen": sorted(list(tool_names)),
        "latest_traces": list_trace_summaries(limit=limit)
    }

def build_tool_usage():
    tool_map = {}
    for response in all_trace_responses():
        for tool_call in response.get("tool_calls", []):
            tool_name = tool_call.get("tool_name", "unknown")
            if tool_name not in tool_map:
                tool_map[tool_name] = {
                    "tool_name": tool_name,
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0
                }
            tool_map[tool_name]["total_calls"] += 1
            if tool_call.get("ok", False):
                tool_map[tool_name]["successful_calls"] += 1
            else:
                tool_map[tool_name]["failed_calls"] += 1

    tools = sorted(tool_map.values(), key=lambda item: item["total_calls"], reverse=True)
    total_tool_calls = sum(item["total_calls"] for item in tools)
    return {
        "total_tool_calls": total_tool_calls,
        "tools": tools
    }

def build_risk_summary():
    governance_flags = {}
    output_flags = {}
    reflection_risk_levels = {}
    human_review_required_count = 0

    for response in all_trace_responses():
        governance = response.get("governance", {})
        output_guardrail = response.get("output_guardrail", {})
        reflection = response.get("reflection", {})

        for flag in governance.get("risk_flags", []):
            increment_counter(governance_flags, flag)

        for flag in output_guardrail.get("risk_flags", []):
            increment_counter(output_flags, flag)

        increment_counter(reflection_risk_levels, reflection.get("risk_level", "unknown"))

        if reflection.get("human_review_required", False):
            human_review_required_count += 1

    return {
        "governance_risk_flags": governance_flags,
        "output_guardrail_risk_flags": output_flags,
        "reflection_risk_levels": reflection_risk_levels,
        "human_review_required_count": human_review_required_count
    }

def build_agent_stats():
    agent_map = {}
    total_steps = 0

    for response in all_trace_responses():
        for step in response.get("steps", []):
            total_steps += 1
            agent_name = step.get("agent_name", "unknown")
            action = step.get("action", "unknown")

            if agent_name not in agent_map:
                agent_map[agent_name] = {
                    "agent_name": agent_name,
                    "total_steps": 0,
                    "actions": {}
                }

            agent_map[agent_name]["total_steps"] += 1
            increment_counter(agent_map[agent_name]["actions"], action)

    agents = sorted(agent_map.values(), key=lambda item: item["total_steps"], reverse=True)
    return {
        "total_steps": total_steps,
        "agents": agents
    }
