import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from app.services.llm_service import generate_with_ollama
from app.services.tool_registry_service import execute_tool
from app.services.vector_search_service import search_vector_index

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = PROJECT_ROOT / "data" / "logs"

def ensure_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def summarise_text(text, limit=240):
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."

def add_step(steps, agent_name, action, input_summary, output_summary, metadata=None):
    if metadata is None:
        metadata = {}
    step = {
        "step_index": len(steps) + 1,
        "agent_name": agent_name,
        "action": action,
        "input_summary": summarise_text(input_summary),
        "output_summary": summarise_text(output_summary),
        "metadata": metadata
    }
    steps.append(step)
    return step

def rewrite_query(original_query, steps):
    prompt_lines = [
        "You are a query rewriting agent for an insurance Retrieval Augmented Generation system.",
        "Rewrite the user question into a precise search query for insurance policy retrieval.",
        "Keep the rewritten query short and focused.",
        "Return only the rewritten query.",
        "",
        "USER QUESTION:",
        original_query
    ]
    prompt = "\n".join(prompt_lines)
    result = generate_with_ollama(prompt)
    if result["ok"]:
        rewritten = result["response"].strip().replace("\"", "")
    else:
        rewritten = original_query
    if not rewritten:
        rewritten = original_query
    add_step(
        steps,
        "QueryRewriteAgent",
        "rewrite_query",
        original_query,
        rewritten,
        {"llm_used": result.get("model", "unknown"), "fallback_used": not result["ok"]}
    )
    return rewritten

def decide_if_more_context_needed(results):
    if not results:
        return True, "No retrieved chunks were returned."
    top_score = results[0]["score"]
    if top_score < 0.30:
        return True, "Top similarity score is low, so another retrieval attempt is useful."
    return False, "Retrieved context appears sufficient for a first answer."

def run_insurance_tools(query, results, steps):
    tool_calls = []

    coverage_input = {"query": query}
    coverage_result = execute_tool("coverage_check_tool", coverage_input)
    tool_calls.append({
        "tool_name": coverage_result["tool_name"],
        "ok": coverage_result["ok"],
        "input": coverage_input,
        "result": coverage_result["result"],
        "error": coverage_result["error"]
    })
    add_step(
        steps,
        "ToolCallingAgent",
        "execute_coverage_check_tool",
        coverage_input,
        coverage_result["result"],
        {"tool_name": "coverage_check_tool", "ok": coverage_result["ok"]}
    )

    evidence_input = {"query": query}
    evidence_result = execute_tool("evidence_check_tool", evidence_input)
    tool_calls.append({
        "tool_name": evidence_result["tool_name"],
        "ok": evidence_result["ok"],
        "input": evidence_input,
        "result": evidence_result["result"],
        "error": evidence_result["error"]
    })
    add_step(
        steps,
        "ToolCallingAgent",
        "execute_evidence_check_tool",
        evidence_input,
        evidence_result["result"],
        {"tool_name": "evidence_check_tool", "ok": evidence_result["ok"]}
    )

    fraud_input = {"query": query}
    fraud_result = execute_tool("fraud_signal_tool", fraud_input)
    tool_calls.append({
        "tool_name": fraud_result["tool_name"],
        "ok": fraud_result["ok"],
        "input": fraud_input,
        "result": fraud_result["result"],
        "error": fraud_result["error"]
    })
    add_step(
        steps,
        "ToolCallingAgent",
        "execute_fraud_signal_tool",
        fraud_input,
        fraud_result["result"],
        {"tool_name": "fraud_signal_tool", "ok": fraud_result["ok"]}
    )

    coverage_status = coverage_result["result"].get("coverage_status", "unknown_from_tool_rules")
    fraud_risk_level = fraud_result["result"].get("fraud_risk_level", "low")
    missing_evidence_count = 0

    if not results:
        missing_evidence_count += 1

    human_review_input = {
        "coverage_status": coverage_status,
        "fraud_risk_level": fraud_risk_level,
        "missing_evidence_count": missing_evidence_count
    }
    human_review_result = execute_tool("human_review_tool", human_review_input)
    tool_calls.append({
        "tool_name": human_review_result["tool_name"],
        "ok": human_review_result["ok"],
        "input": human_review_input,
        "result": human_review_result["result"],
        "error": human_review_result["error"]
    })
    add_step(
        steps,
        "ToolCallingAgent",
        "execute_human_review_tool",
        human_review_input,
        human_review_result["result"],
        {"tool_name": "human_review_tool", "ok": human_review_result["ok"]}
    )

    return tool_calls

def build_answer_prompt(original_query, rewritten_query, results, tool_calls):
    context_sections = []
    for index, result in enumerate(results, start=1):
        section_lines = [
            f"SOURCE {index}",
            f"Document ID: {result['document_id']}",
            f"Chunk ID: {result['chunk_id']}",
            f"Source file: {result['source_filename']}",
            f"Similarity score: {result['score']}",
            "Context text:",
            result["text"]
        ]
        context_sections.append("\n".join(section_lines))
    context_text = "\n\n---\n\n".join(context_sections)
    tool_text = json.dumps(tool_calls, indent=2)
    prompt_lines = [
        "You are an insurance policy analysis agent.",
        "Answer using only the retrieved context and the structured tool results below.",
        "Do not invent policy rules, claim decisions, exclusions, or legal conclusions.",
        "If evidence is weak or review is required, clearly say human review is required.",
        "Start with a direct answer, then explain retrieved evidence and tool results.",
        "Mention source chunk IDs and relevant tool names used.",
        "",
        "ORIGINAL USER QUESTION:",
        original_query,
        "",
        "REWRITTEN SEARCH QUERY:",
        rewritten_query,
        "",
        "RETRIEVED CONTEXT:",
        context_text,
        "",
        "STRUCTURED TOOL RESULTS:",
        tool_text,
        "",
        "FINAL ANSWER:"
    ]
    return "\n".join(prompt_lines)

def reflect_on_answer(original_query, answer, results, tool_calls, steps):
    source_ids = [result["chunk_id"] for result in results]
    tool_names = [tool_call["tool_name"] for tool_call in tool_calls]
    human_review_required = False
    for tool_call in tool_calls:
        if tool_call["tool_name"] == "human_review_tool":
            human_review_required = tool_call["result"].get("human_review_required", False)

    prompt_lines = [
        "You are a reflection and critique agent for an insurance agentic RAG system.",
        "Check whether the answer is grounded in retrieved sources and structured tool outputs.",
        "Return a short critique with approval status, risk level, and reason.",
        "",
        "USER QUESTION:",
        original_query,
        "",
        "ANSWER:",
        answer,
        "",
        "AVAILABLE SOURCE CHUNK IDS:",
        ", ".join(source_ids),
        "",
        "TOOLS USED:",
        ", ".join(tool_names)
    ]
    critique_prompt = "\n".join(prompt_lines)
    critique_result = generate_with_ollama(critique_prompt)
    critique_text = critique_result["response"] if critique_result["ok"] else "Reflection model failed. Manual review recommended."

    if human_review_required:
        approved = False
        risk_level = "medium"
    elif not results:
        approved = False
        risk_level = "high"
    else:
        approved = True
        risk_level = "low"

    reflection = {
        "approved": approved,
        "risk_level": risk_level,
        "human_review_required": human_review_required,
        "reason": critique_text
    }
    add_step(
        steps,
        "ReflectionAgent",
        "check_answer_with_tool_results",
        answer,
        critique_text,
        {"source_chunk_ids": source_ids, "tool_names": tool_names, "llm_used": critique_result.get("model", "unknown")}
    )
    return reflection

def save_trace(trace_id, trace_payload):
    ensure_log_dir()
    trace_file = LOG_DIR / f"agentic_trace_{trace_id}.json"
    trace_file.write_text(json.dumps(trace_payload, indent=2), encoding="utf-8")
    return str(trace_file)

def run_agentic_rag(query, document_id=None, top_k=3, max_loops=2):
    trace_id = str(uuid.uuid4())
    steps = []
    add_step(
        steps,
        "SupervisorAgent",
        "receive_task",
        query,
        "Started agentic RAG workflow with tool calling.",
        {"document_id": document_id, "top_k": top_k, "max_loops": max_loops}
    )

    rewritten_query = rewrite_query(query, steps)
    final_results = []
    search_response = None
    loop_count = 0

    for loop_number in range(1, max_loops + 1):
        loop_count = loop_number
        if loop_number == 1:
            retrieval_query = rewritten_query
        else:
            retrieval_query = query + " insurance policy coverage exclusions evidence requirements"

        search_response = search_vector_index(retrieval_query, document_id=document_id, top_k=top_k)
        current_results = search_response["results"]
        final_results = current_results
        top_score = current_results[0]["score"] if current_results else 0.0

        add_step(
            steps,
            "RetrievalAgent",
            "semantic_search",
            retrieval_query,
            f"Retrieved {len(current_results)} chunks. Top score: {top_score}",
            {"loop_number": loop_number, "embedding_model": search_response["embedding_model"]}
        )

        needs_more_context, reason = decide_if_more_context_needed(current_results)
        add_step(
            steps,
            "SupervisorAgent",
            "context_sufficiency_decision",
            retrieval_query,
            reason,
            {"needs_more_context": needs_more_context, "loop_number": loop_number}
        )

        if not needs_more_context:
            break

    tool_calls = run_insurance_tools(query, final_results, steps)

    if not final_results:
        answer = "The provided documents do not contain enough information to answer this question. Human review is required because no retrieved context was available."
        llm_model = "none"
        embedding_model = search_response["embedding_model"] if search_response else "unknown"
    else:
        answer_prompt = build_answer_prompt(query, rewritten_query, final_results, tool_calls)
        llm_result = generate_with_ollama(answer_prompt)
        if not llm_result["ok"]:
            raise RuntimeError(llm_result.get("error", "LLM answer generation failed."))
        answer = llm_result["response"]
        llm_model = llm_result["model"]
        embedding_model = search_response["embedding_model"]
        add_step(
            steps,
            "AnswerAgent",
            "generate_grounded_answer_with_tools",
            answer_prompt,
            answer,
            {"llm_model": llm_model, "prompt_characters": len(answer_prompt)}
        )

    reflection = reflect_on_answer(query, answer, final_results, tool_calls, steps)

    sources = []
    for result in final_results:
        sources.append({
            "document_id": result["document_id"],
            "chunk_id": result["chunk_id"],
            "chunk_index": result["chunk_index"],
            "score": result["score"],
            "source_filename": result["source_filename"],
            "text": result["text"]
        })

    status = "approved" if reflection.get("approved") else "needs_review"
    response_payload = {
        "query": query,
        "rewritten_query": rewritten_query,
        "answer": answer,
        "status": status,
        "llm_model": llm_model,
        "embedding_model": embedding_model,
        "total_sources_used": len(sources),
        "sources": sources,
        "tool_calls": tool_calls,
        "trace_id": trace_id,
        "trace_file": "",
        "loop_count": loop_count,
        "reflection": reflection,
        "steps": steps
    }

    trace_payload = {
        "trace_id": trace_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "response": response_payload
    }
    trace_file = save_trace(trace_id, trace_payload)
    response_payload["trace_file"] = trace_file
    return response_payload