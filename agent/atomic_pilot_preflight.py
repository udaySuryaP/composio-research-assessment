"""Freeze previous pilots before the authorized fresh 12-app run."""
import hashlib
import subprocess
from agent import stage02 as s

RUN='atomic-pilot-20260917'

def main():
    d=s.ROOT/'data/correction'/RUN
    if d.exists():raise ValueError('New run ID must not already exist')
    hashes={p.name:{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest()
        for f in p.rglob('*') if f.is_file()} for p in (s.ROOT/'data/correction').iterdir() if p.is_dir()}
    s.save(d/'preflight-history-hashes.json',hashes,exclusive=True)
    s.save(d/'preflight-checkout.json',{'branch':subprocess.check_output(['git','branch','--show-current'],cwd=s.ROOT,text=True).strip(),
        'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=s.ROOT,text=True).strip(),
        'status':subprocess.check_output(['git','status','--short'],cwd=s.ROOT,text=True)},exclusive=True)
    print('Frozen prior pilot trees:',{k:len(v) for k,v in hashes.items()})

if __name__=='__main__':main()
