"""Phase 03: PineTS (via LocalProvider) vs independent Python reference implementations.

Reference definitions follow the official v6 reference pseudocode, with the TradingView-verified correction that
ta.ema is SMA-seeded (probe T1, 2026-11-27). Data: synthetic 15m base aggregated to the 60m chart on the UTC grid.
Each comparison checks warm-up (first non-na bar) and values (rel. tol 1e-9). Results feed compatibility.json.
"""
import csv
import math
import sys
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / 'tools'))
import pinelab_core as core  # noqa: E402

PROBE = LAB / 'testing' / 'regression' / 'fixtures' / 'indicator_reference_probe.pine'
DATA = LAB / 'testing' / 'synthetic_data' / 'synth_15m_seed7.csv'
NA = None


def load(path):
    with open(path) as f:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]


def aggregate(rows, ms):
    out = {}
    for r in rows:
        k = int(r['time']) - int(r['time']) % ms
        if k not in out:
            out[k] = dict(time=k, open=r['open'], high=r['high'], low=r['low'], close=r['close'], volume=r['volume'], sub=[r['close']])
        else:
            a = out[k]
            a['high'] = max(a['high'], r['high']); a['low'] = min(a['low'], r['low']); a['close'] = r['close']
            a['volume'] += r['volume']; a['sub'].append(r['close'])
    return [out[k] for k in sorted(out)]


# ---------- reference implementations ----------
def sma(s, n):
    return [NA if i < n - 1 or any(v is None for v in s[i - n + 1:i + 1]) else sum(s[i - n + 1:i + 1]) / n for i in range(len(s))]


def _seeded(s, n, alpha):
    out, prev, seed = [], None, sma(s, n)
    for i, v in enumerate(s):
        if prev is None:
            prev = seed[i]
        elif v is not None:
            prev = alpha * v + (1 - alpha) * prev
        out.append(prev)
    return out


def ema(s, n):
    return _seeded(s, n, 2 / (n + 1))


def rma(s, n):
    return _seeded(s, n, 1 / n)


def rsi(c, n):
    u = [None] + [max(c[i] - c[i - 1], 0) for i in range(1, len(c))]
    d = [None] + [max(c[i - 1] - c[i], 0) for i in range(1, len(c))]
    ru, rd = rma(u, n), rma(d, n)
    return [None if a is None or b is None else (100.0 if b == 0 else (0.0 if a == 0 else 100 - 100 / (1 + a / b))) for a, b in zip(ru, rd)]


def true_range(b, handle_na):
    out = []
    for i, x in enumerate(b):
        if i == 0:
            out.append(x['high'] - x['low'] if handle_na else None)
        else:
            pc = b[i - 1]['close']
            out.append(max(x['high'] - x['low'], abs(x['high'] - pc), abs(x['low'] - pc)))
    return out


def window(s, n, f):
    return [NA if i < n - 1 else f(s[i - n + 1:i + 1]) for i in range(len(s))]


def stdev_pop(s, n):
    def f(w):
        m = sum(w) / n
        return math.sqrt(sum((x - m) ** 2 for x in w) / n)
    return window(s, n, f)


def cross(a, b, up):
    out = [0]
    for i in range(1, len(a)):
        if None in (a[i], b[i], a[i - 1], b[i - 1]):
            out.append(0)
        elif up:
            out.append(1 if a[i] > b[i] and a[i - 1] <= b[i - 1] else 0)
        else:
            out.append(1 if a[i] < b[i] and a[i - 1] >= b[i - 1] else 0)
    return out


def pivot(s, L, R, high):
    out = [None] * len(s)
    for i in range(L + R, len(s)):
        c = s[i - R]
        nb = s[i - R - L:i - R] + s[i - R + 1:i + 1]
        if (high and all(c > x for x in nb)) or (not high and all(c < x for x in nb)):
            out[i] = c
    return out


@pytest.fixture(scope='module')
def ctx():
    rows = load(DATA)
    h1 = aggregate(rows, 3600000)
    d1 = aggregate(rows, 86400000)
    h4 = aggregate(rows, 4 * 3600000)
    res = core.run_engine(PROBE, csv=DATA, base_tf='15', timeframe='60')
    assert res['ok'], res.get('error')
    return dict(rows=rows, h1=h1, d1=d1, h4=h4, res=res, p=res['plots'])


def assert_series(got, exp, tol=1e-9, name=''):
    assert len(got) == len(exp), name
    first_got = next((i for i, v in enumerate(got) if v is not None), None)
    first_exp = next((i for i, v in enumerate(exp) if v is not None), None)
    assert first_got == first_exp, f'{name}: warm-up differs (first non-na {first_got} vs {first_exp})'
    bad = [(i, g, e) for i, (g, e) in enumerate(zip(got, exp))
           if (g is None) != (e is None) or (g is not None and abs(g - e) > tol * max(1.0, abs(e)))]
    assert not bad, f'{name}: {len(bad)} mismatches, first {bad[:3]}'


def test_bar_alignment(ctx):
    assert [t for t in ctx['res']['time']] == [b['time'] for b in ctx['h1']]


@pytest.mark.parametrize('name,fn', [
    ('sma20', lambda c: sma([b['close'] for b in c['h1']], 20)),
    ('ema20', lambda c: ema([b['close'] for b in c['h1']], 20)),
    ('rma14', lambda c: rma([b['close'] for b in c['h1']], 14)),
    ('rsi14', lambda c: rsi([b['close'] for b in c['h1']], 14)),
    ('atr14', lambda c: rma(true_range(c['h1'], True), 14)),
    ('tr_handle_na', lambda c: true_range(c['h1'], True)),
    ('highest10', lambda c: window([b['high'] for b in c['h1']], 10, max)),
    ('lowest10', lambda c: window([b['low'] for b in c['h1']], 10, min)),
    ('stdev20', lambda c: stdev_pop([b['close'] for b in c['h1']], 20)),
    ('change1', lambda c: [None] + [c['h1'][i]['close'] - c['h1'][i - 1]['close'] for i in range(1, len(c['h1']))]),
    ('cum_volume', lambda c: [sum(b['volume'] for b in c['h1'][:i + 1]) for i in range(len(c['h1']))]),
    ('array_mean5', lambda c: sma([b['close'] for b in c['h1']], 5)),
    ('pivothigh_2_2', lambda c: pivot([b['high'] for b in c['h1']], 2, 2, True)),
    ('pivotlow_2_2', lambda c: pivot([b['low'] for b in c['h1']], 2, 2, False)),
])
def test_numeric_reference(ctx, name, fn):
    tol = 1e-7 if name == 'cum_volume' else 1e-9
    assert_series(ctx['p'][name], fn(ctx), tol, name)


def test_cross_and_state(ctx):
    c = [b['close'] for b in ctx['h1']]
    f, s = ema(c, 10), ema(c, 30)
    assert ctx['p']['crossover_10_30'] == cross(f, s, True)
    assert ctx['p']['crossunder_10_30'] == cross(f, s, False)
    cnt, out = 0, []
    for b in ctx['h1']:
        cnt += b['close'] > b['open']
        out.append(cnt)
    assert ctx['p']['var_bull_count'] == out


def test_htf_previous_close_lookahead_on(ctx):
    days = {d['time']: d['close'] for d in ctx['d1']}
    keys = sorted(days)
    exp = []
    for b in ctx['h1']:
        k = keys.index(b['time'] - b['time'] % 86400000)
        exp.append(days[keys[k - 1]] if k > 0 else None)
    assert ctx['p']['htf_d_prev_close'] == exp


def test_htf_default_lookahead_off_historical(ctx):
    # Documented historical behaviour: the HTF value of a period appears on the chart bar that closes the period;
    # before that the previous completed period's value is shown (na before the first completed period).
    days = {d['time']: d['close'] for d in ctx['d1']}
    keys = sorted(days)
    exp = []
    for i, b in enumerate(ctx['h1']):
        day = b['time'] - b['time'] % 86400000
        last_of_day = i == len(ctx['h1']) - 1 or ctx['h1'][i + 1]['time'] - ctx['h1'][i + 1]['time'] % 86400000 != day
        k = keys.index(day)
        exp.append(days[day] if last_of_day else (days[keys[k - 1]] if k > 0 else None))
    assert ctx['p']['htf_d_close_default'] == exp


def test_htf_4h_previous_high(ctx):
    h4 = {d['time']: d['high'] for d in ctx['h4']}
    keys = sorted(h4)
    exp = []
    for b in ctx['h1']:
        k = keys.index(b['time'] - b['time'] % (4 * 3600000))
        exp.append(h4[keys[k - 1]] if k > 0 else None)
    assert ctx['p']['htf_4h_prev_high'] == exp


def test_lower_timeframe_arrays(ctx):
    assert ctx['p']['ltf15_count'] == [len(b['sub']) for b in ctx['h1']]
    assert ctx['p']['ltf15_last'] == [b['sub'][-1] for b in ctx['h1']]


def test_warmup_documentation(ctx):
    """Record first non-na bar per series (documented in TEST_REPORT); asserts the documented TradingView facts."""
    first = {k: next((i for i, v in enumerate(v) if v is not None), None) for k, v in ctx['p'].items()}
    assert first['ema20'] == 19          # TradingView-verified (T1): SMA-seeded
    assert first['sma20'] == 19
    assert first['rsi14'] == 14 and first['atr14'] == 13 and first['stdev20'] == 19
    assert first['pivothigh_2_2'] is None or first['pivothigh_2_2'] >= 4


TIE_CASES = {  # highs -> (bar where pivot is reported, value); PineTS 0.13.1 observed rule, TradingView UNVERIFIED (probe T11)
    'tie_left': ([1, 2, 5, 5, 3, 2, 1, 1], [(5, 5)]),
    'tie_right': ([1, 2, 3, 5, 5, 2, 1, 1], [(6, 5)]),
    'plateau3': ([1, 2, 5, 5, 5, 2, 1, 1], [(6, 5)]),
    'tie_far_right': ([1, 2, 3, 5, 3, 5, 1, 1], [(7, 5)]),
}


@pytest.mark.parametrize('case', sorted(TIE_CASES))
def test_pivot_tie_rule_local(tmp_path, case):
    highs, expected = TIE_CASES[case]
    f = tmp_path / 'ties.csv'
    f.write_text('time,open,high,low,close,volume\n' + ''.join(
        f'{1704067200000 + i * 3600000},{h - 0.5},{h},{h - 1},{h - 0.5},1\n' for i, h in enumerate(highs)))
    s = tmp_path / 'ties.pine'
    s.write_text('//@version=6\nindicator("ties")\nplot(ta.pivothigh(high, 2, 2), "ph")\n')
    r = core.run_engine(s, csv=f, base_tf='60', timeframe='60')
    assert [(i, v) for i, v in enumerate(r['plots']['ph']) if v is not None] == expected
