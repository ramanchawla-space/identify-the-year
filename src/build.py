import json, os, random, sys
SP = os.path.dirname(os.path.abspath(__file__)) + '/'
DST = os.path.join(SP, '..', 'index.html')
G = json.load(open(SP + 'final.json'))
sys.path.insert(0, SP)
from riddles import assign
RIDDLES = assign([q['y'] for q in G])   # the hint is a maths riddle that works out to the year

out = []
for i, q in enumerate(G, 1):
    media = []
    for m in q['m']:
        if not m.get('local'):
            continue
        d = {'t': m['t'], 'src': m['local'], 'cat': m.get('cat')}
        if m.get('localposter'): d['poster'] = m['localposter']
        if m.get('start'): d['start'] = m['start']
        media.append(d)
    # every exhibit must have its matching clue, and every round needs a clip with sound
    assert len(media) == len(q['c']), f"round {i} ({q['y']}): {len(media)} exhibits vs {len(q['c'])} clues"
    assert any(m['t'] == 'video' for m in media), f"round {i} ({q['y']}): no sound clip"
    out.append({'y': q['y'], 'm': media, 'c': q['c'], 'h': RIDDLES[i-1], 'e': q['e']})

# Base order (the page reshuffles on every visit) where neighbouring rounds are at least 3 years apart.
rng = random.Random(2026)
for attempt in range(100000):
    rng.shuffle(out)
    if all(abs(a['y'] - b['y']) >= 3 for a, b in zip(out, out[1:])):
        break
else:
    raise SystemExit('could not find a well-spread order')

tpl = open(SP + 'template.html').read()
open(DST, 'w').write(tpl.replace('/*__DATA__*/[]', json.dumps(out, ensure_ascii=False, indent=0)))
print(len(out), 'rounds; order:', [o['y'] for o in out])
