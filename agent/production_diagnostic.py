"""Minimal sanitized model service diagnostic; no credential output."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from agent import stage02 as s

def main():
 root=s.ROOT; s.ROOT=Path('U:/composio-research-assessment'); s.load_env(); s.ROOT=root
 payload={'model':os.getenv('OPENAI_MODEL',s.MODEL),'messages':[{'role':'user','content':'Reply OK.'}],'max_tokens':3}
 request=Request('https://api.openai.com/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'],'Content-Type':'application/json'})
 try:
  with urlopen(request,timeout=30) as response: result={'status':response.status,'model':payload['model'],'token_limit':response.headers.get('x-ratelimit-limit-tokens'),'remaining_tokens':response.headers.get('x-ratelimit-remaining-tokens'),'remaining_requests':response.headers.get('x-ratelimit-remaining-requests')}
 except HTTPError as exc:
  error=json.loads(exc.read()).get('error',{}); result={'status':exc.code,'type':error.get('type'),'code':error.get('code'),'message':s.safe(error.get('message'))}
 s.save(s.ROOT/'data/correction/full100-production-live-20260917/model-diagnostic.json',result)
 print(result)

if __name__=='__main__': main()
