import unittest,json,re
from agent import stage04 as s
class SubmissionTests(unittest.TestCase):
 def test_projection_and_integrity(self): s.check()
 def test_paired_sample_and_coverage(self):
  summary=s.read('human-review-summary.json'); p=s.read('patterns.json')
  self.assertEqual([summary[k] for k in ['scored_items','first_pass_correct','final_correct','unclear_unscored','pending_items','human_reviewed_apps']],[35,7,35,5,0,20])
  self.assertEqual([p['summary'][k] for k in ['total_apps','categories','checked_critical_claims','unresolved_critical_claims','fully_resolved','partially_resolved','all_unknown_critical']],[100,10,44,656,0,22,78])
 def test_all_unknown_is_unresolved(self):
  text=s.OUT.read_text(encoding='utf-8');data=json.loads(re.search(r'<script id="matrix-data" type="application/json">(.*?)</script>',text,re.S).group(1))
  self.assertEqual(sum(r['checked']==0 for r in data),78)
  self.assertIn('Unknown means unresolved',text)
 def test_no_runtime_dependencies_or_secret_patterns(self):
  text=s.OUT.read_text(encoding='utf-8')
  self.assertNotRegex(text,r'fetch\s*\(|XMLHttpRequest|<script[^>]+src=|<link[^>]+href=')
  self.assertNotRegex(text,r'\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b')
if __name__=='__main__':unittest.main()
