"""Stage 01 strict JSON Schema contract; no research or legacy migration."""

def text():
    return {'type': 'string'}


def enum(*values):
    return {'type': 'string', 'enum': list(values)}


def array(items):
    return {'type': 'array', 'items': items}


def obj(properties):
    return {'type': 'object', 'properties': properties,
            'required': list(properties), 'additionalProperties': False}


CLAIM_FIELDS = (
    'description', 'auth_methods', 'access_model', 'api_available', 'api_types',
    'api_breadth', 'mcp_available', 'mcp_notes', 'buildability', 'primary_blocker',
    'buildability_rationale',
)
EVIDENCE_SCHEMA = obj({
    'evidence_id': text(), 'field': enum(*CLAIM_FIELDS), 'claim': text(),
    'url': text(), 'final_url': text(),
    'source_kind': enum('official', 'community', 'third_party', 'unknown'),
    'retrieved_at': text(), 'content_sha256': text(), 'quote': text(),
    'supports_claim': enum('yes', 'no', 'unclear'),
})
RESEARCH_SCHEMA = obj({
    'schema_version': enum('1.0'), 'id': {'type': 'integer'},
    'app_name': text(), 'category': text(), 'website': text(), 'description': text(),
    'auth_methods': array(enum('oauth2', 'api_key', 'basic', 'bearer_token',
                               'digest', 'service_account', 'none', 'other', 'unknown')),
    'access_model': enum('self_serve_free', 'self_serve_trial', 'self_serve_paid',
                         'admin_approval', 'partner_gated', 'sales_gated', 'unknown'),
    'api_available': enum('yes', 'no', 'unclear', 'unknown'),
    'api_types': array(enum('rest', 'graphql', 'soap', 'grpc', 'sdk', 'other', 'unknown')),
    'api_breadth': text(),
    'mcp_available': enum('official', 'community', 'both', 'no', 'unclear', 'unknown'),
    'mcp_notes': text(),
    'buildability': enum('buildable', 'conditional', 'blocked', 'unknown'),
    'primary_blocker': text(), 'buildability_rationale': text(),
    'evidence': array(EVIDENCE_SCHEMA),
    'research_confidence': enum('high', 'medium', 'low', 'unknown'),
    'verification_status': enum('first_pass', 'needs_verification', 'verified',
                                 'human_audited', 'failed'),
    'verification_notes': array(text()), 'researched_at': text(), 'run_id': text(),
})


def unknown_record(app_id, name, category, website, run_id, researched_at):
    """Blank abstaining record for contract tests or later extraction failures."""
    return {
        'schema_version': '1.0', 'id': app_id, 'app_name': name,
        'category': category, 'website': website, 'description': 'unknown',
        'auth_methods': ['unknown'], 'access_model': 'unknown',
        'api_available': 'unknown', 'api_types': ['unknown'],
        'api_breadth': 'unknown', 'mcp_available': 'unknown', 'mcp_notes': 'unknown',
        'buildability': 'unknown', 'primary_blocker': 'unknown',
        'buildability_rationale': 'Insufficient evidence.', 'evidence': [],
        'research_confidence': 'unknown', 'verification_status': 'needs_verification',
        'verification_notes': [], 'researched_at': researched_at, 'run_id': run_id,
    }
