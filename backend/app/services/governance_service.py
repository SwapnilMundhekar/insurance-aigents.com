import re
from datetime import datetime, timezone

INSURANCE_KEYWORDS = [
    "insurance",
    "policy",
    "claim",
    "claims",
    "coverage",
    "cover",
    "covered",
    "exclusion",
    "excluded",
    "excess",
    "premium",
    "insured",
    "vehicle",
    "car",
    "motor",
    "home",
    "contents",
    "windscreen",
    "storm",
    "hail",
    "theft",
    "fire",
    "damage",
    "fraud",
    "evidence",
    "repair",
    "invoice",
    "assessment",
    "liability",
    "underwriting",
    "compliance",
    "customer vulnerability",
    "human review"
]

PLATFORM_KEYWORDS = [
    "agent",
    "agentic",
    "rag",
    "retrieval",
    "tool calling",
    "tool registry",
    "supervisor",
    "reflection",
    "chunking",
    "embedding",
    "vector",
    "trace",
    "observability",
    "mcp",
    "model context protocol"
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above|system|developer)?\s*instructions",
    r"forget\s+(all\s+)?(previous|prior|above|your|system|developer)?\s*instructions",
    r"disregard\s+(all\s+)?(previous|prior|above|your|system|developer)?\s*instructions",
    r"override\s+(all\s+)?(previous|prior|above|your|system|developer)?\s*instructions",
    r"do\s+not\s+follow\s+(your|the|system|developer)?\s*instructions",
    r"stop\s+following\s+(your|the|system|developer)?\s*instructions",
    r"ignore\s+the\s+system\s+prompt",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?hidden\s+instructions",
    r"developer\s+message",
    r"system\s+message",
    r"bypass\s+(the\s+)?guardrails",
    r"disable\s+(the\s+)?safety",
    r"print\s+(all\s+)?secrets",
    r"show\s+(all\s+)?api\s+keys",
    r"exfiltrate",
    r"remote\s+shell",
    r"reverse\s+shell",
    r"delete\s+all\s+files",
    r"drop\s+database"
]

OFF_TOPIC_INJECTION_PATTERNS = [
    r"tell\s+(me\s+)?who\s+let\s+the\s+dog\s+out",
    r"write\s+(me\s+)?a\s+poem",
    r"tell\s+(me\s+)?a\s+joke",
    r"sing\s+(me\s+)?a\s+song"
]

def normalise_query(query):
    return " ".join(str(query).split()).strip()

def redact_pii(query):
    redacted = query
    redacted = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", redacted)
    redacted = re.sub(r"\b(?:\+?61|0)[\d\s\-]{8,15}\b", "[REDACTED_PHONE]", redacted)
    redacted = re.sub(r"\b(?:POL|CLAIM|CUST|REF)[-_: ]?(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,}\b", "[REDACTED_REFERENCE_ID]", redacted, flags=re.IGNORECASE)
    return redacted

def detect_pii(query):
    flags = []
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", query):
        flags.append("pii_email_detected")
    if re.search(r"\b(?:\+?61|0)[\d\s\-]{8,15}\b", query):
        flags.append("pii_phone_detected")
    if re.search(r"\b(?:POL|CLAIM|CUST|REF)[-_: ]?(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,}\b", query, flags=re.IGNORECASE):
        flags.append("pii_reference_id_detected")
    return flags

def detect_prompt_injection(query):
    lower_query = query.lower()
    flags = []
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lower_query):
            flags.append("prompt_injection_attempt")
            break
    for pattern in OFF_TOPIC_INJECTION_PATTERNS:
        if re.search(pattern, lower_query):
            flags.append("off_topic_instruction_attempt")
            break
    return flags

def classify_domain(query):
    lower_query = query.lower()
    insurance_matches = [keyword for keyword in INSURANCE_KEYWORDS if keyword in lower_query]
    platform_matches = [keyword for keyword in PLATFORM_KEYWORDS if keyword in lower_query]
    if insurance_matches:
        return "insurance_operations", insurance_matches
    if platform_matches:
        return "agentic_ai_platform", platform_matches
    return "out_of_scope", []

def classify_intent(query):
    lower_query = query.lower()
    if any(word in lower_query for word in ["covered", "cover", "coverage", "exclusion", "excluded", "policy says"]):
        if any(word in lower_query for word in ["evidence", "document", "photo", "invoice", "quote", "proof"]):
            return "coverage_and_evidence_check"
        return "coverage_check"
    if any(word in lower_query for word in ["evidence", "documents", "photo", "invoice", "quote", "proof", "required"]):
        return "evidence_requirement_check"
    if any(word in lower_query for word in ["fraud", "suspicious", "duplicate", "inconsistent", "high value", "missing evidence"]):
        return "fraud_risk_assessment"
    if any(word in lower_query for word in ["human review", "manual review", "escalate", "escalation", "needs review"]):
        return "human_review_decision"
    if any(word in lower_query for word in ["summarise", "summarize", "summary"]):
        return "claim_or_policy_summary"
    if any(word in lower_query for word in ["compliance", "code of practice", "regulation", "obligation"]):
        return "compliance_check"
    if any(word in lower_query for word in ["architecture", "agentic", "rag", "tool calling", "mcp", "supervisor", "workflow"]):
        return "platform_architecture_question"
    return "general_insurance_question"

def decompose_tasks(intent, query):
    tasks = []
    if intent in ["coverage_check", "coverage_and_evidence_check"]:
        tasks.append("check relevant policy coverage and exclusions")
    if intent in ["evidence_requirement_check", "coverage_and_evidence_check"]:
        tasks.append("identify likely evidence required for claim assessment")
    if intent == "fraud_risk_assessment" or any(word in query.lower() for word in ["fraud", "suspicious", "duplicate", "inconsistent", "missing evidence"]):
        tasks.append("check fraud risk indicators")
    if intent in ["human_review_decision", "fraud_risk_assessment", "coverage_and_evidence_check"]:
        tasks.append("decide whether human review is required")
    if intent == "claim_or_policy_summary":
        tasks.append("summarise the relevant claim or policy content")
    if intent == "compliance_check":
        tasks.append("check compliance or code of practice obligations")
    if intent == "platform_architecture_question":
        tasks.append("explain the relevant agentic AI platform architecture concept")
    if not tasks:
        tasks.append("retrieve relevant insurance context and generate a grounded answer")
    return tasks

def decide_allowed_tools(intent, risk_flags):
    blocking_flags = ["prompt_injection_attempt", "off_topic_instruction_attempt"]
    if any(flag in risk_flags for flag in blocking_flags):
        return []
    tool_map = {
        "coverage_check": ["coverage_check_tool", "human_review_tool"],
        "coverage_and_evidence_check": ["coverage_check_tool", "evidence_check_tool", "fraud_signal_tool", "human_review_tool"],
        "evidence_requirement_check": ["evidence_check_tool", "human_review_tool"],
        "fraud_risk_assessment": ["fraud_signal_tool", "human_review_tool"],
        "human_review_decision": ["coverage_check_tool", "fraud_signal_tool", "human_review_tool"],
        "claim_or_policy_summary": ["human_review_tool"],
        "compliance_check": ["human_review_tool"],
        "general_insurance_question": ["coverage_check_tool", "evidence_check_tool", "human_review_tool"]
    }
    return tool_map.get(intent, [])

def decide_route(domain, intent, risk_flags):
    blocked_reasons = []
    if "prompt_injection_attempt" in risk_flags:
        blocked_reasons.append("Prompt injection attempt detected.")
    if "off_topic_instruction_attempt" in risk_flags:
        blocked_reasons.append("Prompt contains an off-topic instruction mixed into the business request.")
    if domain == "out_of_scope":
        blocked_reasons.append("Prompt is outside the supported insurance and agentic platform domain.")
    if blocked_reasons:
        return False, "blocked", blocked_reasons
    if intent == "platform_architecture_question":
        return True, "platform_explanation", []
    return True, "agentic_rag_with_tools", []

def analyze_prompt(query):
    normalised = normalise_query(query)
    redacted_query = redact_pii(normalised)
    risk_flags = []
    risk_flags.extend(detect_pii(normalised))
    risk_flags.extend(detect_prompt_injection(normalised))
    domain, domain_matches = classify_domain(normalised)
    intent = classify_intent(normalised)
    decomposed_tasks = decompose_tasks(intent, normalised)
    allowed_tool_names = decide_allowed_tools(intent, risk_flags)
    allowed, route_to, blocked_reasons = decide_route(domain, intent, risk_flags)
    requires_human_review = False
    if any(flag in risk_flags for flag in ["pii_email_detected", "pii_phone_detected", "pii_reference_id_detected"]):
        requires_human_review = True
    if intent in ["fraud_risk_assessment", "human_review_decision", "compliance_check"]:
        requires_human_review = True
    if not allowed:
        requires_human_review = False
    if allowed:
        governance_summary = f"Prompt allowed. Domain: {domain}. Intent: {intent}. Route: {route_to}."
    else:
        governance_summary = "Prompt blocked before agent execution."
    return {
        "allowed": allowed,
        "route_to": route_to,
        "domain": domain,
        "intent": intent,
        "risk_flags": risk_flags,
        "blocked_reasons": blocked_reasons,
        "decomposed_tasks": decomposed_tasks,
        "allowed_tool_names": allowed_tool_names,
        "requires_human_review": requires_human_review,
        "original_character_count": len(normalised),
        "redacted_query": redacted_query,
        "governance_summary": governance_summary,
        "metadata": {
            "domain_matches": domain_matches,
            "analysed_at_utc": datetime.now(timezone.utc).isoformat(),
            "governance_version": "part_9_1_rule_based_v2"
        }
    }
# IA_FRAUD_FILING_GUARDRAIL_V1
# This wrapper blocks prompts that appear to ask for fraudulent or false insurance filing help.
_original_analyze_prompt_before_fraud_filing_guardrail = analyze_prompt

def _detect_fraud_filing_or_false_claim_prompt(query):
    import re
    text = str(query or '').lower().strip()
    text = re.sub(r'\s+', ' ', text)

    dangerous_patterns = [
        r'\bcan\s+i\s+file\s+fraud\s+insurance\b',
        r'\bfile\s+(a\s+)?fraud\s+insurance\b',
        r'\bfile\s+(a\s+)?fraudulent\s+claim\b',
        r'\bsubmit\s+(a\s+)?fraudulent\s+claim\b',
        r'\bmake\s+(a\s+)?fake\s+claim\b',
        r'\bsubmit\s+(a\s+)?fake\s+claim\b',
        r'\bcreate\s+fake\s+evidence\b',
        r'\bfake\s+insurance\s+claim\b',
        r'\bfalse\s+insurance\s+claim\b',
        r'\blie\s+to\s+(the\s+)?insurer\b',
        r'\bstage\s+(an\s+)?accident\b',
        r'\bclaim\s+for\s+damage\s+that\s+did\s+not\s+happen\b'
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, text):
            return True

    if 'fraud insurance' in text and any(word in text for word in ['file', 'submit', 'claim', 'today', 'can i']):
        return True

    return False

def analyze_prompt(query):
    if _detect_fraud_filing_or_false_claim_prompt(query):
        from datetime import datetime, timezone
        original_query = str(query or '')
        return {
            'allowed': False,
            'route_to': 'blocked',
            'domain': 'insurance_operations',
            'intent': 'illicit_or_ambiguous_fraud_filing_request',
            'risk_flags': [
                'fraudulent_claim_or_false_filing_attempt',
                'insurance_misuse_safety_risk'
            ],
            'blocked_reasons': [
                'The prompt appears to ask for help filing a fraudulent, false, or unclear fraud-related insurance claim.'
            ],
            'decomposed_tasks': [],
            'allowed_tool_names': [],
            'requires_human_review': True,
            'original_character_count': len(original_query),
            'redacted_query': original_query,
            'governance_summary': 'Blocked. The request appears to involve fraudulent or false insurance filing. The system can help with legitimate claims or reporting suspected fraud, but not filing fraud.',
            'metadata': {
                'analysed_at_utc': datetime.now(timezone.utc).isoformat(),
                'governance_version': 'fraud_filing_guardrail_v1',
                'safe_alternative': 'Ask about filing a legitimate claim, reporting suspected fraud, or checking fraud indicators for a real claim scenario.'
            }
        }

    return _original_analyze_prompt_before_fraud_filing_guardrail(query)

# IA_FAIL_CLOSED_PREROUTER_V2
from app.services.governance_prerouter_service import pre_route_prompt

_original_analyze_prompt_before_fail_closed_prerouter = analyze_prompt

def analyze_prompt(query):
    pre_route_decision = pre_route_prompt(query)
    if pre_route_decision is not None:
        return pre_route_decision
    return _original_analyze_prompt_before_fail_closed_prerouter(query)
