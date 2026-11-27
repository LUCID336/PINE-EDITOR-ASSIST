"""Phase 05: Human/AI feature indicator - JSON contract, parity and independent feature checks (local, PineTS).

The JSON events are taken from Pine Logs (log.info), because alert() does not fire on historical bars (same on
TradingView). Checks: JSON Schema 2.0, business rules (quality consistency, timestamps, dedup), JSON == data-window
plots on the same bar (shared core), independent references for selected features, invalid-HTF degradation.
"""
import csv
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
from test_indicator_reference import aggregate, ema as ref_ema, load as load_csv  # noqa: E402

IND = LAB / 'workspace' / 'indicators' / 'market_features_v2.pine'
SCHEMA = json.loads((LAB / 'workspace' / 'indicators' / 'market_features_v2.schema.json').read_text())
DATA = LAB / 'testing' / 'synthetic_data' / 'synth_15m_seed7.csv'
LOG_INPUT = 'Also write JSON to Pine Logs (testing)'
FEATURES = ['ema', 'rsi', 'atr_pct', 'rvol', 'htf_close', 'htf_trend', 'swing_high', 'dist_swing_atr']
PLOT_OF = {f: f'f_{f}' for f in FEATURES}


def events_from_logs(logs):
    out = []
    for line in logs:
        m = re.match(r'^\[[^\]]+\]\s*(\{.*\})\s*$', line)
        if m:
            out.append(json.loads(m.group(1)))
    return out


def business_validate(ev):
    jsonschema.validate(ev, SCHEMA)
    assert ev['bar_open_ms'] < ev['bar_close_ms']
    expected_quality = 'MISSING' if any(v is None for v in ev['features'].values()) else 'READY'
    assert ev['quality'] == expected_quality, ev


@pytest.fixture(scope='module')
def run():
    res = core.run_engine(IND, csv=DATA, base_tf='15', timeframe='60', inputs={LOG_INPUT: True})
    assert res['ok'], res.get('error')
    return res, events_from_logs(res['logs'])


def test_one_event_per_confirmed_bar(run):
    res, evs = run
    assert len(evs) == len(res['time'])                       # every historical bar is confirmed
    assert [e['bar_open_ms'] for e in evs] == res['time']


def test_schema_and_business_rules(run):
    for ev in run[1]:
        business_validate(ev)


def test_dedup_keys_unique_and_timestamps(run):
    evs = run[1]
    keys = [(e['build'], e['config_id'], e['symbol'], e['timeframe'], e['bar_open_ms']) for e in evs]
    assert len(set(keys)) == len(keys)
    assert all(e['bar_close_ms'] - e['bar_open_ms'] == 3600000 for e in evs)
    assert all(a['bar_open_ms'] < b['bar_open_ms'] for a, b in zip(evs, evs[1:]))


def test_json_equals_plots_shared_core(run):
    res, evs = run
    for i, ev in enumerate(evs):
        for f in FEATURES:
            pv, jv = res['plots'][PLOT_OF[f]][i], ev['features'][f]
            assert (pv is None) == (jv is None), (i, f, pv, jv)
            if pv is not None:
                assert jv == pytest.approx(pv, rel=1e-9, abs=1e-10), (i, f)   # 10-decimal JSON formatting
        assert (res['plots']['quality_ready'][i] == 1) == (ev['quality'] == 'READY')


def test_warmup_is_null_not_zero(run):
    first = run[1][0]['features']
    assert first['ema'] is None and first['rsi'] is None and first['htf_close'] is None
    assert run[1][0]['quality'] == 'MISSING'
    assert any(e['quality'] == 'READY' for e in run[1])


def test_independent_feature_references(run):
    res, evs = run
    h1 = aggregate(load_csv(DATA), 3600000)
    d1 = aggregate(load_csv(DATA), 86400000)
    closes = [b['close'] for b in h1]
    e20 = ref_ema(closes, 20)
    days = {d['time']: d['close'] for d in d1}
    keys = sorted(days)
    for i, ev in enumerate(evs):
        if e20[i] is None:
            assert ev['features']['ema'] is None
        else:
            assert ev['features']['ema'] == pytest.approx(e20[i], rel=1e-9)
        k = keys.index(h1[i]['time'] - h1[i]['time'] % 86400000)
        exp_htf = days[keys[k - 1]] if k > 0 else None
        assert ev['features']['htf_close'] == (pytest.approx(exp_htf) if exp_htf is not None else None)


def test_swing_high_never_backdated(run):
    res, evs = run
    h1 = aggregate(load_csv(DATA), 3600000)
    highs = [b['high'] for b in h1]
    for i, ev in enumerate(evs):
        sh = ev['features']['swing_high']
        if sh is not None:                                     # level must already be observable at bar i
            assert sh in highs[:i - 3 + 1]                     # candidate at least `swing strength` (3) bars back


def test_invalid_htf_degrades_to_null(tmp_path):
    res = core.run_engine(IND, csv=DATA, base_tf='15', timeframe='60', inputs={LOG_INPUT: True, 'Higher timeframe': '30'})
    assert res['ok'], res.get('error')                         # no runtime.error, no divergence
    evs = events_from_logs(res['logs'])
    assert evs and all(e['features']['htf_close'] is None and e['features']['htf_trend'] is None for e in evs)
    assert all(e['quality'] == 'MISSING' for e in evs)


def test_default_emits_nothing():
    res = core.run_engine(IND, csv=DATA, base_tf='15', timeframe='60')
    assert res['ok'] and events_from_logs(res['logs']) == [] and res['alerts'] == []
