import copy
import unittest
from agent import coverage_correction as c
from agent.schema import unknown_record, CLAIM_FIELDS

class CitationTests(unittest.TestCase):
    def setUp(self):
        self.doc={'ok':True,'text':'Developers authenticate the API with an API key.',
            'requested_url':'https://example.com/api','final_url':'https://example.com/api',
            'source_kind':'official','retrieved_at':'2026-09-17T00:00:00Z','content_sha256':'retained-hash'}
        blank=unknown_record(1,'Example','Category','https://example.com','test','now')
        self.ex={'findings':{f:blank[f] for f in CLAIM_FIELDS},'support':[], 'unresolved':[]}
        self.ex['findings']['auth_methods']=['api_key']
        self.ex['support']=[{'field':'auth_methods','passage_ids':['d0:p0'],'reason':'API authentication'}]
        self.ex['surface_support']=[{'field':'auth_methods','label':'api_key','surface':'Example API',
            'context':'resource_api','passage_id':'d0:p0','quote':self.doc['text'],
            'prerequisites':[],'coverage_complete':False}]
        self.audit={'decisions':[{'field':'auth_methods','decision':'supported','reason':'Explicit developer API key'}]}

    def test_metadata_and_quote_come_from_retained_source(self):
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['auth_methods'],['api_key'])
        self.assertEqual(e[0]['quote'],self.doc['text'])
        self.assertEqual(e[0]['content_sha256'],'retained-hash')
        self.assertFalse(status['auth_methods']['human_checked'])

    def test_nonexistent_citation_is_rejected_even_if_model_supports_it(self):
        self.ex['support'][0]['passage_ids']=['invented']
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['auth_methods'],['unknown']);self.assertEqual(e,[])

    def test_grounded_text_does_not_override_semantic_rejection(self):
        self.audit['decisions'][0]['decision']='unsupported'
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['auth_methods'],['unknown']);self.assertEqual(e,[])

    def test_missing_audit_fails_closed(self):
        f,e,status=c.resolve(self.ex,{'decisions':[]},c.passages([self.doc]),[self.doc])
        self.assertEqual(f['auth_methods'],['unknown'])

    def test_failed_retrieval_is_never_a_passage(self):
        self.doc['ok']=False
        self.assertEqual(c.passages([self.doc]),{})

    def test_passage_windows_remain_exact_substrings(self):
        self.doc['text']='a'*3500
        spans=c.passages([self.doc])
        self.assertEqual(len(spans),4)
        self.assertTrue(all(s['text'] in self.doc['text'] for s in spans.values()))

    def set_claim(self, field, value):
        self.ex['findings'][field]=value
        self.ex['support'].append({'field':field,'passage_ids':['d0:p0'],'reason':'candidate'})
        self.audit['decisions'].append({'field':field,'decision':'supported','reason':'model says supported'})

    def test_official_api_does_not_establish_official_mcp(self):
        self.set_claim('mcp_available','official')
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['mcp_available'],'unknown')
        self.assertFalse(any(x['field']=='mcp_available' for x in e))

    def test_signup_or_api_key_does_not_establish_free_access(self):
        self.set_claim('access_model','self_serve_free')
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['access_model'],'unknown')

    def test_http_does_not_establish_rest(self):
        self.doc['text']='Send an HTTP POST request with an API key.'
        self.set_claim('api_types',['rest'])
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['api_types'],['unknown'])

    def test_unresolved_access_prevents_unconditional_buildability(self):
        self.set_claim('api_available','yes');self.set_claim('buildability','buildable')
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['buildability'],'unknown')

    def test_duplicate_support_decisions_fail_closed(self):
        self.audit['decisions'].append(copy.deepcopy(self.audit['decisions'][0]))
        with self.assertRaises(ValueError):c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])

    def test_mixed_unknown_auth_fails_closed(self):
        self.ex['findings']['auth_methods']=['oauth2','unknown']
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['auth_methods'],['unknown'])

    def test_overlong_purpose_is_withheld(self):
        self.set_claim('description','x'*181)
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['description'],'unknown')

    def test_no_blocker_cannot_survive_unresolved_buildability(self):
        self.set_claim('primary_blocker','none documented')
        f,e,status=c.resolve(self.ex,self.audit,c.passages([self.doc]),[self.doc])
        self.assertEqual(f['primary_blocker'],'unknown')

if __name__=='__main__':unittest.main()
