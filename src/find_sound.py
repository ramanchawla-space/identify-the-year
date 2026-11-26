import json,subprocess,time,urllib.parse,re,sys
Q={1:["Hubble launch STS-31","Mandela release 1990","German reunification 1990"],
2:["Desert Storm 1991","Gulf War 1991","Pinatubo 1991"],
3:["Hurricane Andrew 1992","Barcelona 1992 Olympics","STS-49 1992"],
4:["STS-61 Hubble repair 1993","Oslo Accords signing","Waco 1993","1993 launch"],
5:["Mandela inauguration 1994","STS-64 1994","1994 shuttle launch"],
6:["Oklahoma City bombing 1995","STS-71 Mir docking","1995 shuttle"],
7:["Atlanta 1996 Olympics","STS-79 1996","1996 launch"],
8:["Euro 96","1996 shuttle launch STS-80","1996 Clinton"],
9:["Mars Pathfinder 1997","Hong Kong handover 1997","Cassini launch 1997"],
10:["Zarya launch 1998","STS-95 Glenn 1998","Good Friday Agreement 1998","Unity module 1998"],
11:["1999 solar eclipse","STS-93 Chandra 1999","1999 Clinton"],
12:["Sydney 2000 Olympics","Expedition 1 launch 2000","STS-106 2000"],
13:["Concorde 2000","STS-92 2000","2000 Gore Bush debate"],
14:["September 11 2001 attacks","Dennis Tito Soyuz 2001","Mir deorbit 2001"],
15:["2002 World Cup","STS-109 2002","Golden Jubilee 2002"],
16:["Columbia STS-107","Concorde final flight 2003","Iraq war 2003","Spirit launch 2003"],
17:["2004 tsunami","Spirit rover landing 2004","Opportunity landing 2004","Athens 2004"],
18:["Hurricane Katrina 2005","STS-114 Return to Flight","Deep Impact 2005"],
19:["Pope Benedict XVI 2005","Live 8 2005","2005 London bombings"],
20:["Pluto 2006 IAU","New Horizons launch 2006","2006 World Cup","STS-121"],
21:["iPhone 2007","STS-117 2007","2007 Phoenix launch"],
22:["Beijing 2008 Olympics","2008 financial crisis","STS-124 2008"],
23:["Obama election night 2008","Large Hadron Collider 2008","Phoenix Mars 2008"],
24:["US Airways 1549","Obama inauguration 2009","STS-125 Hubble 2009"],
25:["Eyjafjallajökull 2010","Chilean miners rescue","Burj Khalifa opening","Solar Dynamics Observatory launch"],
26:["Deepwater Horizon","2010 FIFA World Cup vuvuzela","Deepwater Horizon oil spill 2010"],
27:["royal wedding 2011 William Kate","Fukushima tsunami 2011","Arab Spring Tahrir 2011","2011 Tohoku tsunami"],
28:["STS-135 launch","Atlantis final landing 2011","Osama bin Laden death Obama statement"],
29:["Curiosity landing 2012","London 2012 Olympics","Red Bull Stratos","Seven Minutes of Terror"],
30:["Hurricane Sandy 2012","Diamond Jubilee 2012","Gangnam Style"],
31:["Chelyabinsk meteor","Pope Francis 2013 habemus papam","2013 Wimbledon"],
32:["Typhoon Haiyan 2013","Mandela memorial 2013","Edward Snowden 2013"],
33:["Philae landing 2014","Ice Bucket Challenge","2014 World Cup Germany"],
34:["New Horizons Pluto flyby 2015","Nepal earthquake 2015","Paris Agreement COP21"],
35:["Falcon 9 landing Orbcomm 2015","2015 Women's World Cup","Falcon 9 Flight 20"],
36:["Juno Jupiter orbit insertion 2016","Rio 2016 Olympics","Brexit referendum 2016"],
37:["2017 eclipse totality","Cassini Grand Finale","Hurricane Harvey 2017"],
38:["Macron 2017","Federer Wimbledon 2017","2017 Macron victory speech"],
39:["Falcon Heavy test flight","Tham Luang cave rescue","2018 World Cup France","Falcon Heavy launch"],
40:["Notre-Dame fire 2019","black hole image Event Horizon Telescope","Greta Thunberg 2019"],
41:["2019 Women's World Cup","Boris Johnson 2019","2019 Cricket World Cup"],
42:["Crew Dragon Demo-2 launch","COVID-19 2020","2020 lockdown","Demo-2 2020"],
43:["Perseverance landing 2021","Ever Given Suez","Perseverance sounds Mars","Tokyo 2020 Olympics"],
44:["Ingenuity flight 2021","Inspiration4 launch","New Shepard NS-16 Bezos","Ingenuity sound"],
45:["James Webb first images 2022","Queen Elizabeth II funeral","2022 World Cup Argentina","Webb telescope 2022"],
46:["Artemis I launch","DART impact 2022","ChatGPT 2022"],
47:["Chandrayaan-3 landing","coronation Charles III 2023","Titan submersible"],
48:["2023 Turkey earthquake","Turkey Syria earthquake 2023","2023 Taylor Swift"],
49:["2024 eclipse totality","Francis Scott Key Bridge collapse","Paris 2024 Olympics","Starship flight 5 booster catch"],
50:["Pope Leo XIV","2025 Los Angeles wildfires","Trump inauguration 2025","Palisades fire"],
51:["Blue Ghost Moon landing","Blue Ghost 2025","Louvre heist 2025","Liverpool 2025"],
52:["2026 Winter Olympics Milano Cortina","2026 FIFA World Cup","America 250 2026"],}
G=json.load(open('final.json'))
def api(params):
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
    for a in range(5):
        r=subprocess.run(['curl','-s','-A','YearQuizBuilder/1.0 (offline team quiz)',url],capture_output=True,text=True).stdout
        try: return json.loads(r)
        except: time.sleep(3*(a+1))
    return {}
def has_audio(md):
    return any(x.get('name')=='audio' for x in (md or []))
import os
out=json.load(open('sound_cands.json')) if os.path.exists('sound_cands.json') else {}
for i,q in enumerate(G,1):
    if str(i) in out: continue
    cands={}
    for qq in Q[i]:
        d=api({'action':'query','format':'json','generator':'search','gsrsearch':f'filetype:video {qq}','gsrnamespace':6,'gsrlimit':15,
               'prop':'imageinfo','iiprop':'url|size|metadata|extmetadata','iiextmetadatalanguage':'en','iiextmetadatafilter':'DateTimeOriginal|ImageDescription|LicenseShortName'})
        for p in (d.get('query',{}).get('pages',{}) or {}).values():
            ii=(p.get('imageinfo') or [{}])[0]
            if not has_audio(ii.get('metadata')): continue
            em=ii.get('extmetadata') or {}
            em=em if isinstance(em,dict) else {}
            date=re.sub('<[^>]+>','',em.get('DateTimeOriginal',{}).get('value',''))[:60]
            desc=re.sub('<[^>]+>','',em.get('ImageDescription',{}).get('value',''))[:160]
            cands[p['title']]={'url':ii.get('url'),'dur':round(ii.get('duration') or 0),'mb':round(ii.get('size',0)/1e6,1),'date':date,'desc':desc,'q':qq}
        time.sleep(0.5)
    out[str(i)]={'y':q['y'],'c':cands}
    json.dump(out,open('sound_cands.json','w'),indent=1,ensure_ascii=False)
    print(i,q['y'],len(cands),flush=True)
json.dump(out,open('sound_cands.json','w'),indent=1,ensure_ascii=False)
print('DONE')
