"""Execute Academy solutions in the local PineTS runtime and evaluate lab acceptance criteria.

Evidence level: THIRD_PARTY_RUNTIME (PineTS 0.13.1). This is real execution of the Pine source,
but NOT TradingView compilation/runtime. Official-editor gates stay NOT_RUN.
Usage: python lab_harness.py [--solutions DIR] [--label NAME] [--json OUT]
"""
import argparse
import hashlib
import json
import math
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT.parent / 'tools' / 'runtime' / 'run_pine.mjs'
T0 = 1704067200000
DAY = 86400000


def bars(rows):
    """rows: list of (open, high, low, close)."""
    return [dict(open=o, high=h, low=l, close=c, volume=1000.0, openTime=T0 + i * DAY)
            for i, (o, h, l, c) in enumerate(rows)]


def flat(closes):
    return bars([(c, c, c, c) for c in closes])


def random_walk(n=300, seed=42):
    rnd, p, rows = random.Random(seed), 100.0, []
    for _ in range(n):
        o = p
        c = max(1.0, o + rnd.gauss(0, 1.2))
        h = max(o, c) + abs(rnd.gauss(0, 0.6))
        l = min(o, c) - abs(rnd.gauss(0, 0.6))
        rows.append((round(o, 4), round(h, 4), round(l, 4), round(c, 4)))
        p = c
    return bars(rows)


def run(source_text, candles):
    with tempfile.TemporaryDirectory() as td:
        s, d, o = Path(td, 's.pine'), Path(td, 'd.json'), Path(td, 'o.json')
        s.write_text(source_text, encoding='utf-8')
        d.write_text(json.dumps(candles))
        subprocess.run(['node', str(RUNTIME), str(s), str(d), 'D', str(o)], check=True,
                       cwd=RUNTIME.parent, timeout=120)
        return json.loads(o.read_text())


def close_enough(a, b, tol=1e-9):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol * max(1.0, abs(b))


def series(res, *names):
    for n in names:
        if n in res.get('plots', {}):
            return res['plots'][n]
    raise KeyError(f'none of {names} in plots {list(res.get("plots", {}))}')


# Each lab: list of (criterion, function(source)->(bool, observed)). Expectations fixed before running.
def lab_L01(src):
    r = run(src, flat([10, 11, 12, 11, 14]))
    sma, chg = series(r, 'SMA'), series(r, 'Change', 'One-bar change')
    return [
        ('SMA len3 bar3=11, bar5=37/3', close_enough(sma[2], 11) and close_enough(sma[4], 37 / 3), sma),
        ('warm-up SMA is na (not 0)', sma[0] is None and sma[1] is None, sma[:2]),
        ('first change missing, others 1,1,-1,3', chg == [None, 1, 1, -1, 3], chg),
    ]


def lab_L02(src):
    c = random_walk()
    on, off = run(src, c), run(src.replace('input.bool(true', 'input.bool(false'), c)
    rsi_on, rsi_off = series(on, 'RSI'), series(off, 'RSI')
    out = [('RSI identical with gate on/off', all(close_enough(a, b) for a, b in zip(rsi_on, rsi_off)), None)]
    if 'RSI manual' in on['plots']:
        man = on['plots']['RSI manual']
        pairs = [(a, b) for a, b in zip(rsi_on, man) if a is not None and b is not None]
        out.append(('built-in RSI == manual rma RSI', len(pairs) > 250 and all(close_enough(a, b, 1e-9) for a, b in pairs),
                    len(pairs)))
        flat_run = run(src, flat([100] * 40))  # adversarial: no price change at all (review finding 2026-11-27)
        b, m = flat_run['plots']['RSI'][-1], flat_run['plots']['RSI manual'][-1]
        out.append(('flat prices: manual RSI == built-in', close_enough(b, m), (b, m)))
    return out


def lab_L03(src):
    # doji, bear, bull(12), doji, bull(14), bear
    r = run(src, bars([(10, 10, 10, 10), (11, 11, 9, 9), (10, 12, 10, 12), (12, 12, 12, 12), (12, 14, 12, 14), (14, 14, 13, 13)]))
    last, cnt = series(r, 'Last bullish close', 'Last confirmed bullish close'), series(r, 'Bull count')
    return [
        ('no state before first bullish close; doji ignored', last[:2] == [None, None] and cnt[:2] == [0, 0], (last, cnt)),
        ('last bullish close 12,12,14,14', last[2:] == [12, 12, 14, 14], last),
        ('bull count 1,1,2,2', cnt[2:] == [1, 1, 2, 2], cnt),
    ]


def lab_L04(src):
    r3 = run(src, flat([10, 11, 12, 11, 14]))
    r1 = run(src.replace('input.int(3', 'input.int(1'), flat([10, 11, 12, 11, 14]))
    rw = run(src, random_walk())
    size3, size1 = series(r3, 'Buffer size'), series(r1, 'Buffer size')
    out = [('size never exceeds N (N=3, N=1)', max(size3) <= 3 and max(size1) <= 1, (size3, size1))]
    if 'B0' in r3['plots']:
        buf = [r3['plots'][k][-1] for k in ('B0', 'B1', 'B2')]
        out.append(('final buffer [12,11,14]', buf == [12, 11, 14], buf))
        out.append(('N=1 final buffer [14]', r1['plots']['B0'][-1] == 14, r1['plots']['B0'][-1]))
    mean = series(rw, 'Buffer mean', 'Confirmed buffer mean')
    sma = [None] * 2 + [sum(x['close'] for x in random_walk()[i - 2:i + 1]) / 3 for i in range(2, 300)]
    out.append(('mean == SMA(3) after warm-up', all(close_enough(a, b, 1e-9) for a, b in zip(mean[2:], sma[2:])), None))
    return out


def lab_L05(src):
    rows = [(100, 101, 99, 100)] * 30 + [(0, 0, 0, 0)]
    r = run(src, bars(rows))
    pct = series(r, 'ATR percent')
    return [('ATR=2, close=100 -> 2 %', close_enough(pct[29], 2.0), pct[29]),
            ('zero denominator -> na', pct[30] is None, pct[30]),
            ('warm-up na, not 0', pct[0] is None, pct[0])]


def lab_L08(src):
    highs = [1, 2, 3, 10, 4, 3, 2, 3, 2, 1, 1]
    # Fixture fix (2026-11-27): a close above the candidate before confirmation necessarily raises that
    # bar's high and invalidates the candidate, so bar 4 only approaches the level (9.9).
    closes = [1, 2, 3, 9, 9.9, 2.5, 2, 10.5, 2, 1, 1]
    r = run(src, bars([(c, max(h, c), min(c, h) - 0.5, c) for h, c in zip(highs, closes)]))
    level = series(r, 'Swing level', 'Confirmed swing high')
    brk = series(r, 'Breakout', 'Close crosses prior level')
    first = next((i for i, v in enumerate(level) if v is not None), None)
    sig = [i for i, v in enumerate(brk) if v]
    return [('pivot at bar 3 observable at bar 5 (right=2)', first == 5 and level[5] == 10, (first, level)),
            ('no signal at or before confirmation bar 5', all(i > 5 for i in sig), sig),
            ('breakout on bar 7 only', sig == [7], sig)]


LABS = {'L01': lab_L01, 'L02': lab_L02, 'L03': lab_L03, 'L04': lab_L04, 'L05': lab_L05, 'L08': lab_L08}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--solutions', default=str(ROOT / 'solutions'))
    ap.add_argument('--label', default='own')
    ap.add_argument('--json')
    a = ap.parse_args()
    report = {}
    for lab, fn in LABS.items():
        f = Path(a.solutions, f'{lab}.pine')
        if not f.exists():
            continue
        src = f.read_text(encoding='utf-8')
        try:
            res = [{'criterion': c, 'pass': bool(ok), 'observed': obs if not isinstance(obs, float) or not math.isnan(obs) else None}
                   for c, ok, obs in fn(src)]
        except Exception as e:  # runtime error or missing plot
            res = [{'criterion': 'execution', 'pass': False, 'observed': str(e)[:300]}]
        report[lab] = {'sha256': hashlib.sha256(src.encode()).hexdigest(), 'results': res}
        status = 'PASS' if all(r['pass'] for r in res) else 'FAIL'
        print(f'[{a.label}] {lab} THIRD_PARTY_RUNTIME {status}')
        for r in res:
            print(f"    {'ok ' if r['pass'] else 'BAD'} {r['criterion']}" + ('' if r['pass'] else f"  observed={r['observed']}"))
    if a.json:
        Path(a.json).write_text(json.dumps({'runtime': 'PineTS 0.13.1 (third party, not TradingView)', 'label': a.label, 'labs': report}, indent=1))


if __name__ == '__main__':
    main()
