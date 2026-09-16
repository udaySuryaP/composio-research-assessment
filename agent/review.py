"""Evidence rules refined with Codex AI assistance; all matches retain exact excerpts.
The checked-in run used these deterministic rules, not an unattended LLM API.
Run python -m agent.review --apply after collection. No network requests here.
"""
import argparse
import copy
import re
from .pipeline import read, write, verify, now, analyze, FIELDS

# AI-session reviewed exceptions. Each non-unknown finding requires an exact match
# in the retrieved document. A changed website cannot silently inherit a finding.
AUTH = {
1:[('OAuth2',r'OAuth 2\.0 protocol')],
9:[('API key',r'X-PW-AccessToken')],
10:[('token',r'Authentication . Provides tokens')],
15:[('token',r'Pylon API uses Bearer authentication')],
29:[('Basic',r'Basic Auth . Aircall customers'),('OAuth2',r'OAuth . Technology Partners')],
72:[('token',r'Personal Access Tokens \(PATs\)'),('OAuth2',r'Personal Access Token \(PAT\) or OAuth token')],
83:[('API key',r'API key cannot `TRADE`')],
86:[('OAuth2',r'Generate OAuth tokens')],
87:[('OAuth2',r'OAuth 2\.0 is required for all new integrations')],
89:[('OAuth2',r'OAuth 2\.0|OAuth2')],
90:[('API key',r'API key or authentication token')],
94:[('OAuth2',r'If your client supports OAuth')],
99:[('API key',r'API key starts with|Authorization: Bearer|API key.*?authentication')],
2:[('OAuth2',r'Any app designed for installation.*?OAuth')],
3:[('OAuth2',r'OAuth 2\.0'),('token',r'x-api-token')],
6:[('OAuth2',r'Podio API uses the OAuth2')],
11:[('OAuth2',r'Zendesk supports using OAuth access tokens')],
12:[('OAuth2',r'OAuth is for if'),('token',r'An Access Token')],
13:[('API key',r'personal API key to authenticate'),('Basic',r'curl -v -u apikey:X')],
14:[('OAuth2',r'through an OAuth implementation'),('token',r'Core API uses Bearer tokens')],
17:[('API key',r'Create a machine user and an API key')],
19:[('OAuth2',r'only via OAuth2'),('token',r'you can use Access Tokens')],
22:[('Basic',r'use HTTP Basic authentication'),('API key',r'Use your API key SID as the username')],
23:[('OAuth2',r'Cliq API uses the OAuth 2\.0')],
25:[('API key',r'generate an API key')],
27:[('token',r"bot.s authentication token")],
28:[('token',r'Authorization: Bearer')],
30:[('API key',r'API Key and Secret'),('Basic',r'Messages supports both JWT and Basic'),('other',r'JSON Web Token')],
36:[('API key',r'private key authentication'),('OAuth2',r'recommend using OAuth to make authorized API calls')],
38:[('OAuth2',r'authentication flow based on OAuth 2')],
39:[('OAuth2',r'conform to the OAuth 2\.0')],
40:[('API key',r'request that contains an API Key')],
41:[('token',r'X-Shopify-Access-Token')],
43:[('token',r'X-Auth-Token'),('OAuth2',r'OAuth scopes')],
45:[('token',r'Token based'),('other',r'OAuth 1\.0a')],
46:[('API key',r'authenticate requests by using an API key'),('OAuth2',r'API key or OAuth access token')],
51:[('Basic',r'Basic authentication is the only way')],
55:[('token',r'Authorization header as Bearer')],
57:[('API key',r'Authenticate and interact.*?API key/token')],
60:[],
61:[('token',r'personal access token'),('OAuth2',r'OAuth app')],
62:[],
63:[('OAuth2',r'Netlify uses OAuth2'),('token',r'personal access token')],
64:[('token',r'Authorization: Bearer')],
65:[('token',r'Personal access token'),('OAuth2',r'OAuth2 allows your application')],
67:[('OAuth2',r'Using OAuth'),('token',r'programmatic access token'),('other',r'key pair authentication')],
68:[('OAuth2',r'OAuth 2\.0'),('other',r'HTTP Digest Authentication')],
69:[('API key',r'write data require reporting access and require an API key')],
70:[('token',r'Authorization: Bearer')],
71:[('OAuth2',r'public connections use the OAuth 2\.0'),('token',r'installation access token')],
73:[('API key',r'Personal API Keys'),('OAuth2',r'Regular API authentication \(OAuth')],
75:[('OAuth2',r'OAuth is an open-standard authentication'),('token',r'PATs are generated')],
76:[('token',r'Personal API token')],
77:[('OAuth2',r'use the OAuth flow'),('token',r'personal API token')],
78:[('token',r'API token')],
79:[('token',r'authenticates using access tokens'),('OAuth2',r'OAuth with Smartsheet')],
80:[('OAuth2',r'OAuth2 Authentication flow'),('token',r'Personal access tokens')],
81:[('API key',r'Stripe API uses API keys')],
82:[('API key',r'client_id Private identifier')],
88:[('token',r'Authorization: "Bearer')],
91:[('token',r'Authorization:Bearer')],
92:[('OAuth2',r'OAuth authentication is still required')],
93:[('API key',r'Generate an API key'),('OAuth2',r'public OAuth app')],
96:[('API key',r'DEVIN_API_KEY')],
97:[('API key',r'Authorization: Key'),('other',r'authenticate through your Higgsfield account')],
100:[('OAuth2',r'standard OAuth2 Authorization Code'),('token',r'Personal Access Token')],
}
ACCESS={
1:('trial',r'Developer Edition provides a free'),
72:('free',r'All plan types|available on all plans'),
76:('trial',r'create a free developer account'),
83:('free',r'`NONE` \| Public market data'),
86:('trial',r'sandbox-quickbooks'),
87:('trial',r'Use the demo company'),
90:('partner',r'requires a standalone contract agreement'),
2:('admin',r'must either be a Super Admin'),
5:('admin',r'Settings → API & Webhooks'),
15:('admin',r'Only Admin users can create API tokens'),
19:('partner',r'includes a review from the Gorgias team'),
25:('free',r'Available on all plans'),
33:('partner',r'LinkedIn evaluates applications based on partnership fit'),
46:('paid',r'Commerce Advanced|Commerce plans|Business plan'),
13:('trial',r'For all trial users'),
20:('trial',r'Gladly API in a separate sandbox environment'),
51:('free',r'Create a free account with DataForSEO'),
95:('free',r'sign up for a free account'),
52:('trial',r'test it in the free trial account'),
53:('paid',r'Ahrefs API is available on eligible paid plans'),
56:('free',r'No account or API key is required for this request'),
81:('trial',r'Test mode secret keys'),
82:('trial',r"Today we.ll start in the Sandbox environment"),
88:('admin',r'Brex dashboard'),
91:('paid',r'Get licenses for Gemini Notebook Enterprise'),
97:('paid',r'Each generation consumes|same credit system'),
100:('admin',r'WAT.s can be generated here.*?users with access'),
}
CAVEATS={
2:'OAuth is required for multi-account installs; installer needs Super Admin or Marketplace Access permissions. Plan-dependent scopes still need checking.',
5:'Workspace schema changes the API; key creation and role scoping need workspace access. Cloud pricing versus self-hosting is a separate check.',
11:'OAuth is the recommended distribution path; basic/API-token customers face migration. Do not design a new multi-customer toolkit around legacy basic auth.',
13:'API key is sent as the Basic-auth username with a dummy password; counting these as independent onboarding options would be misleading.',
15:'Only admins can create API tokens; customer authorization is required.',
19:'Private token use differs from public OAuth distribution, which requires Gorgias review. The primary access label describes public distribution.',
25:'API addon installation and workspace permissions required; public docs say available on all plans.',
28:'Test-number onboarding and production business/phone setup differ. Production permissions and messaging charges need verification.',
29:'Customer Basic-auth credentials and technology-partner OAuth are different paths; do not treat both as identical onboarding.',
30:'Product-specific JWT, key/secret and Basic methods; advanced messaging/webhook features differ.',
33:'Restricted APIs are reviewed for partnership fit; customer role and member consent are additional gates.',
41:'Prefer GraphQL Admin API; token lifecycle, merchant install and production app distribution still need checking.',
43:'Basic credentials in the Tax Provider API section belong to the external tax service; core store access uses its own token/OAuth model.',
45:'PaaS/Magento OAuth 1.0a and bearer-token auth differ from Adobe SaaS IMS authentication. Scope the toolkit to a deployment type.',
46:'Merchant key/API permission levels differ from commercial OAuth Extensions. Plan eligibility requires further confirmation.',
49:'Developer registration is a prerequisite; app review, roles, restricted data and seller authorization require separate investigation.',
52:'API can be tested during a trial; higher volume may require API add-on or funded pay-as-you-go. Trial is not free production.',
53:'Eligible paid plans have API access; other plans only have limited free test queries, not a generally free API.',
54:'MCP is documented, but account token and plan eligibility still need checking.',
56:'Limited no-key trial calls are documented; full tools and higher limits depend on a team plan or API key.',
57:'API key auth differs from proxy-native username/password access. Billing applies.',
58:'Local CLI, not an authenticated hosted SaaS API. Wrap the process with bounded execution and validate inputs.',
60:'This source describes Clay calling external APIs. It does not establish Clay own API credentials, inbound surface or onboarding.',
61:'Use a scoped PAT or OAuth/GitHub App for customer data; password authentication is explicitly unsupported. Rate limits apply.',
62:'REST index contains API-key management endpoints; that alone does not prove API-key authentication. Retrieve auth-specific documentation.',
65:'Management API OAuth/PAT and project data APIs are separate surfaces. Scope MCP to a project and enable read-only mode for initial testing.',
67:'OAuth, PAT, key-pair and workload federation vary; Snowflake account roles and compute costs matter.',
68:'Service-account OAuth is recommended; legacy API keys use HTTP Digest, not HTTP Basic.',
69:'Write operations need an API key; reads also need an application key. Use scopes and organization permissions.',
72:'Legacy API keys are deprecated. PAT/OAuth routes and free-plan rate limits should be verified in current docs.',
74:'Jira Cloud REST and GraphQL references must be scoped separately; avoid extracting auth from embedded frontend metadata.',
78:'Coda reference now presents Superhuman Docs branding; verify current host/product mapping before integration.',
79:'Paid-plan restrictions require a plan-specific source; creating a token does not alone prove free API access.',
80:'Personal access tokens replaced Basic auth from API v1; do not report Basic as a current v2 method.',
81:'Test-mode keys provide sandbox capability; live-mode permissions and money-moving actions need separate checks.',
82:'Sandbox is self-serve; production product access and commercial approval require separate checking.',
84:'Paygent Connect identity is ambiguous in the supplied hint. Do not substitute the Japanese Paygent service or assume NMI credentials apply.',
85:'The supplied docs route returns an FX verification product page rather than usable API documentation. Auth and API remain unresolved.',
88:'Brex currently documents only a production API server; do not promise a free sandbox.',
90:'API contracts are separate from platform subscriptions; contact the Direct Data team for access.',
91:'The retrieved API is Gemini Notebook Enterprise (formerly NotebookLM Enterprise), not the consumer NotebookLM UI. IAM, licensing and preview status matter.',
92:'Official MCP uses OAuth. The help page says there is no public API key; do not label a generic API-key route as available.',
94:'Confirm Consensus academic research identity. Official MCP documentation is available; do not confuse it with unrelated Consensus products.',
96:'Official MCP is authenticated. REST versions and organization/member roles affect available operations.',
97:'MCP account sign-in and server-side API key ID/secret are separate paths. Generation consumes platform credits.',
98:'Local CLI needs no service credential. Browser/runtime dependencies and subprocess input isolation are the main packaging considerations.',
99:'This is the paid TranscriptAPI service from the brief, not an official YouTube transcript endpoint.',
100:'PAT/workspace tokens differ from public OAuth; the OAuth client ID/secret registration process is manual in the docs.',
}

# Descriptions are AI-authored summaries. They are intentionally labelled as
# summaries, not exact quotations or human-verified statements.
DESCRIPTIONS='''Sales and customer relationship management
CRM, marketing and sales automation
Sales pipeline and deal management
Flexible CRM for relationship data
Open-source CRM with workspace-generated APIs
Workspaces and custom business apps
Customer relationship and sales management
Sales CRM with calling and email
CRM for relationship and pipeline management
Deal and relationship intelligence for investment teams
Customer support tickets and helpdesk workflows
Customer messaging and support automation
Helpdesk tickets, customers and agents
Shared inbox and customer communication
B2B support and customer issue management
Customer service and live chat
Developer-oriented customer support platform
Shared inbox and customer support
Ecommerce customer support helpdesk
Customer service and conversation platform
Team messaging and collaboration
Programmable communication APIs
Team messaging and collaboration
Workplace communication and collaboration
Team messaging and collaboration
Community messaging and bot platform
Messaging bots through an HTTP interface
Business messaging on WhatsApp
Business calling and telephony
Programmable messaging, voice and video
Advertising campaign management and reporting
Advertising across Meta platforms
LinkedIn advertising and audience tools
Marketing automation and CRM workflows
Email marketing and audience management
Customer data and marketing automation
Marketing funnels and contact management
Visual discovery, pins and advertising
Publishing and interacting with Threads content
Transactional and marketing email delivery
Commerce storefront and merchant management
WordPress ecommerce extension
Hosted ecommerce platform
Enterprise ecommerce platform
Extensible ecommerce platform
Website commerce and merchant workflows
Embedded ecommerce storefronts
Digital product sales
Amazon seller data and operations
Creator business and monetization platform
SEO and marketing data APIs
SEO and AI-search visibility data
SEO research and website analytics
Web scraping and extraction
Web scraping actors and automation
Web crawling and structured extraction
Web data and proxy infrastructure
Public username discovery CLI
Contact and company enrichment
Sales research and data enrichment
Code hosting and developer collaboration
Web application deployment platform
Web hosting and deployment automation
Internet infrastructure and security
Database and application backend platform
Graph database and Cypher queries
Cloud data warehouse and analytics
Managed MongoDB databases
Infrastructure monitoring and observability
Application error and performance monitoring
Workspace documents and knowledge management
Structured bases and collaborative data
Issue tracking and product development
Project and issue management
Tasks and team project management
Work management and collaborative boards
Tasks and project management
Collaborative documents and structured tables
Spreadsheet-style work management
Time tracking and invoicing
Payments and financial operations
Financial data connectivity
Cryptocurrency exchange and account operations
Payment service identity requires confirmation
FX transaction verification; API not confirmed
Business accounting and financial records
Accounting and business financial records
Corporate cards and spend management
Corporate spend and finance workflows
Private and public market intelligence
Enterprise document-grounded research notebooks
Meeting transcripts and AI notes
Meeting recordings and summaries
Academic literature search and synthesis
Document parsing and structured extraction
AI software engineering workflows
AI image and video generation
Render Mermaid definitions into diagrams
YouTube transcripts through TranscriptAPI
Meeting recordings and insights'''.splitlines()


def evidence(pattern, docs):
    for d in docs:
        if not d['ok']:continue
        m=re.search(pattern,d['text'],re.I)
        if m:
            # Short excerpts limit copied text while retaining a lookup anchor.
            start=max(0,m.start()-25);end=min(len(d['text']),max(m.end()+55,m.start()+110))
            return {'source_id':d['id'],'quote':d['text'][start:end]}
    return None

def claim(value, pieces, status='quote-grounded'):
    return {'value':value,'source_ids':sorted(set(e['source_id'] for e in pieces)), 'quote':pieces[0]['quote'] if pieces else '', 'evidence':pieces,'status':status}

def apply():
    docs_by_app=read('documents.json',{})
    first=read('first-pass.json',[])
    rows=copy.deepcopy(first)
    logs=[]
    assert len(DESCRIPTIONS)==100
    for r in rows:
        aid=r['id'];docs=docs_by_app.get(str(aid),[])
        before=copy.deepcopy(r['fields'])
        r['fields']=verify(r['fields'],docs)
        f=r['fields']
        # Only name/category/product summaries; not used to calculate auth/access patterns.
        f['description']=claim(DESCRIPTIONS[aid-1], [], 'AI summary; not human-verified')
        f['description']['source_ids']=[d['id'] for d in docs if d['ok']][:1]
        if aid in AUTH:
            values=[];pieces=[]
            for value,pattern in AUTH[aid]:
                e=evidence(pattern,docs)
                if e:values.append(value);pieces.append(e)
            f['auth']=claim(sorted(set(values)),pieces) if pieces else claim('unknown',[],'unknown')
        if aid in ACCESS:
            value,pattern=ACCESS[aid];e=evidence(pattern,docs)
            f['access']=claim(value,[e]) if e else claim('unknown',[],'unknown')
        else:
            # Generic trial/sales footer mentions aren't reliable onboarding evidence.
            f['access']=claim('unknown',[],'unknown')
        # Callable surface: explicit API language only; embedded GraphQL frontend
        # metadata is excluded. This is an existence signal, not breadth verification.
        api_patterns=[('REST',r'public REST API|classic REST API|RESTful interface|REST architecture|RESTful HTTP endpoints|RESTful API|REST API|REST APIs'),('GraphQL',r'API is built using GraphQL|REST and GraphQL APIs|GraphQL APIs|GraphQL Admin API|GraphQL API')]
        types=[];pieces=[]
        for value,pattern in api_patterns:
            e=evidence(pattern,docs)
            if e:types.append(value);pieces.append(e)
        if not types:
            e=evidence(r'HTTP-based interface|HTTPS-only API|JSON over HTTP|simple HTTP requests|API request|HTTP requests|curl --request|curl -X (?:GET|POST)|curl --location',docs)
            if e:types=['HTTP API'];pieces=[e]
        if not types:
            e=evidence(r'API uses|API requests|use the [A-Za-z -]{1,40}API|using the API|API authentication',docs)
            if e:types=['Documented API (protocol unverified)'];pieces=[e]
        if aid in [60,85]:types=[];pieces=[]
        if aid==74:
            e=evidence(r'Jira.s REST API|REST API', [d for d in docs if 'basic-auth' in d['url']])
            types=['REST'] if e else [];pieces=[e] if e else []
        f['api']=claim(' + '.join(types)+'; breadth needs endpoint inventory',pieces) if pieces else claim('unknown',[],'unknown')
        # MCP nav labels alone do not prove server availability.
        e=evidence(r'(?:official |remote |the )?MCP server.{0,150}|Model Context Protocol \(MCP\) server',docs)
        confirmed_mcp={8,52,54,56,61,65,71,73,78,81,92,94,95,96,97,99}
        if aid in confirmed_mcp and e:
            f['mcp']=claim('official',[e])
        else:f['mcp']=claim('unknown',[],'unknown')
        if aid in [58,98]:
            e=evidence(r'pipx install|pip install|npm install|mmdc|command line|command-line',docs)
            if e:
                f['api']=claim('Local CLI; no hosted API asserted',[e])
                f['auth']=claim(['other: local execution; no service auth'],[e],'derived from CLI docs')
                f['access']=claim('free',[e],'derived from public CLI installation docs')
        usable=f['api']['value']!='unknown' or f['mcp']['value']=='official'
        verdict='conditional' if usable else 'unknown'
        if aid in [58,98] and f['api']['value']!='unknown':verdict='buildable'
        if aid in [25,56,72] and usable and f['access']['value'] in ['free','trial']:verdict='buildable'
        refs=sorted(set(f['api']['source_ids']+f['auth']['source_ids']+f['mcp']['source_ids']))
        f['buildability']={'value':verdict,'source_ids':refs,'quote':'','status':'feasibility inference; not API-tested','derived_from':['api','auth','mcp','access']}
        caveat=CAVEATS.get(aid,'Developer plan eligibility, credential onboarding, scopes, rate limits and MCP availability need further confirmation before production.')
        f['blocker']={'value':caveat,'source_ids':sorted(set(refs+f['access']['source_ids'])),'quote':'','status':'AI review caveat; verify before production'}
        r['engine']='AI-session-assisted-evidence-rules'
        r['researched_at']=now()
        r['documents']=[{k:v for k,v in d.items() if k!='text'} for d in docs]
        if aid in AUTH or aid in ACCESS or aid in [58,98]:
            for field in ['auth','access','mcp','api']:
                old=before[field]['value'];new=f[field]['value']
                if old!=new:
                    source=f[field]['source_ids']
                    logs.append({'app_id':aid,'app':r['name'],'field':field,'before':old,'after':new,'kind':'AI-assisted rule review','reason':CAVEATS.get(aid,'Refined exact matching and abstained from unsupported keywords; this is an AI review, not a human check.'),'source_url':next((d['url'] for d in docs if source and d['id']==source[0]),docs[0]['url'] if docs else None),'reviewed_at':now()})
    # Put major semantic errors before routine removals in the case-study story.
    priority=[60,80,68,43,12,53,92,97,91]
    logs.sort(key=lambda r:priority.index(r['app_id']) if r['app_id'] in priority else len(priority))
    write('review-log.json',logs)
    expected={2:['OAuth2'],12:['OAuth2','token'],43:['OAuth2','token'],60:'unknown',62:'unknown',68:['OAuth2','other'],72:['OAuth2','token'],80:['OAuth2','token'],92:['OAuth2'],22:['API key','Basic'],81:['API key'],21:['OAuth2']}
    initial={r['id']:r for r in first};final={r['id']:r for r in rows};checks=[]
    for aid,target in expected.items():
        old=initial[aid]['fields']['auth']['value'];new=final[aid]['fields']['auth']['value']
        equal=lambda a,b: sorted(a)==sorted(b) if isinstance(a,list) and isinstance(b,list) else a==b
        checks.append({'app_id':aid,'app':final[aid]['name'],'field':'auth','expected_value':target,'first_value':old,'final_value':new,'first_correct':equal(old,target),'final_correct':equal(new,target),'kind':'AI-evaluated challenge set','reviewer':'Codex AI session','source_urls':[d['url'] for d in final[aid]['documents'] if d['ok']],'notes':CAVEATS.get(aid,'Checked the explicit authentication protocol in retrieved official documentation.'),'selection':'Nine ambiguity/error cases and three control cases, deliberately selected; not random or independent. This is not human or population accuracy.'})
    write('challenge-checks.json',checks)
    write('results.json',rows)
    write('review-run.json',{'engine':'AI-session-assisted deterministic evidence rules','reviewed_at':now(),'apps':len(rows),'changes':len(logs),'note':'No unattended LLM API was invoked. AI helped inspect retrieved excerpts, author exception rules and explain caveats. Rules are replayable; semantic accuracy needs human review.'})
    analyze()
    print(f'Applied evidence rules to {len(rows)} apps; {len(logs)} logged changes')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');args=p.parse_args()
    if args.apply:apply()
    else:p.print_help()
