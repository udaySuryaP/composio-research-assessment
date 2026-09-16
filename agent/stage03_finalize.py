"""Reproduce Stage03 verified-only projection and coverage from actual reviews/checks.

Unreviewed first-pass claims are preserved in frozen runs and explicit abstention logs,
not promoted into the verified view. No human judgments are generated here.
"""
import copy
import csv
import hashlib
import json
from collections import Counter
from agent import stage03 as t
from agent.schema import CLAIM_FIELDS

UNKNOWN=('unknown','unclear',['unknown'])
POLICY={'version':1,'rule':'Only completed actual Uday usable-source claims, their explicit supporting rationale, and documented targeted official-source checks enter the verified view. Unchecked first-pass claims become explicit unknowns with automated abstention entries. This is a coverage decision, not a declaration that the original claim was false.','sample_denominator_rule':'The same complete actual human yes/no paired claims; actual unclear source judgments excluded. Tests allow lower final accuracy; final values must match recorded judgments.','source_metadata_rule':'Human inspection times, verbatim quotes and captured hashes remain empty when not supplied. Targeted source hashes cover only recorded short excerpts.','coverage_unit':'Claim-level verification; no whole record marked human_audited from two sampled fields.'}

def known(value):return value not in UNKNOWN

def validate_sample(apps,rows,definitions,manifest):
 ids=t.select_sample(apps)
 expected=[(i,t.FIELDS[(index*2+offset)%len(t.FIELDS)]) for index,i in enumerate(ids) for offset in (0,1)]
 if [(r['app_id'],r['field']) for r in definitions]!=expected:raise ValueError('Predeclared sample altered')
 if manifest['seed']!=42 or manifest['selected_ids']!=ids or manifest['review_items']!=40:raise ValueError('Manifest altered')
 for r in definitions:
  row=rows[r['app_id']-1]
  if r['first_pass_value']!=row[r['field']] or r['app_name']!=row['app_name'] or r['category']!=row['category'] or r['sample_kind']!='unbiased':raise ValueError('Sample differs from frozen first pass')

def claim_map(rows,reviews,checks,corrections):
 result={}
 for r in reviews:
  if r['reviewer']=='Uday' and r['source_status']=='usable' and r['final_correct'] in ('yes','no') and r['final_value'] is not None:
   evidence=[dict(evidence_id='human-report-'+r['item_id']+'-'+str(index+1),field=r['field'],claim=json.dumps(r['final_value']) if isinstance(r['final_value'],list) else r['final_value'],url=url,final_url=url,source_kind='official',retrieved_at='',content_sha256='',quote='',supports_claim='yes') for index,url in enumerate(r.get('observed_source_urls',[r['observed_source_url']]))]
   result[r['app_id'],r['field']]={'value':r['final_value'],'method':'human_review','evidence':evidence,'review_item_id':r['item_id'],'notes':r['notes']}
 for c in corrections:
  if c.get('supporting_field_note') and c['method']=='human_review':
   result[c['app_id'],c['field']]={'value':c['corrected_value'],'method':'human_review','evidence':c['evidence'],'review_item_id':c['review_item_id'],'notes':c['reason']}
 for c in checks:
  key=(c['app_id'],c['field'])
  if key in result and result[key]['value']!=c['value']:raise ValueError('Human/automated disagreement requires adjudication')
  if key not in result:result[key]={'value':c['value'],'method':c['method'],'evidence':c['evidence'],'source_id':c['source_id'],'notes':c['reason']}
 return result

def sources_valid(checks,sources):
 by_id={s['source_id']:s for s in sources}
 for c in checks:
  source=by_id[c['source_id']]
  if hashlib.sha256(source['observed_excerpt'].encode()).hexdigest()!=source['excerpt_sha256']:raise ValueError('Targeted excerpt changed')
  for e in c['evidence']:
   if e['quote'] not in source['observed_excerpt'] or e['content_sha256']!=source['excerpt_sha256'] or e['final_url']!=source['final_url']:raise ValueError('Targeted source provenance mismatch')

def build(rows,reviews,checks,corrections,timestamp):
 active=claim_map(rows,reviews,checks,corrections)
 unclear_reviews={(r['app_id'],r['field']):r for r in reviews if r['reviewer']=='Uday' and r['source_status']=='unclear'}
 log=copy.deepcopy([c for c in corrections if not c.get('abstention')]);keys={(c['app_id'],c['field']) for c in log}
 policy_text=json.dumps(POLICY,sort_keys=True)
 for row in rows:
  for field in CLAIM_FIELDS:
   key=(row['id'],field)
   if key in active or not known(row[field]):continue
   if key in keys:raise ValueError('Unchecked correction without a verification decision')
   blank=['unknown'] if isinstance(row[field],list) else 'unknown'
   reason='Unchecked first-pass claim withheld from verified view. No independent Stage03 source judgment exists for this field; retain original as a research lead, not verified truth.'
   e=dict(evidence_id='stage03-coverage-'+str(row['id'])+'-'+field,field=field,claim='unknown',url='repository:data/stage03/verification-policy.json',final_url='repository:data/stage03/verification-policy.json',source_kind='unknown',retrieved_at='',content_sha256=hashlib.sha256(policy_text.encode()).hexdigest(),quote=POLICY['rule'],supports_claim='unclear')
   log.append(dict(app_id=row['id'],app_name=row['app_name'],field=field,original_value=row[field],corrected_value=blank,reason=reason,evidence=[e],method='automated_verification',timestamp=timestamp,abstention=True,semantic_error_confirmed=False,first_pass_locator=f'data/runs/{t.BASE}/apps/{row["id"]:03d}.json',first_pass_sha256=hashlib.sha256((t.s.ROOT/'data/runs'/t.BASE/'apps'/f'{row["id"]:03d}.json').read_bytes()).hexdigest()))
 projected=t.apply_corrections(rows,log)
 matrix=[]
 for row in projected:
  row['evidence']=[]
  row['run_id']='stage03-verification-pattern-analysis'
  row['verification_status']='needs_verification'
  row['verification_notes'].append('Stage03 verified-only view: unchecked claims explicitly unknown; see claim-verification.json and frozen first pass.')
  for field in CLAIM_FIELDS:
   key=(row['id'],field);check=active.get(key);unclear=unclear_reviews.get(key)
   if check:
    row[field]=copy.deepcopy(check['value']);row['evidence'].extend(copy.deepcopy(check['evidence']))
   elif known(row[field]):raise ValueError('Unverified value entered projection')
   matrix.append({'app_id':row['id'],'app_name':row['app_name'],'category':row['category'],'field':field,'first_pass_value':rows[row['id']-1][field],'final_value':row[field],'status':'checked' if check else ('unclear' if unclear else 'unresolved'),'method':check['method'] if check else ('human_review' if unclear else None),'review_item_id':check.get('review_item_id') if check else (unclear['item_id'] if unclear else None),'source_id':check.get('source_id') if check else None,'evidence_ids':[e['evidence_id'] for e in check['evidence']] if check else [],'limitation':check['notes'] if check else (unclear['notes'] if unclear else 'No independent claim-level Stage03 verification; explicit unknown.')})
  row['research_confidence']='medium' if any(known(row[f]) for f in t.FIELDS) else 'unknown'
  if t.s.validate_schema(row):raise ValueError('Invalid projected schema')
 return projected,log,matrix

def tally(rows,field):
 values=Counter(v for row in rows for v in (row[field] if isinstance(row[field],list) else [row[field]]))
 return {v:{'count':n,'denominator':len(rows),'percent':100*n/len(rows) if rows else None} for v,n in sorted(values.items())}

def patterns(rows,matrix,reviews,corrections):
 checked={(c['app_id'],c['field']) for c in matrix if c['status']=='checked'}
 humans=[r for r in reviews if r['reviewer']=='Uday' and r['source_status']=='usable' and r['final_correct'] in ('yes','no')]
 human_by_field={f:[r for r in humans if r['field']==f] for f in t.FIELDS}
 stats={f:{'claims':len(items),'reviewed_claims':sum(r['field']==f and r['reviewer']=='Uday' for r in reviews),'unclear_claims':sum(r['field']==f and r['source_status']=='unclear' for r in reviews),'values':dict(Counter(v for r in items for v in (r['final_value'] if isinstance(r['final_value'],list) else [r['final_value']]))) } for f,items in human_by_field.items()}
 insights=[]
 def insight(key,conclusion,field,accept,limitation):
  items=human_by_field[field];selected=[r for r in items if accept(r['final_value'])]
  insights.append({'id':key,'conclusion':conclusion,'numerator':len(selected),'denominator':len(items),'percent':100*len(selected)/len(items) if items else None,'field':field,'reviewed_denominator':sum(r['field']==field and r['reviewer']=='Uday' for r in reviews),'unclear_claims':sum(r['field']==field and r['source_status']=='unclear' for r in reviews),'app_ids':[r['app_id'] for r in selected],'examples':[r['app_name'] for r in selected],'review_item_ids':[r['item_id'] for r in selected],'caveat':limitation+' Only the predeclared reviewed field subset, not all 100 apps; other unknown claims are excluded.'})
 insight('permission-gates','Plan authorization and administrator onboarding as integration work: admin permissions condition most resolved sampled access findings.','access_model',lambda v:v=='admin_approval','Internal versus public distribution paths can have additional gates; a single access enum does not capture every path.')
 insight('oauth-lifecycle','OAuth lifecycle support belongs in the reusable integration foundation: all resolved sampled auth findings include OAuth2.','auth_methods',lambda v:'oauth2' in v,'Auth values are multi-label; token use and token acquisition differ. This measures six sampled auth claims, not OAuth prevalence across the app list.')
 insight('rest-foundation','A REST connector foundation fits every resolved sampled API-type finding.','api_types',lambda v:'rest' in v,'This establishes documented REST, not absence of other protocols or sufficient endpoint breadth.')
 insight('official-mcp','Official MCP provides an integration path for resolved sampled MCP findings; missing evidence still requires abstention.','mcp_available',lambda v:v=='official','Three other sampled MCP claims remain unclear. Official MCP does not guarantee API feature parity, access eligibility or reduced implementation cost.')
 insight('buildable-with-constraints','Documented self-service workflows make all reviewed buildability examples buildable; production quotas and permissions still matter.','buildability',lambda v:v=='buildable','Includes Twilio trial restrictions and MrScraper quota/target-site constraints. No sandbox proof or integration implementation was performed.')
 critical_known=[sum(known(r[f]) for f in t.FIELDS) for r in rows]
 official={r['id'] for r in rows if any(e['source_kind']=='official' and e['supports_claim']=='yes' for e in r['evidence'])}
 changed={c['app_id'] for c in corrections if not c.get('abstention')}
 coverage={'total_apps':len(rows),'categories':len({r['category'] for r in rows}),'critical_claims':len(rows)*len(t.FIELDS),'checked_critical_claims':sum((r['id'],f) in checked for r in rows for f in t.FIELDS),'unresolved_critical_claims':sum(len(t.FIELDS)-n for n in critical_known),'fully_resolved':sum(n==len(t.FIELDS) for n in critical_known),'partially_resolved':sum(0<n<len(t.FIELDS) for n in critical_known),'all_unknown_critical':critical_known.count(0),'apps_with_usable_official_evidence':len(official),'apps_with_only_third_party_or_community_evidence':sum(bool(r['evidence']) and not any(e['source_kind']=='official' for e in r['evidence']) for r in rows),'apps_without_active_verified_evidence':sum(not r['evidence'] for r in rows),'human_reviewed_apps':len({r['app_id'] for r in reviews if r['reviewer']=='Uday'}),'human_reviewed_items':sum(r['reviewer']=='Uday' for r in reviews),'records_corrected_with_new_findings':len(changed),'original_hard_failures':1,'unresolved_hard_failure_records':sum(r['id']==40 and not any(known(r[f]) for f in t.FIELDS) for r in rows),'record_status_note':'No entire row is human-audited or fully verified; claim-level coverage governs.'}
 categories={c:{'denominator':sum(r['category']==c for r in rows),'buildability':dict(Counter(r['buildability'] for r in rows if r['category']==c)),'human_reviewed_apps':len({r['app_id'] for r in reviews if r['category']==c and r['reviewer']=='Uday'}),'claim_distributions':{f:tally([r for r in rows if r['category']==c],f) for f in ('auth_methods','access_model','api_available','api_types','api_breadth','mcp_available','buildability')}} for c in sorted({r['category'] for r in rows})}
 return {'status':'analysis_with_explicit_unresolved_claims','dataset':'verified-results.json','summary':coverage,'counts':{f:tally(rows,f) for f in ('auth_methods','access_model','api_available','api_types','api_breadth','mcp_available','buildability')},'auth_mixed':{'count':sum(len([v for v in r['auth_methods'] if v!='unknown'])>1 for r in rows),'denominator':len(rows)},'category_comparison':categories,'human_field_subsets':stats,'insights':insights,'limitations':['This verified-only view intentionally contains unknowns where independent Stage03 verification was not performed. Original first-pass findings remain immutable and available for further research.','Unknown is unresolved, not no API/no MCP/blocked.','Auth/API type distributions are multi-label app counts; sums may exceed 100.','No reviewed API-breadth rubric was supplied; all 100 breadth classifications stay unknown rather than guessed from free text.','Category cells have sparse checked coverage. Do not rank categories from missing values.','Human final correctness was reported alongside the proposed correction, not independently re-audited after a delay. The paired result measures those source judgments.']}

def expected_outputs(timestamp):
 apps,rows=t.baseline();definitions=t.s.read(t.OUT/'review-items.json');reviews=t.s.read(t.OUT/'human-review.json');checks=t.s.read(t.OUT/'automated-checks.json');sources=t.s.read(t.OUT/'targeted-source-excerpts.json');corrections=t.s.read(t.OUT/'correction-log.json')
 validate_sample(apps,rows,definitions,t.s.read(t.OUT/'sample-manifest.json'));sources_valid(checks,sources)
 human=t.score(reviews,definitions)
 if human['pending_items']:raise ValueError('Actual human sample incomplete')
 projected,log,matrix=build(rows,reviews,checks,corrections,timestamp)
 # No scored final judgment may refer to a value not actually in the projected dataset.
 for r in reviews:
  if r['source_status']=='usable' and r['final_value']!=projected[r['app_id']-1][r['field']]:raise ValueError('Scored final differs from actual final dataset')
 metrics=patterns(projected,matrix,reviews,log)
 metrics['human_accuracy']=human
 eligible=[r for r in reviews if r['source_status']=='usable' and r['first_pass_correct'] in ('yes','no') and r['final_correct'] in ('yes','no')]
 metrics['human_miss_breakdown']={'initial_unknown_claims_judged_incorrect':sum(r['first_pass_correct']=='no' and not known(r['first_pass_value']) for r in eligible),'initial_known_claims_judged_incorrect_or_incomplete':sum(r['first_pass_correct']=='no' and known(r['first_pass_value']) for r in eligible),'note':'First-pass unknowns counted incorrect only when Uday resolved the source and explicitly judged no. Improvements measure recovery of missing information as well as correction of erroneous positive claims.'}
 return projected,log,matrix,metrics,human

def write_csv(path,rows):
 with path.open('w',newline='',encoding='utf-8') as handle:
  writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)

def generate(timestamp):
 rows,log,matrix,metrics,human=expected_outputs(timestamp)
 t.dump(t.OUT/'verification-policy.json',POLICY)
 t.dump(t.OUT/'correction-log.json',log)
 # Candidate view remains reproducible from the full log, separate from active evidence filtering.
 candidates=t.apply_corrections(t.baseline()[1],log)
 t.dump(t.OUT/'prepared-results.json',candidates);write_csv(t.OUT/'prepared-results.csv',candidates)
 t.dump(t.OUT/'provisional-patterns.json',t.provisional_patterns(candidates))
 for name,value in [('verified-results.json',rows),('claim-verification.json',matrix),('patterns.json',metrics),('pattern-evidence.json',{'insights':metrics['insights'],'claim_matrix':'claim-verification.json','human_reviews':'human-review.json','targeted_checks':'automated-checks.json','caveats':metrics['limitations']}),('human-review-summary.json',human)]:t.dump(t.OUT/name,value)
 write_csv(t.OUT/'verified-results.csv',rows)
 t.dump(t.OUT/'finalization.json',{'generated_at':timestamp,'canonical_commit':t.START,'scope':'Verified-only claim projection with explicit unresolved fields; frozen original findings retained.','human_sample_complete':True,'fully_verified_rows':0,'remaining_limitations':['Unchecked claims remain unknown rather than asserted facts','No independently supported API breadth classification; all values unknown','Unknown MCP and assigned Paygent identity remain unresolved'],'stage_verdict':'COMPLETE','reason':'Stage03 workflow complete with conservative, explicit unknowns: 40 actual sample reviews, targeted official-source checks, verified-only projection, reproducible metrics and bounded insights. No whole-dataset accuracy claim. HQ must audit this low-coverage outcome before authorizing Stage04.'})
 print(json.dumps({'human':human,'coverage':metrics['summary'],'corrections':len(log),'abstentions':sum(c.get('abstention',False) for c in log)}))

def check():
 stamp=t.s.read(t.OUT/'finalization.json')['generated_at'];rows,log,matrix,metrics,human=expected_outputs(stamp)
 for name,value in [('verified-results.json',rows),('correction-log.json',log),('claim-verification.json',matrix),('patterns.json',metrics),('human-review-summary.json',human)]:
  if t.s.read(t.OUT/name)!=value:raise ValueError('Final artifact differs from reproducible inputs: '+name)
 print('Verified-only dataset, all 100 identities, complete actual human sample, source excerpts and all derived metrics reconcile')

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['generate','check']);parser.add_argument('--timestamp');args=parser.parse_args()
 if args.command=='generate':
  if not args.timestamp:raise SystemExit('Explicit generation timestamp required')
  generate(args.timestamp)
 else:check()
