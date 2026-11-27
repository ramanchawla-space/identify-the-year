"""List Commons videos that have an audio track, per year, from Category:Videos of YYYY (2 levels deep).
usage: python3 -I year_videos.py out.json 1990 2026"""
import json, subprocess, time, urllib.parse, sys, os
OUT, Y0, Y1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
UA = 'YearQuizBuilder/1.0 (offline team quiz)'
def api(p):
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p)
    for a in range(6):
        r = subprocess.run(['curl', '-s', '-A', UA, url], capture_output=True, text=True).stdout
        try: return json.loads(r)
        except Exception: time.sleep(5 * (a + 1))
    return {}
def members(cat, typ):
    out, cont = [], {}
    while True:
        d = api({'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtitle': cat, 'cmtype': typ, 'cmlimit': 500, **cont})
        out += [m['title'] for m in d.get('query', {}).get('categorymembers', [])]
        if 'continue' not in d or len(out) > 4000: return out
        cont = {'cmcontinue': d['continue']['cmcontinue']}
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
for y in range(Y0, Y1 + 1):
    if str(y) in res: continue
    root = f'Category:Videos of {y}'
    cats, files, seen = [root], set(), set()
    for depth in range(3):
        nxt = []
        for c in cats:
            if c in seen: continue
            seen.add(c)
            files.update(members(c, 'file'))
            if depth < 2: nxt += members(c, 'subcat')
        cats = nxt
        if len(seen) > 250: break
    files = sorted(files)
    rows = []
    for i in range(0, len(files), 50):
        d = api({'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'iiprop': 'size|metadata', 'titles': '|'.join(files[i:i + 50])})
        for p in d.get('query', {}).get('pages', {}).values():
            ii = (p.get('imageinfo') or [{}])[0]
            aud = any(isinstance(x, dict) and x.get('name') == 'audio' for x in (ii.get('metadata') or []))
            dur = round(ii.get('duration') or 0)
            if aud and 8 <= dur <= 3600: rows.append([p['title'][5:], dur])
        time.sleep(0.3)
    res[str(y)] = sorted(rows)
    json.dump(res, open(OUT, 'w'), indent=0, ensure_ascii=False)
    print(y, len(files), 'files', len(rows), 'with audio', flush=True)
