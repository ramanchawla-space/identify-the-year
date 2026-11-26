import json
import os; SP=os.path.dirname(os.path.abspath(__file__))+'/'
DST=os.path.join(SP,'..','index.html')
G=json.load(open(SP+'final.json'))
out=[]
for q in G:
    media=[]
    for m in q['m']:
        if not m.get('local'): continue
        d={'t':m['t'],'src':m['local']}
        if m.get('localposter'): d['poster']=m['localposter']
        media.append(d)
    # put video last, photos first
    media.sort(key=lambda d:d['t']=='video')
    out.append({'y':q['y'],'m':media,'c':q['c'],'h':q['h'],'e':q['e']})
tpl=open(SP+'template.html').read()
open(DST,'w').write(tpl.replace('/*__DATA__*/[]',json.dumps(out,ensure_ascii=False,indent=0)))
print(len(out),'rounds; media per round:',[len(o['m']) for o in out])
