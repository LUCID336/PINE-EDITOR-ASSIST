"""Phase 05: Human/AI feature indicator v2.1 - JSON contract, parity and independent feature checks (local, PineTS).

JSON events come from Pine Logs (log.info) because alert() does not fire on historical bars (same on TradingView).
Checks: JSON Schema 2.1, business rules (quality/missing consistency, timestamps, dedup), JSON == data-window plots
(shared core), independent references for EVERY feature, exact swing observation index, flat-price and staleness
fixtures, invalid-HTF degradation, default silence. Realtime flicker/rollback/alert delivery: NOT RUN (no ticks).
"""
import json
import re
import sys
from pathlib import Path

import jsonschema
import pytest

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pinelab_core as core  # noqa: E402
from test_indicator_reference import aggregate, ema as ref_ema, load as load_csv, rma, rsi as ref_rsi, sma, true_range  # noqa: E402

IND = LAB / 'workspace' / 'indicators' / 'market_features_v2.pine'
SCHEMA = json.loads((LAB / 'workspace' / 'indicators' / 'market_features_v2_1.schema.json').read_text())
DATA = LAB / 'testing' / 'synthetic_data' / 'synth_15m_seed7.csv'
LOG = 'Also write JSON to Pine Logs (testing)'
FEATURES = ['ema', 'rsi', 'atr_pct', 'rvol', 'htf_close', 'htf_trend', 'swing_high', 'dist_swing_atr']
SWING = 3


def events(res):
    out = []
    for line in res['logs']:
        m = re.match(r'^\[[^\]]+\]\s*(\{.*\})\s*$', line)
        if m:
            out.append(json.loads(m.group(1)))
    return out


def csv_fixture(tmp_path, rows):
    f = tmp_path / 'fx.csv'
    f.write_text('time,open,high,low,close,volume\n' + ''.join(
        f'{1704067200000 + i * 3600000},{o},{h},{l},{c},{v}\n' for i, (o, h, l, c, v) in enumerate(rows)))
    return f


@pytest.fixture(scope='module')
def ctx():
    res = core.run_engine(IND, csv=DATA, base_tf='15', timeframe='60', inputs={LOG: True})
    assert res['ok'], res.get('error')
    rows = load_csv(DATA)
    return dict(res=res, evs=events(res), h1=aggregate(rows, 3600000), d1=aggregate(rows, 86400000))


def approx_or_none(got, exp, rel=1e-9):
    if exp is None:
        return got is None
    return got is not None and got == pytest.approx(exp, rel=rel, abs=1e-10)


def test_one_event_per_confirmed_bar(ctx):
    assert [e['bar_open_ms'] for e in ctx['evs']] == ctx['res']['time']


def test_schema_and_business_rules(ctx):
    for ev in ctx['evs']:
        jsonschema.validate(ev, SCHEMA)
        nulls = [f for f in FEATURES if ev['features'][f] is None]
        assert ev['missing'] == nulls                                  # same list, same order as the export
        assert (ev['quality'] == 'MISSING') == bool(nulls)


def test_timestamps_and_dedup(ctx):
    evs, h1 = ctx['evs'], ctx['h1']
    durations = {h1[i + 1]['time'] - h1[i]['time'] for i in range(len(h1) - 1)}
    assert all(e['bar_close_ms'] - e['bar_open_ms'] in durations for e in evs)  # derived from data, not hard-coded
    keys = [(e['build'], e['config_id'], e['symbol'], e['timeframe'], e['bar_open_ms']) for e in evs]
    assert len(set(keys)) == len(keys)


def test_json_equals_plots_shared_core(ctx):
    res = ctx['res']
    code = {'READY': 1, 'STALE': 2, 'MISSING': 0}
    for i, ev in enumerate(ctx['evs']):
        for f in FEATURES:
            assert approx_or_none(ev['features'][f], res['plots'][f'f_{f}'][i]), (i, f)
        assert res['plots']['quality_code'][i] == code[ev['quality']]


def test_every_feature_against_independent_reference(ctx):
    h1, d1, evs = ctx['h1'], ctx['d1'], ctx['evs']
    c = [b['close'] for b in h1]
    e20, r14, atr = ref_ema(c, 20), ref_rsi(c, 14), rma(true_range(h1, True), 14)
    vb = sma([b['volume'] for b in h1], 20)
    dk = [d['time'] for d in d1]
    d_close, d_ema = [d['close'] for d in d1], ref_ema([d['close'] for d in d1], 10)
    highs = [b['high'] for b in h1]
    swing = None
    for i, ev in enumerate(evs):
        f = ev['features']
        atr_pct = None if atr[i] is None or c[i] == 0 else 100 * atr[i] / c[i]
        rvol = None if vb[i] in (None, 0) else h1[i]['volume'] / vb[i]
        j = dk.index(h1[i]['time'] - h1[i]['time'] % 86400000)
        htf_close = d_close[j - 1] if j > 0 else None
        htf_trend = None if j == 0 or d_ema[j - 1] is None else (1 if d_close[j - 1] > d_ema[j - 1] else -1 if d_close[j - 1] < d_ema[j - 1] else 0)
        if i >= 2 * SWING:
            cand = highs[i - SWING]
            nb = highs[i - 2 * SWING:i - SWING] + highs[i - SWING + 1:i + 1]
            if all(cand >= x for x in highs[i - 2 * SWING:i - SWING]) and all(cand > x for x in highs[i - SWING + 1:i + 1]):
                swing = cand                                             # local tie rule (>= left, > right)
                assert ev['meta']['swing_anchor_ms'] == h1[i - SWING]['time'] and ev['meta']['swing_age_bars'] == 0
        dist = None if swing is None or atr[i] in (None, 0) else (c[i] - swing) / atr[i]
        exp = dict(ema=e20[i], rsi=r14[i], atr_pct=atr_pct, rvol=rvol, htf_close=htf_close, htf_trend=htf_trend,
                   swing_high=swing, dist_swing_atr=dist)
        for k, v in exp.items():
            assert approx_or_none(f[k], v, rel=1e-8), (i, k, f[k], v)
        assert ev['meta']['htf_bar_open_ms'] == (dk[j - 1] if j > 0 else None)


def test_flat_prices_give_missing_not_ready(tmp_path):
    rows = [(100, 100, 100, 100, 10)] * 120                            # ATR = 0 -> atr_pct 0, dist_swing_atr null
    res = core.run_engine(IND, csv=csv_fixture(tmp_path, rows), base_tf='60', timeframe='60', inputs={LOG: True})
    assert res['ok'], res.get('error')
    evs = events(res)
    assert evs and all(e['quality'] == 'MISSING' for e in evs)
    assert all(e['features']['dist_swing_atr'] is None for e in evs)


def test_stale_swing_level(tmp_path):
    # one early swing high, then a long monotonic rise (no new pivot) -> STALE once the level is older than the limit
    rows = [(10 + k, 11 + k, 9 + k, 10.5 + k, 100) for k in range(6)] + [(15, 20, 14, 15, 100)] + \
           [(14 - k * 0.1, 14.5 - k * 0.1, 13 - k * 0.1, 14 - k * 0.1, 100) for k in range(6)] + \
           [(13 + k * 0.05, 13.2 + k * 0.05, 12.9 + k * 0.05, 13.1 + k * 0.05, 100 + k) for k in range(200)]
    res = core.run_engine(IND, csv=csv_fixture(tmp_path, rows), base_tf='60', timeframe='60',
                          inputs={LOG: True, 'Swing level stale after (bars)': 30, 'Higher timeframe': '240'})
    assert res['ok'], res.get('error')
    q = [e['quality'] for e in events(res)]
    assert 'STALE' in q
    stale = [e for e in events(res) if e['quality'] == 'STALE']
    assert all(e['meta']['swing_age_bars'] > 30 or e['meta']['htf_bar_open_ms'] is not None for e in stale)


def test_invalid_htf_degrades_to_null():
    res = core.run_engine(IND, csv=DATA, base_tf='15', timeframe='60', inputs={LOG: True, 'Higher timeframe': '30'})
    assert res['ok'], res.get('error')
    evs = events(res)
    assert evs and all(e['features']['htf_close'] is None and e['quality'] == 'MISSING' and 'htf_close' in e['missing'] for e in evs)


def test_default_emits_nothing():
    res = core.run_engine(IND, csv=DATA, base_tf='15', timeframe='60')
    assert res['ok'] and events(res) == []
