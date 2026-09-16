"""Generate a self-contained report that can be opened directly as a file."""
from pathlib import Path
import shutil
from .pipeline import ROOT

def main():
    site=ROOT/'site'
    source=(site/'index.html').read_text(encoding='utf-8-sig')
    css=(site/'style.css').read_text(encoding='utf-8-sig')
    dataset=(site/'dataset.js').read_text(encoding='utf-8-sig')
    js=(site/'app.js').read_text(encoding='utf-8-sig')
    source=source.replace('<link rel="stylesheet" href="style.css">','<style>'+css+'</style>')
    source=source.replace('<script src="dataset.js" defer></script>','')
    source=source.replace('<script src="app.js" defer></script>','')
    source=source.replace('</body>','<script>'+dataset+'</script><script>'+js+'</script></body>')
    # Portable exports use embedded data, keeping the single HTML useful offline.
    exports={p.name:p.read_text(encoding='utf-8-sig') for p in site.glob('*.json')}
    exports['results.csv']=(site/'results.csv').read_text(encoding='utf-8-sig')
    import json
    helper='''<script>const exportsData=EXPORTS;document.querySelectorAll('a[download]').forEach(a=>{const name=a.getAttribute('href');if(exportsData[name]){a.addEventListener('click',e=>{e.preventDefault();const u=URL.createObjectURL(new Blob([exportsData[name]],{type:name.endsWith('.csv')?'text/csv':'application/json'}));const b=document.createElement('a');b.href=u;b.download=name;b.click();setTimeout(()=>URL.revokeObjectURL(u),1000)})}});</script>'''
    helper=helper.replace('EXPORTS',json.dumps(exports,ensure_ascii=False).replace('</',r'<\/'))
    source=source.replace('</body>',helper+'</body>')
    (ROOT/'case-study.html').write_text(source,encoding='utf-8')
    print('Built portable case-study.html')

if __name__=='__main__':main()
