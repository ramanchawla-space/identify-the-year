import json,subprocess,time,os,urllib.parse,sys
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'final.json')
OUT='media/'
G=json.load(open(SRC))
def get(url,dest,tries=6):
    for a in range(tries):
        c=subprocess.run(['curl','-sL','-o',dest,'-w','%{http_code}','-A','YearQuizBuilder/1.0 (offline team quiz)',url],capture_output=True,text=True).stdout
        if c=='200' and os.path.getsize(dest)>2000: return True
        time.sleep(4*(a+1))
    if os.path.exists(dest): os.remove(dest)
    return False
def alts(url):
    yield url
    for w in ('800px','640px','1280px'):
        if '/960px-' in url: yield url.replace('/960px-','/'+w+'-')
    if '/thumb/' in url and '/960px-' in url:  # original file
        yield url.replace('thumb.wikimedia.org','upload.wikimedia.org').replace('/thumb/','/').rsplit('/',1)[0]
for i,q in enumerate(G):
    for k,m in enumerate(q['m']):
        src=m['src'].split('?')[0].replace('thumb.wikimedia.org','upload.wikimedia.org')
        if m['t']=='video':
            name=src.split('/')[-1]; parts=src.split('/commons/')[1]
            urls=[f"https://upload.wikimedia.org/wikipedia/commons/transcoded/{parts}/{name}.360p.webm",
                  f"https://upload.wikimedia.org/wikipedia/commons/transcoded/{parts}/{name}.240p.vp9.webm"]
            ext='.webm'
        else:
            urls=list(alts(src)); ext=os.path.splitext(urllib.parse.unquote(src))[1].lower().replace('.jpeg','.jpg')
        dest=f"{OUT}q{i+1:02d}-{k+1}{ext}"
        if os.path.exists(dest) and os.path.getsize(dest)>2000: ok=True; st='HAVE'
        else:
            ok=any(get(u,dest,3 if j else 6) for j,u in enumerate(urls)); st='OK' if ok else 'FAIL'
            time.sleep(1)
        m['local']=dest if ok else None
        if m['t']=='video' and m.get('poster'):
            pd=f"{OUT}q{i+1:02d}-{k+1}-poster.jpg"
            if (os.path.exists(pd) and os.path.getsize(pd)>2000) or get(m['poster'].split('?')[0].replace('thumb.wikimedia.org','upload.wikimedia.org'),pd): m['localposter']=pd
        print(i+1,q['y'],m['t'],st,dest,flush=True)
    json.dump(G,open(SRC,'w'),indent=1,ensure_ascii=False)
print('DONE',flush=True)
