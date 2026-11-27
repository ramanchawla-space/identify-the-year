"""Maths-riddle hints: each one has exactly one answer between 1990 and 2026 (checked by brute force)."""
import math
LO, HI = 1990, 2026
def digits(y): return [int(c) for c in str(y)]
def isprime(n): return n > 1 and all(n % p for p in range(2, int(n ** .5) + 1))
def roman(n):
    out = ''
    for v, s in ((1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),(50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')):
        while n >= v: out += s; n -= v
    return out
def pair(y):  # two-digit factor pair closest to the square root
    for a in range(int(y ** .5), 9, -1):
        if y % a == 0 and 10 <= y // a <= 99 and a >= 10: return a, y // a
    return None

# Each template: y -> (text, predicate) or None when it doesn't apply to y.
T = [
 lambda y: (f"Double my last two digits and add 7. You get {2*(y%100)+7}.", lambda x, v=2*(y%100)+7: 2*(x%100)+7 == v) if y % 100 else None,
 lambda y: (f"I am {pair(y)[0]} × {pair(y)[1]}.", lambda x: x == y) if pair(y) else None,
 lambda y: (f"My four digits add up to {sum(digits(y))}, and I end in {y%10}.", lambda x, s=sum(digits(y)), e=y%10: sum(digits(x)) == s and x % 10 == e),
 lambda y: (f"I am 44 squared plus {y-1936}. (Hint: 44 × 44 = 1,936)", lambda x: x == y) if y < 2025 else (f"I am a perfect square: {math.isqrt(y)} × {math.isqrt(y)}.", lambda x: x == y) if math.isqrt(y)**2 == y else None,
 lambda y: (f"I'm a prime number, and my digits add up to {sum(digits(y))}.", lambda x, s=sum(digits(y)): isprime(x) and sum(digits(x)) == s) if isprime(y) else None,
 lambda y: (f"Multiply my last two digits by 3, then subtract 4. You get {3*(y%100)-4}.", lambda x, v=3*(y%100)-4: 3*(x%100)-4 == v) if y % 100 > 1 else None,
 lambda y: (f"Half of me is {y//2:,}.", lambda x: x == y) if y % 2 == 0 else None,
 lambda y: (f"In Roman numerals I'm written {roman(y)}.", lambda x: x == y),
 lambda y: (f"Flip my last two digits and you get {str(y%100).zfill(2)[::-1]}; all four of my digits add up to {sum(digits(y))}.",
            lambda x, r=str(y%100).zfill(2)[::-1], s=sum(digits(y)): str(x%100).zfill(2)[::-1] == r and sum(digits(x)) == s) if (y % 100) % 11 else None,
 lambda y: (f"Add 25 to me and divide by 5: you get {(y+25)//5}.", lambda x: x == y) if y % 5 == 0 else None,
]

def options(y):
    """All templates (index, text) whose only answer in LO..HI is y."""
    out = []
    for k, t in enumerate(T):
        r = t(y)
        if r and [x for x in range(LO, HI + 1) if r[1](x)] == [y]: out.append((k, r[0]))
    return out

def assign(years):
    """One riddle per round: spread the templates evenly, never the same template twice for one year."""
    used, by_year, res = [0] * len(T), {}, []
    for i, y in enumerate(years):
        opts = [o for o in options(y) if o[0] not in by_year.get(y, set())]
        k, text = min(opts, key=lambda o: (used[o[0]], (o[0] * 7 + y) % len(T)))
        used[k] += 1; by_year.setdefault(y, set()).add(k); res.append(text)
    return res

if __name__ == '__main__':
    import sys; sys.path.insert(0, '.')
    from spec import ROUNDS
    for r, h in zip(ROUNDS, assign([r['y'] for r in ROUNDS])): print(r['y'], '|', h)
