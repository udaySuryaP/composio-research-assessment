import copy
import csv
import json
import unittest
from collections import Counter
from agent import stage03 as t
from agent import stage03_finalize as f

class FinalProjectionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.apps,cls.original=t.baseline()
  cls.rows=t.s.read(t.OUT/'verified-results.json')
  cls.matrix=t.s.read(t.OUT/'claim-verification.json')
  cls.metrics=t.s.read(t.OUT/'patterns.json')
  cls.reviews=t.s.read(t.OUT/'human-review.json')
 def test_final_exact_identity_and_no_blanket_human_status(self):
  self.assertEqual(len(self.rows),100)
  self.assertEqual([(r['id'],r['app_name'],r['category']) for r in self.rows],[(a['id'],a['name'],a['category']) for a in self.apps])
  self.assertTrue(all(r['verification_status']=='needs_verification' for r in self.rows))
 def test_every_final_known_claim_has_independent_coverage(self):
  checked={(c['app_id'],c['field']) for c in self.matrix if c['status']=='checked'}
  for row in self.rows:
   for field in f.CLAIM_FIELDS:
    if f.known(row[field]):self.assertIn((row['id'],field),checked)
  self.assertEqual(self.rows[83]['api_types'],['unknown'])
  self.assertEqual(self.rows[83]['mcp_available'],'unknown')
  self.assertEqual(self.rows[49]['access_model'],'unknown')
 def test_independent_counts_and_category_reconciliation(self):
  for field,values in self.metrics['counts'].items():
   expected=Counter()
   for row in self.rows:
    if isinstance(row[field],list):
     for value in row[field]:expected[value]+=1
    else:expected[row[field]]+=1
   self.assertEqual({k:v['count'] for k,v in values.items()},dict(expected))
   self.assertTrue(all(v['denominator']==100 for v in values.values()))
  self.assertEqual(sum(v['denominator'] for v in self.metrics['category_comparison'].values()),100)
  known=sum(f.known(row[field]) for row in self.rows for field in t.FIELDS)
  self.assertEqual(700-known,self.metrics['summary']['unresolved_critical_claims'])
 def test_same_actual_35_paired_items_and_no_unclear_scoring(self):
  eligible=[r for r in self.reviews if r['reviewer']=='Uday' and r['source_status']=='usable' and r['first_pass_correct'] in ('yes','no') and r['final_correct'] in ('yes','no')]
  summary=t.s.read(t.OUT/'human-review-summary.json')
  self.assertEqual(len(eligible),35)
  self.assertEqual(sum(r['first_pass_correct']=='yes' for r in eligible),7)
  self.assertEqual(sum(r['final_correct']=='yes' for r in eligible),35)
  self.assertEqual(summary['first_pass_denominator'],len(eligible))
  self.assertEqual(summary['final_denominator'],len(eligible))
  self.assertEqual(summary['human_reviewed_apps'],20)
  self.assertEqual(summary['unclear_unscored'],5)
  for r in eligible:self.assertEqual(r['final_value'],self.rows[r['app_id']-1][r['field']])
 def test_sample_and_source_tampering_rejected(self):
  defs=copy.deepcopy(t.s.read(t.OUT/'review-items.json'));defs[0]['first_pass_value']=['api_key']
  with self.assertRaises(ValueError):f.validate_sample(self.apps,self.original,defs,t.s.read(t.OUT/'sample-manifest.json'))
  sources=copy.deepcopy(t.s.read(t.OUT/'targeted-source-excerpts.json'));sources[0]['observed_excerpt']='altered'
  with self.assertRaises(ValueError):f.sources_valid(t.s.read(t.OUT/'automated-checks.json'),sources)
 def test_abstentions_are_not_semantic_errors_and_first_pass_preserved(self):
  log=t.s.read(t.OUT/'correction-log.json')
  self.assertTrue(any(c.get('abstention') for c in log))
  for c in log:
   if c.get('abstention'):
    self.assertFalse(c['semantic_error_confirmed'])
    self.assertIn(c['corrected_value'],('unknown',['unknown']))
    self.assertEqual(c['original_value'],self.original[c['app_id']-1][c['field']])
  self.assertEqual(self.original,t.s.read(t.s.ROOT/'data/runs'/t.BASE/'first-pass.json'))
 def test_export_and_insight_denominators_reconcile(self):
  with (t.OUT/'verified-results.csv').open(encoding='utf-8',newline='') as handle:rows=list(csv.DictReader(handle))
  self.assertEqual(len(rows),100)
  for left,right in zip(rows,self.rows):
   for field,value in right.items():self.assertEqual(left[field],json.dumps(value,ensure_ascii=False) if isinstance(value,(dict,list)) else str(value))
  self.assertEqual(len(self.metrics['insights']),5)
  for insight in self.metrics['insights']:
   members=[r for r in self.reviews if r['field']==insight['field'] and r['source_status']=='usable' and r['final_correct'] in ('yes','no')]
   self.assertEqual(insight['denominator'],len(members))
   self.assertEqual(insight['numerator'],len(insight['review_item_ids']))
   self.assertTrue(insight['caveat'])
 def test_reproduce_final_projection(self):
  stamp=t.s.read(t.OUT/'finalization.json')['generated_at']
  rows,log,matrix,metrics,summary=f.expected_outputs(stamp)
  self.assertEqual(rows,self.rows)
  self.assertEqual(metrics,self.metrics)
  self.assertEqual(log,t.s.read(t.OUT/'correction-log.json'))

 def test_unclear_human_work_preserved_in_coverage_matrix(self):
  unclear=[c for c in self.matrix if c['status']=='unclear']
  self.assertEqual(len(unclear),5)
  self.assertTrue(all(c['method']=='human_review' and c['review_item_id'] for c in unclear))
  human_apps={c['app_id'] for c in self.matrix if c['method']=='human_review'}
  self.assertEqual(len(human_apps),20)
