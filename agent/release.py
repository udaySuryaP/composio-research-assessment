"""Validate the accepted release and prepare an exact-byte Pages directory."""
import hashlib
import json
import re
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'submission/composio-assessment-uday.html'
EXPECTED = '0236cf4124273b73d76dd7ba925ab77963da405c1a23c1e97c3fb6e0a338706b'
INPUT = ROOT / 'data/correction/fresh-independent-verification-20260917/final-corrected-dataset.json'

def check():
    data = ART.read_bytes()
    assert hashlib.sha256(data).hexdigest() == EXPECTED
    assert len(data) == 7_564_014 and len(data) < 10_000_000
    text = data.decode('utf-8')
    payload = json.loads(re.search(r'<script id="reviewed-data" type="application/json">(.*?)</script>', text, re.S)[1])
    rows = payload['rows']
    assert len(rows) == len({r['id'] for r in rows}) == 100
    assert len(re.findall(r'<tr id="app-', text)) == 100
    assert len({r['category'] for r in rows}) == 10
    assert payload['input_sha256'] == hashlib.sha256(INPUT.read_bytes()).hexdigest()
    source = json.loads(INPUT.read_text(encoding='utf-8-sig'))
    assert Counter(s['status'] for r in source for s in r['field_status'].values()) == {'source_backed':45,'source_backed_with_caveat':798,'unresolved':457}
    assert [len(payload['patterns']['candidate_groups'][k]) for k in ['likely_buildable_from_public_docs','buildable_with_documented_constraints','gated_or_outreach_required','needs_further_investigation','unresolved']] == [1,65,11,6,17]
    def strings(v):
        if isinstance(v, str): yield v
        elif isinstance(v, dict):
            for x in v.values(): yield from strings(x)
        elif isinstance(v, list):
            for x in v: yield from strings(x)
    visible = re.sub(r'<script id="reviewed-data" type="application/json">.*?</script>', '', text, flags=re.S) + '\n'.join(strings(payload))
    assert not re.search(r'(?i)(?<![A-Za-z])[a-z]:[\\/]|file:/|/(?:Users|home)/(?:udays|uday|runner|root)/', visible)
    assert not re.search(r'sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', visible)
    executable = ''.join(re.findall(r'<script>(.*?)</script>', text, re.S))
    assert not re.search(r'fetch\s*\(|XMLHttpRequest', executable)
    assert not re.search(r'<script[^>]+src=|<link[^>]+href=', text)
    rebuilt = ROOT / 'final-artifact-20260917/composio-assessment-uday.html'
    assert rebuilt.read_bytes() == data
    result = {'status':'PASS','bytes':len(data),'sha256':EXPECTED,'apps':100,'categories':10,'security':'PASS','accepted_bytes_equal':True}
    print(json.dumps(result))
    return data

if __name__ == '__main__':
    data = check()
    if len(sys.argv) > 1 and sys.argv[1] == 'publish':
        output = Path(sys.argv[2]); output.mkdir(parents=True, exist_ok=True)
        assert not any(output.iterdir()), 'Publish directory must be empty'
        (output/'index.html').write_bytes(data)
        (output/'.nojekyll').write_bytes(b'')
        assert (output/'index.html').read_bytes() == data
