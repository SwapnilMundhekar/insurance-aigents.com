def coverage_check_tool(tool_input):
    query = str(tool_input.get("query", "")).lower()

    covered_keywords = [
        "windscreen",
        "accidental damage",
        "theft",
        "fire",
        "storm",
        "hail",
        "malicious damage"
    ]

    exclusion_keywords = [
        "intentional",
        "commercial use",
        "mechanical failure",
        "wear and tear",
        "influence"
    ]

    matched_coverage = [keyword for keyword in covered_keywords if keyword in query]
    matched_exclusions = [keyword for keyword in exclusion_keywords if keyword in query]

    if matched_exclusions:
        status = "potentially_excluded"
    elif matched_coverage:
        status = "potentially_covered"
    else:
        status = "unknown_from_tool_rules"

    return {
        "coverage_status": status,
        "matched_coverage_keywords": matched_coverage,
        "matched_exclusion_keywords": matched_exclusions,
        "tool_reasoning": "This rule based tool checks claim wording against known sample coverage and exclusion indicators."
    }

def evidence_check_tool(tool_input):
    query = str(tool_input.get("query", "")).lower()

    required_evidence = [
        "incident description",
        "photographs of damage",
        "repair invoice or quote",
        "proof of ownership",
        "policy number"
    ]

    if "theft" in query:
        required_evidence.append("police report")

    if "windscreen" in query:
        required_evidence.append("windscreen repair or replacement quote")

    if "storm" in query or "hail" in query:
        required_evidence.append("date and location of weather event")

    return {
        "required_evidence": required_evidence,
        "tool_reasoning": "This tool maps claim type indicators to likely evidence required for assessment."
    }

def fraud_signal_tool(tool_input):
    query = str(tool_input.get("query", "")).lower()

    fraud_signals = []

    if "duplicate" in query:
        fraud_signals.append("duplicate claim indicator")

    if "missing evidence" in query:
        fraud_signals.append("missing evidence indicator")

    if "inconsistent" in query:
        fraud_signals.append("inconsistent description indicator")

    if "high value" in query:
        fraud_signals.append("high value claim indicator")

    risk_score = min(len(fraud_signals) * 25, 100)

    if risk_score >= 50:
        risk_level = "high"
    elif risk_score >= 25:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "fraud_risk_level": risk_level,
        "fraud_risk_score": risk_score,
        "fraud_signals": fraud_signals,
        "tool_reasoning": "This rule based tool detects simple fraud indicators from claim wording."
    }

def human_review_tool(tool_input):
    coverage_status = str(tool_input.get("coverage_status", "unknown"))
    fraud_risk_level = str(tool_input.get("fraud_risk_level", "low"))
    missing_evidence_count = int(tool_input.get("missing_evidence_count", 0))

    reasons = []

    if coverage_status in ["potentially_excluded", "unknown_from_tool_rules"]:
        reasons.append("coverage is excluded or unclear")

    if fraud_risk_level in ["medium", "high"]:
        reasons.append("fraud risk is not low")

    if missing_evidence_count > 0:
        reasons.append("required evidence may be missing")

    should_escalate = len(reasons) > 0

    return {
        "human_review_required": should_escalate,
        "reasons": reasons,
        "tool_reasoning": "This tool applies simple governance rules to decide whether human review is needed."
    }