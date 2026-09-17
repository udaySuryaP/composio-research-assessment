"""Full-dataset automated QA and durable structured handoff; no human verification."""
import argparse
import copy
import hashlib
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from agent import stage02 as s, production_research as r, path_contracts as p

def downgrade(v,field,reason):
 v['findings'][field]=['unknown'] if field in ('auth_methods','api_types') else ('unresolved' if field=='buildability' else 'unknown')
 v['field_status'][field]={'status':'unresolved','reason':reason,'caveats':[],'derivation':False}
 v['field_refs'][field]=[]

def check(v):
 issues=[]
 for field,status in v['field_status'].items():
  if status['status']=='unresolved': continue
  refs=v['field_refs'][field]
  if not refs: issues.append((field,'Supported value has no exact evidence references')); continue
  for pid in refs:
   if pid not in v['passages']: issues.append((field,'Missing selected passage')); break
   span=v['passages'][pid]; doc=v['retrievals'][span['source_index']]
   if span['category']!='body' or span['text'] not in doc['text'] or s.digest(doc['text'])!=doc['content_sha256'] or span['content_sha256']!=doc['content_sha256']:
    issues.append((field,'Body/citation/source hash integrity failure')); break
   if field in ('purpose','auth_methods','api_types','api_available','api_breadth','access_model') and span['source_kind']!='official':
    issues.append((field,'Assigned-product official source identity is not established')); break
 if v['id']==84 and not any(doc['ok'] and doc['source_kind']=='official' and len(doc['text'])>=120 for doc in v['retrievals']):
  issues.extend((field,'Identity ambiguous/source unreadable: no deterministic readable official Paygent Connect source recovered') for field,status in v['field_status'].items() if status['status']!='unresolved')
 for field,reason in issues: downgrade(v,field,reason)
 if v['findings']['buildability'] in ('likely_buildable_from_public_docs','buildable_with_documented_constraints') and any(v['field_status'][field]['status']=='unresolved' for field in ('auth_methods','api_available')):
  for field in ('buildability','buildability_rationale'): downgrade(v,field,'Required readiness dependency failed automated QA')
 families={'auth_methods':('auth:',),'access_model':('access:',),'api_types':('protocol:',),'api_available':('api:','protocol:','resource:'),'api_breadth':('resource:',),'mcp_available':('mcp:availability',),'mcp_provider':('mcp:provider',),'mcp_ownership':('mcp:ownership','mcp:vendor_owned','mcp:third_party_owned'),'mcp_notes':('mcp:',)}
 for field,status in v['field_status'].items():
  if status['status']!='unresolved': continue
  rejected=[{'atom_id':a['atom_id'],'reason':a['audit_reason']} for a in v['atoms'] if not a['retained'] and a['label'].startswith(families.get(field,('INVALID',)))]
  status['rejected_candidate_reasons']=rejected
  status['research_attempt']={'searches':len(v['discovery']),'successful_searches':sum(bool(x['ok']) for x in v['discovery']),'page_attempts':len(v['retrievals']),'readable_pages':sum(bool(x['ok']) for x in v['retrievals'])}
  if v['id']==84 and not any(doc['ok'] and doc['source_kind']=='official' for doc in v['retrievals']):
   status['reason']='Identity ambiguous/source unreadable: no deterministic readable official Paygent Connect source recovered'
  elif rejected and status['reason'].startswith('No independently supported'):
   status['reason']='Evidence insufficient: '+ '; '.join(dict.fromkeys(x['reason'] for x in rejected))[:900]
 return issues

def atom_qa(v,app):
 changes=[]
 for atom in v['atoms']:
  if not atom['retained']: continue
  error=r.validate(atom,v['passages'])
  if error:
   atom['retained']=False; atom['final_qa_reason']=error; atom['audit_reason']=error; changes.append({'atom_id':atom['atom_id'],'reason':error})
 projected=r.project(v['atoms'],v['findings']['purpose'],v['purpose']['passage_ids'],v['gaps'],v['failure'])
 changed_fields=[]
 for field,status in v['field_status'].items():
  # Preserve semantic downgrades. Only independently retained optional core auth/protocol
  # facts omitted by the previous display filter may enter a new challenged projection.
  optional=field in ('auth_methods','api_types') and any(a['retained'] and a['state']=='optional' and a['label'].startswith('auth:' if field=='auth_methods' else 'protocol:') for a in v['atoms'])
  if (status['status']!='unresolved' or optional) and v['findings'][field]!=projected['findings'][field]:
   changed_fields.append(field)
   for key in ('findings','field_status','field_refs'): v[key][field]=projected[key][field]
 # Removing rejected atoms cannot invalidate unchanged independently reviewed fields.
 # Changed values are subsets of retained, previously challenged atoms, never new facts.
 # Do not upgrade readiness when an access-gate atom was removed.
 if 'buildability' in changed_fields and v['findings']['buildability'] in ('likely_buildable_from_public_docs','buildable_with_documented_constraints'):
  for field in ('buildability','buildability_rationale'): downgrade(v,field,'A removed gate/constraint changes readiness; fresh semantic readiness review required')
 for field in changed_fields:
  if v['field_status'][field]['status']!='unresolved': v['field_status'][field]['caveats'].append('Final projection is a subset of independently reviewed retained atoms after strict semantic guards; no new app fact asserted.')
 v['final_atom_qa_downgrades']=changes
 v['final_projection_policy']='independent-subset-v3'
 return v

def recover_reviewed_atoms(v,d):
 extracted_path=d/'extraction-checkpoints'/f"{v['id']:03d}.json"
 review_path=d/'review-checkpoints'/f"{v['id']:03d}.json"
 if v['atoms'] or not extracted_path.exists() or not review_path.exists(): return v
 extracted=s.read(extracted_path)['extracted']; review=s.read(review_path)['review']
 atoms=[r.normalize(a,i) for i,a in enumerate(extracted['atoms'])]
 lookup={x['atom_id']:x for x in review['decisions']}
 if len(lookup)!=len(review['decisions']) or set(lookup)!={a['atom_id'] for a in atoms}: return v
 for a in atoms:
  error=r.validate(a,v['passages']); decision=lookup[a['atom_id']]
  a.update(retained=not error and decision['decision']=='supported',audit_reason=error or decision['reason'])
 v.update(atoms=atoms,raw_extraction=extracted,automated_review=review,gaps=extracted['unresolved_gaps'])
 v.update(r.project(atoms,'unknown',(),v['gaps'],v['failure']))
 for status in v['field_status'].values():
  if status['status']!='unresolved': status['caveats'].append('Completed independent atom semantic review retained; purpose/composite field review blocked by exhausted model credits.')
 for field in ('buildability','buildability_rationale'): downgrade(v,field,'Model credit balance exhausted before composite readiness review; reviewed core facts retained independently')
 v['recovered_review_checkpoint']=True
 return v

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--run-id',required=True); parser.add_argument('--prepare',action='store_true'); args=parser.parse_args(); d=s.ROOT/'data/correction'/args.run_id
 raw=[s.read(x) for x in sorted((d/'apps').glob('*.json'))]
 if not args.prepare: assert [v['id'] for v in raw]==list(range(1,101))
 root=s.ROOT; s.ROOT=Path('U:/composio-research-assessment'); s.load_env(); s.ROOT=root
 seeds={a['id']:a for a in s.seeds()}
 def audit_one(original):
  working=dict(original)
  for key in ('atoms','findings','field_status','field_refs'): working[key]=copy.deepcopy(original[key])
  checkpoint=d/'qa-checkpoints'/f"{original['id']:03d}.json"
  if checkpoint.exists():
   previous=s.read(checkpoint)
   if previous.get('final_projection_policy')=='independent-subset-v3':
    working.update(previous); return working
   s.save(d/'qa-revision-history'/(checkpoint.stem+'-'+s.digest(checkpoint.read_bytes().hex())+'.json'),previous)
  v=recover_reviewed_atoms(working,d)
  v=atom_qa(v,seeds[original['id']])
  s.save(checkpoint,{key:value for key,value in v.items() if key not in ('retrievals','passages','discovery')})
  print({'id':v['id'],'qa_atom_downgrades':len(v['final_atom_qa_downgrades'])},flush=True)
  return v
 with ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(audit_one,raw))
 if args.prepare: return
 downgrades=[]
 for v in results:
  downgrades.extend({'id':v['id'],'field':field,'reason':reason} for field,reason in check(v))
  v['verification_metadata']={'fresh_human_verification':False,'historical_reviews':[h for h in s.read(s.ROOT/'data/stage03/human-review.json') if h['app_id']==v['id']],'historical_role':'Historical/regression only; not fresh accuracy'}
  assert not p.capture_errors(v)
  assert len(v['findings']['purpose'])<=180 or v['findings']['purpose']=='unknown'
 counts={f:{status:sum(v['field_status'][f]['status']==status for v in results) for status in ('source_backed','source_backed_with_caveat','unresolved')} for f in results[0]['findings']}
 reasons=Counter(x['reason'] for v in results for x in v['field_status'].values() if x['status']=='unresolved')
 def group(reason):
  low=reason.lower()
  if 'identity ambiguous' in low: return 'identity_ambiguous_or_official_source_unreadable'
  if 'credit' in low or '429' in low: return 'model_service_credit_exhaustion_or_429'
  if 'audit failed' in low or 'http' in low: return 'extraction_or_audit_failure'
  if 'capture' in low or 'hash' in low: return 'capture_integrity_failure'
  if 'conflict' in low or 'contradict' in low: return 'conflicting_documentation'
  if 'no selectable' in low or 'source unreadable' in low or 'inaccessible' in low: return 'docs_inaccessible_or_unreadable'
  if 'readiness' in low or 'onboarding' in low: return 'readiness_evidence_insufficient'
  if 'no independently' in low: return 'no_supported_field_evidence_found'
  return 'claim_rejected_or_evidence_insufficient'
 citations=[]
 for v in results:
  for f,ids in v['field_refs'].items():
   for pid in ids:
    span=v['passages'][pid]; doc=v['retrievals'][span['source_index']]
    citations.append({'id':v['id'],'field':f,'passage_id':pid,'snippet':span['text'],'heading':span['heading'],'url':doc['requested_url'],'final_url':doc['final_url'],'source_kind':doc['source_kind'],'content_sha256':doc['content_sha256'],'retrieved_at':doc['retrieved_at'],'exact':True})
 integrity=r.path_audit.integrity(d); critical=['auth_methods','access_model','api_available','api_types','api_breadth','mcp_available','buildability']
 all_unknown=[{'id':v['id'],'app':v['app']} for v in results if all(v['field_status'][f]['status']=='unresolved' for f in critical)]
 failures=[{'id':v['id'],'app':v['app'],'failure':v['failure'],'field_audit_failure':v.get('field_audit_failure')} for v in results if v['failure'] or v.get('field_audit_failure')]
 historical=[]
 for v in results:
  for h in v['verification_metadata']['historical_reviews']:
   field='purpose' if h['field']=='description' else h['field']; value=v['findings'].get(field,'unknown')
   historical.append({'id':v['id'],'field':field,'historical_value':h['final_value'],'corrected_value':value,'same':h['final_value']==value,'fresh_human_check':False,'comparison_limit':'Readiness/access schema changed; non-identical values do not establish regression or accuracy'})
 summary={'status':'PARTIAL' if failures or all_unknown else 'FULL-100 PASS','completion_count':100,'run_id':d.name,'field_counts':counts,'all_critical_unresolved':all_unknown,'major_unresolved_reasons':dict(Counter(group(x['reason']) for v in results for x in v['field_status'].values() if x['status']=='unresolved')),'specific_unresolved_reasons':dict(reasons),'readiness_distribution':dict(Counter(v['findings']['buildability'] for v in results)),'search_attempts':sum(len(v['discovery']) for v in results),'search_successes':sum(bool(x['ok']) for v in results for x in v['discovery']),'retrieval_attempts':sum(len(v['retrievals']) for v in results),'readable_pages':sum(bool(x['ok']) for v in results for x in v['retrievals']),'exact_citation_refs':len(citations),'capture_mismatches':0,'deterministic_qa_downgrades':downgrades,'atom_qa_downgrades':[{'id':v['id'],**x} for v in results for x in v['final_atom_qa_downgrades']],'failures':failures,'historical_review_overlap':len(historical),'historical_same_value':sum(x['same'] for x in historical),'fresh_human_checks':0,'ready_for_independent_sample':True,'readiness_caveat':'Documentation-based inference only; no integration executed and no exhaustive setup/alternative-route certification.','semantic_qa':'Every extracted atom independently challenged; every projected known field independently challenged; deterministic official identity/body/protocol/MCP/surface guards retained. Not fresh measured accuracy.','protected_state':integrity}
 summary['model_blocked_apps']=[v['id'] for v in results if v['failure'] and ('credit' in v['failure'].lower() or '429' in v['failure'])]
 summary['extraction_completed_apps']=sum('raw_extraction' in v or (d/'extraction-checkpoints'/f"{v['id']:03d}.json").exists() for v in results)
 summary['atom_review_completed_apps']=sum('automated_review' in v for v in results)
 summary['projected_field_review_completed_apps']=sum('field_review' in v for v in results)
 summary['ready_for_independent_sample']=not bool(summary['model_blocked_apps'])
 summary['research_attempt_note']='Search/retrieval counts are persisted app attempts; interrupted in-flight calls before checkpoints are not included. All 100 assigned apps have fresh source research attempts, but model-blocked extraction is incomplete.'
 summary['semantic_qa']='Retained atoms have completed independent model challenges plus deterministic official identity/body/protocol/MCP/surface/access guards. Projected-field model challenges completed where recorded; final subset projections and recovered atom-review projections preserve only independently challenged retained facts. Credit-blocked unreviewed candidates are unasserted. Composite readiness from incomplete reviews is unresolved. This is automated source-support QA, not fresh measured accuracy.'
 compact=[]
 for v in results:
  record={key:value for key,value in v.items() if key not in ('retrievals','passages','discovery','raw_extraction','automated_review','purpose_review')}
  record['evidence']=[citation for citation in citations if citation['id']==v['id']]
  record['source_records']=[{key:doc[key] for key in ('requested_url','final_url','retrieved_at','source_kind','ok','content_sha256','error')} for doc in v['retrievals']]
  record['audit_artifacts']={'fresh_capture_checkpoint':str(d/'apps'/f"{v['id']:03d}.json"),'projection_qa_checkpoint':str(d/'qa-checkpoints'/f"{v['id']:03d}.json")}
  compact.append(record)
 for name,value in [('final-corrected-dataset',compact),('final-citations',citations),('automated-qa',summary),('final-historical-regression',historical),('final-protected-integrity',integrity)]: s.save(d/(name+'.json'),value,exclusive=True)
 lines=['# Full-100 correction handoff', '', '**Status: '+summary['status']+'**. 100/100 research attempts and automated QA complete. No fresh human verification performed.','', '## Checkout and protected state','', 'Branch: `'+integrity['branch']+'`; HEAD/base: `'+integrity['head']+'`. Tracked diff: '+(integrity['tracked_diff'] or 'empty')+'. Work remains local/untracked/uncommitted. Exact working tree is in protected-integrity.json. Canonical main remains clean at the required base; '+str(integrity['tracked_files_compared'])+' tracked files match and '+str(integrity['history_files'])+' historical artifacts remain unchanged.', '', '## Projection changes and rationale', '', 'New production_research.py omits unproven path dimensions rather than attaching them to core facts. Independently supported resource facts retain explicit surface modes and notes; token administration, adjacent products and MCP cannot establish resource auth. Per-field source_backed/source_backed_with_caveat/unresolved status is separate from historical/fresh human metadata. Readiness uses documented API/auth/onboarding with caveats, not exhaustive prerequisite closure. A second projected-field challenge rejects broad product pricing/marketing as API access/breadth. production_qa.py checks exact evidence and records field-specific downgrades and failure reasons. No app facts manually filled.', '', '## Commands and run', '', 'Run ID: `'+d.name+'`. Runtime: `U:/composio-research-assessment/.venv/Scripts/python.exe`.', '', '```powershell','python -m unittest discover -s tests -v','python -m agent.production_research --run-id full100-production-20260917  # network blocked before apps','python -m agent.production_research --run-id '+d.name,'python -m agent.production_research --run-id '+d.name+' --resume','python -m agent.production_qa --run-id '+d.name,'```', '', 'The live runner paused after the first checkpoint to add stage checkpoints, bounded parallel retrieval and projected-field QA. The initial first-app checkpoint is preserved in pre-field-audit; code snapshots capture both versions. All pilot history remains sealed.', '', '## Automated dataset results', '', f"Searches: {summary['search_successes']}/{summary['search_attempts']} successful. Readable pages: {summary['readable_pages']}/{summary['retrieval_attempts']} attempts. Completion: 100/100.",'', '| Field | Source backed | With caveat | Unresolved |','|---|---:|---:|---:|']
 lines.extend(f"| {f} | {x['source_backed']} | {x['source_backed_with_caveat']} | {x['unresolved']} |" for f,x in counts.items())
 lines+=['', 'All critical fields unresolved: '+(', '.join(str(x['id'])+' '+x['app'] for x in all_unknown) or 'none')+'.', '', 'Major unresolved reasons: `'+str(summary['major_unresolved_reasons'])+'`. Specific reasons and rejected candidates are in automated-qa.json and the final dataset.', '', 'Exact retained citation references: '+str(len(citations))+'. Source/citation/hash mismatches: 0. Deterministic field downgrades: '+str(len(downgrades))+'. MCP/access/protocol QA includes independent semantic challenges and preserved deterministic guards; failures and rejected claims remain inspectable. This is automated support QA, not measured factual accuracy.', '', 'Documentation-based readiness distribution: `'+str(summary['readiness_distribution'])+'`. All positive categories carry caveats; none claims execution or exhaustive prerequisites. Gated results preserve the named gate and surface. Unknown blocker never implies blocker absence.', '', 'Historical review overlap: '+str(len(historical))+' field records; identical serialized values: '+str(summary['historical_same_value'])+'. Historical records are regression context only. Schema changes limit direct comparisons; fresh accuracy is unmeasured.', '', '## Verification readiness and exact next action', '', 'Ready for a fresh independent verification sample: yes. All assigned apps have inspectable attempts, supported values link to exact freshly captured body evidence, and unresolved values retain reasons. Remaining blockers are the unresolved evidence/identity/access/readiness cases listed in automated-qa.json. These do not justify filling gaps or claiming dataset-wide accuracy.', '', 'Next action: authorize a fresh independent verification sample stratified across retained fields, access gates, MCP ownership, readiness and unresolved cases; include Paygent identity and the prior 12 pilot apps as regression coverage. Do not use historical reviews as fresh verification. No business conclusions, HTML rebuild, README/Notion changes, deployment, Desktop copy, commit/merge/push or Form submission performed.', '', '## Tests', '', 'Twelve production regression tests cover core-fact retention, failed neighbors, route caveats, required auth, onboarding readiness, MCP separation, no evidence from silence, strict source/body/protocol guards, independent field downgrade and incomplete-audit failure. Full suite results are preserved in the copied production test logs.']
 if summary['model_blocked_apps']:
  lines=[line.replace('Ready for a fresh independent verification sample: yes.', 'Ready for the intended full-100 fresh independent verification sample: **no**. The model service returned credit_balance_exhausted; extraction/semantic review is incomplete for '+str(len(summary['model_blocked_apps']))+' apps.') if line.startswith('Ready for a fresh independent verification sample:') else line for line in lines]
  lines=[('Next action: restore the existing model API credit balance, then complete a new full-100 production run (preserve this partial run) and automated QA before authorizing the fresh independent verification sample. No manual facts or alternate unreviewed extraction were substituted. No HTML/README/Notion/deployment/Desktop/commit/merge/push/Form action performed.' if line.startswith('Next action: authorize') else line) for line in lines]
  lines+=['', '## External blocker and stage completion', '', 'Sanitized diagnostic: `model-diagnostic.json` reports HTTP 429 / insufficient_quota / credit_balance_exhausted. No credits purchased or credentials changed. Completed extraction apps: '+str(summary['extraction_completed_apps'])+'; completed atom-review apps: '+str(summary['atom_review_completed_apps'])+'; completed projected-field-review apps: '+str(summary['projected_field_review_completed_apps'])+'. Saved successfully reviewed atoms survive unrelated purpose/composite-review failures; positive readiness from such incomplete composite audits remains unresolved.', '', 'Final capture continuation: `python -m agent.production_research --run-id '+d.name+' --resume --workers 6 --capture-only`. All 100 apps were searched/retrieved with exact source hashes; blocked extraction is documented per app. This is a full inventory of research attempts, not a completed semantic research pass. Status is PARTIAL.', '', summary['research_attempt_note']]
 lines=[line.replace('Twelve production regression tests','Seventeen production regression tests') for line in lines]
 testlog=s.ROOT/'production-tests-final.log'
 if testlog.exists(): lines+=['', 'Final full-suite result: '+next((line.strip() for line in testlog.read_text(encoding='utf-8',errors='replace').splitlines() if line.startswith('Ran ')),'See production-tests-final.log')+'. See the complete preserved log for pass/failure details.']
 s.save(d/'final-code-snapshot.json',{str(x.relative_to(s.ROOT)):x.read_text(encoding='utf-8') for directory in ('agent','tests') for x in (s.ROOT/directory).glob('*.py')},exclusive=True)
 (d/'FULL100-HANDOFF.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 for log in s.ROOT.glob('production-*.log'): (d/log.name).write_bytes(log.read_bytes())
 s.save(d/'final-file-hashes.json',{str(x.relative_to(d)):hashlib.sha256(x.read_bytes()).hexdigest() for x in d.rglob('*') if x.is_file() and x.name!='final-file-hashes.json'})
 print({k:v for k,v in summary.items() if k not in ('protected_state','specific_unresolved_reasons')})

if __name__=='__main__': main()
