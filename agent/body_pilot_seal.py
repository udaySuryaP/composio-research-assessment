"""Seal only a fully reviewed downgrade-only body pilot."""
import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from agent import stage02 as s, body_pilot as b, coverage_correction as c

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def buildability(atoms,review,findings):
    if not review.get('completeness_established') or review.get('unresolved_gaps') or review.get('likely_categories_searched_not_established'):
        return 'unknown','Prerequisite completeness remains unresolved for this surface/mode.'
    if any(not c.known(findings[f]) for f in ('auth_methods','api_types','api_available','api_breadth')):
        return 'unknown','Retained resource API dependencies remain unresolved.'
    prerequisites=[a for a in atoms if a['retained'] and a['label'].startswith('prerequisite:') and a['mode']==review['surface_or_mode']]
    if not prerequisites: return 'unknown','No evidenced setup prerequisites retained.'
    return 'conditional','Documentation-based conditional integration; '+ '; '.join(a['fact'] for a in prerequisites)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--run-id',required=True); args=parser.parse_args()
    d=s.ROOT/'data/correction'/args.run_id
    values=[s.read(p) for p in sorted((d/'apps').glob('*.json'))]
    assert [v['id'] for v in values]==c.PILOT
    judgments=s.read(d/'primary-decisions.json')
    expected={(v['id'],a['atom_id']) for v in values for a in v.get('atoms',[]) if a['retained']}
    expected|={(v['id'],'purpose') for v in values if c.known(v.get('findings',{}).get('description','unknown'))}
    assert {(j['id'],j['atom_id']) for j in judgments}==expected and len(judgments)==len(expected)
    lookup={(j['id'],j['atom_id']):j for j in judgments}
    final=[]; citations=[]; family=Counter(); promoted=Counter(); displays=Counter(); body=Counter(); capture_failures=[]; integrity_downgrades=[]
    for v in values:
        for doc in v['retrievals']:
            body.update(f['category'] for f in doc['fragments'])
            if s.digest(doc['text'])!=doc['content_sha256']:
                capture_failures.append({'id':v['id'],'url':doc['requested_url'],'recorded_hash':doc['content_sha256'],'saved_text_hash':s.digest(doc['text']),'reason':'Pre-serialization hash does not match saved scrubbed source; no source hash repaired.'})
        atoms=copy.deepcopy(v.get('atoms',[]))
        for a in atoms:
            if not a['retained']: continue
            f=a['label'].split(':')[0]; promoted[f]+=1
            j=lookup[v['id'],a['atom_id']]
            assert j['decision'] in ('retain','downgrade') and j['reason']
            a['retained']=j['decision']=='retain'; a['primary_audit']=j
            bad=[pid for pid in a['passage_ids'] if s.digest(v['retrievals'][v['passages'][pid]['source_index']]['text'])!=v['retrievals'][v['passages'][pid]['source_index']]['content_sha256']]
            if a['retained'] and bad:
                a['retained']=False; a['integrity_reason']='Captured source hash does not match saved text.'
                integrity_downgrades.append({'id':v['id'],'atom_id':a['atom_id'],'passage_ids':bad})
            if a['retained']: family[f]+=1
        purpose=v.get('findings',{}).get('description','unknown')
        if c.known(purpose) and lookup[v['id'],'purpose']['decision']=='downgrade': purpose='unknown'
        # MCP resource/action atoms stay in their own surface display, never primary breadth.
        findings=b.derive([a for a in atoms if a['mode']!='mcp' or a['label'].startswith('mcp:')],purpose)
        active=[a for a in atoms if a['retained'] and a.get('state')!='deprecated']
        if any(a['label'] in ('protocol:rest','protocol:graphql','protocol:soap','protocol:grpc') and a['mode'] in ('primary','personal','public_app') for a in active):
            findings['api_available']='yes' # An evidenced resource API protocol entails API existence.
        if any(a['label']=='mcp:provider' and 'official' in a['fact'].lower() for a in active) and any(a['label']=='mcp:availability' for a in active):
            findings['mcp_available']='official' # Explicitly audited official provider plus availability; no all-atom cascade.
        mcp=[a['fact'] for a in atoms if a['retained'] and a['label'].startswith('mcp:')]
        if mcp: findings['mcp_notes']='; '.join(mcp)
        displays.update(f for f,x in findings.items() if c.known(x))
        fact_displays={f:[{'mode':a['mode'],'label':a['label'],'state':a.get('state'),'fact':a['fact'],'atom_id':a['atom_id']} for a in atoms if a['retained'] and a['label'].startswith(f+':')] for f in b.VALUES}
        reviews=[]
        for mode in sorted({'primary'}|{a['mode'] for a in atoms}):
            found=[a for a in atoms if a['retained'] and a['mode']==mode and a['label'].startswith('prerequisite:')]
            reviews.append({'surface_or_mode':mode,'prerequisites_found_with_evidence':found,'likely_categories_searched_not_established':[cat for cat in b.VALUES['prerequisite'] if not any(a['label']=='prerequisite:'+cat for a in found)],'search_queries':[x['query'] for x in v['discovery']],'alternative_paths':v.get('completeness',{}).get('alternative_auth_access_paths',[]),'unresolved_gaps':v.get('completeness',{}).get('unresolved_gaps',['No readable body evidence']),'completeness_established':False,'primary_review':'Inventory lacks a traceable exhaustive setup/access search and applicable path closure; buildability remains unknown.'})
        findings['buildability'],rationale=buildability(atoms,next(r for r in reviews if r['surface_or_mode']=='primary'),findings)
        findings['buildability_rationale']=rationale if findings['buildability']!='unknown' else 'unknown'
        for a in atoms:
            if not a['retained']: continue
            for pid in a['passage_ids']:
                span=v['passages'][pid]; doc=v['retrievals'][span['source_index']]
                assert span['category']=='body' and span['text'] in doc['text'] and s.digest(doc['text'])==doc['content_sha256']
                citations.append({'id':v['id'],'atom_id':a['atom_id'],'passage_id':pid,'quote':span['text'],'heading':span['heading'],'paragraph_index':span['paragraph_index'],'requested_url':doc['requested_url'],'final_url':doc['final_url'],'retrieved_at':doc['retrieved_at'],'source_kind':doc['source_kind'],'content_sha256':doc['content_sha256'],'exact':True})
        if c.known(purpose):
            for pid in v['purpose']['passage_ids']:
                span=v['passages'][pid]; doc=v['retrievals'][span['source_index']]
                assert span['text'] in doc['text'] and s.digest(doc['text'])==doc['content_sha256']
                citations.append({'id':v['id'],'atom_id':'purpose','passage_id':pid,'quote':span['text'],'heading':span['heading'],'paragraph_index':span['paragraph_index'],'requested_url':doc['requested_url'],'final_url':doc['final_url'],'retrieved_at':doc['retrieved_at'],'source_kind':doc['source_kind'],'content_sha256':doc['content_sha256'],'exact':True})
        final.append({'id':v['id'],'app_name':v['app_name'],'findings':findings,'atomic_display_fields':fact_displays,'atoms':atoms,'completeness_reviews':reviews,'failure':v['failure']})
    preflight=s.read(d/'preflight.json'); history=preflight['history']
    assert all(p.exists() and s.digest(p.read_bytes().hex())==h for name,h in history.items() for p in [s.ROOT/name])
    canonical=Path('U:/composio-research-assessment')
    tracked=subprocess.check_output(['git','ls-files'],cwd=s.ROOT,text=True).splitlines()
    compared=[n for n in tracked if (canonical/n).exists()]
    differences=[n for n in compared if sha(s.ROOT/n)!=sha(canonical/n)]
    assert not differences
    integrity={'history_files_unchanged':len(history),'tracked_files_compared':len(compared),'differences':differences,'canonical_branch':subprocess.check_output(['git','branch','--show-current'],cwd=canonical,text=True).strip(),'canonical_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=canonical,text=True).strip(),'canonical_status':subprocess.check_output(['git','status','--short'],cwd=canonical,text=True).strip(),'checkout_branch':subprocess.check_output(['git','branch','--show-current'],cwd=s.ROOT,text=True).strip(),'checkout_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=s.ROOT,text=True).strip(),'checkout_status':subprocess.check_output(['git','status','--short'],cwd=s.ROOT,text=True),'accepted_bytes':(canonical/'submission/composio-assessment-uday.html').stat().st_size,'accepted_sha256':sha(canonical/'submission/composio-assessment-uday.html')}
    assert integrity['canonical_branch']=='main' and not integrity['canonical_status']
    historical=[{'id':h['app_id'],'field':h['field'],'historical_value':h['final_value'],'pilot_value':v['findings'][h['field']],'same':h['final_value']==v['findings'][h['field']],'fresh_human_check':False} for h in s.read(s.ROOT/'data/stage03/human-review.json') for v in final if h['app_id']==v['id']]
    summary={'status':'PILOT FAIL','safe_to_scale':False,'run_id':args.run_id,'selected_ids':c.PILOT,'atomic_promoted':dict(promoted),'atomic_retained':dict(family),'atomic_downgraded':{f:promoted[f]-family[f] for f in promoted},'derived_display_counts':dict(displays),'retained_display_fields':sum(displays.values()),'atomic_family_displays':{f:sum(bool(v['atomic_display_fields'][f]) for v in final) for f in b.VALUES},'citations':len(citations),'exact_citations':len(citations),'search_successes':sum(x['ok'] for v in values for x in v['discovery']),'search_attempts':sum(len(v['discovery']) for v in values),'readable_pages':sum(x['ok'] for v in values for x in v['retrievals']),'page_attempts':sum(len(v['retrievals']) for v in values),'body_classification_counts':dict(body),'selected_body_passages':sum(len(v['passages']) for v in values),'failures':[{'id':v['id'],'failure':v['failure']} for v in values if v['failure']],'reason':'Body-aware atoms recover useful evidence, but primary semantic downgrades and incomplete setup/access inventories still prevent a reliable scale decision. Buildability completeness is not demonstrated.'}
    out=d/'primary-audit'
    summary['source_capture_hash_failures']=len(capture_failures); summary['integrity_atom_downgrades']=len(integrity_downgrades)
    for name,value in [('final-audited-results.json',final),('citation-quality.json',citations),('integrity.json',integrity),('historical-regression.json',historical),('acceptance-decision.json',summary),('source-capture-hash-failures.json',capture_failures),('integrity-downgrades.json',integrity_downgrades)]: s.save(out/name,value,exclusive=True)
    s.save(d/'code-snapshot.json',{n:sha(s.ROOT/n) for n in ('agent/body_pilot.py','agent/body_pilot_seal.py','tests/test_body_pilot.py')},exclusive=True)
    print(json.dumps(summary))

if __name__=='__main__': main()
