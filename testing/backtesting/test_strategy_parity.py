"""Phase 04: PineTS broker emulator vs independent Python replay for the example long/flat strategy.

Positive check: identical closed trades (bars, prices, pnl). Negative controls: wrong slippage, wrong commission and
on-close fills in the replay MUST produce mismatches (proves the comparison discriminates).
"""
import sys
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtester as bt  # noqa: E402
import pinelab  # noqa: E402
import pinelab_core as core  # noqa: E402

STRAT = LAB / 'workspace' / 'strategies' / 'ema_trend_longflat_v1.pine'
DATA = LAB / 'testing' / 'synthetic_data' / 'synth_60m_seed11.csv'


@pytest.fixture(scope='module')
def run():
    res = core.run_engine(STRAT, csv=DATA, base_tf='60', timeframe='60')
    assert res['ok'], res.get('error')
    bars = pinelab._load_bars(DATA, '60', '60', res['time'])
    ent = [bool(x) for x in res['plots']['sig_entry_long']]
    ext = [bool(x) for x in res['plots']['sig_exit_long']]
    eng = res['strategy']['closedtrades']
    return dict(res=res, bars=bars, ent=ent, ext=ext, eng=eng)


def replay(run, **kw):
    base = dict(initial_capital=10000, qty_type='fixed', qty_value=50, commission_pct=0.05, slippage_ticks=2, mintick=0.0001)
    base.update(kw)
    return [t for t in bt.run(run['bars'], run['ent'], run['ext'], bt.Params(**base)).trades if not t.forced_exit]


def mismatches(run, trades):
    n = abs(len(run['eng']) - len(trades))
    for a, b in zip(run['eng'], trades):
        if (a['entry_bar_index'], a['exit_bar_index']) != (b.entry_bar, b.exit_bar) or abs(a['entry_price'] - b.entry_price) > 1e-6 \
                or abs(a['exit_price'] - b.exit_price) > 1e-6 or abs(a['profit'] - b.pnl) > 1e-6:
            n += 1
    return n


def test_engine_has_trades(run):
    assert len(run['eng']) >= 10


def test_parity_exact(run):
    assert mismatches(run, replay(run)) == 0


def test_fill_is_next_bar_open_plus_slippage(run):
    for t in run['eng']:
        assert t['entry_price'] == pytest.approx(run['bars'][t['entry_bar_index']]['open'] + 2 * 0.0001)
        assert run['ent'][t['entry_bar_index'] - 1]          # signal on the previous bar's close


@pytest.mark.parametrize('wrong', [dict(slippage_ticks=0), dict(commission_pct=0.1), dict(process_orders_on_close=True),
                                   dict(qty_value=49)])
def test_negative_controls_detected(run, wrong):
    assert mismatches(run, replay(run, **wrong)) > 0


def test_cli_backtest_report_shape():
    import argparse
    env = pinelab.cmd_run_backtest(argparse.Namespace(script=str(STRAT), data=str(DATA), base_tf='60', tf='60', inputs=None,
                                                      oos=0.3, cost_stress=2.0))
    assert env['status'] == 'OK' and not env['errors']
    s = env['summary']
    assert s['parity_engine_vs_replay']['trade_mismatches'] == 0
    split = s['chronological_split']
    assert split['in_sample_bars'][1] == split['out_of_sample_bars'][0]           # contiguous, no overlap
    assert s['cost_stress']['metrics']['net_profit'] < s['independent_replay']['metrics']['net_profit']
    assert env['source_sha256'] and env['data_sha256'] and env['engine']['version']


def test_signals_recomputed_independently(run):
    """Independent recomputation of the strategy signals (EMA cross + prior-day HTF filter) from raw bars (review fix)."""
    sys.path.insert(0, str(LAB / 'testing' / 'regression'))
    from test_indicator_reference import cross, ema
    closes = [b['close'] for b in run['bars']]
    up, dn = cross(ema(closes, 20), ema(closes, 50), True), cross(ema(closes, 20), ema(closes, 50), False)
    days = {}
    for b in run['bars']:
        days[b['time'] - b['time'] % 86400000] = b['close']
    keys = sorted(days)
    d_close = [days[k] for k in keys]
    d_ema = ema(d_close, 10)
    trend = {}
    for j in range(1, len(keys)):                     # previous completed day: close > its EMA(10)
        trend[keys[j]] = d_ema[j - 1] is not None and d_close[j - 1] > d_ema[j - 1]
    exp_entry = [bool(up[i]) and trend.get(b['time'] - b['time'] % 86400000, False) for i, b in enumerate(run['bars'])]
    assert run['ent'] == exp_entry
    assert run['ext'] == [bool(x) for x in dn]
