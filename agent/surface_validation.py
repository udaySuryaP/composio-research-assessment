"""Fail-closed surface contracts. Exact quotes are necessary, never proof of truth.

Contracts supplement the existing field schema; token exchange, MCP and UI login
must not be flattened into resource authentication. No product facts live here.
"""
import re
from agent.schema import obj, array, text, enum, CLAIM_FIELDS

SCHEMA = array(obj({
    'field': enum(*CLAIM_FIELDS), 'label': text(), 'surface': text(),
    'context': enum('resource_api', 'token_exchange', 'mcp', 'web_login',
                    'developer_onboarding', 'api_reference', 'product', 'unknown'),
    'passage_id': text(), 'quote': text(),
    'prerequisites': array(text()), 'coverage_complete': {'type': 'boolean'},
}))

PROMPT = '''
Additional mandatory per-surface contract:
Assess ONE named primary resource API surface. Keep that exact surface name in
all auth/access/API/buildability contracts; do not merge adjacent products.
Provide surface_support for every promoted critical field, one entry per auth or
protocol label (label must equal the findings label), otherwise label equals the
entire finding. Quote an exact contiguous BODY passage of 40-650 characters from
its passage_id, containing both the fact AND its API/surface context. Navigation,
footer keywords, generic plans and unrelated examples are insufficient.
context resource_api means RESOURCE authentication, never OAuth token exchange,
SSO, admin UI login, MCP auth or deprecated credentials. Name PAT/bot credentials
as bearer_token, not api_key; other requires a named mechanism in the quote.
Access contracts must show API/developer credential ELIGIBILITY: permissions are
not approval, paid features are not paid credential issuance. Public-app review,
partner approval, admin permission, sales gates and basic eligibility must be
separate prerequisites, not inferred from each other. Withhold flattened access
if a single canonical label misrepresents the named surface.
API type/breadth contracts require api_reference context and body evidence, not
navigation or a single endpoint generalized to all resources. Breadth explicitly
says inspected scope and lists only evidenced resources/actions.
For buildability contracts list every documented prerequisite (account, auth,
permissions, deployment/permalinks, plan/credit/rate limits, production/public-app
review, etc.). coverage_complete is true only if the retained docs establish all
requirements for this named surface. Missing requirements => unknown, never a
confident positive. Rationale must name the surface and every prerequisite.
MCP contracts use context mcp, explicit vendor implementation/ownership evidence,
and notes preserve preview, publisher, transport/client/session and gates.
Unknown fields need no contract. Do not invent a contract to satisfy validation.
'''

AUTH = {
    'oauth2': r'oauth(?:\s*2(?:\.0)?)?', 'api_key': r'api[ _-]?keys?',
    'basic': r'\bbasic\b', 'bearer_token': r'bearer|personal access token|bot token',
    'digest': r'\bdigest\b', 'service_account': r'service account',
    'none': r'no authentication|unauthenticated', 'other': r'authentication|authenticate',
}
ACCESS = {
    'self_serve_free': r'free|no cost|without charge', 'self_serve_trial': r'trial',
    'self_serve_paid': r'paid|subscription|purchase',
    'admin_approval': r'(?:admin(?:istrator)?|super admin).{0,90}(?:approv|generat|creat.*key)',
    'partner_gated': r'partner.{0,90}(?:approv|apply|application|access)',
    'sales_gated': r'contact sales|sales team',
}
PROTOCOL = {'rest': r'\bREST(?:ful)?\b', 'graphql': r'\bGraphQL\b',
            'soap': r'\bSOAP\b', 'grpc': r'\bgRPC\b', 'sdk': r'\bSDK\b'}
CRITICAL = {'auth_methods', 'access_model', 'api_available', 'api_types',
            'api_breadth', 'mcp_available', 'mcp_notes', 'buildability', 'buildability_rationale'}

def check(field, value, extracted, spans):
    if 'atomic_contract' in extracted:
        from agent.atomic_contracts import check as atomic_check
        return atomic_check(field,value,extracted,spans)
    if field not in CRITICAL:
        return None
    entries = [e for e in extracted.get('surface_support', []) if e['field'] == field]
    labels = value if isinstance(value, list) else [value]
    if sorted(e['label'] for e in entries) != sorted(labels):
        return 'Per-surface contract missing, duplicated, or does not cover the complete finding.'
    support_ids = {p for s in extracted['support'] if s['field'] == field for p in s['passage_ids']}
    contexts = {
        'auth_methods': {'resource_api'}, 'access_model': {'developer_onboarding', 'resource_api'},
        'api_available': {'api_reference', 'resource_api'}, 'api_types': {'api_reference'},
        'api_breadth': {'api_reference'}, 'mcp_available': {'mcp'}, 'mcp_notes': {'mcp'},
        'buildability': {'developer_onboarding', 'api_reference'},
        'buildability_rationale': {'developer_onboarding', 'api_reference'},
    }
    for e in entries:
        span = spans.get(e['passage_id'], {})
        q = e['quote']; surface = e['surface'].strip()
        if (e['passage_id'] not in support_ids or not 40 <= len(q) <= 650
                or q not in span.get('text', '') or not surface or surface == 'unknown'):
            return 'Surface contract lacks an exact bounded body quote in the field citation.'
        if e['context'] not in contexts[field]:
            return 'Evidence belongs to a different surface context (login/token exchange/MCP/adjacent product).'
        if field not in ('mcp_available', 'mcp_notes') and span.get('source_kind') != 'official':
            return 'Critical resource claim requires official developer evidence.'
        if field not in ('mcp_available', 'mcp_notes') and not re.search(r'\bAPI\b|developer|REST|GraphQL', q, re.I):
            return 'Body quote does not establish developer/API context.'
        if field == 'auth_methods':
            if not re.search(AUTH.get(e['label'], r'(?!)'), q, re.I):
                return 'Resource auth label not explicitly established by its own body quote.'
            if re.search(r'MCP|model context protocol|SSO|single sign.on|Sunshine Conversations', q+' '+span.get('url',''), re.I):
                return 'Auth evidence contains a distinct MCP/login/adjacent-product surface; regenerate isolated resource evidence.'
            if e['label'] == 'basic' and re.search(r'token endpoint|token exchange|client_secret|client secret|access token', q, re.I):
                return 'Basic OAuth client/token-exchange authentication is not resource API Basic auth.'
            if e['label'] == 'api_key' and re.search(r'personal access token|replac|deprecat|no longer', q, re.I):
                return 'PAT or retired API-key evidence cannot establish current API-key authentication.'
        if field == 'access_model':
            if not re.search(ACCESS.get(value, r'(?!)'), q, re.I | re.S):
                return 'Named API credential eligibility gate is not explicit in the bounded body quote.'
            if not re.search(r'credentials?|API.{0,60}(?:access|key|token|plan)|developer.{0,60}(?:account|access)|(?:key|token).{0,60}(?:creat|generat)', q, re.I | re.S):
                return 'Generic plan/permissions text does not establish developer credential eligibility.'
            if re.search(r'Copilot|SSO|single sign.on', q, re.I):
                return 'Access evidence concerns unrelated paid/login features.'
            if value == 'admin_approval' and not re.search(r'approv|generat|creat.{0,30}key', q, re.I):
                return 'Admin permissions do not by themselves establish admin credential approval.'
        if field == 'api_types':
            if value == ['other'] or e['label'] == 'other' or not re.search(PROTOCOL.get(e['label'], r'(?!)'), q, re.I):
                return 'API protocol lacks a named explicit developer reference; MCP is not an API type.'
        if field == 'api_breadth':
            if 'inspected' not in value.lower() or re.search(r'\bevery\b|\ball\b|comprehensive|extensive|and more', value, re.I):
                return 'Breadth must be bounded to inspected resources/actions, without exhaustive generalization.'
        if field in ('mcp_available', 'mcp_notes'):
            if not re.search(r'\bMCP\b|model context protocol', q, re.I):
                return 'MCP body evidence must explicitly establish an implementation.'
            if field == 'mcp_available' and value in ('official', 'both'):
                if span.get('source_kind') != 'official' or not re.search(r'server|connector|remote', q, re.I):
                    return 'Official MCP requires a vendor-owned implementation, not a product/API mention.'
                if re.search(r'w7s|third.party|community.built|unofficial', q, re.I):
                    return 'Third-party publisher text cannot establish official MCP ownership.'
            if field == 'mcp_notes' and re.search(r'preview', q, re.I) and 'preview' not in value.lower():
                return 'MCP notes omit the documented preview limitation.'
    if field not in ('mcp_available', 'mcp_notes'):
        surfaces = {e['surface'] for e in extracted.get('surface_support', [])
                    if e['field'] in ('auth_methods', 'access_model', 'api_available', 'api_types', 'api_breadth')}
        if len(surfaces) != 1:
            return 'Resource/API/access contracts do not identify one consistent integration surface.'
    return None

def buildability_reason(extracted, findings):
    if 'atomic_contract' in extracted:
        if findings['buildability'] not in ('buildable','conditional'): return None
        from agent.atomic_contracts import prerequisite_reason
        return prerequisite_reason(extracted,findings)
    # A positive conditional verdict still needs evidenced prerequisites.
    if findings['buildability'] not in ('buildable', 'conditional'):
        return None
    if (findings['api_available'] != 'yes' or any(findings[f] in ('unknown', ['unknown'])
            for f in ('auth_methods', 'access_model', 'api_types', 'api_breadth', 'buildability_rationale', 'primary_blocker'))):
        return 'Positive buildability requires retained API, resource auth, access, type/breadth, rationale and blocker evidence.'
    entries = [e for e in extracted.get('surface_support', []) if e['field'] == 'buildability']
    if not entries or any(not e['coverage_complete'] or not e['prerequisites'] for e in entries):
        return 'Buildability prerequisite coverage is missing or incomplete for the assessed surface.'
    rationale = findings['buildability_rationale'].lower()
    surface = entries[0]['surface']
    resource_entries = [e for e in extracted.get('surface_support', []) if e['field'] in ('auth_methods','access_model','api_available','api_types','api_breadth')]
    if any(e['surface'] != surface for e in resource_entries) or surface.lower() not in rationale:
        return 'Buildability scope differs from prerequisite surface or is absent from the rationale.'
    prerequisites = {p for e in entries + resource_entries for p in e['prerequisites']}
    if any(p.lower() not in rationale for p in prerequisites):
        return 'Buildability rationale omits a documented surface prerequisite.'
    return None
