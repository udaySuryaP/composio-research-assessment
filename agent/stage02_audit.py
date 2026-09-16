"""Offline postflight validation of a frozen Stage 02 run; never repairs its artifacts."""
import argparse
from collections import Counter
import hashlib
import json
from agent import stage02 as s


def audit(run_id):
    directory=s.ROOT/'data/runs'/run_id
    manifest=s.read(directory/'manifest.json')
    rows=s.read(directory/'first-pass.json')
    apps={a['id']:a for a in s.seeds()}
    expected=manifest['selected_ids'] if manifest['mode']=='augmentation' else (sorted(apps) if manifest['mode']=='run' else [1,11,31,71])
    errors=[]
    supplementary=[]
    if sorted(r['id'] for r in rows)!=expected:
        errors.append('App set differs from requested run')
    for path,wanted in s.read(directory/'freeze.json').items():
        if hashlib.sha256((directory/path).read_bytes()).hexdigest()!=wanted:
            errors.append('Frozen hash mismatch: '+path)
    for row in rows:
        value=s.read(directory/'apps'/('%03d.json'%row['id']))
        if row!=value['record']:
            errors.append('Aggregate differs from checkpoint: '+str(row['id']))
        errors.extend('Record %s: %s'%(row['id'],e) for e in s.validate_schema(row))
        app=apps[row['id']]
        if any(row[k]!=v for k,v in [('app_name',app['name']),('category',app['category']),('website',s.website(app))]):
            errors.append('Assigned identity mismatch: '+str(row['id']))
        for doc in value['retrievals']:
            if doc['content_sha256']!=s.digest(doc['text']):
                errors.append('Source text hash mismatch: '+str(row['id']))
        flags=s.quality(row,app,value['retrievals'])
        if row['api_available']=='no' and row['auth_methods']!=['unknown']:
            flags.append({'code':'api_auth_contradiction','field':'auth_methods'})
        # Host ownership alone is insufficient to establish repository ownership.
        if any(e['source_kind']=='official' and s.urlparse(e['final_url']).hostname=='github.com' for e in row['evidence']):
            flags.append({'code':'official_repository_ownership_needs_check','field':'evidence'})
        known=[row[f] for f in s.CLAIM_FIELDS if row[f] not in ('unknown','unclear',['unknown'])]
        if not known:
            flags.append({'code':'all_research_fields_unknown','field':None})
        supplementary.append({'id':row['id'],'flags':flags})
    counts=Counter(f['code'] for item in supplementary for f in item['flags'])
    result={'run_id':run_id,'audited_at':s.now(),'record_count':len(rows),'errors':errors,
            'supplementary_flag_counts':dict(counts),'supplementary_flags':supplementary,
            'human_review':False,'note':'Offline integrity/quality validation only; no semantic truth or accuracy claim.'}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    if not s.re.fullmatch(r'[A-Za-z0-9_-]+',args.run_id):
        raise SystemExit('Invalid run ID')
    s.load_env()
    result=audit(args.run_id)
    # A separate Stage 02 artifact, outside the frozen snapshot.
    s.save(s.ROOT/'data'/('stage02-postflight-'+args.run_id+'.json'),result)
    print(json.dumps({k:result[k] for k in ('run_id','record_count','errors','supplementary_flag_counts')}))
    raise SystemExit(bool(result['errors']))


if __name__=='__main__': main()
