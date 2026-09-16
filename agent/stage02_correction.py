"""Bounded HQ correction; preserves the original Stage 02 baseline."""
import hashlib
import json
from importlib.metadata import version
from agent import stage02 as s

RUN = 'stage02-composio-augmentation-20260916'
IDS = [1, 40, 62, 87]

def main():
    s.load_env()
    baseline = s.ROOT/'data/runs/stage02-full-fallback-20260916'
    before = {str(p.relative_to(baseline)): hashlib.sha256(p.read_bytes()).hexdigest() for p in baseline.rglob('*') if p.is_file()}
    for path, wanted in s.read(baseline/'freeze.json').items():
        assert before[path] == wanted
    directory = s.ROOT/'data/runs'/RUN
    assert not directory.exists(), 'Never overwrite an existing correction run'
    client, info = s.catalog()
    s.save(s.ROOT/'data/stage02-correction-live-catalog.json', info, exclusive=True)
    config = s.select_action(info, 'COMPOSIO_SEARCH_TAVILY')
    apps = [a for a in s.seeds() if a['id'] in IDS]
    manifest = {'run_id': RUN, 'started_at': s.now(), 'mode': 'augmentation', 'status':'running',
        'selected_ids': IDS, 'selected_action':config, 'fallback':False,
        'model':s.os.getenv('OPENAI_MODEL',s.MODEL), 'bounds':s.BOUNDS,
        'input_sha256':s.digest(json.dumps(s.seeds(),sort_keys=True)),
        'prompt_sha256':s.digest(s.PROMPT), 'schema_sha256':s.digest(json.dumps(s.RESEARCH_SCHEMA,sort_keys=True))}
    s.save(directory/'manifest.json',manifest)
    values=[]
    for app in apps:
        value=s.checkpoint_app(app,directory,client,config)
        for log in value['discovery']:
            log.update(action=config['slug'], version=config['version'], operation='tools.execute',
                arguments={'query':log['query']}, user_id=s.os.getenv('COMPOSIO_USER_ID','stage02-research'))
        # checkpoint has not been frozen yet; append sanitized invocation metadata.
        s.save(directory/'apps'/('%03d.json'%app['id']),value)
        values.append(value)
        print(json.dumps({'id':app['id'],'search_successes':sum(x['ok'] for x in value['discovery']),
            'pages':len(value['retrievals']),'readable':sum(d['ok'] for d in value['retrievals']), 'failure':value['failure']}),flush=True)
    manifest=s.finalize(directory,values,manifest)
    after={str(p.relative_to(baseline)):hashlib.sha256(p.read_bytes()).hexdigest() for p in baseline.rglob('*') if p.is_file()}
    assert before==after, 'Baseline changed'
    old={r['id']:r for r in s.read(baseline/'first-pass.json')}
    details=[]
    for v in values:
        app=next(a for a in apps if a['id']==v['record']['id'])
        candidates=list(dict.fromkeys(u for log in v['discovery'] if log['ok'] for u in s.urls(log.get('response',{}))))
        consumed=[d['requested_url'] for d in v['retrievals'] if d['requested_url'] in candidates]
        changes={f:{'baseline':old[app['id']][f],'augmentation':v['record'][f]} for f in s.CLAIM_FIELDS if old[app['id']][f]!=v['record'][f]}
        details.append({'id':app['id'],'name':app['name'],'category':app['category'],
            'selection_reason':'Frozen baseline extraction failed' if app['id']==40 else 'Frozen baseline all research fields unknown',
            'candidate_urls':candidates,'consumed_candidate_urls':consumed,
            'new_readable_official_urls':[d['final_url'] for d in v['retrievals'] if d['ok'] and d['source_kind']=='official' and d['final_url'] not in [x['final_url'] for x in s.read(baseline/'apps'/('%03d.json'%app['id']))['retrievals'] if x['ok']]],
            'separate_first_pass_changes':changes,'baseline_values_modified':False})
    report={'recorded_at':s.now(),'authentication':'SUCCESS','key_type':'Platform Project API key (user confirmation)',
        'platform_project':'Not exposed by tested catalog operations; no project identity inferred',
        'sdk_version':version('composio'),'client_version':version('composio-client'),
        'catalog_operations':['toolkits.get(slug=composio_search)','tools.get_raw_composio_tools(toolkits=[composio_search],limit=100)'],
        'run_id':RUN,'manifest':manifest,'search_successes':sum(log['ok'] for v in values for log in v['discovery']),
        'search_failures':sum(not log['ok'] for v in values for log in v['discovery']),
        'apps':details,'baseline_hashes':before,'baseline_hashes_unchanged':True,
        'baseline_weaknesses':{'all_unknown':19,'no_usable_official_source':13,'low_confidence':100,
            'buildability_without_rationale':10,'raw_quote_not_found':349,'raw_negative_without_explicit_evidence':9,'SendGrid_failed':True},
        'stage03_performed':False,'accuracy_claim':None}
    s.save(s.ROOT/'data/stage02-correction-report.json',report,exclusive=True)
    print(json.dumps({'run_id':RUN,'manifest':manifest,'search_successes':report['search_successes'],'search_failures':report['search_failures']}))

if __name__=='__main__':main()
