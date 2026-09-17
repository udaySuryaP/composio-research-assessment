"""Apply primary-agent audit judgments as downgrades only, retain all model output."""
import copy
import hashlib
import json
from pathlib import Path
from agent import stage02 as s, coverage_correction as c
from agent.schema import CLAIM_FIELDS

# Audit judgments, not manually entered product findings. No replacement values.
WITHHOLD={
3:{'description':'Cited footer/company-tail passages do not support the complete SME target and sales-pipeline/customer-relationship description.'},
11:{'description':'REST assertion is smuggled into purpose while cited protocol support was rejected.',
    'auth_methods':'Mixed unknown and populated auth labels; JWT evidence concerns Sunshine Conversations and lacks per-surface scope.',
    'api_breadth':'REST and comprehensive surface assertions exceed the accepted protocol support; regenerate a bounded resource description.'},
26:{'description':'Citations establish developer API capabilities but do not directly establish the complete product-purpose sentence.',
    'auth_methods':'Basic is documented for OAuth token exchange, not standalone resource API authentication; complete list also omits distinct bot-token scope.'},
33:{'description':'Cited Advertising API overview establishes campaign APIs but not every clause of the B2B product-purpose sentence.',
    'api_breadth':'Conflates Advertising API with adjacent Marketing products having separate admission and availability gates.'},
42:{'mcp_notes':'Combines native developer-preview MCP with a separate plugin explicitly published by w7s; ownership and deprecated-endpoint differences are not separated.',
    'primary_blocker':'Store/WordPress/permalink prerequisites and unresolved credential access make unqualified none documented unsuitable.'},
55:{'auth_methods':'OAuth evidence cited from MCP onboarding does not establish OAuth for the platform REST resource API; auth list needs per-surface scope.',
    'buildability':'Unconditional verdict inherits unresolved resource-auth scope and omits credit/Actor and account prerequisites.',
    'primary_blocker':'Unbounded no-blocker finding omits free-plan credits and Actor restrictions.',
    'buildability_rationale':'Straightforward integration inference lacks a separately accepted scoped resource-auth finding.'},
61:{'description':'Exceeds 180-character purpose limit and describes API/MCP surfaces rather than a concise product purpose.',
    'auth_methods':'Conflates personal-access tokens with API keys and OAuth client authentication with resource API Basic auth.',
    'access_model':'Generic paid plans/Copilot references do not establish that API credentials require a paid subscription.',
    'api_types':'Other label conflates MCP with API protocol classification and is not a named independently supported surface.',
    'buildability':'Resource-auth and credential eligibility do not survive strict audit; no unconditional buildable verdict.',
    'primary_blocker':'Unbounded none documented omits token permissions, policies and account prerequisites.',
    'buildability_rationale':'Inference relies on withheld resource-auth and access eligibility.'},
72:{'description':'Exceeds 180-character purpose limit.',
    'auth_methods':'Legacy API keys are replaced by PATs; other is unspecified; list lacks current per-surface credential scope.',
    'api_breadth':'CRUD across every listed resource is not established; Web API, Enterprise APIs and MCP capabilities have different scopes/gates.',
    'buildability':'Unconditional verdict relies on withheld auth and conflates basic API access with Enterprise surface eligibility.',
    'primary_blocker':'None documented fails to disclose explicit permission, plan and call-limit constraints.',
    'buildability_rationale':'Unbounded no-blocker statement and general access model do not support all claimed Enterprise/MCP surfaces.'},
81:{'description':'Broad payments/billing/financial-management/marketplace purpose lacks direct supporting body text in cited navigation-heavy passages.',
    'auth_methods':'API keys and OAuth for Stripe Apps/MCP need explicit per-surface scope; do not flatten into one resource-auth list.',
    'api_breadth':'Extensive and more lacks an inspected-scope boundary; resource navigation is not exhaustive breadth evidence.',
    'mcp_notes':'Official public-preview status is omitted; regenerate notes preserving preview and client/session prerequisites.'},
93:{'description':'Managing meeting data and OAuth support are not scoped to the specific documented read/resource and token-exchange surfaces.',
    'auth_methods':'Combines REST API keys, SDK bearer scheme and OAuth token endpoint without separately scoped resource support.',
    'api_breadth':'Resource names are documented but complete pagination/filtering/transcript claim requires more precise cited examples.',
    'primary_blocker':'No-blocker conclusion ignores explicit account permissions and rate limits while access remains unresolved.'}}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    directory=s.ROOT/'data/correction/strict-pilot-20260917'
    values=s.read(directory/'audited-results.json');final=[];judgments=[];quality=[]
    output=directory/'primary-audit-v2'
    for original in values:
        v=copy.deepcopy(original)
        if v['failure']:
            v['findings']={f:['unknown'] if f in ('auth_methods','api_types') else 'unknown' for f in CLAIM_FIELDS}
        for f in CLAIM_FIELDS:
            if not c.known(v['findings'][f]):continue
            reason=WITHHOLD.get(v['id'],{}).get(f)
            judgments.append({'id':v['id'],'app_name':v['app_name'],'field':f,
                'original_value':v['findings'][f],'decision':'unresolved' if reason else 'retain_source_supported',
                'reason':reason or 'Primary-agent source audit retains this bounded claim and its traceable official-source passages.',
                'review_kind':'primary_agent_audit','independent_human_review':False})
            if reason:
                v['findings'][f]=['unknown'] if f in ('auth_methods','api_types') else 'unknown'
                v['field_status'][f]={'status':'unresolved','human_checked':False,'reason':reason}
        v['evidence']=[e for e in v['evidence'] if c.known(v['findings'][e['field']])]
        v['research_status']='retrieval_failure' if v['failure'] else 'partially_source_supported'
        # Provider/ownership derived only from retained vendor-owned MCP finding.
        v['mcp_provider']=v['app_name'] if v['findings']['mcp_available']=='official' else 'unknown'
        v['mcp_ownership']='vendor_official' if v['findings']['mcp_available']=='official' else 'unresolved'
        v['mcp_provider_evidence']=[e for e in v['evidence'] if e['field']=='mcp_available']
        for f,status in v['field_status'].items():
            if status['status']=='unresolved':
                ids=[pid for sup in v.get('raw_extraction',{}).get('support',[]) if sup['field']==f for pid in sup['passage_ids']]
                status['reason']=v['app_name']+' / '+f+': '+status['reason']
                if 'Invalid passage references' in status['reason']:
                    status['reason']+=' Candidate IDs: '+repr(ids)+'. Regenerate with existing numbered supporting passages; do not infer a value.'
        for e in v['evidence']:
            d=next(d for d in v['retrievals'] if d['requested_url']==e['url'])
            ok=d['ok'] and e['quote'] in d['text'] and e['content_sha256']==s.digest(d['text'])
            quality.append({'id':v['id'],'field':e['field'],'passage_id':e['passage_id'],
                'traceable_exact_quote_hash':ok,'source_kind':e['source_kind']})
            assert ok
        final.append(v)
    s.save(output/'final-audited-results.json',final,exclusive=True)
    s.save(output/'primary-agent-claim-audit.json',judgments,exclusive=True)
    s.save(output/'citation-quality.json',quality,exclusive=True)
    historical=s.read(s.ROOT/'data/stage03/human-review.json')
    comparisons=[]
    for h in historical:
        for v in final:
            if h['app_id']==v['id']:
                comparisons.append({'item_id':h['item_id'],'historical_value':h['final_value'],
                    'pilot_value':v['findings'][h['field']], 'same_value':h['final_value']==v['findings'][h['field']],
                    'historical_judgment':h['final_correct'],'fresh_independent_verification':False})
    s.save(output/'historical-regression.json',comparisons,exclusive=True)
    canonical=Path('U:/composio-research-assessment')
    tracked=__import__('subprocess').check_output(['git','ls-files'],cwd=s.ROOT,text=True).splitlines()
    differences=[name for name in tracked if (canonical/name).exists() and digest(s.ROOT/name)!=digest(canonical/name)]
    integrity={'tracked_files_compared':sum((canonical/n).exists() for n in tracked),'differences':differences,
        'accepted_artifact_bytes':(canonical/'submission/composio-assessment-uday.html').stat().st_size,
        'accepted_artifact_sha256':digest(canonical/'submission/composio-assessment-uday.html')}
    freezes=[]
    for path in sorted((s.ROOT/'data').rglob('freeze.json')):
        if directory in path.parents:continue
        freezes.append({'path':str(path.relative_to(s.ROOT)),'sha256':digest(path)})
    integrity['prior_freeze_files']=freezes
    s.save(output/'integrity.json',integrity,exclusive=True)
    summary={'status':'PILOT FAIL','safe_to_scale':False,'apps':len(final),
        'promoted_fields_audited':len(judgments),'primary_audit_downgrades':sum(x['decision']=='unresolved' for x in judgments),
        'retained_fields':sum(c.known(x) for v in final for x in v['findings'].values()),
        'retained_citations':len(quality),'exact_traceable_citations':sum(q['traceable_exact_quote_hash'] for q in quality),
        'independent_human_accuracy':None,'historical_overlap_claims':len(comparisons),
        'readable_pages':sum(d['ok'] for v in final for d in v['retrievals']),
        'failed_pages':sum(not d['ok'] for v in final for d in v['retrievals']),
        'scope':'Strict 12-app diagnostic pilot only; raw, context-audit and downgraded projections preserved.'}
    s.save(output/'acceptance-decision.json',summary,exclusive=True)
    print(json.dumps(summary)); print(json.dumps(integrity))

if __name__=='__main__':main()
