"""Check submission integrity and prepare a minimal static hosting directory."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
START='cc335e607b8d0a8af4f2715b8a912056bceec274'
ART='submission/composio-assessment-uday.html'
ALLOWED={'README.md','agent/stage04.py','agent/stage05.py','.github/workflows/pages.yml','STAGE05.md','submission/REVIEWER-NOTES.md','submission/COMPLIANCE.md'}
def check():
 data=(ROOT/ART).read_bytes()
 original=subprocess.check_output(['git','show',START+':'+ART],cwd=ROOT)
 assert data.replace(b'\r\n',b'\n')==original,'Accepted HTML changed'
 data=original.replace(b'\n',b'\r\n')
 assert hashlib.sha256(data).hexdigest()=='ea6c6914eb61e597ab8f428bd50abd7e1d5b5ca649bdeaef859bc6bd2dfab9c6'
 assert len(data)==81369 and len(data)<10_000_000
 text=data.decode();rows=json.loads(re.search(r'<script id="matrix-data" type="application/json">(.*?)</script>',text,re.S).group(1))
 assert len(rows)==len({r['id'] for r in rows})==100
 assert len({r['category'] for r in rows})==10
 assert sum(r['checked'] for r in rows)==44
 assert sum(r['checked']>0 for r in rows)==22
 changed=subprocess.check_output(['git','diff',START,'--name-only'],cwd=ROOT,text=True).splitlines()
 extra=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
 assert set(changed+extra)<=ALLOWED,changed+extra
 assert not subprocess.check_output(['git','diff',START,'--','data','site','submission/composio-assessment-uday.html','STAGE01.md','STAGE02.md','STAGE02-CORRECTION.md','STAGE03.md','STAGE04.md'],cwd=ROOT)
 print(json.dumps({'stage05':'PASS','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'apps':100,'categories':10,'accepted_html_equal':True,'evidence_unchanged':True}))
 return data
if __name__=='__main__':
 data=check()
 if len(sys.argv)>1 and sys.argv[1]=='publish':
  output=Path(sys.argv[2]);output.mkdir(parents=True,exist_ok=True)
  assert not any(output.iterdir()),'Publish directory must be empty'
  (output/'index.html').write_bytes(data);(output/'.nojekyll').write_bytes(b'')
  assert (output/'index.html').read_bytes()==data
