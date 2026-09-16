import copy
import unittest
from agent import stage03 as t

class Stage03Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.apps,cls.rows=t.baseline()
  cls.items=t.s.read(t.OUT/'human-review.json')
 def test_sample_deterministic_and_category_coverage(self):
  selected=t.select_sample(self.apps)
  self.assertEqual(selected,t.select_sample(list(reversed(self.apps))))
  self.assertEqual(len(set(selected)),20)
  cats=[a['category'] for a in self.apps if a['id'] in selected]
  self.assertEqual(len(set(cats)),10)
  self.assertTrue(all(cats.count(c)==2 for c in set(cats)))
  self.assertEqual(selected[:4],[2,1,95,94])
 def test_pending_has_no_accuracy_or_reviewer(self):
  result=t.score(self.items,self.items)
  self.assertEqual(result['scored_items'],0)
  self.assertIsNone(result['first_pass_accuracy'])
  self.assertTrue(all(r['reviewer'] is None and r['reviewed_at'] is None for r in self.items))
 def complete(self,index=0):
  r=copy.deepcopy(self.items[index]); r.update(reviewer='Uday',reviewed_at='2026-09-17T10:00:00+05:30',source_status='usable',observed_source_url='https://example.com/docs',notes='Synthetic unit-test fixture, not a real review',observed_correct_value=r['first_pass_value'],final_value=r['first_pass_value'],first_pass_correct='yes',final_correct='yes')
  return r
 def test_paired_accuracy_same_denominator(self):
  a=self.complete(); b=self.complete(1)
  b.update(observed_correct_value='admin_approval',final_value='admin_approval',first_pass_correct='no')
  result=t.score([a,b],self.items)
  self.assertEqual(result['first_pass_denominator'],2)
  self.assertEqual(result['final_denominator'],2)
  self.assertEqual(result['first_pass_accuracy'],0.5)
  self.assertEqual(result['final_accuracy'],1)
 def test_unclear_incomplete_and_ai_excluded(self):
  a=self.complete();a['first_pass_correct']='unclear'
  b=self.complete(1);b['source_status']='inaccessible'
  c=self.complete(2);c['reviewer']='AI'
  d=self.complete(3);d['reviewed_at']=None
  result=t.score([a,b,c,d],self.items)
  self.assertEqual(result['scored_items'],0)
  self.assertEqual(result['unclear_unscored'],2)
 def test_duplicate_and_changed_first_pass_rejected(self):
  a=self.complete()
  with self.assertRaises(ValueError):t.score([a,a],self.items)
  a['first_pass_value']='altered'
  with self.assertRaises(ValueError):t.score([a],self.items)
 def test_invalid_judgment_rejected(self):
  a=self.complete();a['first_pass_correct']='no'
  with self.assertRaises(ValueError):t.score([a],self.items)
  a=self.complete();a['reviewed_at']='yesterday'
  with self.assertRaises(ValueError):t.score([a],self.items)
 def correction(self):
  row=self.rows[0]
  return dict(app_id=row['id'],app_name=row['app_name'],field='api_available',original_value=row['api_available'],corrected_value='yes',reason='Synthetic test only',evidence=[dict(evidence_id='fixture',field='api_available',claim='yes',url='https://example.com',final_url='https://example.com',source_kind='official',retrieved_at='2026-09-17',content_sha256='fixture',quote='API',supports_claim='yes')],method='automated_verification',timestamp='2026-09-17T00:00:00+00:00')
 def test_corrections_preserve_original_and_identities(self):
  original=copy.deepcopy(self.rows)
  result=t.apply_corrections(self.rows,[self.correction()])
  self.assertEqual(self.rows,original)
  self.assertEqual(len(result),100)
  self.assertEqual([(r['id'],r['app_name'],r['category']) for r in result],[(a['id'],a['name'],a['category']) for a in self.apps])
  self.assertEqual(result[0]['api_available'],'yes')
 def test_invalid_correction_references_and_provenance(self):
  for key,value in [('app_id',101),('field','made_up'),('original_value','no'),('corrected_value','invalid'),('evidence',[]),('method','AI_human')]:
   c=self.correction();c[key]=value
   with self.assertRaises(ValueError):t.validate_corrections(self.rows,[c])
 def test_patterns_reconcile_and_no_final_insights(self):
  patterns=t.provisional_patterns(self.rows)
  for field in ('access_model','api_available','api_breadth','mcp_available','buildability'):
   self.assertEqual(sum(patterns['counts'][field].values()),100)
  self.assertEqual(sum(sum(v.values()) for v in patterns['category_buildability'].values()),100)
  self.assertEqual(patterns['insights'],[])
 def test_frozen_files_match_canonical_snapshot_and_prepared_has_no_silent_changes(self):
  integrity=t.s.read(t.OUT/'baseline-integrity.json')
  for run,hashes in integrity['frozen_snapshots'].items():
   for file,wanted in hashes.items():
    self.assertEqual(t.hashlib.sha256((t.s.ROOT/'data/runs'/run/file).read_bytes()).hexdigest(),wanted)
  self.assertEqual(t.s.read(t.OUT/'prepared-results.json'),t.apply_corrections(self.rows,t.s.read(t.OUT/'correction-log.json')))
