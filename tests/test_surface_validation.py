import copy
import json
import unittest
from pathlib import Path
from agent import surface_validation as sv, coverage_correction as c
from agent.schema import CLAIM_FIELDS

class SurfaceTests(unittest.TestCase):
    def test_actual_pilot_wrong_surface_claims_fail_even_with_spoofed_resource_context(self):
        cases=json.loads((Path(__file__).parent/'fixtures/surface-pilot-failures.json').read_text(encoding='utf-8'))
        for case in cases:
            with self.subTest(app=case['app'],field=case['field'],label=case['label']):
                field=case['field']; pid=case['passage_id']
                value=[case['label']] if field=='auth_methods' else case['label']
                contract={k:case[k] for k in ('field','label','context','quote','passage_id')}
                contract.update(surface=case['app']+' API',prerequisites=[],coverage_complete=False)
                ex={'support':[{'field':field,'passage_ids':[pid]}], 'surface_support':[contract]}
                self.assertIn(case['quote'],case['span']['text'])
                self.assertIsNotNone(sv.check(field,value,ex,{pid:case['span']}))
                # Exercise the production projection, even when its model auditor
                # wrongly endorses the original false-positive finding.
                ex['findings']={f:['unknown'] if f in ('auth_methods','api_types') else 'unknown' for f in CLAIM_FIELDS}
                ex['findings'][field]=value;ex['unresolved']=[]
                audit={'decisions':[{'field':field,'decision':'supported','reason':'Incorrect model endorsement'}]}
                findings,evidence,status=c.resolve(ex,audit,{pid:case['span']},[])
                self.assertFalse(c.known(findings[field]))
                self.assertEqual(evidence,[])
                self.assertTrue(status[field]['reason'])

    def example(self,field,value,quote,context='resource_api'):
        label=value[0] if isinstance(value,list) else value
        entry={'field':field,'label':label,'surface':'Example API','context':context,
               'passage_id':'p','quote':quote,'prerequisites':[], 'coverage_complete':False}
        return {'support':[{'field':field,'passage_ids':['p']}],'surface_support':[entry]}, {'p':{'text':quote,'source_kind':'official','url':'https://example.com/api'}}

    def test_resource_bot_token_and_oauth_are_retained_without_basic_token_exchange(self):
        q='Authenticating with the Discord API can be done using a bot token or an OAuth2 bearer token gained through the OAuth2 API.'
        ex,spans=self.example('auth_methods',['bearer_token'],q)
        ex['surface_support'].append(dict(ex['surface_support'][0],label='oauth2'))
        self.assertIsNone(sv.check('auth_methods',['bearer_token','oauth2'],ex,spans))
        ex['surface_support'].append(dict(ex['surface_support'][0],label='basic'))
        self.assertIsNotNone(sv.check('auth_methods',['bearer_token','oauth2','basic'],ex,spans))

    def test_token_exchange_and_web_login_cannot_be_relabelled_as_resource_auth(self):
        for context in ('token_exchange','web_login','mcp'):
            ex,spans=self.example('auth_methods',['oauth2'],'The Example API supports OAuth2 authentication with a token.',context)
            self.assertIsNotNone(sv.check('auth_methods',['oauth2'],ex,spans))

    def test_unrelated_paid_feature_does_not_establish_credential_gate(self):
        ex,spans=self.example('access_model','self_serve_paid','Example API credentials are available to users. Copilot requires a paid subscription.','developer_onboarding')
        self.assertIsNotNone(sv.check('access_model','self_serve_paid',ex,spans))

    def test_same_surface_required_across_fields(self):
        ex,spans=self.example('auth_methods',['api_key'],'Developers authenticate the Example API with an API key.')
        self.assertIsNone(sv.check('auth_methods',['api_key'],ex,spans))
        ex['surface_support'].append(dict(ex['surface_support'][0],field='access_model',label='self_serve_paid',surface='Enterprise API'))
        self.assertIsNotNone(sv.check('auth_methods',['api_key'],ex,spans))

    def test_breadth_example_cannot_become_comprehensive(self):
        ex,spans=self.example('api_breadth','Comprehensive CRUD across every resource','The Example REST API provides a GET endpoint to retrieve a ticket.','api_reference')
        self.assertIsNotNone(sv.check('api_breadth','Comprehensive CRUD across every resource',ex,spans))

    def test_mcp_third_party_and_preview_limitations(self):
        q='The WooCommerce MCP server plugin is published by w7s as a developer preview.'
        ex,spans=self.example('mcp_available','official',q,'mcp')
        self.assertIsNotNone(sv.check('mcp_available','official',ex,spans))
        ex,spans=self.example('mcp_notes','The vendor MCP server is available.',q,'mcp')
        self.assertIsNotNone(sv.check('mcp_notes','The vendor MCP server is available.',ex,spans))

    def build_example(self):
        findings={f:'known' for f in CLAIM_FIELDS}
        findings.update(api_available='yes',auth_methods=['api_key'],access_model='self_serve_paid',api_types=['rest'],api_breadth='Inspected orders',buildability='buildable',primary_blocker='Account and permissions required',buildability_rationale='Example API requires account, permissions and permalinks.')
        entries=[{'field':f,'surface':'Example API','prerequisites':['account','permissions'], 'coverage_complete':True} for f in ('auth_methods','access_model','api_available','api_types','api_breadth','buildability')]
        entries[-1]['prerequisites'].append('permalinks')
        return {'surface_support':entries},findings

    def test_woocommerce_prerequisites_cannot_be_omitted_from_positive_buildability(self):
        ex,f=self.build_example()
        self.assertIsNone(sv.buildability_reason(ex,f))
        f['buildability_rationale']='Example API requires account and permissions.'
        self.assertIsNotNone(sv.buildability_reason(ex,f))

    def test_incomplete_coverage_and_unresolved_protocol_fail_positive_and_conditional(self):
        for value in ('buildable','conditional'):
            ex,f=self.build_example();f['buildability']=value
            ex['surface_support'][-1]['coverage_complete']=False
            self.assertIsNotNone(sv.buildability_reason(ex,f))
            ex,f=self.build_example();f['buildability']=value;f['api_types']=['unknown']
            self.assertIsNotNone(sv.buildability_reason(ex,f))

    def test_buildability_cannot_use_enterprise_access_for_basic_web_api(self):
        ex,f=self.build_example();ex['surface_support'][1]['surface']='Enterprise API'
        self.assertIsNotNone(sv.buildability_reason(ex,f))

    def test_exact_contract_quote_and_complete_labels_required(self):
        ex,spans=self.example('auth_methods',['api_key'],'Developers authenticate the Example API with an API key.')
        ex['surface_support'][0]['quote']='Invented API key body quote that is not present in the document.'
        self.assertIsNotNone(sv.check('auth_methods',['api_key'],ex,spans))
        ex['surface_support']=[]
        self.assertIsNotNone(sv.check('auth_methods',['api_key'],ex,spans))
