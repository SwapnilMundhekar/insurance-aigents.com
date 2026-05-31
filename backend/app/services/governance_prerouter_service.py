import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = PROJECT_ROOT / 'data' / 'indexes'
VERSION = 'policy_scope_gate_v1'

MOTOR_TERMS = [
    'motor', 'vehicle', 'car', 'auto', 'windscreen', 'tyre', 'bumper',
    'comprehensive motor', 'driver', 'driving', 'hail damage to car'
]

HOME_TERMS = [
    'home', 'house', 'building', 'property', 'contents', 'roof',
    'window', 'glass door', 'wall', 'ceiling', 'kitchen', 'bathroom',
    'garage', 'fence', 'burst pipe', 'water damage'
]

TRAVEL_TERMS = [
    'travel', 'trip', 'flight', 'luggage', 'baggage', 'passport',
    'overseas', 'hotel', 'cancelled trip'
]

TOPIC_TERMS = [
    'insurance', 'policy', 'claim', 'claims', 'coverage', 'covered',
    'evidence', 'exclusion', 'exclusions', 'fraud', 'fraudulent',
    'review', 'triage', 'windscreen', 'damage'
]

SCENARIO_TERMS = [
    'customer', 'insured', 'vehicle', 'car', 'home', 'house', 'property',
    'building', 'contents', 'windscreen', 'window', 'storm', 'hail',
    'fire', 'theft', 'damage', 'accident', 'incident', 'photos',
    'photo', 'invoice', 'quote', 'police', 'duplicate', 'inconsistent',
    'missing', 'description', 'lodged', 'reported', 'claimant',
    'repair', 'replacement'
]

QUESTION_TERMS = [
    'is', 'are', 'was', 'were', 'does', 'do', 'did', 'can', 'could',
    'should', 'what', 'when', 'why', 'how', 'covered', 'cover',
    'required', 'require', 'needed', 'need', 'check', 'checked',
    'apply', 'applies', 'assess', 'assessment', 'escalate'
]

FRAUD_TERMS = [
    'fraud', 'fraudulent', 'fake claim', 'false claim',
    'false insurance claim', 'insurance scam', 'fake evidence',
    'stage accident', 'staged accident', 'lie to insurer',
    'mislead insurer'
]

DANGEROUS_FRAUD_ACTION_TERMS = [
    'file', 'submit', 'upload', 'lodge', 'make', 'create',
    'need', 'want', 'can i', 'how do i', 'today', 'now'
]

SAFE_FRAUD_ASSESSMENT_TERMS = [
    'report suspected fraud', 'report fraud', 'suspected fraud',
    'fraud indicators', 'fraud signals', 'what fraud indicators',
    'identify fraud', 'check fraud', 'detect fraud', 'duplicate claim',
    'duplicate', 'inconsistent', 'photos do not match',
    'photo does not match', 'missing evidence', 'human review',
    'manual review', 'risk indicators'
]

def normalise_text(query):
    text = str(query or '').lower().strip()
    text = re.sub(r'[^a-z0-9? ]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def has_any(text, terms):
    return any(term in text for term in terms)

def word_count(text):
    return len([word for word in text.split(' ') if word])

def detect_policy_scope(text):
    has_motor = has_any(text, MOTOR_TERMS)
    has_home = has_any(text, HOME_TERMS)
    has_travel = has_any(text, TRAVEL_TERMS)

    if has_home and has_motor:
        return 'mixed_or_conflicting'
    if has_motor:
        return 'motor'
    if has_home:
        return 'home'
    if has_travel:
        return 'travel'
    return 'unknown'

def detect_indexed_policy_scopes():
    scopes = set()
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(INDEX_DIR.glob('*_chunks.json'), key=lambda path: path.stat().st_mtime, reverse=True)

    for file_path in files:
        try:
            chunks = json.loads(file_path.read_text(encoding='utf-8'))
        except Exception:
            chunks = []

        joined_text_parts = []
        for chunk in chunks[:8]:
            joined_text_parts.append(str(chunk.get('source_filename', '')))
            joined_text_parts.append(str(chunk.get('text', ''))[:2500])

        joined = normalise_text(' '.join(joined_text_parts))

        if has_any(joined, ['comprehensive motor', 'motor insurance', 'vehicle', 'windscreen']):
            scopes.add('motor')
        if has_any(joined, ['home insurance', 'building insurance', 'contents insurance', 'house', 'roof', 'window']):
            scopes.add('home')
        if has_any(joined, ['travel insurance', 'trip cancellation', 'luggage', 'baggage']):
            scopes.add('travel')

    return sorted(list(scopes))

def has_scenario_context(text):
    return has_any(text, SCENARIO_TERMS)

def has_question_or_task(text):
    words = set(text.replace('?', '').split())
    return any(term in words or term in text for term in QUESTION_TERMS)

def is_fragment_or_incomplete(text):
    clean = text.strip().replace('?', '')
    words = clean.split()

    if not clean:
        return True

    exact_fragments = [
        'insurance', 'policy', 'claim', 'coverage', 'covered',
        'fraud', 'fraud insurance', 'fraud indicators', 'fraud indicator',
        'fraud signals', 'windscreen', 'is windscreen',
        'is windscreen covered', 'evidence', 'exclusions', 'human review',
        'what is covered', 'what is covered under insurance'
    ]

    if clean in exact_fragments:
        return True

    if len(words) <= 4 and has_any(clean, TOPIC_TERMS):
        return True

    if clean.startswith('is ') and len(words) <= 6:
        return True

    if clean.startswith('can i ') and len(words) <= 7 and not has_scenario_context(clean):
        return True

    return False

def has_enough_context_for_agentic_rag(text):
    if word_count(text) < 7:
        return False
    if not has_scenario_context(text):
        return False
    if not has_question_or_task(text):
        return False
    return True

def is_fraud_filing_or_false_claim_request(text):
    explicit_patterns = [
        r'\bcan i file fraud insurance\b',
        r'\bi need a fraud upload\b',
        r'\bfraud upload\b',
        r'\bfile fraud insurance\b',
        r'\bsubmit fraud insurance\b',
        r'\bupload fraud insurance\b',
        r'\bfile a fraudulent claim\b',
        r'\bsubmit a fraudulent claim\b',
        r'\bmake a fake claim\b',
        r'\bsubmit a fake claim\b',
        r'\bcreate fake evidence\b',
        r'\bfake insurance claim\b',
        r'\bfalse insurance claim\b',
        r'\blie to insurer\b',
        r'\bstage an accident\b'
    ]

    for pattern in explicit_patterns:
        if re.search(pattern, text):
            return True

    has_fraud_language = has_any(text, FRAUD_TERMS)
    has_dangerous_action = has_any(text, DANGEROUS_FRAUD_ACTION_TERMS)
    has_safe_assessment_context = has_any(text, SAFE_FRAUD_ASSESSMENT_TERMS) and has_scenario_context(text)

    if has_fraud_language and has_dangerous_action and not has_safe_assessment_context:
        return True

    return False

def clarification_response(original_query, reason, suggested_message=None, extra_metadata=None):
    metadata = {
        'analysed_at_utc': datetime.now(timezone.utc).isoformat(),
        'governance_version': VERSION,
        'reason': reason,
        'suggested_message': suggested_message or 'Please describe the actual claim scenario. Example: The customer has windscreen damage after a storm. Is it covered and what evidence is required?',
        'required_context': [
            'policy type',
            'incident description',
            'damage or loss type',
            'available evidence',
            'risk indicators if relevant'
        ]
    }

    if extra_metadata:
        metadata.update(extra_metadata)

    return {
        'allowed': False,
        'route_to': 'clarification_required',
        'domain': 'insurance_operations',
        'intent': 'clarification_required',
        'risk_flags': ['insufficient_or_mismatched_claim_context'],
        'blocked_reasons': [],
        'decomposed_tasks': [],
        'allowed_tool_names': [],
        'requires_human_review': False,
        'original_character_count': len(str(original_query or '')),
        'redacted_query': str(original_query or ''),
        'governance_summary': metadata['suggested_message'],
        'metadata': metadata
    }

def no_matching_policy_document_response(original_query, requested_scope, indexed_scopes):
    indexed_text = ', '.join(indexed_scopes) if indexed_scopes else 'none'
    message = 'I cannot answer this from the indexed policy documents because the question appears to be about ' + requested_scope + ' insurance, but the currently indexed policy scope is: ' + indexed_text + '. Upload or ingest the matching policy document first, or ask about the indexed policy type.'
    return clarification_response(
        original_query,
        'no_matching_policy_document',
        suggested_message=message,
        extra_metadata={
            'requested_policy_scope': requested_scope,
            'indexed_policy_scopes': indexed_scopes
        }
    )

def fraud_block_response(original_query):
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
            'The prompt appears to ask for help filing, submitting, uploading, creating, or enabling a fraudulent, false, or misleading insurance claim.'
        ],
        'decomposed_tasks': [],
        'allowed_tool_names': [],
        'requires_human_review': True,
        'original_character_count': len(str(original_query or '')),
        'redacted_query': str(original_query or ''),
        'governance_summary': 'I cannot help with filing, submitting, uploading, creating, or enabling a fraudulent, false, or misleading insurance claim. I can help with filing a legitimate claim, reporting suspected fraud, or checking fraud indicators for a real claim scenario.',
        'metadata': {
            'analysed_at_utc': datetime.now(timezone.utc).isoformat(),
            'governance_version': VERSION
        }
    }

def pre_route_prompt(query):
    text = normalise_text(query)

    if is_fraud_filing_or_false_claim_request(text):
        return fraud_block_response(query)

    requested_scope = detect_policy_scope(text)

    if requested_scope == 'mixed_or_conflicting':
        if 'home' in text and 'windscreen' in text:
            return clarification_response(
                query,
                'policy_asset_mismatch_home_windscreen',
                suggested_message='I need clarification before checking coverage. Windscreen usually relates to a motor vehicle policy, while home insurance usually refers to windows, fixed glass, building, or contents. Do you mean vehicle windscreen damage under motor insurance, or window or glass damage under home insurance?'
            )
        return clarification_response(
            query,
            'mixed_policy_scope',
            suggested_message='I found mixed policy signals in your question. Please confirm the policy type first: motor, home, travel, or another policy.'
        )

    if is_fragment_or_incomplete(text):
        return clarification_response(query, 'topic_only_fragment_or_insufficient_context')

    if has_any(text, TOPIC_TERMS) and not has_enough_context_for_agentic_rag(text):
        return clarification_response(query, 'insufficient_context_for_grounded_retrieval')

    indexed_scopes = detect_indexed_policy_scopes()

    if requested_scope in ['home', 'travel'] and indexed_scopes and requested_scope not in indexed_scopes:
        return no_matching_policy_document_response(query, requested_scope, indexed_scopes)

    return None
