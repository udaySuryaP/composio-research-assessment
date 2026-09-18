"""Offline, bounded submission corrections; preserve the accepted research ledgers."""
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/correction/fresh-independent-verification-20260917'
OUT = ROOT / 'data/correction/submission-fixes-20260918'
PURPOSES = {
9:'CRM for service businesses to organize contacts, track deals, manage projects, and automate follow-ups.',
11:'Customer and employee service software with AI agents to resolve support issues.',
15:'B2B customer support platform where people and AI agents investigate and resolve customer work.',
17:'Composable AI customer support infrastructure for B2B teams.',
19:'Conversational AI and helpdesk platform for ecommerce customer support and sales.',
22:'Customer communications platform for messaging, voice, email, conversational AI, and identity verification.',
24:'Team workspace combining chat, meetings, documents, knowledge, and workflow automation.',
26:'Voice, video, and text communications platform for communities around gaming.',
30:'Cloud communications platform for customer messaging, voice, video, and identity verification.',
32:'Advertising across Facebook, Instagram, Messenger, and WhatsApp to reach and engage customers.',
33:'Advertising platform for targeting professional audiences on LinkedIn.',
34:'Sales and marketing platform for agencies to capture, nurture, and convert leads, with white-label resale.',
38:'Visual discovery platform where people find ideas and products, with business marketing and advertising tools.',
39:'Meta social app for sharing text updates and joining public conversations.',
41:'Commerce platform for businesses to build stores, sell products, and manage operations.',
42:'Customizable open-source ecommerce platform built on WordPress.',
43:'Commerce platform for building online stores and buying experiences across brands, regions, and channels.',
44:'Salesforce commerce platform for digital storefronts and commerce across channels, using AI, data, and CRM.',
45:'Enterprise digital commerce platform for storefronts and personalized B2B and B2C shopping experiences.',
46:'Website builder with templates, AI building tools, and domains to establish and grow a business online.',
47:'Ecommerce platform to launch an online store or add one to an existing website.',
48:'Platform for creators to sell their knowledge and products online and receive payments.',
49:'Amazon selling-partner integration surface for order, shipment, payment, and related seller business data.',
50:'Creator commerce platform, now branded Commas, combining checkouts, funnels, courses, communities, and payments.',
51:'Data provider for SEO and search marketing analytics used by software companies and agencies.',
55:'Marketplace of ready-to-run automation tools for web data, competitor tracking, lead generation, and integrations.',
59:'B2B data enrichment platform combining vendors to improve contact, email, and mobile-number coverage.',
60:'Go-to-market platform for gathering data, running agent workflows, and launching revenue plays.',
61:'Software development collaboration platform for discovering, building, and contributing to projects.',
62:'Infrastructure platform to deploy apps and agents, with global delivery, serverless functions, and deployment environments.',
63:'Platform to build and deploy web applications on production infrastructure using code or AI.',
64:'Cloud platform to build, secure, and deliver applications, with network security, connectivity, and global compute.',
66:'Graph data platform for connecting stored data and running complex queries at scale.',
68:'Managed cloud document database offering resilience, scalability, and enterprise security.',
69:'Cloud monitoring platform that brings metrics from applications, tools, and services into one place.',
70:'Application performance monitoring and error tracking for developers and software teams.',
73:'Product development platform for planning, tracking issues, and building products with teams and AI agents.',
75:'Work management software for teams and AI agents to plan, automate, and execute workflows.',
76:'Work platform where people and AI agents execute, manage, and operate business work together.',
79:'Work management platform for projects, portfolios, workflow automation, and team coordination.',
80:'Time tracking and management software with reporting and online invoicing.',
81:'Financial services platform for businesses to accept payments, manage billing, and move money.',
82:'Financial connectivity platform that lets people securely connect financial data to apps and services.',
83:'Cryptocurrency exchange and blockchain ecosystem with digital-asset trading and related financial products.',
86:'Cloud accounting software for bookkeeping, invoicing, bill payments, payroll, and financial reporting.',
87:'Small-business accounting software connecting businesses with banks, accountants, bookkeepers, and other apps.',
88:'Business finance platform for company cards, expense management, banking, and financial process automation.',
89:'Spend management platform combining corporate cards, expenses, bill payments, banking, and accounting automation.',
92:'AI meeting assistant for real-time transcription, summaries, insights, action items, and live chat.',
93:'AI notetaker that records, transcribes, and summarizes video meetings and supports team CRM updates.',
94:'AI academic search engine for finding, organizing, and analyzing peer-reviewed scientific literature.'
}

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 rows=read(BASE/'final-corrected-dataset.json');changes=[]
 def put(r,f,v,evidence,caveats=()):
  before={k:copy.deepcopy(r[k][f]) for k in ('findings','field_status','field_refs')}
  r['findings'][f]=v;r['field_refs'][f]=[e['passage_id'] for e in evidence]
  r['field_status'][f]={'status':'source_backed_with_caveat' if caveats or f!='purpose' else 'source_backed','reason':'Bounded official-source submission correction; documentation only, not executed integration verification.','caveats':list(caveats),'derivation':f=='primary_blocker','review_layer':'submission_fixes_agent_review','fresh_human_verification':False}
  r['evidence']=[e for e in r['evidence'] if e['field']!=f]+evidence;r['evidence_index']='final-citations.json'
  changes.append({'id':r['id'],'app':r['app'],'field':f,'before':before,'after':{k:r[k][f] for k in before},'evidence':evidence})
 def evidence(r,f,doc,quote):
  assert quote in doc['text']
  p=OUT/f"{doc['id']:03d}-purpose-source.json"
  return {'id':r['id'],'app':r['app'],'field':f,'passage_id':f"submission:{doc['id']}:{f}",'snippet':quote,'heading':'Official product or documentation excerpt','url':doc['requested_url'],'final_url':doc['final_url'],'source_kind':'official','content_sha256':doc['content_sha256'],'retrieved_at':doc['retrieved_at'],'capture_type':doc['capture_type'],'source_capture':str(p.relative_to(ROOT)).replace('\\','/'),'source_capture_sha256':sha(p),'exact':True,'review_layer':'submission_fixes_agent_review'}
 for r in rows:
  if r['id'] not in PURPOSES:continue
  assert r['field_status']['purpose']['status']=='unresolved'
  doc=read(OUT/f"{r['id']:03d}-purpose-source.json");assert doc['ok']
  selected={43:'Power modern buying experiences across brands, regions, and channels',49:'helps sellers and vendors access their data on orders, shipments, payments, inventory, and other business information.',62:'Global Delivery\nDeployment Environments\nServerless Functions',64:'One platform for your apps, agents, and workforce. Build, secure, and scale without managing infrastructure.',73:'Purpose-built for planning and building products with AI agents.',79:'Manage projects, automate workflows, and build solutions at scale with Smartsheet.'}
  quote=selected.get(r['id']) or doc.get('selected_quote') or ' '.join((doc.get('meta') or [doc['text']])[0].split()[:23])
  # Metadata whitespace must match the archived source exactly.
  if quote not in doc['text']:quote=(doc.get('meta') or [doc['text']])[0][:150]
  v=PURPOSES[r['id']];assert len(v)<=180 and '\n' not in v
  caveats=['Official page explicitly states FanBasis is now Commas; purpose only. Other app findings retain their existing host/identity caveats.'] if r['id']==50 else []
  es=[evidence(r,'purpose',doc,quote)]
  if r['id']==50:
   es[0]['snippet']='FanBasis is now Commas! One place to create, sell, and get paid, with payments built in.'
   es[0]['exact']=False;es[0]['paraphrase']=True
  put(r,'purpose',v,es,caveats)
 r=next(r for r in rows if r['id']==34);doc=read(OUT/'134-purpose-source.json')
 caveat='Official hosted MCP; OAuth consent, approved scopes and selected sub-account boundaries apply. Agency-wide access is rolling out; not executed or certified for every operation.'
 quote='LeadConnector MCP connections use\nOAuth'
 for f,v in {
  'mcp_available':'yes',
  'mcp_provider':[{'surface':'mcp_native','label':'mcp:provider','note':'HighLevel / LeadConnector hosted MCP server documented on the official HighLevel site.','atom_id':'submission-34-mcp'}],
  'mcp_ownership':[{'surface':'mcp_native','label':'mcp:vendor_owned','note':'Official HighLevel / LeadConnector server on services.leadconnectorhq.com.','atom_id':'submission-34-owner'}],
  'mcp_notes':'Official hosted LeadConnector MCP uses OAuth. Operations depend on granted scopes and selected sub-accounts; agency-wide multi-account rollout is conditional. API auth is a separate surface.'
 }.items():put(r,f,v,[evidence(r,f,doc,quote)],[caveat])
 r=next(r for r in rows if r['id']==2)
 docs=[read(OUT/f'{i}-purpose-source.json') for i in (102,202)]
 es=[evidence(r,'primary_blocker',docs[0],'OAuth is required for multiple accounts'),evidence(r,'primary_blocker',docs[1],'Access to specific APIs or endpoints depends on HubSpot account tier.')]
 put(r,'primary_blocker','Required API scopes and account-tier entitlement; multi-account apps need OAuth, while static bearer auth is limited to one account.',es,['Resource and distribution specific; UI content approvals and payment-export permissions are not generic API onboarding gates.'])
 save('field-corrections.json',changes);save('final-corrected-dataset.json',rows);save('final-citations.json',[e for r in rows for e in r['evidence']])
 counts=Counter(s['status'] for r in rows for s in r['field_status'].values())
 save('correction-summary.json',{'baseline_sha256':sha(BASE/'final-corrected-dataset.json'),'purposes_resolved':len(PURPOSES),'purpose_unresolved_ids':[r['id'] for r in rows if r['field_status']['purpose']['status']=='unresolved'],'changed_fields':len(changes),'status_counts':dict(counts),'scope':'Unresolved purpose only, four GoHighLevel MCP fields, one HubSpot blocker. No research API calls; prior verification outcomes unchanged.'})
 print(json.dumps(read(OUT/'correction-summary.json'),indent=2))

if __name__=='__main__':main()
