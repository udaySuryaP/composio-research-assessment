"""Offline correction validation and secret scan; outputs no secret values."""
import hashlib
import json
import os
import re
from agent import stage02 as s
from agent.stage02_audit import audit
from agent.stage02_correction import RUN, IDS

def main():
    s.load_env()
    report=s.read(s.ROOT/'data/stage02-correction-report.json')
    result=audit(RUN)
    assert not result['errors'], result['errors']
    assert result['record_count']==len(IDS)
    baseline=s.ROOT/'data/runs/stage02-full-fallback-20260916'
    actual={str(p.relative_to(baseline)):hashlib.sha256(p.read_bytes()).hexdigest() for p in baseline.rglob('*') if p.is_file()}
    assert actual==report['baseline_hashes']
    consumed=0
    for item in report['apps']:
        v=s.read(s.ROOT/'data/runs'/RUN/'apps'/('%03d.json'%item['id']))
        for log in v['discovery']:
            assert log['action']=='COMPOSIO_SEARCH_TAVILY' and log['version']=='20260903_00'
            assert log['arguments']=={'query':log['query']}
        consumed+=sum(d['ok'] and d['requested_url'] in item['consumed_candidate_urls'] for d in v['retrievals'])
    assert consumed>0, 'No readable Composio-discovered candidate consumed'
    secrets=[v.encode() for k,v in os.environ.items() if any(t in k for t in ('KEY','TOKEN','SECRET','PASSWORD')) and len(v)>=8]
    patterns=rb'\bsk-[A-Za-z0-9_-]{16,}|\b(?:[srp]k_(?:test|live)_[A-Za-z0-9]{10,}|whsec_[A-Za-z0-9]{10,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{15,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{30,})\b'
    scanned=0
    for folder in ('agent','tests','data'):
        for p in (s.ROOT/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                content=p.read_bytes()
                assert not any(x in content for x in secrets), 'Configured secret detected; value suppressed'
                assert not re.search(patterns,content), 'Credential pattern detected; value suppressed'
                scanned+=1
    result.update(baseline_files_verified=len(actual), readable_composio_candidates_consumed=consumed,
        credential_scan='CLEAN', scanned_files=scanned)
    s.save(s.ROOT/'data/stage02-correction-validation.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='supplementary_flags'}))

if __name__=='__main__':main()
