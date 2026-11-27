"""Property tests: Gold Multi-Setup v7 STRATEGY (local PineTS run on synthetic 5m gold data, mintick 0.01).

Checks the order mechanics, not profitability:
entries at the next open after a signal, leg sizes, TP/SL/BE exit prices, BE only after TP1,
no simultaneous long+short positions (netting rule), and that the R accounting matches the trade list.
Local evidence only (PineTS); TradingView fills can differ (intrabar path assumptions)."""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(LAB / 'tools'))
import pinelab_core as core  # noqa: E402

import os  # noqa: E402
STRAT = Path(os.environ.get('GOLD_STRAT_OVERRIDE', LAB / 'workspace' / 'strategies' / 'gold_multi_setup_v07_strategy.pine'))
DATA = LAB / 'testing' / 'synthetic_data' / 'synth_5m_gold_seed21.csv'
TICK = 0.01
PIP = 0.10
RISK = 100.0
STEP = 1.0   # lot step input default (PineTS symbol has no mincontract)
SL = {'FVG': 60, 'EMA': 80, 'BB': 160, 'PB': 120, 'RSI': 160}
RT = {k: 1.0 for k in SL}
MULT = {'TP1': 1.0, 'TP2': 1.5, 'TP3': 2.0, 'TP4': 3.0}
SIG = {'FVG': 'sig_FVG', 'EMA': 'sig_EMA', 'BB': 'sig_BB', 'PB': 'sig_PB', 'RSI': 'sig_RSI'}


@pytest.fixture(scope='module')
def run():
    r = core.run_engine(STRAT, csv=DATA, base_tf='5', timeframe='5', symbol='LOCAL:XAUUSD', mintick=TICK, timeout_s=400)
    assert r['ok'], r.get('error')
    bars = list(csv.DictReader(open(DATA)))
    groups = defaultdict(list)
    for t in r['strategy']['closedtrades']:
        groups[t['entry_id']].append(t)
    return r, bars, groups


def test_strategy_trades_every_enabled_setup_family(run):
    r, _, groups = run
    fams = {g.split('#')[0] for g in groups}
    assert len(groups) > 50 and {'FVG', 'BB'} <= fams


def test_entry_at_next_open_after_signal(run):
    r, bars, groups = run
    for gid, legs in groups.items():
        fam, t = gid.split('#')[0], legs[0]
        sb = t['entry_bar_index'] - 1
        d = 1 if t['size'] > 0 else -1
        assert r['plots'][SIG[fam]][sb] == d, (gid, sb)
        assert abs(t['entry_price'] - float(bars[t['entry_bar_index']]['open'])) < 1e-6, gid


def _leg(fam):
    return math.floor(RISK / (SL[fam] * PIP) / (4 * STEP) + 1e-9) * STEP


def test_leg_sizes_are_quarter_of_risk_sized_qty(run):
    _, _, groups = run
    for gid, legs in groups.items():
        fam = gid.split('#')[0]
        qty = 4 * _leg(fam)
        assert len(legs) <= 4
        assert abs(sum(abs(t['size']) for t in legs) - qty) < 1e-6 or gid == max(groups, key=lambda g: groups[g][0]['entry_bar_index']), gid
        for t in legs:
            if t['exit_comment'] in ('Neues Signal', 'Rest'):   # strategy.close() closes the remaining legs as one record
                assert abs(abs(t['size']) / (qty / 4) - round(abs(t['size']) / (qty / 4))) < 1e-6, (gid, t['size'])
            else:
                assert abs(abs(t['size']) - qty / 4) < 1e-9, (gid, t['size'], qty)


def _exit_ok(level, t, bars, favourable_gap):
    """Exit at the level, or at the bar open when the bar gapped beyond it."""
    px, op = t['exit_price'], float(bars[t['exit_bar_index']]['open'])
    if abs(px - level) <= TICK + 1e-9:
        return True
    return abs(px - op) < 1e-9 and favourable_gap(op, level)


def test_exit_prices_match_tp_sl_be_levels(run):
    _, bars, groups = run
    checked = defaultdict(int)
    for gid, legs in groups.items():
        fam = gid.split('#')[0]
        for t in legs:
            d, e, c = (1 if t['size'] > 0 else -1), t['entry_price'], t['exit_comment']
            slD = SL[fam] * PIP
            if c in MULT:
                lvl = e + d * slD * RT[fam] * MULT[c]
                assert _exit_ok(lvl, t, bars, lambda o, l: (o - l) * d > 0), (gid, c, t['exit_price'], lvl)
            elif c == 'SL':
                assert _exit_ok(e - d * slD, t, bars, lambda o, l: (l - o) * d > 0), (gid, t['exit_price'], e - d * slD)
            elif c == 'BE':
                assert _exit_ok(e, t, bars, lambda o, l: (l - o) * d > 0), (gid, t['exit_price'], e)
            else:
                assert c in ('Neues Signal', 'Rest') or c.startswith(fam + ' '), c   # own-setup reversal carries the new entry comment
            checked[c] += 1
    assert checked['TP1'] > 10 and checked['SL'] > 10 and checked['BE'] > 10, dict(checked)


def test_be_only_after_tp1_bar_and_tp_order(run):
    _, _, groups = run
    for gid, legs in groups.items():
        by = {t['exit_comment']: t for t in legs}
        if 'BE' in by:
            assert 'TP1' in by and min(t['exit_bar_index'] for t in legs if t['exit_comment'] == 'BE') > by['TP1']['exit_bar_index'], gid
        if any(c in by for c in ('TP2', 'TP3', 'TP4')):
            assert 'TP1' in by, gid
        if 'SL' in by:   # a full stop-out happens before TP1: all four legs stop together
            assert all(t['exit_comment'] == 'SL' for t in legs) and len(legs) == 4, gid


def test_no_simultaneous_long_and_short(run):
    _, _, groups = run
    iv = []
    for gid, legs in groups.items():
        d = 1 if legs[0]['size'] > 0 else -1
        iv.append((legs[0]['entry_bar_index'], max(t['exit_bar_index'] for t in legs), d, gid))
    iv.sort()
    for i, (s1, e1, d1, g1) in enumerate(iv):
        for s2, e2, d2, g2 in iv[i + 1:]:
            if s2 >= e1:
                break
            assert d1 == d2, (g1, g2)


def _trade_r(gid, legs):
    fam = gid.split('#')[0]
    return sum(t['profit'] for t in legs) / (4 * _leg(fam) * SL[fam] * PIP)


def test_r_accounting_matches_trade_list(run):
    r, _, groups = run
    net = sum(t['profit'] for legs in groups.values() for t in legs)
    assert abs(net - r['strategy']['netprofit']) < 1e-6
    open_ids = {t['entry_id'] for t in (r['strategy']['opentrades'] or [])}
    total_r = sum(_trade_r(g, l) for g, l in groups.items() if g not in open_ids)
    assert abs(r['plots']['net_R_total'][-1] - total_r) < 1e-6
    for legs in groups.values():
        for t in legs:
            assert abs(t['commission'] - abs(t['size']) * 0.10 * 2) < 1e-9


def test_dashboard_counts_match_trade_list(run):
    r, _, groups = run
    open_ids = {t['entry_id'] for t in (r['strategy']['opentrades'] or [])}
    done = {g: l for g, l in groups.items() if g not in open_ids}
    assert r['plots']['trades_counted'][-1] == len(done)
    assert r['plots']['wins_counted'][-1] == sum(1 for g, l in done.items() if _trade_r(g, l) > 0)
    assert r['plots']['tp1_hits_counted'][-1] == sum(1 for l in done.values() if any(t['exit_comment'] in MULT for t in l))
    assert r['plots']['entries_rejected'][-1] == 0


V7 = LAB / 'workspace' / 'indicators' / 'gold_multi_setup_v07.pine'


def _core(text):
    a = text.index('\nrealTk')
    b = text.index('\n', text.index('\nMULT') + 1)
    return text[a:b]


def test_signal_core_is_verbatim_copy_of_indicator():
    assert _core(STRAT.read_text()) == _core(V7.read_text())


def test_signals_identical_to_indicator_at_runtime(run, tmp_path):
    r = run[0]
    src = V7.read_text() + ''.join(
        f'\nplot(sigB.get({k}) ? 1 : sigS.get({k}) ? -1 : 0, "{n}", display = display.data_window)'
        for k, n in enumerate(SIG.values())) + '\n'
    p = tmp_path / 'v7_sig.pine'
    p.write_text(src)
    ind = core.run_engine(p, csv=DATA, base_tf='5', timeframe='5', symbol='LOCAL:XAUUSD', mintick=TICK, timeout_s=400)
    assert ind['ok'], ind.get('error')
    for n in SIG.values():
        assert ind['plots'][n] == r['plots'][n], n
    assert sum(abs(x) for n in SIG.values() for x in r['plots'][n]) > 50


def test_no_missed_or_premature_exits(run):
    """Independent of the engine: between entry and exit no active level was touched; on the exit bar one was.
    The BE stop is active from the bar after the TP1 fill (re-issued at that bar's close)."""
    _, bars, groups = run
    H = [float(b['high']) for b in bars]
    Lo = [float(b['low']) for b in bars]
    n = 0
    for gid, legs in groups.items():
        fam = gid.split('#')[0]
        d, e, eb = (1 if legs[0]['size'] > 0 else -1), legs[0]['entry_price'], legs[0]['entry_bar_index']
        slD = SL[fam] * PIP
        tp1 = [t for t in legs if t['exit_comment'] == 'TP1']
        be_from = tp1[0]['exit_bar_index'] + 1 if tp1 else 10 ** 9
        for t in legs:
            c = t['exit_comment']
            if c in ('Neues Signal', 'Rest') or c.startswith(fam + ' '):
                continue
            leg_mult = MULT[t['exit_id'].split()[0]]   # the exit order id names the leg (TPn <entry id>), also for SL/BE fills
            if c in MULT:
                assert t['exit_id'].split()[0] == c, (gid, t['exit_id'], c)
            for b in range(eb, t['exit_bar_index'] + 1):
                stop = e if b >= be_from else e - d * slD
                hit_stop = (Lo[b] <= stop + 1e-9) if d == 1 else (H[b] >= stop - 1e-9)
                hit_tp = leg_mult is not None and ((H[b] >= e + slD * leg_mult - 1e-9) if d == 1 else (Lo[b] <= e - slD * leg_mult + 1e-9))
                if b < t['exit_bar_index']:
                    assert not hit_stop, (gid, c, b, 'stop touched earlier')
                    assert not hit_tp, (gid, c, b, 'tp touched earlier')
                else:
                    assert hit_stop or hit_tp, (gid, c, b, 'exit without touch')
            n += 1
    assert n > 300


def test_conflicting_opposite_signal_is_skipped_not_reversed():
    """With EMA-Cross on, the data contain a short signal while another setup is long: it must be skipped and
    counted, never reverse (= silently close) the other setup's trade."""
    r = core.run_engine(STRAT, csv=DATA, base_tf='5', timeframe='5', symbol='LOCAL:XAUUSD', mintick=TICK,
                        inputs={'EMA-Cross 9/21': True}, timeout_s=400)
    assert r['ok'], r.get('error')
    assert r['plots']['conflicts_skipped'][-1] >= 1
    allowed = set(MULT) | {'SL', 'BE', 'Neues Signal', 'Rest'}
    for t in r['strategy']['closedtrades']:   # a reversal may only close the SAME setup's trade
        fam = t['entry_id'].split('#')[0]
        assert t['exit_comment'] in allowed or t['exit_comment'].startswith(fam + ' '), (t['entry_id'], t['exit_comment'])
