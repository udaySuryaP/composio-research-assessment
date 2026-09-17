import sys
from agent import stage02 as s

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for aid in map(int,sys.argv[1:]):
        v=s.read(s.ROOT/'data/correction/body-pilot-v3-20260917/apps'/f'{aid:03d}.json')
        print('APP',aid,v['app_name']); print('PURPOSE',v.get('purpose'),v.get('purpose_error'))
        ids=set()
        for a in v.get('atoms',[]):
            if a['retained']:
                print(a['atom_id'],a['label'],a['mode'],a['state'],a['fact'],'IDS',a['passage_ids']); ids.update(a['passage_ids'])
        ids.update(v.get('purpose',{}).get('passage_ids',[]))
        for pid in sorted(ids):
            if pid not in v['passages']: print('INVALID',pid); continue
            p=v['passages'][pid]
            print('PASSAGE',pid,p['url'],'HEADING',p['heading'],'TEXT',p['text'])

if __name__=='__main__': main()
