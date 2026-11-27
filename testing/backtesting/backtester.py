"""Independent, transparent long/flat backtester (Pine Engineering Lab V5).

Fill model (TradingView-verified 2026-11-27, probe T9, 87 trades): a market order created on the close of bar i
fills at the OPEN of bar i+1 (process_orders_on_close = false). Percent commission is charged per side on the fill
value (rate * qty * price). Slippage: `slippage` ticks * mintick against the trade direction (TradingView parameter
semantics; slippage itself NOT yet TradingView-verified).
Sizing: 'fixed' = qty units (verified). 'percent_of_equity' follows the PineTS-observed rule
qty = equity * pct / 100 / (fill_price * (1 + commission_rate))  -> TradingView parity UNVERIFIED.
This is a model, not the TradingView broker emulator.
"""
from dataclasses import dataclass, field, asdict
import math


@dataclass
class Params:
    initial_capital: float = 10000.0
    qty_type: str = 'fixed'            # 'fixed' | 'percent_of_equity'
    qty_value: float = 1.0
    commission_pct: float = 0.0        # percent per side, e.g. 0.1 = 0.1 %
    slippage_ticks: int = 0
    mintick: float = 0.0001
    process_orders_on_close: bool = False


@dataclass
class Trade:
    entry_bar: int
    entry_time: int
    entry_price: float
    qty: float
    entry_commission: float
    exit_bar: int = None
    exit_time: int = None
    exit_price: float = None
    exit_commission: float = 0.0
    pnl: float = None
    forced_exit: bool = False


@dataclass
class Result:
    params: dict
    segment: tuple
    trades: list = field(default_factory=list)
    equity: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def _fill_price(bars, i, side, p, on_close_bar=None):
    base = bars[on_close_bar]['close'] if on_close_bar is not None else bars[i]['open']
    slip = p.slippage_ticks * p.mintick
    return base + slip if side == 'buy' else base - slip


def run(bars, entry_sig, exit_sig, params=None, start=0, end=None, bars_per_year=24 * 365):
    """bars: list of dicts with time/open/high/low/close. entry_sig/exit_sig: bool per bar (evaluated at bar close).
    Only signals with index in [start, end) may open trades; an open trade is force-closed at the close of bar end-1."""
    p = params or Params()
    n = len(bars)
    end = n if end is None else min(end, n)
    if not 0 <= start < end:
        raise ValueError(f'empty or invalid segment [{start}, {end})')
    rate = p.commission_pct / 100.0
    cash = p.initial_capital
    pos = None
    trades, equity = [], []
    pending = None  # ('entry'|'exit', signal_bar)
    for i in range(start, end):
        # 1) execute order queued on the previous bar's close at this bar's open
        if pending and not p.process_orders_on_close:
            kind, sbar = pending
            if kind == 'entry' and pos is None:
                px = _fill_price(bars, i, 'buy', p)
                eq = cash
                qty = p.qty_value if p.qty_type == 'fixed' else eq * p.qty_value / 100.0 / (px * (1 + rate))
                comm = rate * qty * px
                cash -= comm
                pos = Trade(i, bars[i]['time'], px, qty, comm)
            elif kind == 'exit' and pos is not None:
                px = _fill_price(bars, i, 'sell', p)
                _close(pos, i, bars[i]['time'], px, rate)
                cash += pos.qty * (px - pos.entry_price) - pos.exit_commission
                trades.append(pos)
                pos = None
            pending = None
        # 2) evaluate signals at this bar's close
        if pos is not None and exit_sig[i]:
            pending = ('exit', i)
        elif pos is None and entry_sig[i] and i < end - 1:
            pending = ('entry', i)
        if pending and p.process_orders_on_close:  # fill on the signal bar's close
            kind, _ = pending
            if kind == 'entry':
                px = _fill_price(bars, i, 'buy', p, on_close_bar=i)
                qty = p.qty_value if p.qty_type == 'fixed' else cash * p.qty_value / 100.0 / (px * (1 + rate))
                comm = rate * qty * px
                cash -= comm
                pos = Trade(i, bars[i]['time'], px, qty, comm)
            else:
                px = _fill_price(bars, i, 'sell', p, on_close_bar=i)
                _close(pos, i, bars[i]['time'], px, rate)
                cash += pos.qty * (px - pos.entry_price) - pos.exit_commission
                trades.append(pos)
                pos = None
            pending = None
        # 3) mark to market at close
        equity.append(cash + (pos.qty * (bars[i]['close'] - pos.entry_price) if pos else 0.0))
    if pos is not None:  # force close at the segment's last close (no slippage: accounting close, flagged)
        i = end - 1
        _close(pos, i, bars[i]['time'], bars[i]['close'], rate)
        pos.forced_exit = True
        cash += pos.qty * (pos.exit_price - pos.entry_price) - pos.exit_commission
        trades.append(pos)
        equity[-1] = cash
    res = Result(params=asdict(p), segment=(start, end), trades=trades, equity=equity)
    res.metrics = metrics(bars, trades, equity, p, start, end, bars_per_year)
    return res


def _close(t, i, time, px, rate):
    t.exit_bar, t.exit_time, t.exit_price = i, time, px
    t.exit_commission = rate * t.qty * px
    t.pnl = t.qty * (px - t.entry_price) - t.entry_commission - t.exit_commission


def metrics(bars, trades, equity, p, start, end, bars_per_year):
    pnl = [t.pnl for t in trades]
    wins = [x for x in pnl if x > 0]
    losses = [x for x in pnl if x < 0]          # zero-P&L trades are neutral in both win rate and profit factor
    peak, mdd, mdd_pct = p.initial_capital, 0.0, 0.0   # drawdown measured from initial capital onwards
    for e in equity:
        peak = max(peak, e)
        mdd = max(mdd, peak - e)
        mdd_pct = max(mdd_pct, (peak - e) / peak * 100 if peak > 0 else 0)
    rets = [(equity[k] / equity[k - 1] - 1) for k in range(1, len(equity)) if equity[k - 1] > 0]
    mu = sum(rets) / len(rets) if rets else 0.0
    sd = math.sqrt(sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)) if len(rets) > 1 else 0.0
    in_pos = sum(t.exit_bar - t.entry_bar for t in trades)
    first, last = bars[start]['close'], bars[end - 1]['close']
    return {
        'trades': len(trades),
        'net_profit': round(sum(pnl), 10),
        'gross_profit': round(sum(wins), 10),
        'gross_loss': round(sum(losses), 10),
        'profit_factor': (sum(wins) / -sum(losses)) if losses else None,
        'profit_factor_note': None if losses else ('no losing trades (infinite)' if wins else 'no decisive trades'),
        'win_rate': len(wins) / len(trades) if trades else None,
        'neutral_trades': sum(1 for x in pnl if x == 0),
        'avg_trade': sum(pnl) / len(trades) if trades else None,
        'commission_paid': sum(t.entry_commission + t.exit_commission for t in trades),
        'max_drawdown': mdd,
        'max_drawdown_pct': mdd_pct,
        'exposure_pct': 100.0 * in_pos / max(1, end - start),
        'return_pct': 100.0 * (equity[-1] / p.initial_capital - 1) if equity else 0.0,
        'buy_hold_return_pct': 100.0 * (last / first - 1),
        'sharpe_bar_annualized': (mu / sd * math.sqrt(bars_per_year)) if sd > 0 else None,
        'definition_sharpe': f'mean/stdev of per-bar mark-to-market equity returns * sqrt({bars_per_year:g} bars/year); rf = 0',
        'definition_max_drawdown': 'largest peak-to-trough decline of bar-CLOSE mark-to-market equity, peak starts at initial capital '
                                   '(intrabar extremes ignored; differs from TradingView/PineTS definitions)',
        'exposure_definition': 'bars between entry fill bar and exit fill bar / segment bars',
        'forced_exits': sum(1 for t in trades if t.forced_exit),
    }
