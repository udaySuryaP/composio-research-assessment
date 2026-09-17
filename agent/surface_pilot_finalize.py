"""Seal a new pilot after explicit primary audit; never modify previous outputs."""
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from agent import stage02 as s, coverage_correction as c
from agent.schema import CLAIM_FIELDS

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',required=True)
    args=parser.parse_args();d=s.ROOT/'data/correction'/args.run_id
    raw=[s.read(p) for p in sorted((d/'apps').glob('*.json'))]
    secondary=s.read(d/'audited-results.json')
    values=s.read(d/'primary-audit-baseline.json') if (d/'primary-audit-baseline.json').exists() else secondary
    judgments=s.read(d/'primary-audit-decisions.json')
    expected={(v['id'],f) for v in values for f,x in v['findings'].items() if c.known(x)}
    assert len(judgments)==len(expected) and {(j['id'],j['field']) for j in judgments}==expected
    assert len(values)==12 and [v['id'] for v in values]==c.PILOT
    decisions={(j['id'],j['field']):j for j in judgments}
    final=copy.deepcopy(values)
    for v in final:
        for f in CLAIM_FIELDS:
            if not c.known(v['findings'][f]):continue
            j=decisions[v['id'],f]
            assert j['decision'] in ('retain','downgrade') and j['reason'].strip()
            if j['decision']=='downgrade':
                v['findings'][f]=['unknown'] if f in ('auth_methods','api_types') else 'unknown'
                v['field_status'][f]={'status':'unresolved','human_checked':False,'reason':j['reason']}
        reason=c.sv.buildability_reason(v.get('raw_extraction',{}),v['findings'])
        if reason:
            for f in ('buildability','buildability_rationale'):
                v['findings'][f]='unknown';v['field_status'][f]={'status':'unresolved','human_checked':False,'reason':'Primary audit dependency cascade: '+reason}
        if v['findings']['primary_blocker'].lower() in ('none','none documented','no blockers') and v['findings']['buildability']=='unknown':
            v['findings']['primary_blocker']='unknown';v['field_status']['primary_blocker']={'status':'unresolved','human_checked':False,'reason':'Primary audit: prerequisites unresolved; no-blocker claim withheld.'}
        v['evidence']=[e for e in v['evidence'] if c.known(v['findings'][e['field']])]
        for f in CLAIM_FIELDS:
            if not c.known(v['findings'][f]):
                status=v['field_status'][f]
                if status['reason']=='Retrieved evidence does not establish this field.':
                    status['reason']=f'{v["app_name"]} / {f}: inspected official sources supplied no traceable support for this field; silence is not evidence of absence.'
                assert status['reason'].strip()
            else:
                assert any(e['field']==f for e in v['evidence'])
                assert c.sv.check(f,v['findings'][f],v['raw_extraction'],v['passages']) is None
        v['mcp_provider']=v['app_name'] if v['findings']['mcp_available']=='official' else 'unknown'
        v['mcp_ownership']='vendor_official' if v['mcp_provider']!='unknown' else 'unresolved'
    quality=[]
    for v in final:
        for e in v['evidence']:
            doc=next(x for x in v['retrievals'] if x['requested_url']==e['url'])
            ok=(doc['ok'] and e['quote'] in doc['text'] and e['content_sha256']==doc['content_sha256']==s.digest(doc['text'])
                and e['final_url']==doc['final_url'] and e['retrieved_at']==doc['retrieved_at'] and e['source_kind']==doc['source_kind'])
            assert ok
            quality.append({'id':v['id'],'field':e['field'],'passage_id':e['passage_id'],'exact_quote_url_time_hash':ok})
    history=s.read(d/'preflight-history-hashes.json')
    for folder,hashes in history.items():
        base=s.ROOT/'data/correction'/folder
        current={str(p.relative_to(base)):sha(p) for p in base.rglob('*') if p.is_file()}
        assert current==hashes
    canonical=Path('U:/composio-research-assessment')
    tracked=subprocess.check_output(['git','ls-files'],cwd=s.ROOT,text=True).splitlines()
    differences=[n for n in tracked if (canonical/n).exists() and sha(s.ROOT/n)!=sha(canonical/n)]
    assert not differences
    integrity={'prior_pilot_files_unchanged':{f:len(h) for f,h in history.items()},'tracked_files_compared':sum((canonical/n).exists() for n in tracked),'tracked_differences':differences,
        'canonical_branch':subprocess.check_output(['git','branch','--show-current'],cwd=canonical,text=True).strip(),
        'canonical_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=canonical,text=True).strip(),
        'canonical_status':subprocess.check_output(['git','status','--short'],cwd=canonical,text=True).strip(),
        'accepted_artifact_bytes':(canonical/'submission/composio-assessment-uday.html').stat().st_size,
        'accepted_artifact_sha256':sha(canonical/'submission/composio-assessment-uday.html')}
    assert integrity['canonical_branch']=='main' and not integrity['canonical_status']
    old=s.read(s.ROOT/'data/correction/strict-pilot-20260917/primary-audit-v2/final-audited-results.json')
    changes=[{'id':v['id'],'app_name':v['app_name'],'field':f,'before':o['findings'][f],'after':v['findings'][f],
        'reason':v['field_status'][f]['reason']} for v,o in zip(final,old) for f in CLAIM_FIELDS if o['findings'][f]!=v['findings'][f]]
    comparisons=[]
    for h in s.read(s.ROOT/'data/stage03/human-review.json'):
        for v in final:
            if h['app_id']==v['id']:
                comparisons.append({'item_id':h['item_id'],'field':h['field'],'historical_value':h['final_value'],'pilot_value':v['findings'][h['field']],
                    'same_value':h['final_value']==v['findings'][h['field']],'historical_judgment':h['final_correct'],'fresh_human_check':False})
    raw_known=sum(c.known(x) for v in raw for x in v.get('raw_extraction',{}).get('findings',{}).values())
    pipeline_known=sum(c.known(x) for v in raw for x in v.get('findings',{}).values())
    final_known=sum(c.known(x) for v in final for x in v['findings'].values())
    verdict=s.read(d/'primary-verdict.json') if (d/'primary-verdict.json').exists() else {
        'status':'PILOT FAIL','safe_to_scale':False,'reason':'Per-surface checks fail closed, but extraction repeatedly violates the contract and useful scoped coverage collapses; no positive buildability validates complete prerequisite extraction. Do not scale a mostly abstaining pipeline.'}
    summary={'status':verdict['status'],'safe_to_scale':verdict['safe_to_scale'],'selected_ids':c.PILOT,'raw_candidate_fields':raw_known,
        'pipeline_promotions':pipeline_known,'validator_withheld_candidates':raw_known-pipeline_known,
        'primary_audit_baseline_fields':len(expected),
        'context_promotions':sum(c.known(x) for v in secondary for x in v['findings'].values()),
        'context_downgrades':pipeline_known-sum(c.known(x) for v in secondary for x in v['findings'].values()),
        'primary_audit_downgrades':sum(j['decision']=='downgrade' for j in judgments),'retained_fields':final_known,
        'retained_citations':len(quality),'exact_citations':sum(q['exact_quote_url_time_hash'] for q in quality),
        'positive_buildability':sum(v['findings']['buildability'] in ('buildable','conditional') for v in final),
        'retained_critical_fields':{f:sum(c.known(v['findings'][f]) for v in final) for f in c.CRITICAL},
        'search_successes':sum(log['ok'] for v in raw for log in v['discovery']),
        'readable_pages':sum(doc['ok'] for v in raw for doc in v['retrievals']),
        'attempted_pages':sum(len(v['retrievals']) for v in raw),'failures':[{'id':v['id'],'error':v['failure']} for v in raw if v['failure']],
        'historical_comparisons':comparisons,'independent_human_accuracy':None,
        'reason':verdict['reason']}
    out=d/'primary-audit'
    for name,value in [('final-audited-results.json',final),('citation-quality.json',quality),('historical-regression.json',comparisons),('integrity.json',integrity),('before-after.json',changes),('acceptance-decision.json',summary)]:
        s.save(out/name,value,exclusive=True)
    code=['agent/coverage_correction.py','agent/surface_validation.py','agent/strict_pilot_audit.py','agent/surface_pilot_finalize.py','tests/test_coverage_correction.py','tests/test_surface_validation.py','tests/fixtures/surface-pilot-failures.json']
    if (s.ROOT/'agent/atomic_contracts.py').exists():
        code+=['agent/atomic_contracts.py','tests/test_atomic_contracts.py']
    s.save(d/'code-snapshot.json',{n:sha(s.ROOT/n) for n in code},exclusive=True)
    log_prefix='atomic' if args.run_id.startswith('atomic-') else 'surface'
    for name in (f'{log_prefix}-pilot-run.log',f'{log_prefix}-pilot-context-audit.log',f'{log_prefix}-tests-before.log',f'{log_prefix}-tests-final.log'):
        shutil.copyfile(s.ROOT/name,d/name)
    print(json.dumps(summary))

if __name__=='__main__':main()
