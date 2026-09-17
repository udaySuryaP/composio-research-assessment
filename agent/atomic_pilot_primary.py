"""Primary-agent judgments after individual source review; no replacement facts."""
import copy
from agent import stage02 as s, coverage_correction as c

JUDGMENTS={
    (3,'api_available'):('retain','Selected reference body explicitly says this reference implements the RESTful Pipedrive API and describes resource requests validated by an API token.'),
    (11,'api_available'):('downgrade','The selected 0:500 range contains only security/auth navigation, headings and a truncated On this page fragment. Useful authentication body follows later but is not selected evidence.'),
    (26,'description'):('retain','Official company body explicitly defines Discord as the communications platform enabling meaningful gaming connections through voice, video and text. Concise product purpose, no API assertions. Supplemental company-history prose is genuine body evidence.'),
    (33,'description'):('downgrade','Selected 0:160 range begins with migration/deprecation text and ends Build technology to g. It does not substantiate creating/managing/optimizing advertising or reaching professional audiences.'),
    (33,'auth_methods'):('retain','Each listed permission is explicitly described as member 3-legged OAuth; cited resource permission table includes Advertising API and authenticated member consent. No Basic/token-exchange or adjacent auth is promoted.'),
    (33,'api_available'):('downgrade','Selected 0:1000 range is Microsoft Learn browser/access/navigation/deprecation boilerplate. Advertising API availability is present later in the source, but not established by this selected range.'),
    (42,'api_available'):('downgrade','Selected 0:500 range is the documentation navigation/resource index, not body proof. The real introduction/requirements later in this document cannot replace the selected citation during downgrade-only review.'),
    (55,'mcp_available'):('downgrade','Selected 0:500 range is an integrations menu with an MCP title. It does not establish actual vendor implementation/ownership/availability. The source body later does, but cannot be substituted manually.'),
    (55,'mcp_notes'):('downgrade','Selected 0:1000 range reaches only the opening generic interaction sentence. It does not support the complete discover/run Actors, storage and documentation action list, nor separately establish all prerequisites/limitations.'),
    (72,'description'):('downgrade','The guide tail supports an AI-native workflow platform, but the complete trusted AI apps and embedded-agent sentence borrows navigation labels from the MCP article. Product-purpose body evidence does not support every clause.'),
    (72,'api_available'):('downgrade','Selected 0:100 range is the help-page title, Contact support and signup navigation. API existence cannot be promoted from this range as body evidence.'),
    (72,'mcp_available'):('downgrade','Selected 0:100 range begins mid-word and describes MCP-compatible tools scaffolding workspaces. It does not establish Airtable ownership and implementation/availability with complete atomic evidence.'),
    (72,'mcp_notes'):('downgrade','Selected 0:100 range does not support official publisher, open-standard implementation, secure data connection and permission-respecting behavior as a complete statement.'),
    (81,'description'):('retain','Official homepage body states financial infrastructure, accepting payments and offering financial services; selected following body reports active subscriptions managed on Stripe Billing, and the first passage explicitly supports billing and embedding payments. Concise product-purpose sentence without API/auth assertions.'),
    (81,'api_available'):('retain','Selected reference body explicitly defines the Stripe API as REST resource-oriented URLs and describes JSON responses, authentication and sandbox/live modes.'),
    (93,'api_available'):('downgrade','Selected 0:500 range is quickstart/documentation index and navigation with truncated endpoint headings. Resource API body appears later but is not selected citation evidence.'),
}

PREREQUISITE_REVIEW={
3:'API-token header requirements are explicit in authentication body; extracted paid-plan atom is not reliable credential eligibility and gate inventory omits several unknown categories. No completeness certification.',
11:'Body requires verified user and global OAuth for multi-customer apps; extracted prerequisite list only repeats credential creation and misses verification/distribution rules. Product pricing/marketplace gates cannot satisfy the resource surface.',
26:'Source documents restricted OAuth scopes/partner approval and state/CSRF requirements, plus installation-context authorization. Extracted client_id_and_secret alone does not capture these; absence-based not_required gates are unsupported.',
33:'Source establishes approved access, consent and Company Page/Ad Account roles. Extracted paid standard tier and admin assertions must not substitute permission roles or approval; inventory only lists OAuth.',
35:'Only API key/OAuth token prerequisites were proposed, with unsupported paid-plan inference and unknown roles/review gates. No reliable complete primary setup inventory.',
42:'Source explicitly requires WooCommerce 3.5+, WordPress 4.4+, and pretty permalinks; default permalinks do not work. Extractor only lists credential creation and labels it product, omitting real deployment prerequisites.',
55:'Body describes free monthly credits, signup/API-token Console workflow and REST token integration; raw paid-plan-required inference overstates extended-usage plans. Product-tagged atoms and missing other gate cannot establish primary prerequisites.',
61:'Authentication body requires token scopes/permissions with endpoint-specific constraints, and GitHub App/PAT/workflow alternatives. Only credential_creation is extracted; generic paid product pricing cannot prove required API payment.',
72:'Body requires matching PAT scope, base resource and collaborator role for write action, documents 5 requests/sec/base, and separates Enterprise-only features. Raw inventory conflates Enterprise/MCP with basic Web API and legacy keys.',
81:'Source separates key permissions and sandbox/live operation from MCP administrator/session/refund approval. No complete primary access-gate/prerequisite inventory retained; MCP approvals cannot satisfy resource API access.',
84:'No readable source, so identity, prerequisites and absence remain unresolved. No manual replacement product or data supplied.',
93:'Quickstart distinguishes OAuth limitations on transcript/summary inclusion; SDK OAuth body requires app registration. A credential-only inventory with unknown account/public-app gates is incomplete.',
}

def main():
    d=s.ROOT/'data/correction/atomic-pilot-20260917';secondary=s.read(d/'audited-results.json')
    raw=[s.read(p) for p in sorted((d/'apps').glob('*.json'))];baseline=[];decisions=[]
    for v,context in zip(raw,secondary):
        assert v['id']==context['id']
        baseline.append(copy.deepcopy(context if v['failure'] else v))
        for f,x in v.get('findings',{}).items():
            if not c.known(x):continue
            decision,reason=JUDGMENTS[v['id'],f]
            decisions.append({'id':v['id'],'app_name':v['app_name'],'field':f,'decision':decision,'reason':reason,
                'passage_ids':[e['passage_id'] for e in v['evidence'] if e['field']==f],
                'source_review':'primary_agent_individual_saved_source_review','human_checked':False})
    assert {(j['id'],j['field']) for j in decisions}==set(JUDGMENTS)
    s.save(d/'primary-audit-baseline.json',baseline,exclusive=True)
    s.save(d/'primary-audit-decisions.json',decisions,exclusive=True)
    s.save(d/'primary-prerequisite-audit.json',[{'id':v['id'],'app_name':v['app_name'],'positive_buildability':False,
        'completeness_established':False,'reason':PREREQUISITE_REVIEW[v['id']]} for v in baseline],exclusive=True)
    s.save(d/'primary-verdict.json',{'status':'PILOT FAIL','safe_to_scale':False,
        'reason':'Exact code-attached quotations recover integrity, but useful retention is only 5/132 versus 2/132 and 44/132; no access, API protocol/breadth or prerequisite-derived buildability survives. Selected fragments/navigation and wrong atom surfaces still prevent actionable integration research. This is not practically useful enough to justify scaling.'},exclusive=True)
    print('Primary audited all',len(decisions),'pipeline promotions; downgrade-only from pipeline baseline.')

if __name__=='__main__':main()
