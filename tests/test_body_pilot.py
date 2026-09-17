import unittest
from agent import body_pilot as b

class BodyTests(unittest.TestCase):
    def test_nav_body_heading_provenance(self):
        fragments=b.parse('<nav><p>The API supports REST and allows access to resources.</p></nav><article><h2>Authentication</h2><p>Developers authenticate the resource API using personal access tokens.</p></article>','text/html')
        docs=[{'ok':True,'fragments':fragments,'source_kind':'official','final_url':'https://example.com'}]
        spans=b.passages(docs)
        self.assertEqual(len(spans),1)
        self.assertEqual(next(iter(spans.values()))['heading'],'Authentication')
        self.assertEqual(next(iter(spans.values()))['text'],'Developers authenticate the resource API using personal access tokens.')
    def test_no_arbitrary_offsets_or_free_label(self):
        self.assertNotIn('start',b.ATOM['properties'])
        self.assertNotIn('end',b.ATOM['properties'])
        self.assertIn('auth:api_key',b.ATOM['properties']['label']['enum'])
        self.assertNotIn('API key authentication',b.ATOM['properties']['label']['enum'])
    def test_bad_atom_does_not_erase_valid_atom(self):
        spans={'p':{'text':'The API is RESTful and uses API key authentication.','heading':'Reference','category':'body','source_kind':'official'}}
        atoms=[{'atom_id':'a0','label':'protocol:rest','mode':'primary','fact':'REST API','passage_ids':['p']},{'atom_id':'a1','label':'auth:oauth2','mode':'adjacent','fact':'OAuth','passage_ids':['missing']}]
        decisions=[{'atom_id':'a0','decision':'supported','reason':'Explicit'},{'atom_id':'a1','decision':'supported','reason':'Wrong'}]
        kept=b.retain(atoms,decisions,spans)
        self.assertTrue(kept[0]['retained']); self.assertFalse(kept[1]['retained'])
        self.assertEqual(b.derive(kept)['api_types'],['rest'])
    def test_http_does_not_establish_rest(self):
        spans={'p':{'text':'Make HTTP requests to retrieve all account resources.','heading':'API','category':'body','source_kind':'official'}}
        self.assertIsNotNone(b.valid({'label':'protocol:rest','mode':'primary','passage_ids':['p']},spans))
    def test_completeness_not_certified_by_model(self):
        review=b.completeness([],[],[],[])
        self.assertFalse(review['completeness_established'])
        self.assertIn('version',review['categories_searched_not_established'])
        self.assertEqual(b.derive([])['buildability'],'unknown')
    def test_true_product_purpose_remains_whole(self):
        fragments=b.parse('<h1>Example</h1><p>Example helps teams organize their projects and collaborate on work.</p>','text/html')
        self.assertEqual(fragments[-1]['category'],'body')
        self.assertTrue(fragments[-1]['text'].endswith('work.'))
    def test_oversize_block_is_not_truncated(self):
        docs=[{'ok':True,'fragments':[{'text':'word '*2000,'category':'body'}],'source_kind':'official','final_url':'https://example.com'}]
        self.assertFalse(b.passages(docs))
    def test_script_metadata_cannot_spill_into_body(self):
        fragments=b.parse('<script type="application/ld+json">{"description":"The API supports REST"}</script><p>Example helps teams organize projects and collaborate on work.</p>','text/html')
        self.assertEqual(fragments[0]['category'],'hidden')
        self.assertEqual(fragments[1]['category'],'body')
        self.assertNotIn('description',fragments[1]['text'])
    def test_mcp_cannot_supply_primary_breadth(self):
        spans={'p':{'text':'The MCP connector supports reading and updating customer resources.','heading':'MCP','category':'body','source_kind':'official'}}
        self.assertIsNotNone(b.valid({'label':'resource:read','mode':'personal','passage_ids':['p']},spans))
    def test_layout_sidebar_class_does_not_hide_main_body(self):
        fragments=b.parse('<body class="has-left-sidebar has-right-sidebar"><main><h2>Developer access</h2><p>Developers must register an application before accessing this API.</p></main></body>','text/html')
        self.assertEqual(fragments[-1]['category'],'body')
        self.assertEqual(fragments[-1]['heading'],'Developer access')
    def test_mcp_resource_atoms_do_not_derive_primary_breadth(self):
        atom={'retained':True,'mode':'mcp','label':'resource:read','state':'available','fact':'Read CRM records'}
        self.assertEqual(b.derive([atom])['api_breadth'],'unknown')
    def test_failed_duplicate_label_does_not_erase_valid_auth_atom(self):
        spans={'p':{'text':'Developers authenticate the resource API using an API key.','heading':'Authentication','category':'body','source_kind':'official'}}
        atoms=[{'atom_id':'a0','label':'auth:api_key','mode':'primary','fact':'API key','passage_ids':['p']},{'atom_id':'a1','label':'auth:api_key','mode':'adjacent','fact':'Wrong adjacent API','passage_ids':['missing']}]
        decisions=[{'atom_id':'a0','decision':'supported','reason':'Explicit'},{'atom_id':'a1','decision':'unsupported','reason':'Invalid'}]
        self.assertEqual(b.derive(b.retain(atoms,decisions,spans))['auth_methods'],['api_key'])
    def test_model_completeness_flag_cannot_derive_buildability(self):
        from agent.body_pilot_seal import buildability
        verdict,_=buildability([],{'coverage_complete':True,'surface_or_mode':'primary','completeness_established':False},b.derive([]))
        self.assertEqual(verdict,'unknown')
    def test_documentation_redaction_precedes_body_hash(self):
        from agent import stage02 as s
        from unittest.mock import MagicMock,patch
        from email.message import Message
        response=MagicMock(); response.__enter__.return_value=response
        response.geturl.return_value='https://example.com/api'
        response.headers=Message(); response.headers['Content-Type']='text/html; charset=utf-8'
        response.read.return_value=('<p>The API uses sk_test_12345678901234567890 for authentication in this documentation example. '+ 'This is documentation body content. '*4+'</p>').encode()
        with patch.object(b,'build_opener') as opener, patch.object(s,'public_url'):
            opener.return_value.open.return_value=response
            saved=s.safe(b.retrieve('https://example.com/api','official'))
        self.assertTrue(saved['ok'])
        self.assertEqual(s.digest(saved['text']),saved['content_sha256'])
        self.assertIn('[REDACTED_DOCUMENTATION_CREDENTIAL]',saved['text'])
