"""Stable surface identities and fail-closed inventory review for the next pilot."""
import re
from agent import body_pilot as b, stage02 as s
from agent.schema import obj, array, text, enum

MODES = {
 'product': 'Product purpose only; never integration facts.',
 'primary': 'Assigned resource API, with no alternative route inferred.',
 'token_admin': 'Token/key administration and issuance, not resource authentication.',
 'personal_integration': 'Private/personal resource integration.',
 'public_app': 'Distributed/public application integration.',
 'enterprise': 'Enterprise product surface only.',
 'adjacent': 'Distinct adjacent product; never assigned primary.',
 'mcp_native': 'Vendor native MCP surface.',
 'mcp_plugin': 'Installed plugin/adapter MCP surface.',
}
DIMENSIONS = {'scope':('unspecified','scoped','unscoped'),
 'transport':('unspecified','local','remote'),
 'commercial':('unspecified','payment_required','plan_gated','explicit_no_payment')}
LABELS = b.LABELS+('auth:personal_access_token','auth:oauth1','mcp:vendor_owned','mcp:third_party_owned')
ATOM = obj({'label':enum(*LABELS),'mode':enum(*MODES),
 **{k:enum(*v) for k,v in DIMENSIONS.items()},
 'state':enum('available','required','optional','deprecated','not_required'),
 'note':text(),'passage_ids':array(text())})
SCHEMA = obj({'atoms':array(ATOM),'unresolved_gaps':array(text()),'alternative_paths':array(text())})
CATEGORIES = {
 'account':'developer account eligibility signup prerequisites',
 'credential':'API token key creation issuance requirements',
 'registration':'OAuth application registration redirect URI setup',
 'scopes':'API OAuth scopes roles permissions requirements',
 'admin':'API administrator authorization permissions requirements',
 'app_review':'public app approval review production access requirements',
 'plan':'API pricing plan payment subscription eligibility',
 'partner':'API partner program sales approval access gates',
 'configuration':'API installation configuration setup product specific requirements',
 'version':'API integration minimum version runtime requirements',
}

def identity(atom):
 return '/'.join([atom['mode']]+[atom.get(k,'unspecified') for k in DIMENSIONS])

def normalize(atom,index):
 family=atom['label'].split(':')[0]
 # Canonical facts are sufficient for enum families; notes cannot compound them.
 fact=atom['label'].split(':')[1] if family in ('auth','access','protocol','api') or atom['label'] in ('mcp:vendor_owned','mcp:third_party_owned') else atom['note'].strip()
 return {**atom,'atom_id':f'a{index}','path_id':identity(atom),'fact':fact}

def capture_errors(value):
 errors=[]
 for i,doc in enumerate(value['retrievals']):
  if doc['text']!='\n\n'.join(f['text'] for f in doc['fragments']) or s.digest(doc['text'])!=doc['content_sha256']:
   errors.append({'source_index':i,'reason':'Saved fragments/text/hash mismatch'})
 for pid,p in value.get('passages',{}).items():
  doc=value['retrievals'][p['source_index']]
  if p['text'] not in doc['text'] or p.get('content_sha256',doc['content_sha256'])!=doc['content_sha256']:
   errors.append({'passage_id':pid,'reason':'Citation text/hash mismatch'})
 return errors

def validate(atom,spans):
 mode=atom['mode']; family=atom['label'].split(':')[0]
 if mode not in MODES or mode=='product': return 'Product is reserved for purpose; invalid integration mode'
 if any(atom.get(k,'unspecified') not in vs for k,vs in DIMENSIONS.items()): return 'Invalid path dimension'
 if atom.get('path_id')!=identity(atom): return 'Unstable path identity'
 if not atom['passage_ids'] or any(p not in spans for p in atom['passage_ids']): return 'Missing passage'
 if family=='mcp' and mode not in ('mcp_native','mcp_plugin'): return 'MCP mode mismatch'
 if mode=='token_admin' and family in ('auth','protocol','resource','api'): return 'Token administration cannot establish resource API facts'
 legacy={**atom,'mode':{'personal_integration':'personal','token_admin':'token_exchange','mcp_native':'mcp','mcp_plugin':'mcp'}.get(mode,mode)}
 # MCP auth/setup is retained on its own path, never resource-auth projection.
 if mode.startswith('mcp_') and family!='mcp':
  legacy['mode']='adjacent'
 return b.valid(legacy,spans)

def purpose_error(value,ids,spans):
 if value=='unknown': return 'Product purpose unresolved'
 if len(value)>180 or '\n' in value or not value.strip(): return 'Purpose must be <=180 characters'
 if re.search(r'\bAPIs?\b|REST|GraphQL|OAuth|\bMCP\b|endpoints?|authentication|developers?',value,re.I): return 'Developer/API capability summary rejected'
 if not ids or any(p not in spans or spans[p]['source_kind']!='official' for p in ids): return 'Official product body required'
 if any(re.search(r'\bAPIs?\b|OAuth|\bMCP\b|developers?|endpoints?',spans[p]['text'],re.I) for p in ids): return 'Developer evidence cannot supply product purpose'
 return None

def inventory_review(atoms,discovery,spans,model_assertion=None):
 """Independent deterministic review: search completion alone is never closure."""
 paths=sorted({'primary/unspecified/unspecified/unspecified'}|{identity(a) for a in atoms})
 reviews=[]
 for path in paths:
  found=[a for a in atoms if a.get('retained') and identity(a)==path and a['label'].startswith('prerequisite:')]
  book=[]
  for category in CATEGORIES:
   logs=[x for x in discovery if x.get('category')==category]
   evidence=[a['atom_id'] for a in found if a['label']=='prerequisite:'+category]
   book.append({'category':category,'searched':bool(logs),'successful_searches':sum(bool(x['ok']) for x in logs),
    'queries':[x['query'] for x in logs],'evidenced_atom_ids':evidence,
    'state':'evidenced_requirement' if evidence else 'unresolved_applicability_or_requirement'})
  gaps=[x['category'] for x in book if not x['evidenced_atom_ids']]
  reviews.append({'path_id':path,'reviewer':'independent deterministic inventory rules',
   'category_search_bookkeeping':book,'prerequisites_found':found,'completeness_established':False,
   'unresolved_gaps':gaps or ['All listed categories evidenced, but alternative-path applicability closure remains unproven'],
   'reason':'Category searches and extraction assertions cannot prove exhaustive applicability or alternative-path closure.'})
 return reviews

def project(atoms,purpose='unknown'):
 # Legacy summary uses only undifferentiated primary resource path. Alternatives
 # retain their evidence in per-path displays; no path can satisfy another.
 primary=[{**a,'mode':'primary'} for a in atoms if identity(a)=='primary/unspecified/unspecified/unspecified']
 primary=[{**a,'label':'auth:other'} if a['label'] in ('auth:personal_access_token','auth:oauth1') else a for a in primary]
 findings=b.derive(primary,purpose)
 if findings['api_types']!=['unknown']: findings['api_available']='yes'
 mcp=[a for a in atoms if a.get('retained') and a['mode'].startswith('mcp_') and a['label'].startswith('mcp:')]
 if mcp: findings['mcp_notes']='; '.join(a['path_id']+': '+a['fact']+' ('+a['state']+')' for a in mcp)
 owners=[]
 for path in {identity(a) for a in mcp}:
  active=[a for a in mcp if identity(a)==path and a['state']=='available']
  if any(a['label']=='mcp:availability' for a in active):
   if any(a['label']=='mcp:vendor_owned' for a in active): owners.append('official')
   if any(a['label']=='mcp:third_party_owned' for a in active): owners.append('community')
 if owners: findings['mcp_available']='both' if len(set(owners))>1 else owners[0]
 return findings
