"""Primary audit pack and downgrade-only seal; never writes replacement facts."""
import argparse
import copy
import hashlib
import subprocess
from collections import Counter
from pathlib import Path
from agent import path_contracts as p, stage02 as s, coverage_correction as c

def integrity(d):
 pre=s.read(d/'preflight.json'); canonical=Path('U:/composio-research-assessment')
 sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
 tracked=subprocess.check_output(['git','ls-files'],text=True).splitlines()
 compared=[n for n in tracked if (canonical/n).exists()]
 result={'history_files':len(pre['history']),'history_unchanged':all((s.ROOT/n).exists() and s.digest((s.ROOT/n).read_bytes().hex())==h for n,h in pre['history'].items()),
  'tracked_files_compared':len(compared),'tracked_differences':[n for n in compared if sha(s.ROOT/n)!=sha(canonical/n)],
  'canonical_branch':subprocess.check_output(['git','branch','--show-current'],cwd=canonical,text=True).strip(),
  'canonical_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=canonical,text=True).strip(),
  'canonical_status':subprocess.check_output(['git','status','--short'],cwd=canonical,text=True).strip(),
  'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
  'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  'working_tree':subprocess.check_output(['git','status','--short'],text=True),
  'tracked_diff':subprocess.check_output(['git','diff','--stat','HEAD'],text=True),
  'accepted_sha256':sha(canonical/'submission/composio-assessment-uday.html'),
  'accepted_bytes':(canonical/'submission/composio-assessment-uday.html').stat().st_size}
 assert result['history_unchanged'] and not result['tracked_differences'] and not result['canonical_status'] and result['canonical_branch']=='main'
 return result

def pack(values):
 for v in values:
  print('APP',v['id'],v['app_name'],'FAILURE',v['failure'])
  print('PURPOSE',v.get('purpose'),v.get('purpose_error'))
  ids=set(v.get('purpose',{}).get('passage_ids',[]))
  for a in v.get('atoms',[]):
   if a['retained']:
    print(a['atom_id'],a['label'],a['path_id'],a['state'],repr(a['fact']),a['passage_ids']); ids.update(a['passage_ids'])
  for pid in sorted(ids):
   if pid in v['passages']:
    x=v['passages'][pid]; print(pid,x['url'],'CONTEXT',x['heading'],'TEXT',x['text'])

def seal(d,values):
 decisions=s.read(d/'primary-decisions.json'); lookup={(x['id'],x['atom_id']):x for x in decisions}
 expected={(v['id'],a['atom_id']) for v in values for a in v.get('atoms',[]) if a['retained']}
 expected|={(v['id'],'purpose') for v in values if c.known(v.get('findings',{}).get('description','unknown'))}
 assert set(lookup)==expected and len(decisions)==len(expected)
 final=[]; citations=[]; display_decisions=[]; promoted=Counter(); kept=Counter(); captures=[]
 for v in values:
  errors=p.capture_errors(v); captures.extend({'id':v['id'],**x} for x in errors)
  atoms=copy.deepcopy(v.get('atoms',[]))
  for a in atoms:
   if not a['retained']: continue
   promoted[a['label'].split(':')[0]]+=1
   decision=lookup[v['id'],a['atom_id']]; assert decision['decision'] in ('retain','downgrade') and decision['reason']
   a['primary_audit']=decision
   a['retained']=decision['decision']=='retain' and not p.validate(a,v['passages']) and not errors
   if a['retained']: kept[a['label'].split(':')[0]]+=1
  purpose=v.get('findings',{}).get('description','unknown')
  if c.known(purpose) and (lookup[v['id'],'purpose']['decision']!='retain' or errors): purpose='unknown'
  findings=p.project(atoms,purpose); candidates=p.project(v.get('atoms',[]),v.get('findings',{}).get('description','unknown'))
  reviews=p.inventory_review(atoms,v['discovery'],v['passages'])
  primary=next(x for x in reviews if x['path_id']=='primary/unspecified/unspecified/unspecified')
  unresolved='Primary prerequisite inventory unclosed: '+', '.join(primary['unresolved_gaps'])+'. Alternative-path applicability remains unproven.'
  for f,value in candidates.items():
   if c.known(value): display_decisions.append({'id':v['id'],'field':f,'decision':'retain' if c.known(findings[f]) else 'downgrade','reason':'Derived solely from independently audited matching-path atoms; no replacement findings.'})
  for a in atoms:
   if not a['retained']: continue
   for pid in a['passage_ids']:
    span=v['passages'][pid]; doc=v['retrievals'][span['source_index']]
    assert span['text'] in doc['text'] and s.digest(doc['text'])==doc['content_sha256'] and span['content_sha256']==doc['content_sha256']
    citations.append({'id':v['id'],'atom_id':a['atom_id'],'path_id':a['path_id'],'passage_id':pid,'quote':span['text'],'section_context':span.get('section_context',[]),'content_sha256':doc['content_sha256'],'requested_url':doc['requested_url'],'final_url':doc['final_url'],'retrieved_at':doc['retrieved_at'],'source_kind':doc['source_kind'],'exact':True})
  if c.known(purpose):
   for pid in v['purpose']['passage_ids']:
    span=v['passages'][pid]; doc=v['retrievals'][span['source_index']]
    assert span['text'] in doc['text'] and s.digest(doc['text'])==doc['content_sha256']
    citations.append({'id':v['id'],'atom_id':'purpose','passage_id':pid,'quote':span['text'],'content_sha256':doc['content_sha256'],'exact':True})
  path_displays={path:[a for a in atoms if a['retained'] and a['path_id']==path] for path in sorted({a['path_id'] for a in atoms if a['retained']})}
  final.append({'id':v['id'],'app_name':v['app_name'],'findings':findings,'atoms':atoms,'path_displays':path_displays,'completeness_reviews':reviews,'buildability_unresolved_reason':unresolved,'failure':v['failure']})
 counts=Counter(f for v in final for f,x in v['findings'].items() if c.known(x))
 summary={'status':'PILOT FAIL','safe_to_scale':False,'run_id':d.name,'promoted_atoms':dict(promoted),'retained_atoms':dict(kept),'downgraded_atoms':dict(promoted-kept),
  'display_counts':dict(counts),'retained_display_fields':sum(counts.values()),'citations':len(citations),'exact_citations':len(citations),
  'source_capture_errors':captures,'search_attempts':sum(len(v['discovery']) for v in values),'search_successes':sum(bool(x['ok']) for v in values for x in v['discovery']),
  'page_attempts':sum(len(v['retrievals']) for v in values),'readable_pages':sum(bool(x['ok']) for v in values for x in v['retrievals']),
  'category_searches':dict(Counter(x['category'] for v in values for x in v['discovery'])),'failures':[{'id':v['id'],'failure':v['failure']} for v in values if v['failure']],
  'reason':'Primary inventory/path closure remains unproven; buildability cannot be derived. Path evidence supports partial investigation only.'}
 historical=[{'id':h['app_id'],'field':h['field'],'historical_value':h['final_value'],'pilot_value':v['findings'][h['field']],'same':h['final_value']==v['findings'][h['field']],'fresh_human_check':False} for h in s.read(s.ROOT/'data/stage03/human-review.json') for v in final if h['app_id']==v['id']]
 out=d/'primary-audit'
 for name,value in [('final-audited-results',final),('acceptance-decision',summary),('citation-quality',citations),('display-decisions',display_decisions),('integrity',integrity(d)),('historical-regression',historical)]: s.save(out/(name+'.json'),value,exclusive=True)
 print(summary)

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--run-id',required=True); parser.add_argument('--pack',nargs='*',type=int); args=parser.parse_args()
 d=s.ROOT/'data/correction'/args.run_id; values=[s.read(x) for x in sorted((d/'apps').glob('*.json'))]
 if args.pack is not None: pack([v for v in values if not args.pack or v['id'] in args.pack]); return
 assert [v['id'] for v in values]==c.PILOT; seal(d,values)

if __name__=='__main__': main()
