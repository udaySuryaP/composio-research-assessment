import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from agent import stage02 as s
from agent.schema import unknown_record

class Stage02Tests(unittest.TestCase):
    def setUp(self):
        self.app=s.seeds()[0]
        self.record=unknown_record(1,self.app['name'],self.app['category'],s.website(self.app),'test',s.now())
        self.doc={'requested_url':'https://developer.salesforce.com/docs','final_url':'https://developer.salesforce.com/docs',
                  'retrieved_at':s.now(),'source_kind':'official','ok':True,'text':'This API uses OAuth 2.0 authentication.',
                  'content_sha256':s.digest('This API uses OAuth 2.0 authentication.')}
    def evidence(self,field,quote):
        return {'evidence_id':'e1','field':field,'claim':'claim','url':self.doc['requested_url'],
                'final_url':self.doc['final_url'],'source_kind':'official','retrieved_at':self.doc['retrieved_at'],
                'content_sha256':self.doc['content_sha256'],'quote':quote,'supports_claim':'yes'}
    def codes(self,record=None,docs=None):
        return {f['code'] for f in s.quality(record or self.record,self.app,docs if docs is not None else [self.doc])}
    def test_exact_seed_integrity(self):
        apps=s.seeds()
        self.assertEqual(len(apps),100)
        self.assertEqual(set(s.Counter(a['category'] for a in apps).values()),{10})
        self.assertEqual(sorted(a['id'] for a in apps),list(range(1,101)))
    def test_schema_rejects_extra_and_wrong_enum(self):
        self.assertEqual(s.validate_schema(self.record),[])
        bad=dict(self.record,api_available='probably',extra=True)
        self.assertEqual(len(s.validate_schema(bad)),2)
    def test_real_excerpt_and_provenance(self):
        self.record['auth_methods']=['oauth2']
        self.record['evidence']=[self.evidence('auth_methods','OAuth 2.0 authentication')]
        self.assertNotIn('quote_not_found',self.codes())
        self.assertNotIn('provenance_mismatch',self.codes())
        self.record['evidence'][0]['content_sha256']='fake'
        self.assertIn('provenance_mismatch',self.codes())
    def test_fabricated_quote_abstains_preserving_raw(self):
        self.record['auth_methods']=['oauth2']
        self.record['evidence']=[self.evidence('auth_methods','Fabricated quote')]
        accepted,flags,repairs=s.accept(self.record,self.app,[self.doc],'test')
        self.assertEqual(accepted['auth_methods'],['unknown'])
        self.assertEqual(self.record['auth_methods'],['oauth2'])
        self.assertIn('auth_methods',repairs)
    def test_failed_retrieval_never_supports_negative(self):
        self.record['api_available']='no'
        self.record['evidence']=[self.evidence('api_available','No API exists')]
        failed=dict(self.doc,ok=False,text='No API exists')
        self.assertIn('negative_without_explicit_evidence',self.codes(docs=[failed]))
        accepted,_,_=s.accept(self.record,self.app,[failed],'test')
        self.assertEqual(accepted['api_available'],'unknown')
    def test_unknown_enum_and_auth_contradiction(self):
        self.record['api_types']=['rest','unknown']
        self.record['api_available']='no'
        self.assertIn('mixed_unknown_enum',self.codes())
        self.assertIn('api_auth_contradiction',self.codes())
    def test_critical_community_evidence_flagged(self):
        self.record['auth_methods']=['oauth2']
        self.record['evidence']=[self.evidence('auth_methods','OAuth 2.0')]
        self.record['evidence'][0]['source_kind']='community'
        self.assertIn('nonofficial_critical_evidence',self.codes(docs=[dict(self.doc,source_kind='community')]))
    def test_checkpoint_resume_avoids_external_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            value={'record':self.record}
            s.save(directory/'apps/001.json',value,exclusive=True)
            with patch.object(s,'discover',side_effect=AssertionError('Must not discover')):
                self.assertEqual(s.process(self.app,directory,object(),{}),value)
    def test_exclusive_freeze_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'first-pass.json'
            s.save(path,[self.record],exclusive=True)
            original=path.read_bytes()
            with self.assertRaises(FileExistsError):
                s.save(path,[],exclusive=True)
            self.assertEqual(path.read_bytes(),original)
    def test_unexpected_app_failure_checkpointed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(s,'process',side_effect=RuntimeError('secret error body')):
                value=s.checkpoint_app(self.app,Path(tmp),None,None)
            self.assertEqual(value['record']['verification_status'],'failed')
            self.assertNotIn('secret error body',json.dumps(value))
            self.assertTrue((Path(tmp)/'apps/001.json').exists())
    def test_safe_env_loading_no_interpolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'.env').write_text('OPENAI_MODEL="test-model"\nCOMPOSIO_USER_ID=$(unsafe)\n',encoding='utf-8')
            with patch.object(s,'ROOT',Path(tmp)),patch.dict(s.os.environ,{},clear=True):
                s.load_env()
                self.assertEqual(s.os.getenv('OPENAI_MODEL'),'test-model')
                self.assertEqual(s.os.getenv('COMPOSIO_USER_ID'),'$(unsafe)')
    def test_model_strict_output_and_usage_mocked(self):
        from io import BytesIO
        response=BytesIO(json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(self.record)}}],
                'usage':{'prompt_tokens':12,'completion_tokens':8}}).encode())
        with patch.dict(s.os.environ,{'OPENAI_API_KEY':'test-key'}),patch.object(s,'urlopen',return_value=response) as call:
            record,usage,error=s.extract(self.app,[self.doc],'test')
        body=json.loads(call.call_args.args[0].data)
        self.assertEqual(body['response_format']['json_schema']['strict'],True)
        self.assertEqual(body['response_format']['json_schema']['schema'],s.RESEARCH_SCHEMA)
        self.assertEqual(usage['input_tokens'],12)
        self.assertIsNone(error)
    def test_url_validation_and_search_candidate_consumption(self):
        self.assertFalse(s.valid_url('file:///secret'))
        self.assertFalse(s.valid_url('https://user:password@example.com'))
        self.assertEqual(s.urls({'results':[{'url':self.doc['requested_url']}] }),[self.doc['requested_url']])

class CredentialScrubbingTests(unittest.TestCase):
    def test_documentation_credential_patterns_are_redacted(self):
        with patch.dict(s.os.environ,{},clear=True):
            samples=['sk_test_'+'A'*30,'whsec_'+'B'*30,'ghp_'+'C'*30]
            for sample in samples:
                result=s.safe({'text':'Documentation example '+sample})
                self.assertNotIn(sample,result['text'])
                self.assertIn('[REDACTED_DOCUMENTATION_CREDENTIAL]',result['text'])

class DiscoveryTests(unittest.TestCase):
    def test_action_requires_live_catalog_and_dated_version(self):
        info={'tools':[{'slug':'LIVE_SEARCH','input_parameters':{'properties':{'query':{'type':'string'}},'required':['query']}}],
              'toolkit':{'meta':{'version':'20260903_00'},'auth_schemes':[]}}
        selected=s.select_action(info,'LIVE_SEARCH')
        self.assertEqual(selected['query_key'],'query')
        with self.assertRaises(ValueError): s.select_action(info,'GUESS')
        info['toolkit']['meta']['version']='latest'
        with self.assertRaises(ValueError): s.select_action(info,'LIVE_SEARCH')
    def test_discovery_invokes_inspected_action_and_version(self):
        from unittest.mock import Mock
        client=Mock()
        client.tools.execute.return_value={'successful':True,'data':{'results':[{'url':'https://example.com/docs'}]}}
        config={'slug':'LIVE_SEARCH','query_key':'query','version':'20260903_00'}
        logs=s.discover(client,config,s.seeds()[0])
        self.assertEqual(len(logs),2)
        self.assertEqual(client.tools.execute.call_count,2)
        self.assertEqual(client.tools.execute.call_args.kwargs['version'],'20260903_00')
        self.assertEqual(s.urls(logs[0]['response']),['https://example.com/docs'])
    def test_raw_identity_mismatch_is_not_silently_lost(self):
        app=s.seeds()[0]
        raw=unknown_record(999,'wrong',app['category'],s.website(app),'test',s.now())
        accepted,flags,_=s.accept(raw,app,[],'test')
        self.assertEqual(accepted['id'],1)
        self.assertIn('raw_identity_mismatch',{f['code'] for f in flags})

class PostflightTests(unittest.TestCase):
    def test_frozen_run_and_checkpoint_consistency_then_detect_tampering(self):
        from agent.stage02_audit import audit
        apps=s.seeds()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            s.save(root/'data/apps.json',apps)
            directory=root/'data/runs/test-smoke'
            values=[]
            for index in (0,10,30,70):
                app=apps[index]
                record=unknown_record(app['id'],app['name'],app['category'],s.website(app),'test-smoke',s.now())
                value={'record':record,'raw_extraction':None,'quality_flags':s.quality(record,app,[]),
                       'deterministic_repairs':[],'discovery':[],'retrievals':[],'metrics':{},'failure':None}
                s.save(directory/'apps'/('%03d.json'%app['id']),value,exclusive=True)
                values.append(value)
            s.finalize(directory,values,{'mode':'smoke','run_id':'test-smoke'})
            with patch.object(s,'ROOT',root):
                result=audit('test-smoke')
                self.assertEqual(result['errors'],[])
                self.assertEqual(result['record_count'],4)
                path=directory/'first-pass.json'
                changed=s.read(path);changed[0]['app_name']='substituted product'
                s.save(path,changed)
                result=audit('test-smoke')
                self.assertTrue(any('Frozen hash mismatch' in e for e in result['errors']))
                self.assertTrue(any('Assigned identity mismatch' in e for e in result['errors']))

if __name__=='__main__': unittest.main()
