# Output Guardrails

Output guardrails validate the final answer before it is returned to the user.

## Why output guardrails are required

Input guardrails protect the system before the agent runs. Output guardrails protect the user and the organisation after the answer is generated.

## Checks performed

- local path leakage
- secret-like text leakage
- Personally Identifiable Information leakage
- unsupported insurance decision wording
- missing source evidence
- missing human review escalation
- reflection approval status

## Status outcomes

| Status | Meaning |
|---|---|
| approved | Answer passed output validation |
| needs_review | Answer can be shown but requires human review |
| blocked | Answer is blocked because unsafe or sensitive content may be present |

## Agentic RAG integration

The Agentic RAG workflow now includes an `OutputGuardrailAgent` step before the response is returned.
