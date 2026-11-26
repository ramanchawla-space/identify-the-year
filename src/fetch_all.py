"""Resolve every exhibit in spec.py, download it into media/, and process sound clips with ffmpeg.
Writes final.json, which build.py turns into index.html.  Safe to re-run: existing outputs are skipped."""
import json, os, re, glob, subprocess, time, urllib.parse, shutil, sys
SP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SP)
MEDIA = os.path.join(ROOT, 'media')
TMP = os.path.join(SP, 'tmp'); os.makedirs(TMP, exist_ok=True)
sys.path.insert(0, SP)
from spec import ROUNDS
UA = 'YearQuizBuilder/1.0 (offline team quiz)'
CLIP_SECONDS = 45

# ---- title index from earlier search results ----
titles = set()
for f in ('sound_cands.json', 'aus_cands.json', 'te_cands.json', 'gap_cands.json'):
    p = os.path.join(SP, f)
    if not os.path.exists(p): continue
    d = json.load(open(p))
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == 'title' and isinstance(v, str): titles.add(v)
                if isinstance(k, str) and k.startswith('File:'): titles.add(k[5:])
                walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(d)

def resolve(name):
    if name in titles: return name
    hits = sorted(t for t in titles if t.startswith(name))
    if len(hits) >= 1: return hits[0]
    return name  # try as an exact title anyway

def api(params):
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    for a in range(5):
        r = subprocess.run(['curl', '-s', '-A', UA, url], capture_output=True, text=True).stdout
        try: return json.loads(r)
        except Exception: time.sleep(3 * (a + 1))
    return {}

def get(url, dest, tries=6):
    for a in range(tries):
        code = subprocess.run(['curl', '-sL', '-o', dest, '-w', '%{http_code}', '-A', UA, url], capture_output=True, text=True).stdout
        if code == '200' and os.path.exists(dest) and os.path.getsize(dest) > 2000:
            time.sleep(1.5); return True
        if code == '404': break
        time.sleep(45 if code == '429' else 5 * (a + 1))
    if os.path.exists(dest): os.remove(dest)
    return False

def ff(*args):
    return subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *args], capture_output=True, text=True)

def mean_volume(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'volumedetect', '-vn', '-f', 'null', '-'], capture_output=True, text=True)
    m = re.search(r'mean_volume: (-?[\d.]+) dB', r.stderr)
    return float(m.group(1)) if m else None

def has_audio(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return 'audio' in r.stdout

def process_clip(src, out, poster, start, length=CLIP_SECONDS):
    """Trim to CLIP_SECONDS from `start`, normalise loudness, H.264/AAC mp4 at 480p max."""
    if not os.path.exists(out):
        pre = ['-user_agent', UA, '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '10'] if src.startswith('http') else []
        r = ff(*pre, '-ss', str(start), '-i', src, '-t', str(length),
               '-vf', "scale='min(854,iw)':-2", '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '26', '-pix_fmt', 'yuv420p',
               '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '2',
               '-movflags', '+faststart', out)
        if r.returncode != 0:
            print('   ffmpeg error:', r.stderr[-300:]); return False
    if not os.path.exists(poster):
        ff('-ss', '2', '-i', out, '-frames:v', '1', '-q:v', '4', poster)
    return True

# ---- resolve all Commons titles to URLs in batches ----
items = []
for ri, r in enumerate(ROUNDS, 1):
    assert len(r['m']) == 4, ri
    assert sorted(m[0] for m in r['m']) == sorted(['world', 'aus', 'tech', 'ent']), ri
    for k, m in enumerate(r['m'], 1):
        items.append((ri, k, m))
need = sorted({resolve(m[1]) for _, _, m in items if not m[1].startswith('local:')})
info = {}
for i in range(0, len(need), 40):
    batch = need[i:i + 40]
    d = api({'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'iiprop': 'url|mime|size', 'iiurlwidth': 960,
             'titles': '|'.join('File:' + t for t in batch)})
    norm = {n['to']: n['from'] for n in d.get('query', {}).get('normalized', [])}
    for p in d.get('query', {}).get('pages', {}).values():
        t = norm.get(p['title'], p['title'])[5:]
        ii = (p.get('imageinfo') or [None])[0]
        if ii: info[t] = ii
        else: info[t] = None
    time.sleep(0.5)

out_rounds = []
problems = []
for ri, r in enumerate(ROUNDS, 1):
    media, clues = [], []
    for k, m in enumerate(r['m'], 1):
        cat, src, clue = m[0], m[1], m[2]
        is_video = len(m) > 3
        start = m[3] if is_video else 0
        length = m[4] if len(m) > 4 else CLIP_SECONDS
        base = os.path.join(MEDIA, f'r{ri:02d}-{k}')
        entry = {'cat': cat}
        if src.startswith('local:'):
            lf = sorted(glob.glob(os.path.join(MEDIA, src[6:] + '.*')) + glob.glob(os.path.join(SP, 'originals', src[6:] + '.*')))
            lf = [f for f in lf if '-poster' not in f]
            if not lf: problems.append(f'r{ri} {src} missing local'); continue
            raw = lf[0]
        else:
            t = resolve(src); ii = info.get(t)
            if not ii: problems.append(f'r{ri} not found on Commons: {src}'); continue
            if is_video:
                raw = None
                out_mp4 = base + '.mp4'
                if os.path.exists(out_mp4): raw = out_mp4
                else:
                    d = api({'action': 'query', 'format': 'json', 'prop': 'videoinfo', 'viprop': 'derivatives|url', 'titles': 'File:' + t})
                    vi = (list(d.get('query', {}).get('pages', {}).values())[0].get('videoinfo') or [{}])[0]
                    der = {x.get('transcodekey'): x['src'] for x in vi.get('derivatives', [])}
                    order = [der[k] for k in ('480p.vp9.webm', '480p.webm', '360p.vp9.webm', '360p.webm', '360p.mpeg4.mov', '240p.vp9.webm') if k in der]
                    order.append(vi.get('url', ii['url']).split('?')[0])
                    for u in order:
                        ok = False
                        for attempt in range(3):
                            if process_clip(u.split('?')[0], out_mp4, base + '-poster.jpg', start, length): ok = True; break
                            if os.path.exists(out_mp4): os.remove(out_mp4)
                            time.sleep(60)
                        if ok: raw = out_mp4; break
                    time.sleep(8)
                    if not raw:
                        problems.append(f'r{ri} video download failed: {t}'); continue
            else:
                url = ii.get('thumburl') or ii['url']
                ext = os.path.splitext(urllib.parse.unquote(url.split('?')[0]))[1].lower().replace('.jpeg', '.jpg')
                if ext not in ('.jpg', '.png', '.gif', '.webp'): ext = '.jpg'
                dest = base + ext
                if not os.path.exists(dest):
                    if not get(url, dest): problems.append(f'r{ri} image download failed: {t}'); continue
                    time.sleep(0.8)
                raw = dest
        if is_video:
            out, poster = base + '.mp4', base + '-poster.jpg'
            if not os.path.exists(out) and not has_audio(raw):
                problems.append(f'r{ri} clip has NO audio track: {src}'); continue
            if not os.path.exists(out) and not process_clip(raw, out, poster, start, length): problems.append(f'r{ri} clip processing failed: {src}'); continue
            mv = mean_volume(out)
            if mv is None or mv < -40: problems.append(f'r{ri} clip is (nearly) silent ({mv} dB): {src}')
            entry.update(t='video', local=os.path.relpath(out, ROOT), localposter=os.path.relpath(poster, ROOT), vol=mv)
        else:
            if src.startswith('local:'):
                dest = base + os.path.splitext(raw)[1]
                if not os.path.exists(dest): shutil.copy(raw, dest)
                raw = dest
            entry.update(t='img', local=os.path.relpath(raw, ROOT))
        media.append(entry); clues.append(clue)
    print(f'r{ri:02d} {r["y"]}: {len(media)} exhibits', flush=True)
    out_rounds.append({'y': r['y'], 'm': media, 'c': clues, 'h': r['h'], 'e': r['e']})

json.dump(out_rounds, open(os.path.join(SP, 'final.json'), 'w'), indent=1, ensure_ascii=False)
print('\nPROBLEMS:' if problems else '\nNo problems.')
for p in problems: print(' -', p)
