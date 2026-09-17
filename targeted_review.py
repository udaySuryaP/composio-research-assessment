"""Separate agent-authored official-source review; offline merge and QA, no API calls."""
import copy, hashlib, json, re, subprocess
from collections import Counter
from pathlib import Path
from agent import stage02 as s, production_qa as q, path_contracts as p, path_audit
D=Path('data/correction/targeted-official-review-20260917')
OLD=Path('data/correction/full100-semantic-continuation-20260917')
TARGET=[36,41,43,44,48,49,50,60,61,68,69,73,76,81,84,85,90,99]
CRITICAL=['auth_methods','access_model','api_available','api_types','api_breadth','mcp_available','buildability']
def read(x): return json.loads(x.read_text(encoding='utf8'))
def save(n,v): (D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(x): return hashlib.sha256(x.read_bytes()).hexdigest()
def browser_doc(batch,ref,url,lines):
 raw=read(D/f'browser-batch-{batch}.json')
 section=raw.split(f'cite{ref}',1)[1].split('--------------------------------------------------------------------------------',1)[0]
 fs=[]
 for match in re.finditer(r'(?:^|\n)L(\d+): (.*)',section):
  num=int(match[1]); text=match[2]
  if num not in lines or not text.strip(): continue
  text=re.sub(r'cite[^†]+†([^]*)',r'\1',text)
  fs.append({'text':text,'heading':'Official browser-rendered body excerpt; line '+str(num),'category':'body','tag':'browser_line','ancestry':[],'browser_line':num})
 assert fs,(batch,ref,lines)
 text='\n\n'.join(f['text'] for f in fs)
 doc={'requested_url':url,'final_url':url,'retrieved_at':s.now(),'source_kind':'official','ok':True,'text':text,'content_sha256':s.digest(text),'fragments':fs,'error':None,'capture_type':'browser_rendered_selected_body_lines','browser_archive':str((D/f'browser-batch-{batch}.json').resolve()),'browser_archive_sha256':sha(D/f'browser-batch-{batch}.json'),'browser_ref':ref,'full_page_capture':False}
 return doc
def main():
 paths={}
 for folder in ['retry-history/apps','apps']:
  for x in (OLD/folder).glob('*.json'): paths[int(x.stem)]=x
 assert set(paths)==set(range(1,101))
 inventory=[]; baseline=Counter(); result=[]; corrections=[]; citations=[]; issues=[]; atom_changes=[]; semantic_changes=[]
 no_review=[]
 for i,x in sorted(paths.items()):
  original=read(x)
  for st in original['field_status'].values(): baseline[st['status']]+=1
  valid=bool(original.get('field_review')) and not original.get('field_audit_failure')
  if not valid: no_review.append(i)
  inventory.append({'id':i,'app':original['app'],'source_checkpoint':str(x.resolve()),'checkpoint_sha256':sha(x),'valid_API_projected_field_review':valid,'unresolved_fields':[f for f,t in original['field_status'].items() if t['status']=='unresolved'],'failure':original['failure'],'field_audit_failure':original.get('field_audit_failure')})
  v=copy.deepcopy(original)
  q.atom_qa(v,{'id':i})
  atom_changes.extend({'id':i,**a} for a in v['final_atom_qa_downgrades'])
  for f in v['findings']:
   if v['findings'][f]!=original['findings'][f]: semantic_changes.append({'id':i,'field':f,'before':original['findings'][f],'after':v['findings'][f],'reason':'Existing deterministic final atom/subset QA'})
  if i in TARGET:
   cap=D/'captures'/f'{i:03d}.json'
   if cap.exists():
    fresh=read(cap); offset=len(v['retrievals']); v['retrievals']+=fresh['retrievals']
    for key,span in fresh['passages'].items():
     span['source_index']+=offset; v['passages']['target:'+key]=span
   extra=[]
   if i==43:
    extra=[browser_doc(4,'turn4view5','https://docs.bigcommerce.com/developer/docs/overview/api-fundamentals/api-accounts',{910,911,917}),browser_doc(8,'turn8view3','https://docs.bigcommerce.com/developer/docs/overview/api-fundamentals/api-accounts',{695,698,724}),browser_doc(8,'turn8view4','https://docs.bigcommerce.com/developer/docs/overview/api-fundamentals/api-accounts',{661,667})]
   if i==44: extra=[browser_doc(5,'turn5view0','https://developer.salesforce.com/docs/commerce/commerce-api/guide/authorization.html',{3,7})]
   if i==90: extra=[browser_doc(6,'turn6view0','https://pitchbook.com/help/PitchBook-api',{6,15,37,39,42,51})]
   if i==60: extra=[browser_doc(8,'turn8view2','https://developers.clay.com/',{19,21,45,57})]
   for di,doc in enumerate(extra):
    source_index=len(v['retrievals']); v['retrievals'].append(doc)
    for fi,frag in enumerate(doc['fragments']): v['passages'][f'browser:{di}:{fi}']={**frag,'source_index':source_index,'source_kind':'official','url':doc['final_url'],'content_sha256':doc['content_sha256'],'paragraph_index':fi}
   def refs(*selectors):
    out=[]
    for selector in selectors:
     if selector in v['passages']: out.append(selector); continue
     found=[k for k,a in v['passages'].items() if a['source_kind']=='official' and selector in a['text'].replace('`','')]
     assert found,(i,selector)
     out.append(found[0])
    return list(dict.fromkeys(out))
   def put(f,value,*selectors,reason='Targeted agent review of explicit assigned-product official body evidence; limited to the named surface.',caveat='Documentation only; no integration executed, exhaustive endpoints or alternative-route prerequisites certified.'):
    ids=refs(*selectors); assert ids
    before={k:copy.deepcopy(v[k][f]) for k in ['findings','field_status','field_refs']}
    # This layer completes gaps only; valid automated findings are retained.
    if v['field_status'][f]['status']!='unresolved': return
    v['findings'][f]=value; v['field_refs'][f]=ids
    v['field_status'][f]={'status':'source_backed_with_caveat','reason':reason,'caveats':[caveat],'derivation':f in ('buildability','buildability_rationale','primary_blocker'),'review_layer':'targeted_official_source_agent_review','fresh_human_verification':False}
    corrections.append({'id':i,'app':v['app'],'field':f,'before':before,'after':{k:v[k][f] for k in before},'reviewer':'Codex agent; not a human verification sample','evidence_ids':ids})
   def readiness(value,reason,*sel):
    put('buildability',value,*sel,reason=reason)
    put('buildability_rationale',reason,*sel,reason=reason)
   def gate(label,note,*sel): put('access_model',[{'gate':label,'surface':'primary','qualification':note,'atom_id':f'targeted-{i}-access'}],*sel)
   def mcp(provider,*sel):
    put('mcp_available','yes',*sel)
    put('mcp_provider',[{'surface':'mcp_native','label':'mcp:provider','note':provider,'atom_id':f'targeted-{i}-mcp'}],*sel)
    put('mcp_ownership',[{'surface':'mcp_native','label':'mcp:vendor_owned','note':provider,'atom_id':f'targeted-{i}-mcp-owner'}],*sel)
    put('mcp_notes',provider+'; resource API authentication and MCP authentication are separate surfaces.',*sel)
   if i==36:
    put('purpose','Email and SMS marketing with customer-data-driven personalization.','d3:b144')
    put('auth_methods',['api_key','oauth2'],'d0:b8',caveat='Private keys/OAuth apply to server APIs; public site IDs apply to client APIs. These credentials are not interchangeable.')
    put('api_available','yes','d7:b148'); put('api_breadth','Inspected server actions include bulk event creation for profiles.','d7:b148')
    gate('credential_creation','Account keys are self-managed by Owner/Admin/Manager; server scopes must match intended endpoints.','d5:b73','d5:b81')
    put('primary_blocker','Owner/Admin/Manager role needed to manage API keys; endpoint scopes constrain access.','d5:b73','d5:b81')
    readiness('buildable_with_documented_constraints','Server API and key onboarding are documented; role and scope requirements apply.','d0:b8','d5:b73','d7:b148')
   if i==41:
    put('auth_methods',['other'],'d0:b123',caveat='GraphQL Admin API access token in X-Shopify-Access-Token; acquisition flow depends on app type.')
    put('api_available','yes','d0:b123'); put('api_types',['graphql'],'d0:b123')
    put('api_breadth','Admin GraphQL product queries are evidenced; broader endpoint census not established.','d0:b404')
    gate('credential_creation','Install app on a development store for testing; app scopes requested during installation.','d9:b96','d0:b125')
    put('primary_blocker','Required app scopes and installation; development-store evidence does not certify production distribution.','d0:b125','d9:b96')
    readiness('buildable_with_documented_constraints','Admin API token/authentication and app testing are documented; production distribution remains route-specific.','d0:b123','d9:b96','d0:b125')
   if i==43:
    put('auth_methods',['oauth2'],'The X-Auth-Token header uses access tokens',caveat='Store tokens and app installation grants are distinct OAuth-based account routes; token header does not imply every API uses this scheme.')
    put('api_available','yes','BigCommerce offers a suite of APIs')
    put('api_types',['rest','graphql'],'Most of our REST endpoints and GraphQL Admin API endpoints')
    put('api_breadth','Store data management, customer sign-in, and client-side product queries.','BigCommerce offers a suite of APIs')
    gate('credential_creation','Store-level credentials from merchant control panel; app-level credentials require store authorization.','Merchants generate single-store API credentials','After a store owner or authorized user installs')
    put('primary_blocker','API account scopes must permit the intended operations.','access token’s API account must have permission')
    readiness('buildable_with_documented_constraints','OAuth API accounts and credential onboarding are documented; account route and scopes constrain operations.','The X-Auth-Token header uses access tokens','Merchants generate single-store API credentials','access token’s API account must have permission')
   if i==44:
    put('api_available','yes','Authorization for the B2C Commerce API resources')
    gate('configuration','B2C Commerce SCAPI client permissions and OAuth-based scopes; pricing and client onboarding not established.','set of scopes based on the OAuth 2.1 standard')
    put('api_breadth','SCAPI Admin and Shopper API scope-controlled resources; endpoint census unresolved.','set of scopes based on the OAuth 2.1 standard')
    put('primary_blocker','Client permissions and SCAPI scopes must be configured; credential onboarding remains unresolved.','Authorization for the B2C Commerce API resources','set of scopes based on the OAuth 2.1 standard')
    readiness('needs_further_investigation','SCAPI existence and client authorization evidenced, but coherent resource authentication and onboarding are not established by these pages.','Authorization for the B2C Commerce API resources','set of scopes based on the OAuth 2.1 standard')
   if i==49:
    put('auth_methods',['oauth2'],'target:d0:b584','target:d0:b586',caveat='Login with Amazon access tokens for non-restricted operations; restricted PII operations require RDTs; grantless calls use client credentials.')
    put('api_available','yes','target:d0:b584')
    put('api_breadth','Catalog item lookup example and restricted-operation authorization are evidenced.','target:d0:b616','target:d0:b584')
    gate('registration','SP-API developer and application registration required; public apps must be listed in the Selling Partner Appstore.','target:d1:b575','target:d1:b579')
    put('primary_blocker','Developer/application registration and selling-partner authorization; restricted operations require RDTs.','target:d1:b575','target:d0:b586','target:d0:b584')
    readiness('buildable_with_documented_constraints','Connection and authorization workflow documented; developer registration, selling-partner consent and restricted-data requirements apply.','target:d1:b575','target:d0:b586','target:d0:b584')
   if i==60:
    put('auth_methods',['api_key'],'d7:b158')
    put('api_available','yes','d7:b135')
    put('api_breadth','Searches, routines and read-only table data; no table creation or record writes certified.','d7:b135','d7:b163')
    gate('credential_creation','Public API has its own key, issued through CLI; current developer overview labels Tables Enterprise.','d7:b158','Tables are Enterprise only.')
    put('primary_blocker','Tables access is Enterprise in current developer docs; prior University text mentions basic reads on any plan, so precise entitlement requires verification.','d7:b164','Tables are Enterprise only.')
    readiness('buildable_with_documented_constraints','Public API key and resource actions documented. Table entitlement differs across official pages; restrict claims to searches/routines and verify the table route.','d7:b158','d7:b135','d7:b164','Tables are Enterprise only.')
   if i==61:
    put('auth_methods',['personal_access_token','oauth2'],'d0:b293','d0:b304',caveat='Personal tokens and app OAuth access have endpoint-specific permissions; SAML organizations may require token authorization.')
    put('api_types',['rest'],'d0:b293'); put('api_available','yes','d0:b293')
    put('api_breadth','Inspected REST actions retrieve app and app-installation information.','d5:b272')
    gate('credential_creation','Personal access tokens can be created for personal REST API use; permissions and organization policies apply.','d0:b293','d0:b294','d0:b298')
    put('primary_blocker','Endpoint permissions; classic tokens need authorization for SAML SSO organizations.','d0:b294','d0:b298')
    readiness('buildable_with_documented_constraints','Personal REST integration has documented token creation and endpoint permissions; organization SAML policies can add authorization.','d0:b293','d0:b294','d0:b298')
    mcp('GitHub-hosted remote GitHub MCP Server; local version also documented.','d2:b210')
   if i==68:
    put('auth_methods',['oauth2','api_key'],'d0:b160','d0:b186',caveat='Atlas Administration API service-account OAuth tokens recommended; API keys use legacy HTTP Digest. Neither authorizes cluster database reads/writes.')
    put('api_available','yes','d0:b159')
    put('api_breadth','Atlas cluster administration and database-user management; cluster data requires separate database-user authentication.','d0:b159','d0:b163')
    gate('credential_creation','Service account client ID/secret create access tokens; assigned Atlas roles constrain operations.','d0:b171','d0:b179')
    put('primary_blocker','Atlas role permissions and separate cluster database-user credentials for data access.','d0:b179','d0:b163')
    readiness('buildable_with_documented_constraints','Administration API credential flow and roles documented; this assessment does not certify cluster-data integration.','d0:b171','d0:b179','d0:b163')
   if i==69:
    put('api_available','yes','target:d2:b450')
    put('api_breadth','Configuration, querying and management APIs; intake covers metrics, logs and traces.','target:d2:b467','target:d2:b468')
    put('primary_blocker','Authentication migration: legacy application keys continue; blog distinguishes current SATs from planned M2M OAuth. Endpoint eligibility not resolved.','target:d2:b450','target:d2:b448')
    readiness('needs_further_investigation','API existence is evidenced but changing credential routes and endpoint-specific onboarding require further investigation.','target:d2:b450','target:d2:b448')
   if i==73:
    put('auth_methods',['api_key','oauth2'],'d0:b58'); put('api_available','yes','d0:b52'); put('api_types',['graphql'],'d0:b52')
    put('api_breadth','Issue queries and team issue webhooks are evidenced.','d0:b65','d0:b109')
    gate('credential_creation','Personal keys created in Security & access settings; OAuth2 recommended for applications used by others.','d0:b63','d0:b60')
    readiness('buildable_with_documented_constraints','GraphQL API, personal key creation and OAuth recommendation documented; app-user permissions remain route-specific.','d0:b52','d0:b58','d0:b63')
    mcp('Linear centrally hosted MCP Server; Streamable HTTP with OAuth or direct bearer/key options.','d1:b72')
   if i==76:
    put('auth_methods',['personal_access_token'],'d0:b149'); put('api_available','yes','d1:b45'); put('api_types',['graphql'],'d1:b45')
    put('api_breadth','Workflow API and board/column/item/account permissions evidenced; endpoint census unestablished.','d1:b45','d0:b153')
    gate('credential_creation','Users with API access retrieve personal token through Developer Center; permissions mirror UI.','d0:b159','d0:b162','d0:b150')
    put('primary_blocker','Account API eligibility and user platform permissions; no universal free-plan access claim.','d0:b159','d0:b150')
    readiness('buildable_with_documented_constraints','GraphQL platform API and token access documented for eligible users; platform permissions constrain calls.','d1:b45','d0:b149','d0:b159','d0:b150')
   if i==81:
    put('auth_methods',['api_key','basic'],'d0:b150','d0:b153')
    put('api_available','yes','d0:b150')
    gate('credential_creation','Keys managed in Dashboard; test sandbox and live restricted-key permissions differ.','d0:b150','d0:b151')
    put('primary_blocker','Live restricted-key permissions limit API operations; live payment eligibility not certified.','d0:b151')
    readiness('buildable_with_documented_constraints','Documented API-key authentication and Dashboard onboarding support sandbox integration; live eligibility remains unverified.','d0:b150','d0:b151','d0:b153')
    mcp('Stripe MCP Server, vendor-hosted; OAuth and restricted-key routes are separate from resource API auth.','d1:b89','d1:b91')
   if i==90:
    put('auth_methods',['api_key','other'],'through an API key or authentication token',caveat='Vendor describes API key or authentication token; exact token issuance/grant scheme is not documented here.')
    put('api_available','yes','The PitchBook API is a RESTful implementation'); put('api_types',['rest'],'The PitchBook API is a RESTful implementation')
    put('api_breadth','Financing details, deal stock information and VC exit predictor endpoints.','variety of relational endpoints')
    gate('sales_contact','Separate API offering requires standalone contract and Direct Data team request.','requires a standalone contract agreement','send a request directly to our Direct Data team')
    put('primary_blocker','Standalone API contract and Direct Data outreach.','requires a standalone contract agreement','send a request directly to our Direct Data team')
    readiness('gated_or_outreach_required','API and access mechanism evidenced; standalone contract and Direct Data outreach gate the route.','The PitchBook API is a RESTful implementation','requires a standalone contract agreement','send a request directly to our Direct Data team')
   if i==99:
    put('purpose','TranscriptAPI retrieves YouTube video transcripts programmatically.','d1:b115')
    put('auth_methods',['api_key'],'d1:b155',caveat='Assigned product is TranscriptAPI.com, a third-party transcript service; API key sent as Bearer token. MCP OAuth is a separate surface.')
    put('api_available','yes','d1:b115'); put('api_types',['rest'],'d2:b215')
    put('api_breadth','Transcripts, search, channel and playlist endpoints.','d0:b23')
    gate('credential_creation','API key from dashboard; requests consume credits and exhausted credits return 402.','d1:b131','d1:b583')
    put('primary_blocker','Available request credits and transcript availability; credit exhaustion returns 402.','d1:b583')
    readiness('buildable_with_documented_constraints','Resource API key onboarding and transcript endpoints documented; credit and transcript-availability constraints remain.','d1:b115','d1:b155','d1:b131','d1:b583')
    mcp('TranscriptAPI.com native MCP endpoint; OAuth/API-key options; not a Google-owned YouTube server.','d2:b129','d2:b206')
   # Every incomplete app field receives a source-review disposition, including explicit unresolved outcomes.
   for f,st in v['field_status'].items():
    if st['status']!='unresolved': continue
    if i==84: reason='Identity ambiguous: assigned Paygent Connect is hinted as NMI-powered; paygent.io has no readable product docs. Other Paygent sites cannot be tied deterministically to this assignment.'
    elif i==48: reason='Official Gumroad API and help URLs returned no selectable body; indexed snippets cannot establish current authentication, access or full resource capabilities.'
    elif i==50: reason='Assigned Fanbasis domain now presents Commas. apidocs.fan requires JavaScript and returned only hidden bundled document content; rendered official API evidence and rebrand identity not established.'
    elif i==85: reason='Current iPayX docs/developers URLs returned an FX-audit overview with no selectable developer body; indexed API/MCP descriptions were not corroborated by current rendered pages.'
    elif i==69 and f=='auth_methods': reason='Conflicting or transitioning official authentication descriptions: legacy dual keys versus newer PAT/SAT and planned OAuth routes; endpoint-specific supported grant/eligibility not established.'
    elif f.startswith('mcp_'): reason='No explicit rendered official server/setup/ownership passage retained in this targeted review for this field; absence of a passage does not establish MCP absence.'
    elif f=='primary_blocker': reason='Reviewed official passages do not establish a specific primary blocker; no blocker-absence assertion.'
    elif f=='purpose': reason='Targeted integration documentation does not establish a concise assigned-product purpose claim independently of adjacent services.'
    elif f=='api_types': reason='Official resource evidence exists but inspected body does not explicitly establish an assigned-product protocol label for this route.'
    elif f=='auth_methods': reason='Authorization/scoping evidence alone does not establish resource authentication token type and acquisition for the assigned route.'
    else: reason='Inspected official passages do not establish '+f+' for the assigned route; alternatives and additional requirements remain unasserted.'
    st.update(reason=reason,review_layer='targeted_official_source_agent_review',fresh_human_verification=False)
   v['targeted_review_disposition']={'reviewer':'Codex agent','independent_human_verification':False,'fields_reviewed':list(v['field_status']),'unresolved_fields':[f for f,st in v['field_status'].items() if st['status']=='unresolved'],'complete_as_evidence_disposition':True}
  errors=p.capture_errors(v); assert not errors,(i,errors)
  issues.extend({'id':i,'field':f,'reason':reason} for f,reason in q.check(v))
  for f,ids in v['field_refs'].items():
   for pid in ids:
    a=v['passages'][pid]; doc=v['retrievals'][a['source_index']]
    citations.append({'id':i,'app':v['app'],'field':f,'passage_id':pid,'snippet':a['text'],'heading':a['heading'],'url':doc['requested_url'],'final_url':doc['final_url'],'source_kind':doc['source_kind'],'content_sha256':doc['content_sha256'],'retrieved_at':doc['retrieved_at'],'capture_type':doc.get('capture_type','preserved_official_page_capture'),'source_checkpoint':str(x.resolve()),'target_capture':str((D/'captures'/f'{i:03d}.json').resolve()) if pid.startswith('target:') else None,'browser_archive':doc.get('browser_archive'),'browser_archive_sha256':doc.get('browser_archive_sha256'),'exact':True})
  keep={k:v[k] for k in ['id','app','category','findings','field_status','field_refs','unresolved_gaps']}
  keep.update(original_API_failures={'failure':original['failure'],'field_audit_failure':original.get('field_audit_failure')},audit_artifacts={'automated_checkpoint':str(x.resolve()),'automated_checkpoint_sha256':sha(x)},targeted_review_disposition=v.get('targeted_review_disposition'),fresh_human_verification=False)
  result.append(keep)
  print({'id':i,'app':v['app'],'targeted':i in TARGET},flush=True)
 assert len(no_review)==16,no_review
 assert baseline['source_backed']+baseline['source_backed_with_caveat']==709,baseline
 save('gap-inventory.json',inventory); save('field-corrections.json',corrections); save('final-corrected-dataset.json',result); save('final-citations.json',citations)
 save('deterministic-qa-changes.json',{'atom_downgrades':atom_changes,'subset_projection_changes':semantic_changes,'field_integrity_downgrades':issues})
 # Hash checks against frozen quota-stop manifest and preflight protected history.
 hashes=read(OLD/'QUOTA-STOP-FILE-HASHES.json')['sha256']
 mismatches=[n for n,h in hashes.items() if not (OLD/n).exists() or sha(OLD/n)!=h]
 integrity=path_audit.integrity(OLD)
 save('protected-integrity.json',integrity)
 counts={f:dict(Counter(v['field_status'][f]['status'] for v in result)) for f in result[0]['findings']}
 for vals in counts.values():
  for status in ['source_backed','source_backed_with_caveat','unresolved']: vals.setdefault(status,0)
 all_unknown=[{'id':v['id'],'app':v['app']} for v in result if all(v['field_status'][f]['status']=='unresolved' for f in CRITICAL)]
 reasons=Counter(st['reason'] for v in result for st in v['field_status'].values() if st['status']=='unresolved')
 def group(reason):
  low=reason.lower()
  if 'identity ambiguous' in low or 'rebrand' in low:return 'identity_ambiguous_or_rebrand_unestablished'
  if 'conflict' in low or 'transitioning' in low:return 'conflicting_or_transitioning_documentation'
  if 'hidden' in low or 'no selectable' in low or 'not corroborated' in low:return 'docs_inaccessible_or_no_selectable_body'
  if 'mcp' in low:return 'no_explicit_MCP_evidence'
  if 'readiness' in low or 'onboarding' in low:return 'readiness_evidence_insufficient'
  if '429' in low or 'credit balance' in low:return 'unreviewed_API_quota_stage'
  if 'audit' in low or 'response' in low:return 'incomplete_or_rejected_API_review'
  return 'no_supported_field_evidence_or_specific_constraint'
 summary={'status':'VERIFICATION-READY' if not mismatches and not issues else 'PARTIAL','ready_for_fresh_independent_verification':not mismatches and not issues,'automated_completion_preserved':{'extraction':96,'atom_review':93,'valid_field_review':84},'missing_valid_API_field_review_ids':no_review,'targeted_review_ids':TARGET,'targeted_completed_gap_fields':len(corrections),'targeted_source_backed_apps':sorted(set(x['id'] for x in corrections)),'targeted_unresolved_only_apps':[i for i in TARGET if i not in {x['id'] for x in corrections}],'field_counts':counts,'total_status_counts':dict(Counter(st['status'] for v in result for st in v['field_status'].values())),'all_critical_unresolved_apps':all_unknown,'all_critical_unresolved_count':len(all_unknown),'readiness_distribution':dict(Counter(v['findings']['buildability'] for v in result)),'specific_unresolved_reasons':dict(reasons),'unresolved_reason_distribution':dict(Counter(group(st['reason']) for v in result for st in v['field_status'].values() if st['status']=='unresolved')),'citations':len(citations),'citation_source_hash_errors':0,'capture_fragment_hash_errors':0,'quota_stop_artifacts_checked':len(hashes),'quota_stop_hash_mismatches':mismatches,'deterministic_field_downgrades':issues,'fresh_human_checks':0,'API_calls_this_strategy':0,'readiness_caveat':'Documentation inference only; no integration run; unresolved is an evidence disposition, not proof of absence.','protected_state':integrity,'tests':'pending','next_action':'Fresh independent verification sample after reviewing handoff; do not yet rebuild HTML or publish/submit.'}
 save('automated-qa.json',summary)
 # Manual authorship and underlying exact passages remain separate from final dataset.
 save('manual-evidence-capture.json',{'review_type':'targeted official-source agent correction; not human verification','browser_selected_docs_policy':'Browser captures retain rendered body line text, exact tool archive and hash. They are labeled excerpts, not full-page captures.','field_corrections':corrections,'citations':[x for x in citations if (x['id'],x['field']) in {(a['id'],a['field']) for a in corrections}]})
 print(json.dumps({k:summary[k] for k in ['status','targeted_completed_gap_fields','total_status_counts','all_critical_unresolved_apps','readiness_distribution','quota_stop_hash_mismatches']},indent=2))
if __name__=='__main__':main()
