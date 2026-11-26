# usage: python3 -I search.py queries.json out.json   ; queries: [[key, query, filetype], ...]
import json,subprocess,time,urllib.parse,re,sys,os
Q=json.load(open(sys.argv[1])); OUT=sys.argv[2]
out=json.load(open(OUT)) if os.path.exists(OUT) else {}
def api(params):
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
    for a in range(5):
        r=subprocess.run(['curl','-s','-A','YearQuizBuilder/1.0 (offline team quiz)',url],capture_output=True,text=True).stdout
        try: return json.loads(r)
        except: time.sleep(3*(a+1))
    return {}
for key,qq,ft in Q:
    k=f"{key}|{qq}|{ft}"
    if k in out: continue
    d=api({'action':'query','format':'json','generator':'search','gsrsearch':f'filetype:{ft} {qq}','gsrnamespace':6,'gsrlimit':10,
       'prop':'imageinfo','iiprop':'url|size|metadata|extmetadata','iiurlwidth':960,'iiextmetadatalanguage':'en','iiextmetadatafilter':'DateTimeOriginal'})
    res=[]
    for p in (d.get('query',{}).get('pages',{}) or {}).values():
        ii=(p.get('imageinfo') or [{}])[0]
        em=ii.get('extmetadata'); em=em if isinstance(em,dict) else {}
        aud=any(x.get('name')=='audio' for x in (ii.get('metadata') or []) if isinstance(x,dict))
        if ft=='video' and not aud: continue
        date=re.sub('<[^>]+>','',(em.get('DateTimeOriginal') or {}).get('value',''))[:40]
        res.append({'title':p['title'][5:],'url':ii.get('url'),'thumb':ii.get('thumburl'),'date':date,'dur':round(ii.get('duration') or 0),'mb':round(ii.get('size',0)/1e6,1),'idx':p.get('index',99)})
    res.sort(key=lambda r:r['idx'])
    out[k]=res
    json.dump(out,open(OUT,'w'),indent=1,ensure_ascii=False)
    print(k,len(res),flush=True); time.sleep(0.4)
print('DONE',flush=True)
