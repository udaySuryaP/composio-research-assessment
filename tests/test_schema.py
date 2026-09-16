import json
import unittest
from agent.schema import CLAIM_FIELDS, RESEARCH_SCHEMA, unknown_record


class CanonicalContractTests(unittest.TestCase):
    def test_strict_objects_require_every_property(self):
        def check(node):
            if node.get('type') == 'object':
                self.assertFalse(node['additionalProperties'])
                self.assertEqual(set(node['required']), set(node['properties']))
                for child in node['properties'].values():
                    check(child)
            elif node.get('type') == 'array':
                check(node['items'])
        check(RESEARCH_SCHEMA)
        json.dumps(RESEARCH_SCHEMA)

    def test_blank_record_is_explicitly_unknown_not_false(self):
        row = unknown_record(1, 'Example', 'Example category',
                             'https://example.com', 'contract-test', '2026-09-16T00:00:00Z')
        self.assertEqual(set(row), set(RESEARCH_SCHEMA['required']))
        self.assertEqual(row['api_available'], 'unknown')
        self.assertEqual(row['auth_methods'], ['unknown'])
        self.assertEqual(row['mcp_available'], 'unknown')
        self.assertEqual(row['verification_status'], 'needs_verification')
        self.assertEqual(row['evidence'], [])
        for field, definition in RESEARCH_SCHEMA['properties'].items():
            if 'enum' in definition:
                self.assertIn(row[field], definition['enum'])

    def test_evidence_is_field_attributable(self):
        evidence = RESEARCH_SCHEMA['properties']['evidence']['items']
        self.assertEqual(set(evidence['properties']['field']['enum']), set(CLAIM_FIELDS))
        self.assertTrue({'url', 'final_url', 'quote', 'claim', 'retrieved_at',
                         'content_sha256', 'supports_claim'} <= set(evidence['required']))


if __name__ == '__main__':
    unittest.main()
