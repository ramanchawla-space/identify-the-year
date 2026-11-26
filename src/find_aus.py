import json,subprocess,time,urllib.parse,re
A={1:"Bob Hawke 1990",2:"Paul Keating 1991",3:"Eddie Mabo",4:"Sydney 2000 Olympic bid 1993",5:"1994 Eastern seaboard bushfires Sydney",
6:"Shane Warne 1995",7:"Port Arthur 1996",8:"John Howard 1996",9:"Thredbo landslide 1997",10:"1998 Sydney to Hobart",
11:"1999 Australian republic referendum",12:"Cathy Freeman 2000",13:"Sydney 2000 Olympic torch",14:"Centenary of Federation 2001",
15:"2002 Bali bombings",16:"2003 Canberra bushfires",17:"Ian Thorpe 2004",18:"Cronulla riots 2005",19:"Schapelle Corby",
20:"Steve Irwin",21:"Kevin Rudd 2007 election",22:"National Apology Stolen Generations 2008",23:"2008 Sydney World Youth Day",
24:"Black Saturday bushfires 2009",25:"Julia Gillard 2010",26:"Australian 2010 election",27:"2011 Brisbane floods",
28:"Cyclone Yasi 2011",29:"Julia Gillard 2012",30:"Sally Pearson London 2012",31:"Kevin Rudd 2013",32:"Tony Abbott 2013",
33:"Lindt Cafe siege 2014",34:"Malcolm Turnbull 2015",35:"2015 AFC Asian Cup",36:"2016 Australian federal election",
37:"2017 Australian Marriage Law Postal Survey",38:"Sydney marriage equality rally 2017",39:"Scott Morrison 2018",
40:"Ashleigh Barty 2019",41:"2019–20 Australian bushfire season",42:"Black Summer bushfires 2020",43:"Ashleigh Barty Wimbledon 2021",
44:"Melbourne lockdown 2021",45:"Anthony Albanese 2022",46:"2022 eastern Australia floods Lismore",47:"Matildas 2023 World Cup",
48:"2023 Australian Indigenous Voice referendum",49:"Australia Paris 2024 Olympics",50:"Anthony Albanese 2025",51:"2025 Australian federal election",52:"2026 Australia"}
def api(params):
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
    for a in range(5):
        r=subprocess.run(['curl','-s','-A','YearQuizBuilder/1.0 (offline team quiz)',url],capture_output=True,text=True).stdout
        try: return json.loads(r)
        except: time.sleep(3*(a+1))
    return {}
import os
out=json.load(open('aus_cands.json')) if os.path.exists('aus_cands.json') else {}
for i,qq in A.items():
    if str(i) in out: continue
    res=[]
    for ft in ('bitmap','video'):
        d=api({'action':'query','format':'json','generator':'search','gsrsearch':f'filetype:{ft} {qq}','gsrnamespace':6,'gsrlimit':12,
           'prop':'imageinfo','iiprop':'url|size|metadata|extmetadata','iiurlwidth':960,'iiextmetadatalanguage':'en','iiextmetadatafilter':'DateTimeOriginal'})
        for p in (d.get('query',{}).get('pages',{}) or {}).values():
            ii=(p.get('imageinfo') or [{}])[0]
            aud=any(x.get('name')=='audio' for x in (ii.get('metadata') or []))
            if ft=='video' and not aud: continue
            date=re.sub('<[^>]+>','',((ii.get('extmetadata') if isinstance(ii.get('extmetadata'),dict) else {}).get('DateTimeOriginal') or {}).get('value',''))[:40]
            res.append({'t':ft,'title':p['title'][5:],'url':ii.get('url'),'thumb':ii.get('thumburl'),'date':date,'dur':round(ii.get('duration') or 0),'mb':round(ii.get('size',0)/1e6,1)})
        time.sleep(0.4)
    out[str(i)]={'q':qq,'r':res}
    json.dump(out,open('aus_cands.json','w'),indent=1,ensure_ascii=False)
    print(i,qq,len(res),flush=True)
json.dump(out,open('aus_cands.json','w'),indent=1,ensure_ascii=False)
print('DONE')
