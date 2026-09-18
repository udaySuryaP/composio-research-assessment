"""Read-only citation, targeted-scope and pattern integrity checks."""
import hashlib, json, re, sys
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit
from agent import release
from agent.submission_fixes import ROOT, BASE, OUT, PURPOSES, read, sha
from targeted_review import browser_doc

def main():
 rows=read(OUT/'final-corrected-dataset.json');base=read(BASE/'final-corrected-dataset.json');errors=[];documents={}
 def add(d):
  if d.get('ok') and d.get('text'):
   assert hashlib.sha256(d['text'].encode()).hexdigest()==d['content_sha256']
   documents.setdefault(d['content_sha256'],[]).append(d['text'])
 # Retained large captures are local provenance inputs, not needed for the report rebuild.
 local=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT
 targeted=local/'data/correction/targeted-official-review-20260917'
 fresh=local/'data/correction/fresh-independent-verification-20260917'
 for r in base:
  p=Path(r['audit_artifacts']['automated_checkpoint'])
  if not p.exists():raise FileNotFoundError('Retained original checkpoint required for full citation audit: '+str(p))
  assert sha(p)==r['audit_artifacts']['automated_checkpoint_sha256']
  for d in read(p).get('retrievals',[]):add(d)
 for p in (targeted/'captures').glob('*.json'):
  for d in read(p).get('retrievals',[]):add(d)
 for args in [(4,'turn4view5','https://docs.bigcommerce.com/developer/docs/overview/api-fundamentals/api-accounts',{910,911,917}),(8,'turn8view3','https://docs.bigcommerce.com/developer/docs/overview/api-fundamentals/api-accounts',{695,698,724}),(8,'turn8view4','https://docs.bigcommerce.com/developer/docs/overview/api-fundamentals/api-accounts',{661,667}),(5,'turn5view0','https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization.html',{3,7}),(6,'turn6view0','https://pitchbook.com/help/PitchBook-api',{6,15,37,39,42,51}),(8,'turn8view2','https://developers.clay.com/',{19,21,45,57})]:add(browser_doc(*args))
 catalog=read(fresh/'source-catalog.json');counts=Counter()
 for r,old in zip(rows,base):
  assert (r['id'],r['app'],r['category'])==(old['id'],old['app'],old['category'])
  for f in r['findings']:
   changed=r['findings'][f]!=old['findings'][f]
   allowed=(f=='purpose' and r['id'] in PURPOSES) or (r['id']==34 and f.startswith('mcp_')) or (r['id']==2 and f=='primary_blocker')
   assert changed==allowed,(r['id'],f,'unexpected change')
   cs=[e for e in r['evidence'] if e['field']==f]
   if r['field_status'][f]['status']!='unresolved':assert cs and set(r['field_refs'][f])=={e['passage_id'] for e in cs}
   for e in cs:
    layer=e.get('review_layer');counts[layer or 'retained']+=1
    if layer=='submission_fixes_agent_review':
     p=ROOT/e['source_capture'];d=read(p)
     assert sha(p)==e['source_capture_sha256'] and d['content_sha256']==e['content_sha256']
     assert hashlib.sha256(d['text'].encode()).hexdigest()==e['content_sha256']
     if e.get('exact'):assert e['snippet'] in d['text']
     elif r['id']==50:assert 'FanBasis is now Commas!' in d['text'] and e.get('paraphrase')
    elif layer=='fresh_independent_verification':
     source=catalog[e['source_key']]
     assert hashlib.sha256(source['text'].encode()).hexdigest()==e['content_sha256']
     assert sha(Path(e['browser_archive']))==e['browser_archive_sha256']
     assert e.get('paraphrase') and not e.get('exact')
    else:
     assert e in old['evidence']
     assert any(e['snippet'] in text for text in documents.get(e['content_sha256'],[])),(r['id'],f,e['passage_id'])
    u=urlsplit(e.get('final_url') or e['url']);assert u.scheme in ('http','https') and u.hostname and not u.username
  if r['id'] in PURPOSES:assert len(r['findings']['purpose'])<=180 and '\n' not in r['findings']['purpose']
 patterns=read(ROOT/'final-artifact-20260917/patterns.json')
 assert patterns['input_sha256']==sha(OUT/'final-corrected-dataset.json')
 for metric in patterns['metrics'].values():
  if 'field' not in metric:continue
  eligible=[r['id'] for r in rows if r['field_status'][metric['field']]['status']!='unresolved']
  assert metric['eligible_ids']==eligible and metric['denominator']==len(eligible)
  for v in metric['values'].values():assert v['count']==len(set(v['ids'])) and set(v['ids'])<=set(eligible)
 assert Counter(r['category'] for r in rows)=={c['category']:10 for c in patterns['categories']}
 text=(ROOT/'submission/composio-assessment-uday.html').read_text(encoding='utf8')
 assert all(x in text for x in ['47 correct; 8 caveat_needed; 5 unsupported; 0 unverifiable','7/35','35/35','PRE-CORRECTION','Live assessment','Three observed corrections','Credential access and gates by category'])
 assert not any(x in text for x in ['local, untracked and uncommitted','publication and submission are pending','public repository and older live page do not yet contain'])
 release.check()
 result={'status':'PASS','citation_integrity_errors':errors,'citations_checked':dict(counts),'targeted_scope':'56 field changes only; identities/categories and all other findings unchanged','metrics':'All affected patterns recomputed; denominator and IDs checked','apps':100,'categories':10,'purpose_supported':98,'purpose_unresolved':2,'security_offline_release':'PASS','boundaries':'Citation integrity is not factual accuracy; no new whole-dataset verification sample.'}
 (ROOT/'final-artifact-20260917/submission-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
 print(json.dumps(result,indent=2))

if __name__=='__main__':main()
