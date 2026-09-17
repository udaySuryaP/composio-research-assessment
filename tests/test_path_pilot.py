import unittest
from agent import path_contracts as p, path_pilot as r, stage02 as s

class PathTests(unittest.TestCase):
 def atom(self,mode='primary',label='auth:api_key',**kw):
  return p.normalize({'mode':mode,'label':label,'scope':'unspecified','transport':'unspecified','commercial':'unspecified','state':'available','note':'','passage_ids':['p'],**kw},0)
 def test_path_identities_are_stable_and_disjoint(self):
  atoms=[self.atom(mode) for mode in p.MODES]
  self.assertEqual(len({a['path_id'] for a in atoms}),len(p.MODES))
  self.assertNotEqual(p.identity(self.atom(scope='scoped')),p.identity(self.atom(scope='unscoped')))
 def test_alternative_paths_cannot_supply_primary_projection(self):
  for mode in ('token_admin','personal_integration','public_app','enterprise','mcp_native','mcp_plugin'):
   self.assertEqual(p.project([{**self.atom(mode),'retained':True}])['auth_methods'],['unknown'])
 def test_token_administration_cannot_establish_resource_auth(self):
  span={'p':{'category':'body','text':'Create API keys for authenticating all resource requests.','heading':'Keys','source_kind':'official'}}
  self.assertIn('administration',p.validate(self.atom('token_admin'),span))
 def test_mcp_native_plugin_disjoint(self):
  self.assertNotEqual(p.identity(self.atom('mcp_native')),p.identity(self.atom('mcp_plugin')))
 def test_mcp_ownership_and_availability_cannot_cross_paths(self):
  owner={**self.atom('mcp_native','mcp:vendor_owned'),'retained':True}
  available={**self.atom('mcp_plugin','mcp:availability',note='Available plugin MCP server'),'retained':True}
  self.assertEqual(p.project([owner,available])['mcp_available'],'unknown')
  available=self.atom('mcp_native','mcp:availability',note='Available native MCP server')
  self.assertEqual(p.project([owner,{**available,'retained':True}])['mcp_available'],'official')
 def test_product_mode_reserved_for_purpose(self):
  self.assertIsNotNone(p.validate(self.atom('product'),{}))
 def test_enum_facts_do_not_require_compound_prose(self):
  self.assertEqual(self.atom(note='Unsupported gratuitous compound claim')['fact'],'api_key')
 def test_plural_api_purpose_rejected(self):
  spans={'p':{'source_kind':'official','text':'Advertising APIs enable developers to manage campaigns.'}}
  self.assertIsNotNone(p.purpose_error('Advertising APIs help manage campaigns.',['p'],spans))
 def test_nested_section_context_excludes_navigation(self):
  fragments=r.parse('<nav><h2>Noise</h2><p>API reference and account signup navigation links here.</p></nav><article><h1>Setup</h1><h2>OAuth</h2><h3>Public apps</h3><p>Register your application and request the appropriate permissions.</p><h2>Keys</h2><p>Administrators can create credentials for personal integrations here.</p></article>','text/html')
  body=[f for f in fragments if f['category']=='body']
  self.assertEqual(body[0]['section_context'],['Setup','OAuth','Public apps'])
  self.assertEqual(body[1]['section_context'],['Setup','Keys'])
 def test_search_bookkeeping_requires_actual_category_queries(self):
  review=p.inventory_review([], [{'category':'version','query':'minimum versions','ok':True}],{})[0]
  book={x['category']:x for x in review['category_search_bookkeeping']}
  self.assertTrue(book['version']['searched']); self.assertFalse(book['account']['searched'])
 def test_independent_completeness_ignores_model_assertion(self):
  logs=[{'category':cat,'query':cat,'ok':True} for cat in p.CATEGORIES]
  review=p.inventory_review([],logs,{},model_assertion={'coverage_complete':True})[0]
  self.assertFalse(review['completeness_established']); self.assertTrue(review['unresolved_gaps'])
 def test_saved_capture_and_citation_hash_fail_closed(self):
  text='Example body paragraph with complete credential setup requirements.'
  doc={'text':text,'fragments':[{'text':text}],'content_sha256':s.digest(text)}
  value={'retrievals':[doc],'passages':{'p':{'text':text,'source_index':0,'content_sha256':doc['content_sha256']}}}
  self.assertFalse(p.capture_errors(value))
  value['passages']['p']['content_sha256']='wrong'
  self.assertTrue(p.capture_errors(value))
  doc['text']+=' changed'
  self.assertGreaterEqual(len(p.capture_errors(value)),2)
 def test_category_specific_discovery_covers_actual_calls(self):
  from unittest.mock import MagicMock
  client=MagicMock(); client.tools.execute.return_value={'successful':True}
  logs=r.discover(client,{'slug':'search','query_key':'query','version':'1'},{'name':'Example','website_hint':'https://example.com','docs_urls':[]})
  self.assertTrue(set(p.CATEGORIES)<=set(x['category'] for x in logs))
  self.assertEqual(client.tools.execute.call_count,len(logs))

if __name__=='__main__': unittest.main()
