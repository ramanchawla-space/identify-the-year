"""Blur text in exhibits that would give the year away (dates on plaques, captions, discs, video overlays).
Run after fetch_all.py and before build.py.  Untouched copies are kept in src/originals/unredacted/, so the
blur is always applied to the original and re-running is safe.
Regions are fractions of the frame: (x0, x1, y0, y1, [t0, t1]) with an optional time window in seconds for video."""
import os, shutil, subprocess
SP = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(SP, '..', 'media')
KEEP = os.path.join(SP, 'originals', 'unredacted'); os.makedirs(KEEP, exist_ok=True)

REDACT = {
    'r02-2.jpg': [(.60, .76, .56, .70)],              # 1991: "World Champions 1991" plaque
    'r04-1.mp4': [(.15, .85, .85, .93)],              # 1993: Waco footage date/time stamp
    'r05-3.jpg': [(.64, .94, .49, .64), (.76, .96, .31, .40)],  # 1995: "Windows 95" and the (c) 1995 line on the CD
    'r12-2.jpg': [(.37, .60, .42, .48)],              # 2002: "Bali 12 Oktober 2002" on the memorial
    'r20-4.jpg': [(.37, .47, .40, .47)],              # 2010: "2010" on a banner
    'r32-4.jpg': [(.01, .17, .54, .69)],              # 2020: Gianna Bryant's dates on a memorial sign
    'r33-1.mp4': [(.08, .32, .86, .95, 10.5, 23.5)],  # 2021: "29 March 2021" satellite label
}

def chain(regions, w='iw', h='ih'):
    """ffmpeg filtergraph that blurs each region of [0] in turn."""
    parts, last = [], '0:v'
    for i, r in enumerate(regions):
        x0, x1, y0, y1 = r[:4]
        en = f":enable='between(t,{r[4]},{r[5]})'" if len(r) > 4 else ''
        parts.append(f"[{last}]split[b{i}][c{i}];[c{i}]crop=trunc(iw*{x1-x0:.3f}/2)*2:trunc(ih*{y1-y0:.3f}/2)*2:trunc(iw*{x0}/2)*2:trunc(ih*{y0}/2)*2,boxblur=luma_radius='min(10\\,min(w\\,h)/4)':luma_power=3:chroma_radius='min(5\\,min(cw\\,ch)/4)':chroma_power=3[k{i}];"
                     f"[b{i}][k{i}]overlay=trunc(main_w*{x0}/2)*2:trunc(main_h*{y0}/2)*2{en}[o{i}]")
        last = f'o{i}'
    return ';'.join(parts), f'[{last}]'

for name, regions in REDACT.items():
    path, keep = os.path.join(MEDIA, name), os.path.join(KEEP, name)
    if not os.path.exists(path): print('missing', name); continue
    if not os.path.exists(keep): shutil.copy(path, keep)
    graph, out = chain(regions)
    tmp = path + '.tmp' + os.path.splitext(name)[1]
    extra = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart'] \
        if name.endswith('.mp4') else ['-frames:v', '1', '-q:v', '3']
    r = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', keep, '-filter_complex', graph,
                        '-map', out, *(['-map', '0:a?'] if name.endswith('.mp4') else []), *extra, tmp], capture_output=True, text=True)
    if r.returncode: print('FAILED', name, r.stderr[-300:]); continue
    os.replace(tmp, path)
    print('blurred', name)
