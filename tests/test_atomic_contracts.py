import copy
import unittest
import json
from pathlib import Path
from agent import atomic_contracts as a, coverage_correction as c
from agent.schema import CLAIM_FIELDS

class AtomicTests(unittest.TestCase):
    def setUp(self):
        self.q='Developers authenticate the Example resource API with an API key. Saved\u0001source text remains exact.'
        self.spans={'p':{'text':self.q,'source_kind':'official','source_index':0,'url':'https://example.com/api'}}
        self.ref={'passage_id':'p','start':0,'end':-1}
        self.entry={'field':'auth_methods','label':'api_key','assessed_surface':'primary','context':'resource_api','reference':self.ref}
        self.raw={'entries':[self.entry],'access_gates':[],'prerequisites':[],'resource_groups':[],'scope_boundary':'','mcp_atoms':[]}
        self.app={'name':'Example'}

    def ex(self):
        return {'atomic_contract':a.bind(self.raw,self.spans,self.app),'_spans':self.spans}

    def test_quote_mutation_truncation_control_characters_cannot_be_model_authored(self):
        bound=a.bind_reference(self.ref,self.spans)
        self.assertEqual(bound['quote'],self.q)
        self.assertIn('\u0001',bound['quote'])
        self.assertNotIn('quote',a.REF['properties'])

    def test_real_sealed_model_quote_drift_is_replaced_by_saved_passage_text(self):
        cases=json.loads((Path(__file__).parent/'fixtures/atomic-quote-failures.json').read_text(encoding='utf-8'))
        self.assertEqual(len(cases),11)
        for case in cases:
            with self.subTest(app=case['id'],field=case['field']):
                pid=case['passage_id'];span=case['span']
                self.assertNotIn(case['model_quote'],span['text'])
                result=a.bind_reference({'passage_id':pid,'start':0,'end':-1},{pid:span})
                self.assertEqual(result['quote'],span['text'])

    def test_invalid_ids_and_offsets_rejected(self):
        for ref in ({'passage_id':'missing','start':0,'end':-1},dict(self.ref,start=-1),dict(self.ref,end=99999),dict(self.ref,start=True),dict(self.ref,start=10,end=2)):
            with self.assertRaises(ValueError):a.bind_reference(ref,self.spans)

    def test_duplicate_and_wrong_atomic_labels_fail(self):
        self.assertIsNone(a.check('auth_methods',['api_key'],self.ex(),self.spans))
        self.raw['entries'].append(copy.deepcopy(self.entry))
        self.assertIsNotNone(a.check('auth_methods',['api_key'],self.ex(),self.spans))
        self.raw['entries'][1]['label']='oauth2'
        self.assertIsNotNone(a.check('auth_methods',['api_key','oauth2'],self.ex(),self.spans))

    def test_adjacent_unresolved_attempt_does_not_erase_primary(self):
        self.raw['entries'].append(dict(self.entry,assessed_surface='adjacent',reference={'passage_id':'missing','start':0,'end':-1}))
        self.assertIsNone(a.check('auth_methods',['api_key'],self.ex(),self.spans))

    def test_surface_is_canonical_and_separate_from_context(self):
        ex=self.ex();self.assertEqual(ex['atomic_contract']['entries'][0]['canonical_surface'],'example:resource-api')
        for context in ('token_exchange','web_login','mcp'):
            self.raw['entries'][0]['context']=context
            self.assertIsNotNone(a.check('auth_methods',['api_key'],self.ex(),self.spans))

    def test_navigation_is_not_body(self):
        self.spans['p']['text']='[API keys](https://example.com) [REST](https://example.com) Authentication Resources'
        self.assertIsNotNone(a.check('auth_methods',['api_key'],self.ex(),self.spans))
        refs=[a.bind_reference(self.ref,self.spans)]
        self.assertIsNotNone(a.purpose_check('Example manages customer relationships.',refs,self.spans))

    def test_support_link_and_api_title_are_not_body_assertions(self):
        self.spans['p']['text']="Getting started with Airtable's Web API | Airtable Help Center Contact support Sign up for free All"
        self.assertFalse(a.body_guard(self.spans['p']['text']))

    def test_purpose_is_distinct_from_api_summary(self):
        refs=[a.bind_reference(self.ref,self.spans)]
        for purpose in ('Example provides a REST API for customer resources.','Example API supports OAuth authentication.'):
            self.assertIsNotNone(a.purpose_check(purpose,refs,self.spans))
        self.spans['p']['text']='Example is a customer relationship platform that helps teams manage sales pipelines.'
        refs=[a.bind_reference(self.ref,self.spans)]
        self.assertIsNone(a.purpose_check('Example helps teams manage sales pipelines.',refs,self.spans))

    def test_generic_http_is_not_protocol_classification(self):
        self.entry.update(field='api_types',label='rest',context='api_reference')
        self.spans['p']['text']='Developers can send HTTP requests to retrieve resource API data with a key.'
        self.assertIsNotNone(a.check('api_types',['rest'],self.ex(),self.spans))

    def test_missing_prerequisite_atoms_prevent_positive(self):
        findings={f:'known' for f in CLAIM_FIELDS};findings.update(api_available='yes',auth_methods=['api_key'],api_types=['rest'],access_model='self_serve_free',api_breadth='Inspected scope: orders')
        self.assertIsNotNone(a.prerequisite_reason(self.ex(),findings))
        self.assertEqual(a.derive(self.ex(),findings)[0],'unknown')

    def test_negative_access_gate_cannot_be_inferred_from_silence(self):
        self.raw['access_gates']=[{'name':'partner_approval','value':'not_required','assessed_surface':'primary',
            'context':'developer_onboarding','references':[self.ref],'reason':'No partner approval mentioned.'}]
        atom=self.ex()['atomic_contract']['access_gates'][0]
        self.assertFalse(a.atom_ok(atom,self.spans))

    def test_paid_feature_is_not_evidenced_paid_credential_prerequisite(self):
        self.spans['p']['text']='The Example API uses a personal access token. Paid plans offer more features.'
        self.raw['access_gates']=[{'name':'paid_plan','value':'required','assessed_surface':'primary',
            'context':'developer_onboarding','references':[self.ref],'reason':'Paid plans required.'}]
        atom=self.ex()['atomic_contract']['access_gates'][0]
        self.assertFalse(a.atom_ok(atom,self.spans))

    def test_evidence_metadata_and_quotes_are_code_attached_in_projection(self):
        ex=self.ex();ex.update(findings={f:['unknown'] if f in ('auth_methods','api_types') else 'unknown' for f in CLAIM_FIELDS},support=[{'field':'auth_methods','passage_ids':['p']}],unresolved=[])
        ex['findings']['auth_methods']=['api_key']
        doc={'ok':True,'text':self.q,'requested_url':'https://example.com/api','final_url':'https://example.com/api','retrieved_at':'now','source_kind':'official','content_sha256':'hash'}
        f,e,status=c.resolve(ex,{'decisions':[{'field':'auth_methods','decision':'supported','reason':'Explicit resource key'}]},self.spans,[doc])
        self.assertEqual(f['auth_methods'],['api_key']);self.assertEqual(e[0]['quote'],self.q)
        self.assertEqual(e[0]['content_sha256'],'hash')
