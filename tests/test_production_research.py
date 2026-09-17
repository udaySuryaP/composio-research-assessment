import unittest
from agent import production_research as r, path_contracts as p

class ProductionTests(unittest.TestCase):
 def atom(self,label='auth:api_key',mode='primary',note='',state='available'):
  return {**r.normalize({'label':label,'mode':mode,'note':note,'state':state,'passage_ids':['p']},0),'retained':True}
 def test_core_survives_missing_dimensions_and_setup(self):
  result=r.project([self.atom()])
  self.assertEqual(result['findings']['auth_methods'],['api_key'])
  self.assertEqual(result['findings']['buildability'],'needs_further_investigation')
  self.assertEqual(result['field_status']['auth_methods']['status'],'source_backed_with_caveat')
 def test_failed_neighbor_does_not_blank_protocol(self):
  bad={**self.atom(),'retained':False}
  self.assertEqual(r.project([bad,self.atom('protocol:rest')])['findings']['api_types'],['rest'])
 def test_alternative_route_is_explicit(self):
  result=r.project([self.atom(mode='public_app')])
  self.assertEqual(result['findings']['auth_methods'],['api_key'])
  self.assertEqual(result['findings']['buildability'],'unresolved')
  self.assertIn('Surface-specific',result['field_status']['auth_methods']['caveats'][1])
 def test_no_silence_absence_or_no_blocker(self):
  projected=r.project([]); result=projected['findings']
  self.assertEqual(result['mcp_available'],'unknown')
  self.assertEqual(result['primary_blocker'],'unknown')
  self.assertEqual(projected['field_status']['buildability']['status'],'unresolved')
 def test_readiness_needs_documented_onboarding(self):
  atoms=[self.atom(),self.atom('protocol:rest'),self.atom('prerequisite:credential',mode='token_admin',note='Create an API key',state='required')]
  self.assertEqual(r.project(atoms)['findings']['buildability'],'likely_buildable_from_public_docs')
 def test_mcp_auth_does_not_establish_resource_auth(self):
  self.assertEqual(r.project([self.atom(mode='mcp_native')])['findings']['auth_methods'],['unknown'])
 def test_identity_protocol_and_body_guards_preserved(self):
  spans={'p':{'category':'body','text':'Use HTTPS to request your resources with a key.','heading':'API','source_kind':'official'}}
  self.assertIsNotNone(p.validate(self.atom('protocol:rest'),spans))
  spans['p']['source_kind']='third_party'
  self.assertIsNotNone(p.validate(self.atom(),spans))
  spans['p']['category']='navigation'
  self.assertIsNotNone(p.validate(self.atom(),spans))
 def test_mcp_owner_does_not_imply_availability(self):
  self.assertEqual(r.project([self.atom('mcp:vendor_owned',mode='mcp_native',note='Vendor owns server X')])['findings']['mcp_available'],'unknown')
 def test_history_and_fresh_review_separate(self):
  self.assertNotIn('human_checked',r.project([self.atom()])['field_status']['auth_methods'])
 def test_required_auth_is_current_auth(self):
  self.assertEqual(r.project([self.atom(state='required')])['findings']['auth_methods'],['api_key'])
 def test_field_downgrade_preserves_other_supported_fields(self):
  from unittest.mock import patch
  v={'atoms':[],'passages':{'p':{'text':'Example evidence'}},**r.project([self.atom(),self.atom('access:paid_plan',note='All products cost money')])}
  decisions=[{'atom_id':field,'decision':'unsupported' if field=='access_model' else 'supported','reason':'Product pricing does not establish API gate' if field=='access_model' else 'Supported'} for field,x in v['field_status'].items() if x['status']!='unresolved']
  with patch.object(r.c,'call',return_value=({'decisions':decisions},{})):
   result=r.field_audit(v,{'name':'Example'})
  self.assertEqual(result['findings']['auth_methods'],['api_key'])
  self.assertEqual(result['findings']['access_model'],'unknown')
 def test_missing_field_review_fails_closed(self):
  from unittest.mock import patch
  v={'atoms':[],'passages':{'p':{'text':'Example evidence'}},**r.project([self.atom()])}
  with patch.object(r.c,'call',return_value=({'decisions':[]},{})):
   result=r.field_audit(v,{'name':'Example'})
  self.assertEqual(result['findings']['auth_methods'],['unknown'])
  self.assertIn('field_audit_failure',result)
 def test_mcp_actions_cannot_enter_api_breadth_without_mcp_word_in_body(self):
  spans={'p':{'category':'body','text':'Create a record and update its fields using these tools.','heading':'Tools','source_kind':'official','url':'https://example.com/docs/mcp'}}
  self.assertIn('MCP surface',r.validate(self.atom('resource:create',note='Create records'),spans))
 def test_product_pricing_does_not_establish_api_gate(self):
  spans={'p':{'category':'body','text':'All product subscriptions require an annual paid contract for businesses.','heading':'Pricing','source_kind':'official','url':'https://example.com/pricing'}}
  self.assertIn('credential/access',r.validate(self.atom('access:paid_plan',note='Products need a subscription'),spans))
 def test_body_hash_mismatch_downgrades_only_referenced_field(self):
  from agent import production_qa as q
  value=r.project([self.atom(),self.atom('protocol:rest')]); value['field_refs']['api_types']=['other']; value['field_refs']['api_available']=['other']; value['field_refs']['buildability']=['other']; value['field_refs']['buildability_rationale']=['other']
  doc={'text':'Valid resource authentication evidence body.','content_sha256':r.s.digest('Valid resource authentication evidence body.'),'ok':True,'source_kind':'official'}
  v={'id':1,'atoms':[],'discovery':[],'retrievals':[doc],'passages':{'p':{'text':doc['text'],'category':'body','source_index':0,'source_kind':'official','content_sha256':doc['content_sha256']},'other':{'text':'Changed','category':'body','source_index':0,'source_kind':'official','content_sha256':'wrong'}},**value}
  q.check(v)
  self.assertEqual(v['findings']['auth_methods'],['api_key'])
  self.assertEqual(v['findings']['api_types'],['unknown'])
 def test_final_atom_downgrade_preserves_previously_reviewed_auth(self):
  from unittest.mock import patch
  from agent import production_qa as q
  auth=self.atom(); paid={**self.atom('access:paid_plan',note='Products cost money'),'atom_id':'a1','passage_ids':['price']}
  spans={'p':{'text':'Authenticate API resource requests using an API key.','heading':'Auth','category':'body','source_kind':'official','url':'https://example.com/auth'},'price':{'text':'Our product subscriptions require annual paid contracts for business users.','heading':'Pricing','category':'body','source_kind':'official','url':'https://example.com/pricing'}}
  v={'id':1,'atoms':[auth,paid],'passages':spans,'purpose':{'passage_ids':[]},'gaps':[],'failure':None,**r.project([auth,paid])}
  with patch.object(r,'field_audit',side_effect=AssertionError('Unchanged reviewed fields must survive unavailable adjacent review')):
   result=q.atom_qa(v,{'name':'Example'})
  self.assertEqual(result['findings']['auth_methods'],['api_key'])
  self.assertEqual(result['findings']['access_model'],'unknown')
 def test_saved_atom_review_survives_purpose_quota_failure(self):
  from unittest.mock import patch
  from pathlib import Path
  from agent import production_qa as q
  raw={'label':'auth:api_key','mode':'primary','state':'available','note':'','passage_ids':['p']}
  extraction={'extracted':{'atoms':[raw],'unresolved_gaps':[],'alternative_paths':[]}}
  review={'review':{'decisions':[{'atom_id':'a0','decision':'supported','reason':'Explicit resource auth'}]}}
  span={'text':'Authenticate API resource requests using an API key.','heading':'Auth','category':'body','source_kind':'official','url':'https://example.com/auth'}
  v={'id':12,'atoms':[],'passages':{'p':span},'failure':'model_service_credit_balance_exhausted'}
  with patch.object(Path,'exists',return_value=True),patch.object(q.s,'read',side_effect=[extraction,review]):
   result=q.recover_reviewed_atoms(v,Path('unused'))
  self.assertEqual(result['findings']['auth_methods'],['api_key'])
  self.assertEqual(result['findings']['buildability'],'unresolved')
  self.assertTrue(result['recovered_review_checkpoint'])

if __name__=='__main__': unittest.main()
