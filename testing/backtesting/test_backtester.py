"""Hand-computed fixtures for the independent backtester (expected values derived on paper, not from the code)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtester as bt  # noqa: E402


def mk(opens, closes):
    return [dict(time=i, open=o, high=max(o, c), low=min(o, c), close=c) for i, (o, c) in enumerate(zip(opens, closes))]


BARS = mk([100, 101, 104, 108, 110, 107], [101, 103, 107, 109, 108, 106])
ENTRY = [True, False, False, False, False, False]
EXIT = [False, False, False, True, False, False]


def test_next_bar_open_fill_and_percent_commission():
    p = bt.Params(initial_capital=10000, qty_type='fixed', qty_value=10, commission_pct=0.1)
    r = bt.run(BARS, ENTRY, EXIT, p)
    t = r.trades[0]
    assert (t.entry_bar, t.entry_price) == (1, 101)          # signal on bar 0 close -> fill at bar 1 open
    assert (t.exit_bar, t.exit_price) == (4, 110)            # exit signal bar 3 -> fill at bar 4 open
    assert t.entry_commission == pytest.approx(0.001 * 10 * 101)
    assert t.exit_commission == pytest.approx(0.001 * 10 * 110)
    assert t.pnl == pytest.approx(10 * 9 - 1.01 - 1.10)      # 87.89
    assert r.metrics['net_profit'] == pytest.approx(87.89)


def test_slippage_ticks_against_direction():
    p = bt.Params(qty_value=10, slippage_ticks=2, mintick=0.5)
    t = bt.run(BARS, ENTRY, EXIT, p).trades[0]
    assert t.entry_price == 102.0 and t.exit_price == 109.0  # +1 on buy, -1 on sell
    assert t.pnl == pytest.approx(70.0)


def test_process_orders_on_close_fills_signal_bar_close():
    p = bt.Params(qty_value=1, process_orders_on_close=True)
    t = bt.run(BARS, ENTRY, EXIT, p).trades[0]
    assert (t.entry_bar, t.entry_price, t.exit_bar, t.exit_price) == (0, 101, 3, 109)


def test_mark_to_market_drawdown():
    p = bt.Params(initial_capital=1000, qty_value=10)
    r = bt.run(BARS, ENTRY, [False] * 6, p)                  # never exits -> forced close at last close
    # equity: bar0 1000, bar1 1000+10*(103-101)=1020, bar2 1060, bar3 1080, bar4 1070, bar5 1050 (forced exit at 106)
    assert r.equity == pytest.approx([1000, 1020, 1060, 1080, 1070, 1050])
    assert r.metrics['max_drawdown'] == pytest.approx(30)
    assert r.trades[0].forced_exit and r.metrics['forced_exits'] == 1


def test_segment_blocks_entries_outside_and_forces_close():
    p = bt.Params(qty_value=1)
    entries = [False, False, True, False, False, False]
    r = bt.run(BARS, entries, [False] * 6, p, start=0, end=4)
    t = r.trades[0]
    assert (t.entry_bar, t.exit_bar, t.exit_price, t.forced_exit) == (3, 3, 109, True)
    r2 = bt.run(BARS, [False, False, False, False, True, False], [False] * 6, p, start=0, end=4)
    assert r2.trades == []                                    # signal at/after segment end ignored


def test_percent_of_equity_sizing_rule():
    p = bt.Params(initial_capital=10000, qty_type='percent_of_equity', qty_value=100, commission_pct=0.1)
    t = bt.run(BARS, ENTRY, EXIT, p).trades[0]
    assert t.qty * t.entry_price * 1.001 == pytest.approx(10000)
