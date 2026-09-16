"""Read-only credential-pattern scan; never prints matching content or secrets."""
import json
import os
import re
import subprocess
from pathlib import Path
from agent import stage02 as s

def scan():
 paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=s.ROOT).decode().split('\0')
 paths=[p for p in paths if p]
 secrets=[]
 env=s.ROOT/'.env'
 if env.exists():
  for line in env.read_text(encoding='utf-8').splitlines():
   if '=' in line and not line.lstrip().startswith('#'):
    key,value=line.split('=',1);value=value.strip().strip('"').strip("'")
    if key.strip() in ('OPENAI_API_KEY','COMPOSIO_API_KEY') and len(value)>=12:secrets.append(value)
 for key in ('OPENAI_API_KEY','COMPOSIO_API_KEY'):
  if os.environ.get(key):secrets.append(os.environ[key])
 pattern=re.compile(r'\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|sk_(?:live|test)_[A-Za-z0-9]{16,}|whsec_[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{15,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{30,})\b')
 failures=[]
 for name in paths:
  path=s.ROOT/name
  if not path.is_file():continue
  text=path.read_bytes().decode('utf-8',errors='replace')
  if pattern.search(text) or any(secret in text for secret in secrets):failures.append(name)
 ignored=subprocess.run(['git','check-ignore','-q','.env'],cwd=s.ROOT).returncode==0
 tracked_env=any(p=='.env' or (p.startswith('.env.') and p!='.env.example') for p in paths)
 result={'files_scanned':len(paths),'credential_findings':len(failures),'finding_paths':failures,'env_ignored':ignored,'env_secret_files_tracked':tracked_env,'limitation':'Configured-key and recognized-pattern scan; not an exhaustive secret guarantee or CVE audit.'}
 print(json.dumps(result))
 if failures or not ignored or tracked_env:raise SystemExit(1)
 return result
if __name__=='__main__':scan()
