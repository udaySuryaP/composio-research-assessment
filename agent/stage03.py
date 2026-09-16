"""Offline Stage 03 preparation. No automated human judgments or final claims."""
import argparse
import copy
import csv
import hashlib
import json
import random
from datetime import datetime
from collections import Counter
from pathlib import Path
from agent import stage02 as s
from agent.stage02_audit import audit
from agent.schema import CLAIM_FIELDS

START = '0e4090c69242e0281338f97fc27c3ccd009aa51a'
BASE = 'stage02-full-fallback-20260916'
AUG = 'stage02-composio-augmentation-20260916'
OUT = s.ROOT / 'data/stage03'
FIELDS = ('auth_methods', 'access_model', 'api_available', 'api_types', 'mcp_available', 'buildability', 'primary_blocker')
QUESTIONS = {
 'auth_methods': 'Which methods authenticate the developer API? Distinguish end-user login and third-party examples.',
 'access_model': 'Can a developer obtain API access directly, or is payment, admin, partner or sales approval required?',
 'api_available': 'Does this product expose an inbound developer API? Outbound webhooks alone do not establish this.',
 'api_types': 'Which API protocols are explicitly documented for this product?',
 'mcp_available': 'Is an MCP server documented? Check publisher ownership; an app marketplace is not MCP.',
 'buildability': 'Considering auth, onboarding, gates, breadth and docs, is integration buildable, conditional, blocked or unknown?',
 'primary_blocker': 'What concrete restriction blocks integration, if any? Absence of evidence is not proof of no blocker.'}

def dump(path, value):
 path.parent.mkdir(parents=True, exist_ok=True)
 path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def baseline():
 apps = s.seeds()
 lock = s.read(s.ROOT/'data/stage02-input-lock.json')['identities']
 assert [(a['id'],a['name'],a['category']) for a in apps] == [(a['id'],a['name'],a['category']) for a in lock]
 for run in (BASE,AUG,'stage02-smoke-seeds-20260916','stage02-smoke-grounded-20260916'):
  result = audit(run)
  if result['errors']: raise ValueError(result['errors'])
 return apps, s.read(s.ROOT/'data/runs'/BASE/'first-pass.json')

def select_sample(apps):
 rng = random.Random(42)
 categories = sorted({a['category'] for a in apps})
 return [a['id'] for c in categories for a in rng.sample(sorted([a for a in apps if a['category']==c],key=lambda a:a['id']),2)]

def score(reviews, expected):
 expected = {r['item_id']:r for r in expected}
 seen=set(); paired=[]; unclear=0
 for r in reviews:
  key=r.get('item_id')
  if key not in expected or key in seen: raise ValueError('Unknown/duplicate review item')
  seen.add(key); original=expected[key]
  for f in ('app_id','field','first_pass_value','sample_kind'):
   if r.get(f)!=original[f]: raise ValueError('Review changed frozen item identity/value')
  if r.get('sample_kind')!='unbiased': continue
  if r.get('reviewer') and r.get('reviewer')!='Uday': continue
  if r.get('reviewed_at'):
   try:
    stamp=datetime.fromisoformat(r['reviewed_at'])
    if stamp.tzinfo is None: raise ValueError('Timestamp requires timezone')
   except (ValueError,TypeError): raise ValueError('Invalid review timestamp')
  if r.get('first_pass_correct')=='unclear' or r.get('final_correct')=='unclear' or r.get('source_status') in ('inaccessible','ambiguous','outdated','unclear'):
   unclear+=1; continue
  if not (r.get('reviewer')=='Uday' and r.get('reviewed_at') and r.get('source_status')=='usable' and r.get('observed_source_url') and r.get('notes') and r.get('observed_correct_value') is not None and r.get('final_value') is not None): continue
  if r.get('first_pass_correct') not in ('yes','no') or r.get('final_correct') not in ('yes','no'): continue
  if r['final_value'] != r['observed_correct_value']: raise ValueError('Final value must match observed value before scoring')
  if r['final_correct']!='yes': raise ValueError('Final judgment contradicts observed value')
  if (r['first_pass_value']==r['observed_correct_value']) != (r['first_pass_correct']=='yes'): raise ValueError('First-pass judgment contradicts observed value')
  if not s.valid_url(r['observed_source_url']): raise ValueError('Invalid observed source URL')
  paired.append(r)
 n=len(paired); first=sum(r['first_pass_correct']=='yes' for r in paired); final=sum(r['final_correct']=='yes' for r in paired)
 return {'scored_items':n,'first_pass_correct':first,'first_pass_denominator':n,'final_correct':final,'final_denominator':n,'first_pass_accuracy':first/n if n else None,'final_accuracy':final/n if n else None,'absolute_improvement':(final-first)/n if n else None,'unclear_unscored':unclear,'pending_items':len(expected)-n-unclear,'human_reviewed_apps':len({r['app_id'] for r in paired}),'limitation':'Only actual Uday judgments on the same unbiased paired claims are scored; no whole-dataset accuracy inference.'}

def validate_corrections(rows, corrections):
 by_id={r['id']:r for r in rows}; seen=set()
 for c in corrections:
  key=(c['app_id'],c['field'])
  if key in seen or c['app_id'] not in by_id or c['field'] not in CLAIM_FIELDS: raise ValueError('Invalid correction identity/field')
  seen.add(key)
  row=by_id[c['app_id']]
  if c['app_name']!=row['app_name'] or c['original_value']!=row[c['field']] or c['corrected_value']==c['original_value']: raise ValueError('Invalid original/corrected value')
  if c['method'] not in ('automated_verification','composio_augmentation','human_review') or not c['reason'] or not c['evidence'] or not c['timestamp']: raise ValueError('Incomplete correction provenance')
  candidate=copy.deepcopy(row); candidate[c['field']]=c['corrected_value']
  if s.validate_schema(candidate): raise ValueError('Correction violates canonical schema')

def apply_corrections(rows, corrections):
 validate_corrections(rows,corrections); result=copy.deepcopy(rows); by_id={r['id']:r for r in result}
 for c in corrections:
  row=by_id[c['app_id']]; row[c['field']]=c['corrected_value']; row['verification_status']='needs_verification'
  row['verification_notes'].append('Stage03 correction: '+c['reason'])
  row['evidence'].extend(c['evidence'])
 for row in result:
  if s.validate_schema(row): raise ValueError('Invalid resulting record')
 assert [(r['id'],r['app_name'],r['category']) for r in result]==[(r['id'],r['app_name'],r['category']) for r in rows]
 return result

def provisional_patterns(rows):
 fields=('auth_methods','access_model','api_available','api_types','api_breadth','mcp_available','buildability')
 counts={f:dict(Counter(v for r in rows for v in (r[f] if isinstance(r[f],list) else [r[f]]))) for f in fields}
 return {'status':'provisional_unverified','denominator':len(rows),'counts':counts,'array_count_note':'Auth and API type are multi-label app counts; totals may exceed 100. API breadth remains original free text; no guessed breadth buckets.','category_buildability':{c:dict(Counter(r['buildability'] for r in rows if r['category']==c)) for c in sorted({r['category'] for r in rows})},'insights':[],'caveat':'Final verified patterns and product conclusions withheld pending source verification and actual human review.'}

def prepare():
 apps,rows=baseline(); by_id={r['id']:r for r in rows}; app_by_id={a['id']:a for a in apps}
 ids=select_sample(apps)
 # Predeclared rotation of two bounded fields per app, independent of findings.
 worksheet=[]
 for index,app_id in enumerate(ids):
  row=by_id[app_id]
  for offset in (0,1):
   field=FIELDS[(index*2+offset)%len(FIELDS)]
   evidence=[e for e in row['evidence'] if e['field']==field]
   official=[e['final_url'] for e in evidence if e['source_kind']=='official']
   worksheet.append({'item_id':f'{app_id:03d}:{field}','sample_kind':'unbiased','app_id':app_id,'app_name':row['app_name'],'category':row['category'],'field':field,'first_pass_value':row[field],'first_pass_evidence_urls':[e['final_url'] for e in evidence],'official_source_candidates':list(dict.fromkeys(official+app_by_id[app_id]['docs_urls'])),'source_candidate_note':'Stage02 official attribution/seed; Uday must confirm product identity and ownership. Candidate may not support this field.','what_to_verify':QUESTIONS[field],'reviewer':None,'reviewed_at':None,'source_status':None,'observed_source_url':None,'observed_correct_value':None,'first_pass_correct':None,'final_value':None,'final_correct':None,'correction_reason':None,'notes':None})
 OUT.mkdir(parents=True,exist_ok=True)
 review_path=OUT/'human-review.json'
 if review_path.exists() and s.read(review_path)!=worksheet: raise ValueError('Existing worksheet differs; refusing to overwrite judgments')
 dump(review_path,worksheet)
 dump(OUT/'sample-manifest.json',{'seed':42,'algorithm':'Python Random(42), categories lexically sorted, numeric ID order within category, sample 2/category','selected_ids':ids,'categories':sorted({a['category'] for a in apps}),'review_fields':list(FIELDS),'field_rule':'Two fields per app, fixed rotation FIELDS[(2*index+offset)%7], offsets 0 and 1','review_items':len(worksheet),'declared_before_judgments':True})
 flags=s.read(s.ROOT/'data/runs'/BASE/'quality-flags.json')
 challenge=[]
 for entry in flags:
  if any(f['code']!='low_confidence' for f in entry['flags']): challenge.append({'app_id':entry['id'],'app_name':by_id[entry['id']]['app_name'],'flags':entry['flags'],'sample_kind':'challenge_unscored','semantic_error_confirmed':False})
 failures=s.read(s.ROOT/'data/runs'/BASE/'failures.json')
 aug=s.read(s.ROOT/'data/runs'/AUG/'first-pass.json')
 differences=[{'app_id':r['id'],'field':f,'first_pass_value':by_id[r['id']][f],'augmentation_candidate':r[f],'evidence':[e for e in r['evidence'] if e['field']==f],'status':'unverified_candidate'} for r in aug for f in CLAIM_FIELDS if r[f]!=by_id[r['id']][f]]
 dump(OUT/'challenge-set.json',{'scored':False,'quality_candidates':challenge,'hard_failures':failures,'augmentation_disagreements':differences,'all_unknown_ids':[r['id'] for r in rows if all(r[f] in ('unknown','unclear',['unknown']) for f in FIELDS)]})
 correction_path=OUT/'correction-log.json'
 if not correction_path.exists(): dump(correction_path,[])
 corrections=s.read(correction_path); final=apply_corrections(rows,corrections)
 dump(OUT/'prepared-results.json',final)
 with (OUT/'prepared-results.csv').open('w',newline='',encoding='utf-8') as handle:
  writer=csv.DictWriter(handle,fieldnames=list(final[0])); writer.writeheader()
  writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in final)
 dump(OUT/'human-review-summary.json',score(worksheet,worksheet))
 dump(OUT/'provisional-patterns.json',provisional_patterns(final))
 dump(OUT/'failure-analysis.json',{'status':'pre_human_review','observations':[{'pattern':'Extraction hard failure','examples':failures,'detection':'Frozen failures.json','mitigation':'Keep explicit unknown record; SendGrid augmentation is an unverified candidate.'},{'pattern':'Grounding/negative-claim quality flags','examples':challenge,'detection':'Frozen deterministic quality flags','mitigation':'Targeted challenge review; flags alone are not semantic errors.'}],'semantic_failure_modes':[]})
 snapshots={run:s.read(s.ROOT/'data/runs'/run/'freeze.json') for run in (BASE,AUG,'stage02-smoke-seeds-20260916','stage02-smoke-grounded-20260916')}
 dump(OUT/'baseline-integrity.json',{'canonical_commit':START,'identities':100,'frozen_snapshots':snapshots,'audit_errors':[]})
 text=['# Uday review — pending','', 'Inspect the official page yourself. Confirm product identity and source ownership. Answer observed value, yes/no/unclear for first pass, proposed final value, yes/no/unclear for final, source URL and notes. Use unclear/unscored for inaccessible, ambiguous or outdated pages. Reviewer and timestamp remain blank until your review.','']
 for index,item in enumerate(worksheet):
  text += [f"## Item {index+1}: {item['item_id']}",f"App: {item['app_name']} ({item['category']})",f"Field: {item['field']}",f"First-pass finding: {json.dumps(item['first_pass_value'])}",f"First-pass evidence: {', '.join(item['first_pass_evidence_urls']) or 'None'}",'Official source candidates: '+', '.join(item['official_source_candidates']), 'What to verify: '+item['what_to_verify'],'']
 (OUT/'REVIEW.md').write_text('\n'.join(text),encoding='utf-8')
 print(json.dumps({'status':'BLOCKED','apps_sampled':len(ids),'categories':10,'review_items':len(worksheet),'scored_items':0,'corrections':len(corrections)}))

def main():
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('command',choices=['prepare','check']); args=parser.parse_args()
 if args.command=='prepare': prepare()
 else:
  apps,rows=baseline(); validate_corrections(rows,s.read(OUT/'correction-log.json'))
  prepared=s.read(OUT/'prepared-results.json')
  if prepared!=apply_corrections(rows,s.read(OUT/'correction-log.json')): raise ValueError('Silent prepared-result mutation')
  if len(prepared)!=100: raise ValueError('Identity count')
  print('All four freezes, 100 identities, correction audit and prepared dataset verified')
if __name__=='__main__': main()
