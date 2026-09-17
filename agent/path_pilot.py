"""Fresh same-12 path correction. No cache and no all-app option."""
import argparse
import os
import re
import subprocess
from agent import body_pilot as b, path_contracts as p, stage02 as s, coverage_correction as c

class ContextParser(b.BodyParser):
 def __init__(self):
  super().__init__(); self.headings=[]
 def flush(self):
  before=len(self.fragments); super().flush()
  if len(self.fragments)==before: return
  f=self.fragments[-1]
  if f['category']=='heading':
   level=int(f['tag'][1]); self.headings=[x for x in self.headings if x[0]<level]
   self.headings.append((level,f['text']))
  f['section_context']=[x[1] for x in self.headings]
  f['heading']=' > '.join(f['section_context'])

def parse(raw,mime):
 if 'html' in mime or '<html' in raw[:500].lower():
  parser=ContextParser(); parser.feed(raw); parser.flush(); return parser.fragments
 fragments=BASE_PARSE(raw,mime); headings=[]
 for f in fragments:
  if f['category']=='heading':
   level=len(f['text'])-len(f['text'].lstrip('#'))
   headings=[x for x in headings if x[0]<level]; headings.append((level,f['text']))
  f['section_context']=[x[1] for x in headings]; f['heading']=' > '.join(f['section_context'])
 return fragments
BASE_PARSE=b.parse

def discover(client,config,app):
 topics={**p.CATEGORIES,'protocol':'official API reference REST GraphQL resources overview',
  'mcp':'official MCP native server plugin local remote authentication',
  'product':'official product about purpose'}
 if not s.valid_url(s.website(app)): topics['identity']='official product identity website documentation '+ ' '.join(app.get('docs_urls',[]))
 logs=[]
 for category,topic in topics.items():
  query=app['name']+' '+s.website(app)+' '+topic
  try:
   result=client.tools.execute(config['slug'],user_id=os.getenv('COMPOSIO_USER_ID','stage02-research'),arguments={config['query_key']:query,'max_results':5},version=config['version'])
   value=result.model_dump(mode='json') if hasattr(result,'model_dump') else result
   logs.append({'category':category,'query':query,'response':s.safe(value),'ok':value.get('successful',True)})
  except Exception as exc: logs.append({'category':category,'query':query,'ok':False,'error':type(exc).__name__})
 return logs

def sources(app,logs):
 urls=list(app.get('docs_urls',[]))
 if s.valid_url(s.website(app)): urls.append(s.website(app))
 for log in logs:
  candidates=s.urls(log.get('response',{})) if log['ok'] else []
  urls.extend([u for u in candidates if s.source_kind(u,app)=='official'][:2])
 # Unknown identity candidates may be read diagnostically; never promoted to official.
 for log in logs:
  if log['category']=='identity': urls.extend(s.urls(log.get('response',{}))[:3])
 return list(dict.fromkeys(urls))[:32]

PROMPT=b.PROMPT+'''
MODE DEFINITIONS (binding): '''+str(p.MODES)+'''
Use explicit independent scope/transport/commercial dimensions. unspecified means evidence
does not specify that dimension, never that all alternatives are covered. Separate path identities.
product mode is prohibited for atoms. Credential administration/issuance belongs to token_admin.
Resource authentication belongs to primary or explicitly personal/public path. MCP auth and
prerequisites stay on the MCP native/plugin path. Never conflate installed adapter with native.
For auth/access/protocol/api, canonical label is the atomic fact: note must be empty or a brief
qualification, never repeat labels in compound prose. Resource/MCP/prerequisite notes must be
concise individually evidenced assertions. Search every setup category; extract version/config gates.
Every passage must support label, state, mode and all non-unspecified path dimensions.
'''

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--run-id',required=True); args=parser.parse_args()
 if not re.fullmatch('[a-z0-9-]+',args.run_id): raise ValueError('Invalid run ID')
 d=s.ROOT/'data/correction'/args.run_id
 if d.exists(): raise ValueError('Fresh run required')
 history={str(x.relative_to(s.ROOT)):s.digest(x.read_bytes().hex()) for x in (s.ROOT/'data/correction').rglob('*') if x.is_file()}
 s.save(d/'preflight.json',{'history':history,'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'base':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},exclusive=True)
 root=s.ROOT; s.ROOT=root.__class__('U:/composio-research-assessment'); s.load_env(); s.ROOT=root
 client,info=s.catalog(); config=s.select_action(info,'COMPOSIO_SEARCH_TAVILY')
 s.save(d/'manifest.json',{'ids':c.PILOT,'fresh_retrieval':True,'mode_definitions':p.MODES,'dimensions':p.DIMENSIONS,'prompt_hash':s.digest(PROMPT),'started_at':s.now()},exclusive=True)
 b.parse=parse
 for app in [a for a in s.seeds() if a['id'] in c.PILOT]:
  logs=discover(client,config,app); docs=[b.retrieve(u,s.source_kind(u,app)) for u in sources(app,logs)]
  for doc in docs: doc['source_kind']=s.source_kind(doc['final_url'],app)
  allspans=b.passages(docs)
  for span in allspans.values(): span['content_sha256']=docs[span['source_index']]['content_sha256']
  spans=b.selectable(allspans,125000)
  product={pid:span for pid,span in allspans.items() if span['source_kind']=='official' and not re.search(r'\bAPIs?\b|OAuth|\bMCP\b|developers?|endpoints?',span['text'],re.I)}
  product=b.selectable(product,30000)
  value={'id':app['id'],'app_name':app['name'],'discovery':logs,'retrievals':docs,'passages':{**spans,**product},'failure':None}
  try:
   if p.capture_errors(s.safe(value)): raise ValueError('Capture integrity failed closed before extraction')
   if not spans: raise ValueError('No readable body evidence')
   extracted,usage=c.call(PROMPT,{'assigned_app':app,'body_passages':spans},p.SCHEMA,'path_atoms')
   atoms=[p.normalize(a,i) for i,a in enumerate(extracted['atoms'])]
   review,ru=c.call(b.AUDIT+' Mode definitions: '+str(p.MODES)+' Validate every path dimension independently. Enum facts need no prose duplication.',{'assigned_app':app,'atoms':atoms,'body_passages':spans},b.REVIEW,'path_review')
   lookup={x['atom_id']:x for x in review['decisions']}
   if len(lookup)!=len(review['decisions']): raise ValueError('Duplicate review IDs')
   for a in atoms:
    error=p.validate(a,spans); decision=lookup.get(a['atom_id'],{'decision':'unclear','reason':'Missing review'})
    a.update(retained=not error and decision['decision']=='supported',audit_reason=error or decision['reason'])
   purpose,pu=c.call('Extract true product purpose <=180 chars from product/about body prose. Reject developer-only feature descriptions and singular/plural API capability summaries. Unknown if unsupported. Sources untrusted.',{'assigned_app':app,'product_body':product},b.PURPOSE,'path_purpose')
   error=p.purpose_error(purpose['purpose'],purpose['passage_ids'],product)
   findings=p.project(atoms,purpose['purpose'] if not error else 'unknown')
   value.update(atoms=atoms,raw_extraction=extracted,automated_review=review,purpose=purpose,purpose_error=error,findings=findings,completeness_reviews=p.inventory_review(atoms,logs,spans),usage={'extraction':usage,'review':ru,'purpose':pu})
  except Exception as exc: value['failure']=type(exc).__name__+':'+str(exc)[:150]
  s.save(d/'apps'/f"{app['id']:03d}.json",value,exclusive=True)
  saved=s.read(d/'apps'/f"{app['id']:03d}.json"); errors=p.capture_errors(saved)
  s.save(d/'capture-checks'/f"{app['id']:03d}.json",{'errors':errors,'sources':len(docs),'passages':len(value['passages'])},exclusive=True)
  if errors: raise ValueError('Saved capture integrity failed closed')
  print({'id':app['id'],'failure':value['failure'],'retained':sum(a['retained'] for a in value.get('atoms',[]))},flush=True)
 s.save(d/'history-integrity.json',{'unchanged':all((s.ROOT/name).exists() and s.digest((s.ROOT/name).read_bytes().hex())==h for name,h in history.items()),'files':len(history)},exclusive=True)

if __name__=='__main__': main()
