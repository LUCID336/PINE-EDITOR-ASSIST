"""Regression: Gold Multi-Setup v7 must reproduce v6 signals, trades, statistics and webhook JSON
(with gap-realistic statistics off; on gap-free data both settings must agree)."""
import json, sys
from pathlib import Path
import pytest

LAB = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(LAB / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pinelab_core as core  # noqa: E402
from instrument import instrument  # noqa: E402

V6 = LAB / 'workspace' / 'indicators' / 'gold_multi_setup_v06_original.pine'
V7 = LAB / 'workspace' / 'indicators' / 'gold_multi_setup_v07.pine'
DATA = LAB / 'testing' / 'synthetic_data' / 'synth_5m_gold_seed21.csv'


def run(src_path, tmp_path, name, inputs=None, data=DATA):
    p = tmp_path / f'{name}.pine'
    p.write_text(instrument(src_path.read_text()))
    r = core.run_engine(p, csv=data, base_tf='5', timeframe='5', inputs=inputs, timeout_s=300)
    assert r['ok'], r.get('error')
    return r


@pytest.fixture(scope='module')
def both(tmp_path_factory):
    t = tmp_path_factory.mktemp('gold')
    return run(V6, t, 'v6'), run(V7, t, 'v7', inputs={'Gap-realistische Statistik': False}), run(V7, t, 'v7d')


def test_original_produces_trades(both):
    v6 = both[0]
    assert sum(v6['plots'][f'stN_{k}'][-1] for k in range(5)) > 20     # the test data actually exercises the engine


@pytest.mark.parametrize('series', [f'{n}_{k}' for k in range(5) for n in ('sDir', 'sStage', 'stR', 'stN', 'stW')] + ['dayCnt'])
def test_engine_state_identical(both, series):
    v6, v7, _ = both
    assert v7['plots'][series] == v6['plots'][series]


def test_webhook_payloads_identical(both):
    v6, v7, _ = both
    assert len(v6['logs']) > 50
    assert v7['logs'] == v6['logs']
    for line in v6['logs'][:20]:
        json.loads(line.split('] ', 1)[1])                               # every payload is valid JSON


def test_default_gap_setting_identical_on_gapless_data(both):
    _, v7, v7d = both
    assert all(v7d['plots'][f'stR_{k}'] == v7['plots'][f'stR_{k}'] for k in range(5))


def test_gap_realistic_loss_exceeds_one_r(tmp_path):
    """Constructed gap through the SL: v6 books exactly -1R, v7 (default) books the real loss from the gap open."""
    rows = [l for l in DATA.read_text().splitlines()[1:]]
    v6, v7 = run(V6, tmp_path, 'g6'), run(V7, tmp_path, 'g7')
    k = next(k for k in range(5) if v6['plots'][f'stN_{k}'][-1] > 0)
    # find a stop-loss bar in v6 (stR drops by exactly 1)
    st = v6['plots'][f'stR_{k}']
    i = next(i for i in range(1, len(st)) if st[i] is not None and st[i - 1] is not None and abs((st[i - 1] - st[i]) - 1.0) < 1e-9)
    hdr = 'time,open,high,low,close,volume'
    cols = rows[i].split(',')
    d = v6['plots'][f'sDir_{k}'][i - 1]
    o, h, l, c = map(float, cols[1:5])
    shift = -40.0 if d == 1 else 40.0                                   # open 40 $ beyond the stop
    o2 = o + shift
    cols[1:5] = [f'{o2:.2f}', f'{max(h, o2, c):.2f}', f'{min(l, o2, c):.2f}', f'{c:.2f}']
    rows[i] = ','.join(cols)
    f = tmp_path / 'gap.csv'
    f.write_text(hdr + '\n' + '\n'.join(rows) + '\n')
    g6, g7 = run(V6, tmp_path, 'gg6', data=f), run(V7, tmp_path, 'gg7', data=f)
    loss6 = g6['plots'][f'stR_{k}'][i - 1] - g6['plots'][f'stR_{k}'][i]
    loss7 = g7['plots'][f'stR_{k}'][i - 1] - g7['plots'][f'stR_{k}'][i]
    assert loss6 == pytest.approx(1.0) and loss7 > 1.0


def test_only5m_blocks_new_signals_on_other_timeframes(tmp_path):
    p = tmp_path / 'v7_15.pine'
    p.write_text(instrument(V7.read_text()))
    r = core.run_engine(p, csv=DATA, base_tf='5', timeframe='15', timeout_s=300)
    assert r['ok'], r.get('error')
    assert sum(r['plots'][f'stN_{k}'][-1] for k in range(5)) == 0 and r['logs'] == []
