"""Bounded rate-limit recovery with fresh retrieval, preserving failed attempts."""
import time
import copy
from urllib.error import HTTPError
from agent import coverage_correction as c, stage02 as s
from pathlib import Path

def main():
    d=s.ROOT/'data/correction/atomic-pilot-20260917'
    original=s.ROOT;s.ROOT=Path('U:/composio-research-assessment');s.load_env();s.ROOT=original
    client,info=s.catalog();config=s.select_action(info,'COMPOSIO_SEARCH_TAVILY')
    original_call=c.call
    def bounded_call(*args,**kwargs):
        if len(args)>3 and args[3]=='coverage_support':
            args=list(args);payload=copy.deepcopy(args[1]);claims=payload['claims']
            payload['atomic_contract']=claims[0].get('atomic_contract',{}) if claims else {}
            for claim in claims:claim.pop('atomic_contract',None)
            args[1]=payload
        for attempt in range(4):
            try:return original_call(*args,**kwargs)
            except HTTPError as exc:
                if exc.code!=429 or attempt==3:raise
                print('Rate limit; bounded retry',attempt+1,flush=True)
                time.sleep(55)
    c.call=bounded_call
    # Avoid duplicating the complete atom inventory inside every support claim.
    values=[]
    for app in [a for a in s.seeds() if a['id'] in c.PILOT]:
        p=d/'apps'/f"{app['id']:03d}.json"
        if p.exists():
            v=s.read(p)
            if v['failure'] and v['failure'].startswith('HTTPError:429'):
                saved=d/'failed-attempts'/p.name;saved.parent.mkdir(parents=True,exist_ok=True)
                p.rename(saved)
                print('Fresh retrieval recovery:',app['name'],flush=True)
                v=c.research(app,d,client,config,False)
            values.append(v)
        else:values.append(c.research(app,d,client,config,False))
    s.save(d/'recovery-policy.json',{'fresh_retrieval':True,'failed_attempts_preserved':True,
        'model_retry_429_attempts':4,'backoff_seconds':55,'sequential_app_recovery':True,
        'support_prompt_sha256':s.digest(c.AUDIT_PROMPT)},exclusive=True)
    print(c.summarize(d,values),flush=True)

if __name__=='__main__':main()
