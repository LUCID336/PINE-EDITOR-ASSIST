# Open items (V5, 2026-11-27)

| # | Item | Status | Next step |
|---|---|---|---|
| 1 | TradingView compile of new scripts (`market_features_v21.txt`, `ema_trend_longflat_v01.txt`) | NOT RUN | operator runs them through the TradingView Copilot/editor (the strategy had a v6 compile error before review fix) |
| 2 | Pivot tie side on TradingView | UNVERIFIED | run probe T11 (`testing/regression/tv_probes/T11_pivot_tie_side.pine`) |
| 3 | Slippage semantics and `percent_of_equity` sizing on TradingView | UNVERIFIED | TV backtest probe with slippage > 0 and percent sizing |
| 4 | Drawdown definition of TradingView / PineTS | UNVERIFIED | compare `run_pine_backtest` max drawdown with replay definitions |
| 5 | Sessions, holidays, DST, weekend gaps in local data | NOT MODELLED | session-shaped synthetic fixtures + LocalProvider session calendar |
| 6 | Realtime ticks, rollback, `once`, alert delivery | NOT TESTABLE LOCALLY | TradingView replay/realtime checks |
| 7 | Type/qualifier checking (simple vs series etc.) | PARTIAL (literal types, bool-na only) | extend checker with ledger qualifiers |
| 8 | v5 scripts locally | UNVERIFIED | v5 fixture set; migration via V3 sheet M73 |
| 9 | Academy labs L06, L07, L09–L16 | NOT RUN | continue with harness; L06/L07 now possible locally via LocalProvider |
| 10 | Academy L01–L05, L08 | BLOCKED (compile PASS on TV; realtime/reload checks missing) | realtime checks on TradingView |
| 11 | Windows installation | NOT RUN (no Windows host) | operator runs `py install.py` and reports output |
| 12 | Lab code licence | OPEN (operator decision) | choose licence before redistribution (AGPL note for PineTS) |
| 13 | `aggressor_side`, footprint, fundamentals locally | UNSUPPORTED | wait for PineTS support / provider data |
| 14 | 886 API entries UNVERIFIED locally | OPEN | extend reference tests per namespace (arrays, maps, matrices, strings, drawings) |
| 15 | Real market data backtests and walk-forward | NOT RUN | operator-supplied data with checked rights |
