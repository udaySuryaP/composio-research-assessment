import copy
import json
from pathlib import Path
import unittest
from agent.pipeline import verify, score_reviews, FIELDS, ROOT

class EvidenceChecks(unittest.TestCase):
    def test_fabricated_quote_and_missing_document_are_rejected(self):
        fields={f:{'value':'unknown','source_ids':[],'quote':''} for f in FIELDS}
        fields['auth']={'value':['OAuth2'],'source_ids':[1],'quote':'OAuth2 definitely supported'}
        fields['access']={'value':'free','source_ids':[999],'quote':'Free for everyone'}
        docs=[{'id':1,'ok':True,'text':'This page describes a paid plan.'}]
        result=verify(fields,docs)
        self.assertEqual(result['auth']['value'],'unknown')
        self.assertEqual(result['access']['value'],'unknown')
        self.assertEqual(result['auth']['rejected_value'],['OAuth2'])

    def test_failed_retrieval_never_establishes_api_absence(self):
        fields={f:{'value':'unknown','source_ids':[],'quote':''} for f in FIELDS}
        fields['api']={'value':'no API','source_ids':[1],'quote':'Forbidden by access policy'}
        self.assertEqual(verify(fields,[{'id':1,'ok':False,'text':'Forbidden by access policy'}])['api']['value'],'unknown')

    def test_ai_blank_and_duplicate_reviews_do_not_inflate_human_accuracy(self):
        good={'app_id':1,'field':'auth','kind':'human','reviewer':'Uday','reviewed_at':'2026-09-16','source_url':'https://example.com/docs','notes':'Checked auth in docs','first_correct':False,'final_correct':True}
        ai=dict(good,kind='AI');blank=dict(good,app_id=2,reviewer=None);integer=dict(good,app_id=3,first_correct=1)
        result=score_reviews([good,copy.deepcopy(good),ai,blank,integer])
        self.assertEqual(result['scored_fields'],1)
        self.assertEqual(result['reviewed_apps'],1)
        self.assertEqual(result['first_correct'],0)
        self.assertEqual(result['final_correct'],1)

    def test_submission_covers_exact_set_and_valid_field_citations(self):
        rows=json.loads((ROOT/'data/results.json').read_text(encoding='utf-8'))
        self.assertEqual(sorted(r['id'] for r in rows),list(range(1,101)))
        self.assertEqual(len(set(r['name'] for r in rows)),100)
        self.assertEqual(len(set(r['category'] for r in rows)),10)
        for row in rows:
            self.assertEqual(set(row['fields']),set(FIELDS))
            docs={d['id']:d for d in row['documents']}
            for item in row['fields'].values():
                for source_id in item['source_ids']:
                    self.assertIn(source_id,docs)
                    self.assertTrue(docs[source_id]['ok'])
                if item.get('status')=='quote-grounded':
                    self.assertTrue(item['quote'])
                    self.assertTrue(item['source_ids'])

    def test_summary_and_portable_output_match_snapshot(self):
        rows=json.loads((ROOT/'data/results.json').read_text(encoding='utf-8'))
        summary=json.loads((ROOT/'data/summary.json').read_text(encoding='utf-8'))
        self.assertEqual(summary['total'],len(rows))
        self.assertEqual(sum(summary['counts']['access'].values()),len(rows))
        self.assertEqual(sum(summary['counts']['buildability'].values()),len(rows))
        self.assertTrue((ROOT/'site/dataset.js').read_text(encoding='utf-8').startswith('window.RESEARCH_DATA = '))

if __name__=='__main__':unittest.main()
