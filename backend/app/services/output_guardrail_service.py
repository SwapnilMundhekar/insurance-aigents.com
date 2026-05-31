import re
from typing import Any, Dict, List

LOCAL_PATH_PATTERNS = [
    r"[A-Za-z]:\\\\Users\\\\[^\s\"']+",
    r"C:\\\\Users\\\\[^\s\"']+",
    r"/Users/[^\s\"']+",
    r"/home/[^\s\"']+"
]

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"(?i)api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{16,}",
    r"(?i)password\s*[:=]\s*[^\s]{6,}",
    r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"
]

PII_PATTERNS = {
    "pii_email_leak": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "pii_phone_leak": r"\b(?:\+?61|0)[\d\s\-]{8,15}\b",
    "pii_reference_id_leak": r"\b(?:POL|CLAIM|CUST|REF)[-_: ]?(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,}\b"
}

OVERCONFIDENT_DECISION_PATTERNS = [
    r"(?i)\bclaim\s+is\s+approved\b",
    r"(?i)\bclaim\s+has\s+been\s+approved\b",
    r"(?i)\bwe\s+will\s+pay\b",
    r"(?i)\bguaranteed\s+covered\b",
    r"(?i)\bdefinitely\s+covered\b",
    r"(?i)\bmust\s+be\s+paid\b"
]

def contains_pattern(text: str, patterns: List[str]) -> bool:
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False

def detect_pii_leaks(answer: str) -> List[str]:
    flags = []
    for flag, pattern in PII_PATTERNS.items():
        if re.search(pattern, answer):
            flags.append(flag)
    return flags

def mask_sensitive_output(answer: str) -> str:
    safe_answer = answer
    safe_answer = re.sub(r"[A-Za-z]:\\\\Users\\\\[^\s\"']+", "[REDACTED_LOCAL_PATH]", safe_answer)
    safe_answer = re.sub(r"C:\\\\Users\\\\[^\s\"']+", "[REDACTED_LOCAL_PATH]", safe_answer)
    safe_answer = re.sub(r"/Users/[^\s\"']+", "[REDACTED_LOCAL_PATH]", safe_answer)
    safe_answer = re.sub(r"/home/[^\s\"']+", "[REDACTED_LOCAL_PATH]", safe_answer)
    safe_answer = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", safe_answer)
    safe_answer = re.sub(r"\b(?:\+?61|0)[\d\s\-]{8,15}\b", "[REDACTED_PHONE]", safe_answer)
    safe_answer = re.sub(r"\b(?:POL|CLAIM|CUST|REF)[-_: ]?(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,}\b", "[REDACTED_REFERENCE_ID]", safe_answer, flags=re.IGNORECASE)
    return safe_answer

def source_ids_from_sources(sources: List[Dict[str, Any]]) -> List[str]:
    ids = []
    for source in sources:
        chunk_id = source.get("chunk_id")
        if chunk_id:
            ids.append(str(chunk_id))
    return ids

def has_human_review_required(tool_calls: List[Dict[str, Any]], reflection: Dict[str, Any]) -> bool:
    if reflection.get("human_review_required", False):
        return True
    for tool_call in tool_calls:
        if tool_call.get("tool_name") == "human_review_tool":
            result = tool_call.get("result", {})
            if result.get("human_review_required", False):
                return True
    return False

def validate_agentic_output(answer: str, sources: List[Dict[str, Any]], tool_calls: List[Dict[str, Any]], governance: Dict[str, Any], reflection: Dict[str, Any]) -> Dict[str, Any]:
    risk_flags = []
    blocked_reasons = []
    required_actions = []

    safe_answer = mask_sensitive_output(answer)
    source_ids = source_ids_from_sources(sources)
    source_count = len(sources)
    intent = governance.get("intent", "")
    domain = governance.get("domain", "")

    if contains_pattern(answer, LOCAL_PATH_PATTERNS):
        risk_flags.append("local_path_leak_detected")
        required_actions.append("redact_local_paths")

    if contains_pattern(answer, SECRET_PATTERNS):
        risk_flags.append("secret_like_text_detected")
        blocked_reasons.append("Answer appears to contain secret-like text.")
        required_actions.append("block_answer_and_review_logs")

    pii_flags = detect_pii_leaks(answer)
    risk_flags.extend(pii_flags)
    if pii_flags:
        required_actions.append("redact_personal_identifiers")

    insurance_intents_need_sources = [
        "coverage_check",
        "coverage_and_evidence_check",
        "evidence_requirement_check",
        "fraud_risk_assessment",
        "human_review_decision",
        "claim_or_policy_summary",
        "compliance_check",
        "general_insurance_question"
    ]

    if domain == "insurance_operations" and intent in insurance_intents_need_sources and source_count == 0:
        risk_flags.append("no_sources_for_insurance_answer")
        required_actions.append("return_needs_review_due_to_missing_sources")

    if contains_pattern(answer, OVERCONFIDENT_DECISION_PATTERNS):
        risk_flags.append("overconfident_claim_decision_language")
        required_actions.append("downgrade_to_decision_support_language")

    human_review_required = has_human_review_required(tool_calls, reflection)

    if human_review_required and "human review" not in answer.lower():
        risk_flags.append("human_review_required_not_clearly_stated")
        required_actions.append("state_human_review_required")
        safe_answer = safe_answer + "\n\nHuman review is required before this can be treated as a final claim decision."

    if source_count > 0:
        missing_all_source_mentions = True
        for source_id in source_ids:
            if source_id in answer:
                missing_all_source_mentions = False
                break
        if missing_all_source_mentions:
            risk_flags.append("source_chunks_not_mentioned_in_answer")
            required_actions.append("include_source_chunk_references")

    allowed_to_return = True
    final_status = "approved"

    if blocked_reasons:
        allowed_to_return = False
        final_status = "blocked"
        safe_answer = "The generated answer was blocked by output guardrails because it may contain unsafe or sensitive content. Human review is required."
    elif human_review_required or risk_flags:
        final_status = "needs_review"

    if final_status == "approved" and not reflection.get("approved", False):
        final_status = "needs_review"
        risk_flags.append("reflection_not_approved")

    summary = f"Output guardrail completed. Final status: {final_status}. Risk flags: {len(risk_flags)}."

    return {
        "allowed_to_return": allowed_to_return,
        "final_status": final_status,
        "risk_flags": sorted(list(set(risk_flags))),
        "blocked_reasons": blocked_reasons,
        "required_actions": sorted(list(set(required_actions))),
        "safe_answer": safe_answer,
        "summary": summary,
        "metadata": {
            "source_count": source_count,
            "tool_call_count": len(tool_calls),
            "domain": domain,
            "intent": intent,
            "reflection_approved": reflection.get("approved", False),
            "human_review_required": human_review_required
        }
    }
