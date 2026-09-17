"""Independent evidence projection; fresh full inventory, checkpointed and audit-only."""
import argparse
import os
import re
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from agent import body_pilot as b, path_pilot as r, path_contracts as p
from agent import stage02 as s, coverage_correction as c, path_audit
from agent.schema import obj, array, text, enum

ATOM=obj({'label':enum(*p.LABELS),'mode':enum(*p.MODES),'state':enum('available','required','optional','deprecated','not_required'),'note':text(),'passage_ids':array(text())})
SCHEMA=obj({'atoms':array(ATOM),'unresolved_gaps':array(text()),'alternative_paths':array(text())})
PROMPT=b.PROMPT+'\nMode definitions: '+str(p.MODES)+'''
Extract core facts independently. Do not assert scope/transport/commercial dimensions.
Unknown dimensions remain unasserted. Notes must qualify the actual resource/product/credential
route when evidenced, never infer universal access. For auth/access/protocol/api use an empty
note or a supported qualification. MCP availability, provider and ownership must name the
same actual server/product in notes; do not merge multiple servers. credential_creation means
documented self-service credential issuance, not free access. Retain setup requirements individually.
Prefer the strongest at most 36 independent facts. Select 1-3 best exact passage IDs per fact;
do not cite duplicate language examples of the same endpoint. Use only IDs actually present in input.
'''

def normalize(raw,i):
 return p.normalize({**raw,**{k:'unspecified' for k in p.DIMENSIONS}},i)

def validate(atom,spans):
 error=p.validate(atom,spans)
 if error: return error
 family=atom['label'].split(':')[0]
 if atom['mode'] in ('primary','personal_integration','public_app','enterprise','token_admin'):
  context=atom['note']+' '+atom['fact']+' '+' '.join(spans[pid]['url']+' '+spans[pid]['heading'] for pid in atom['passage_ids'])
  if family in ('auth','protocol','resource','api','access','prerequisite') and re.search(r'\bMCP\b|model context protocol|/mcp(?:/|$|[?#])',context,re.I): return 'MCP surface cannot establish resource API/access facts'
 if atom['label'] in ('access:paid_plan','access:trial','access:sales_contact','access:partner_approval'):
  body=' '.join(spans[pid]['text'] for pid in atom['passage_ids'])
  if not re.search(r'\bAPI\b|developer|credential|\btoken\b|\bkeys?\b|OAuth|integration',body,re.I): return 'Product pricing/trial/sales evidence does not establish API credential/access eligibility'
 return None

def discover(client,config,app):
 topics={**p.CATEGORIES,'protocol':'official API reference REST GraphQL resources overview','mcp':'official MCP native server plugin local remote authentication','product':'official product about purpose'}
 if not s.valid_url(s.website(app)): topics['identity']='official product identity website documentation '+ ' '.join(app.get('docs_urls',[]))
 def search(item):
  category,topic=item; query=app['name']+' '+s.website(app)+' '+topic
  try:
   result=client.tools.execute(config['slug'],user_id=os.getenv('COMPOSIO_USER_ID','stage02-research'),arguments={config['query_key']:query,'max_results':5},version=config['version'])
   value=result.model_dump(mode='json') if hasattr(result,'model_dump') else result
   return {'category':category,'query':query,'response':s.safe(value),'ok':value.get('successful',True)}
  except Exception as exc: return {'category':category,'query':query,'ok':False,'error':type(exc).__name__}
 with ThreadPoolExecutor(max_workers=3) as pool: return list(pool.map(search,topics.items()))

def project(atoms,purpose='unknown',purpose_ids=(),gaps=(),failure=None):
 kept=[a for a in atoms if a.get('retained') and a['state']!='deprecated' and a['mode'] not in ('adjacent','product')]
 resource=[a for a in kept if a['mode'] in ('primary','personal_integration','public_app','enterprise')]
 out={}; statuses={}; refs={}
 def put(field,value,selected=(),reason='',derived=False):
  known=value not in ('unknown','unresolved',['unknown'])
  out[field]=value; refs[field]=list(dict.fromkeys(pid for a in selected for pid in a['passage_ids']))
  caveats=['Inspected documentation only; route alternatives and full prerequisite inventory are not certified.'] if known and field!='purpose' else []
  if any(a['mode']!='primary' for a in selected): caveats.append('Surface-specific facts; see atom modes and notes. No cross-route applicability asserted.')
  unresolved=failure or (reason if field in ('buildability','buildability_rationale','primary_blocker') else 'No independently supported assigned-product evidence for '+field)
  statuses[field]={'status':('source_backed_with_caveat' if caveats or derived else 'source_backed') if known else 'unresolved','reason':reason if known else unresolved,'caveats':caveats,'derivation':derived}
 put('purpose',purpose,reason='Official product body purpose' if purpose!='unknown' else 'Product-purpose evidence insufficient or rejected'); refs['purpose']=list(purpose_ids) if purpose!='unknown' else []
 for family,field in [('auth','auth_methods'),('protocol','api_types')]:
  aa=[a for a in resource if a['label'].startswith(family+':') and a['state'] in ('available','required','optional')]
  put(field,list(dict.fromkeys(a['label'].split(':')[1] for a in aa)) or ['unknown'],aa,'Retained independent resource facts')
 aa=[a for a in resource if a['label'].startswith(('api:','protocol:','resource:')) and a['state']=='available']
 put('api_available','yes' if aa else 'unknown',aa,'Documented API/protocol/resource evidence',True)
 aa=[a for a in resource if a['label'].startswith('resource:')]
 put('api_breadth','Inspected documented actions: '+'; '.join(a['fact'] for a in aa) if aa else 'unknown',aa,'Inspected resource/action groups, not endpoint census')
 access=[a for a in kept if a['label'].startswith('access:') and not a['mode'].startswith('mcp_') and a['state'] in ('available','required')]
 put('access_model',[{'gate':a['label'].split(':')[1],'surface':a['mode'],'qualification':a['note'],'atom_id':a['atom_id']} for a in access] or 'unknown',access,'Only explicitly documented access dimensions; unspecified pricing/access remains unknown')
 mcp=[a for a in kept if a['label'].startswith('mcp:')]
 available=[a for a in mcp if a['label']=='mcp:availability' and a['state']=='available']
 put('mcp_available','yes' if available else 'unknown',available,'Explicit server availability; ownership assessed separately')
 for suffix,labels in [('provider',('mcp:provider',)),('ownership',('mcp:vendor_owned','mcp:third_party_owned','mcp:ownership')),('notes',tuple(x for x in p.LABELS if x.startswith('mcp:')))]:
  aa=[a for a in mcp if a['label'] in labels]
  put('mcp_'+suffix,[{'surface':a['mode'],'label':a['label'],'note':a['note'],'atom_id':a['atom_id']} for a in aa] or 'unknown',aa,'Independent MCP evidence; server names preserved in atom notes')
 gates=[a for a in access if a['label'] in ('access:partner_approval','access:sales_contact','access:public_app_review')]
 primary=[a for a in resource if a['mode'] in ('primary','personal_integration')]
 auth=[a for a in primary if a['label'].startswith('auth:') and a['state'] in ('available','required','optional')]
 api=[a for a in primary if a['label'].startswith(('api:','protocol:','resource:')) and a['state']=='available']
 setup=[a for a in kept if a['mode'] in ('primary','personal_integration','token_admin') and a['label'] in ('access:credential_creation','prerequisite:credential','prerequisite:registration')]
 constraints=[a for a in kept if a['mode'] in ('primary','personal_integration') and (a['label'].startswith('prerequisite:') or a in access) and a['state']=='required']
 readiness='unresolved'; selected=[]; reason='Insufficient coherent documented resource API, authentication and credential onboarding evidence.'
 if gates:
  readiness='gated_or_outreach_required'; selected=gates; reason='An evidenced route requires approval/review/outreach; applicability is limited to its named surface.'
 elif api and auth and setup:
  readiness='buildable_with_documented_constraints' if constraints else 'likely_buildable_from_public_docs'; selected=api+auth+setup+constraints; reason='Documentation supports a resource API, resource credentials and onboarding; integration has not been executed.'
 elif api or auth:
  readiness='needs_further_investigation'; selected=api+auth; reason='Core resource evidence retained, but credential onboarding or coherent auth/API support is incomplete.'
 put('buildability',readiness,selected,reason,True)
 put('buildability_rationale',reason if readiness!='unresolved' else 'unknown',selected,reason,True)
 blockers=gates or [a for a in constraints if a['label'] in ('access:paid_plan','access:admin_permission','prerequisite:admin','prerequisite:version','prerequisite:configuration')]
 put('primary_blocker','; '.join(a['label']+': '+(a['note'] or a['fact'])+' ['+a['mode']+']' for a in blockers) if blockers else 'unknown',blockers,'Documented constraint; not a claim that all blockers are known' if blockers else reason+' No absence-of-blockers claim.')
 return {'findings':out,'field_status':statuses,'field_refs':refs,'unresolved_gaps':list(gaps)}

def research(app,d,client,config,capture_only=False):
 retrieval_checkpoint=d/'retrieval-checkpoints'/f"{app['id']:03d}.json"
 discovery_checkpoint=d/'discovery'/f"{app['id']:03d}.json"
 if retrieval_checkpoint.exists():
  saved=s.read(retrieval_checkpoint); logs=saved['discovery']; docs=saved['retrievals']
 else:
  logs=s.read(discovery_checkpoint) if discovery_checkpoint.exists() else discover(client,config,app)
  if not discovery_checkpoint.exists(): s.save(discovery_checkpoint,logs,exclusive=True)
  print({'id':app['id'],'stage':'discovery','searches':len(logs)},flush=True)
  with ThreadPoolExecutor(max_workers=4) as pool: docs=list(pool.map(lambda u:b.retrieve(u,s.source_kind(u,app)),r.sources(app,logs)))
 for doc in docs: doc['source_kind']=s.source_kind(doc['final_url'],app)
 allspans=b.passages(docs)
 for span in allspans.values(): span['content_sha256']=docs[span['source_index']]['content_sha256']
 spans=b.selectable(allspans,125000)
 product=b.selectable({pid:x for pid,x in allspans.items() if x['source_kind']=='official' and not re.search(r'\bAPIs?\b|OAuth|\bMCP\b|developers?|endpoints?',x['text'],re.I)},30000)
 v={'id':app['id'],'app':app['name'],'category':app.get('category','unknown'),'discovery':logs,'retrievals':docs,'passages':{**spans,**product},'atoms':[],'failure':None,'purpose':{'purpose':'unknown','passage_ids':[]},'gaps':[]}
 if not retrieval_checkpoint.exists(): s.save(retrieval_checkpoint,v,exclusive=True)
 print({'id':app['id'],'stage':'retrieval','pages':len(docs),'readable':sum(x['ok'] for x in docs)},flush=True)
 try:
  if p.capture_errors(s.safe(v)): raise ValueError('Capture integrity failure')
  if not spans: raise ValueError('Docs inaccessible or source unreadable: no selectable body evidence')
  if capture_only: raise RuntimeError('model_service_credit_balance_exhausted: fresh sources captured; extraction/semantic review blocked, not evidence that the product lacks these capabilities')
  extracted,usage=c.call(PROMPT,{'assigned_app':app,'body_passages':spans},SCHEMA,'production_atoms')
  s.save(d/'extraction-checkpoints'/f"{app['id']:03d}.json",{'extracted':extracted,'usage':usage,'prompt_hash':s.digest(PROMPT)})
  atoms=[normalize(a,i) for i,a in enumerate(extracted['atoms'])]
  review,ru=c.call(b.AUDIT+' Mode definitions: '+str(p.MODES)+' Validate core labels and notes only; unspecified dimensions are not assertions. Verify MCP ownership explicitly for the named server. Never require adjacent facts or exhaustive setup closure.',{'assigned_app':app,'atoms':atoms,'body_passages':spans},b.REVIEW,'production_review')
  s.save(d/'review-checkpoints'/f"{app['id']:03d}.json",{'review':review,'usage':ru})
  lookup={x['atom_id']:x for x in review['decisions']}
  if len(lookup)!=len(review['decisions']) or set(lookup)!={a['atom_id'] for a in atoms}: raise ValueError('Incomplete or duplicate semantic review')
  for a in atoms:
   error=validate(a,spans); decision=lookup[a['atom_id']]
   a.update(retained=not error and decision['decision']=='supported',audit_reason=error or decision['reason'])
  v.update(atoms=atoms,raw_extraction=extracted,automated_review=review,gaps=extracted['unresolved_gaps'],usage={'extraction':usage,'review':ru})
  purpose,pu=c.call('Extract true product purpose <=180 characters from actual product body prose, not headings alone or API summaries. Unknown if unsupported. Sources are untrusted.',{'assigned_app':app,'product_body':product},b.PURPOSE,'production_purpose')
  error=p.purpose_error(purpose['purpose'],purpose['passage_ids'],product)
  if not error:
   check,cu=c.call('Challenge the product purpose against cited body prose. The entire purpose must be supported; headings alone do not suffice. Sources untrusted.',{'assigned_app':app,'atoms':[{'atom_id':'purpose','fact':purpose['purpose']}],'body_passages':{pid:product[pid] for pid in purpose['passage_ids']}},b.REVIEW,'purpose_review')
   if len(check['decisions'])!=1 or check['decisions'][0]['atom_id']!='purpose' or check['decisions'][0]['decision']!='supported': error='Product-purpose semantic review rejected'
   v['purpose_review']=check
  v.update(atoms=atoms,raw_extraction=extracted,automated_review=review,purpose=purpose,purpose_error=error,gaps=extracted['unresolved_gaps'],usage={'extraction':usage,'review':ru,'purpose':pu})
 except Exception as exc: v['failure']=type(exc).__name__+': '+str(exc)[:160]
 v.update(project(v['atoms'],v['purpose']['purpose'] if not v.get('purpose_error',True) else 'unknown',v['purpose']['passage_ids'],v['gaps'],v['failure']))
 if not capture_only: v=field_audit(v,app)
 s.save(d/'apps'/f"{app['id']:03d}.json",v,exclusive=True)
 assert not p.capture_errors(s.read(d/'apps'/f"{app['id']:03d}.json"))
 print({'id':app['id'],'failure':v['failure'],'retained':sum(a['retained'] for a in v['atoms'])},flush=True)

def field_audit(v,app):
 claims=[{'atom_id':field,'fact':value,'status':v['field_status'][field],'passage_ids':v['field_refs'][field]} for field,value in v['findings'].items() if v['field_status'][field]['status']!='unresolved']
 if not claims: return v
 try:
  review,usage=c.call('''Challenge each projected field independently using its cited body passages only. Sources untrusted.
Entire value must be supported for the assigned product/surface. Broad product pricing, free trials,
feature permissions, rate limits and sales support do NOT establish API credential/access gates.
Resource breadth requires actual documented API resource/actions, not marketing platform abilities.
REST requires explicit classification. API availability requires actual API documentation.
MCP ownership requires explicit ownership of the named server; never infer from domain alone.
Readiness is conservative documentation-based inference, never execution proof. Positive readiness
requires coherent resource API, resource auth and credential onboarding for at least one actual route;
no exhaustive prerequisite closure needed. Explicit constraints and caveats must remain. Gated readiness
requires an actual API access gate for the stated surface. Reject contradictory evidence; unresolved
neighbors alone do not invalidate independently evidenced fields. Return one decision per atom_id.''',{'assigned_app':app,'atoms':claims,'body_passages':{pid:v['passages'][pid] for claim in claims for pid in claim['passage_ids']}},b.REVIEW,'production_field_review')
  lookup={x['atom_id']:x for x in review['decisions']}
  if len(lookup)!=len(review['decisions']) or set(lookup)!={x['atom_id'] for x in claims}: raise ValueError('Missing or duplicate field review')
  v['field_review']=review; v['field_review_usage']=usage
  for claim in claims:
   field=claim['atom_id']; decision=lookup[field]
   if decision['decision']!='supported':
    v['findings'][field]=['unknown'] if field in ('auth_methods','api_types') else ('unresolved' if field=='buildability' else 'unknown')
    v['field_status'][field]={'status':'unresolved','reason':decision['reason'],'caveats':[],'derivation':False}; v['field_refs'][field]=[]
  if any(v['field_status'][f]['status']=='unresolved' for f in ('api_available','auth_methods')) and v['findings']['buildability'] in ('likely_buildable_from_public_docs','buildable_with_documented_constraints'):
   for field in ('buildability','buildability_rationale'):
    v['findings'][field]='unresolved' if field=='buildability' else 'unknown'; v['field_status'][field]={'status':'unresolved','reason':'Positive readiness dependencies failed independent field audit','caveats':[],'derivation':True}; v['field_refs'][field]=[]
 except Exception as exc:
  v['field_audit_failure']=type(exc).__name__+': '+str(exc)[:150]
  for claim in claims:
   field=claim['atom_id']; v['findings'][field]=['unknown'] if field in ('auth_methods','api_types') else ('unresolved' if field=='buildability' else 'unknown'); v['field_status'][field]={'status':'unresolved','reason':'Independent field audit failed: '+v['field_audit_failure'],'caveats':[],'derivation':False}; v['field_refs'][field]=[]
 return v

def finalize(d):
 values=[s.read(x) for x in sorted((d/'apps').glob('*.json'))]; citations=[]; errors=[]
 for v in values:
  errors.extend(p.capture_errors(v))
  for a in v['atoms']:
   if a['retained']: assert not p.validate(a,v['passages'])
  for field,ids in v['field_refs'].items():
   for pid in ids:
    span=v['passages'][pid]; doc=v['retrievals'][span['source_index']]
    assert span['text'] in doc['text'] and s.digest(doc['text'])==doc['content_sha256']==span['content_sha256']
    citations.append({'id':v['id'],'field':field,'passage_id':pid,'url':span['url'],'snippet':span['text'],'heading':span['heading'],'content_sha256':doc['content_sha256'],'retrieved_at':doc['retrieved_at'],'exact':True})
 counts={field:dict(Counter(v['field_status'][field]['status'] for v in values)) for field in values[0]['findings']} if values else {}
 historical=[{**h,'corrected_value':next(v for v in values if v['id']==h['app_id'])['findings'].get('purpose' if h['field']=='description' else h['field'],'unknown'),'fresh_human_check':False} for h in s.read(s.ROOT/'data/stage03/human-review.json') if any(v['id']==h['app_id'] for v in values)]
 integrity=path_audit.integrity(d); assert integrity['canonical_head']=='83bd643b087da28d2e1ed1439e381b3a8a9bca7f'
 critical=['auth_methods','access_model','api_available','api_types','api_breadth','mcp_available','buildability']
 summary={'status':'FULL-100 PASS' if len(values)==100 and not errors and not any(v['failure'] for v in values) else 'PARTIAL','run_id':d.name,'completion_count':len(values),'field_counts':counts,'all_critical_unresolved':[{'id':v['id'],'app':v['app']} for v in values if all(v['field_status'][f]['status']=='unresolved' for f in critical)],'unresolved_reasons':dict(Counter(x['reason'] for v in values for x in v['field_status'].values() if x['status']=='unresolved')),'readiness_distribution':dict(Counter(v['findings']['buildability'] for v in values)),'search_attempts':sum(len(v['discovery']) for v in values),'search_successes':sum(bool(x['ok']) for v in values for x in v['discovery']),'retrieval_attempts':sum(len(v['retrievals']) for v in values),'readable_pages':sum(bool(x['ok']) for v in values for x in v['retrievals']),'capture_errors':errors,'exact_citations':len(citations),'failures':[{'id':v['id'],'failure':v['failure']} for v in values if v['failure']],'semantic_qa':'Independent model challenge plus deterministic body/official-identity/protocol/MCP/surface guards; not human accuracy. Unsupported atoms downgraded independently.','ready_for_fresh_sample':len(values)==100 and not errors,'historical_overlap_count':len(historical),'finished_at':s.now()}
 for name,value in [('dataset',values),('citations',citations),('summary',summary),('protected-integrity',integrity),('historical-regression',historical)]: s.save(d/(name+'.json'),value)
 s.save(d/'file-hashes.json',{str(x.relative_to(d)):s.digest(x.read_bytes().hex()) for x in d.rglob('*') if x.is_file() and x.name!='file-hashes.json'})
 print(summary,flush=True)

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--run-id',required=True); parser.add_argument('--resume',action='store_true'); parser.add_argument('--finalize',action='store_true'); parser.add_argument('--workers',type=int,default=3); parser.add_argument('--capture-only',action='store_true'); args=parser.parse_args()
 if not 1<=args.workers<=6: raise ValueError('Workers must be 1..6')
 if not re.fullmatch('[a-z0-9-]+',args.run_id): raise ValueError('Invalid run ID')
 d=s.ROOT/'data/correction'/args.run_id
 if args.finalize: finalize(d); return
 if d.exists() and not args.resume: raise ValueError('Fresh run required')
 if not d.exists():
  history={str(x.relative_to(s.ROOT)):s.digest(x.read_bytes().hex()) for x in (s.ROOT/'data/correction').rglob('*') if x.is_file()}
  s.save(d/'preflight.json',{'history':history,'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'base':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},exclusive=True)
  s.save(d/'manifest.json',{'ids':[a['id'] for a in s.seeds()],'fresh_retrieval':True,'projection':'independent-core-facts','prompt_hash':s.digest(PROMPT),'started_at':s.now()},exclusive=True)
  s.save(d/'code-snapshot.json',{str(x.relative_to(s.ROOT)):x.read_text(encoding='utf-8') for x in (s.ROOT/'agent').glob('*.py')})
 root=s.ROOT; s.ROOT=Path('U:/composio-research-assessment'); s.load_env(); s.ROOT=root
 if args.resume:
  s.save(d/('resume-code-snapshot-'+s.now().replace(':','-')+'.json'),{str(x.relative_to(s.ROOT)):x.read_text(encoding='utf-8') for x in (s.ROOT/'agent').glob('*.py')},exclusive=True)
  for checkpoint in sorted((d/'apps').glob('*.json')):
   v=s.read(checkpoint)
   if not args.capture_only and 'field_review' not in v and any(x['status']!='unresolved' for x in v['field_status'].values()):
    s.save(d/'pre-field-audit'/checkpoint.name,v,exclusive=True)
    app=next(a for a in s.seeds() if a['id']==v['id'])
    v.update(project(v['atoms'],v['purpose']['purpose'] if not v.get('purpose_error',True) else 'unknown',v['purpose']['passage_ids'],v['gaps'],v['failure']))
    s.save(checkpoint,field_audit(v,app))
 client,info=s.catalog(); config=s.select_action(info,'COMPOSIO_SEARCH_TAVILY'); b.parse=r.parse
 pending=[app for app in s.seeds() if not (d/'apps'/f"{app['id']:03d}.json").exists()]
 with ThreadPoolExecutor(max_workers=args.workers) as pool:
  list(pool.map(lambda app:research(app,d,client,config,args.capture_only),pending))
 finalize(d)

if __name__=='__main__': main()
