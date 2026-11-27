# TradingView MCP — Pine tool contract (summary, retrieved 2026-11-27)
Source: https://www.tradingview.com/mcp/docs (public documentation). Own-words summary for interface design; not a copy.

## Data-use constraints (binding when the user's MCP / AI Copilot is used)
Personal use only; no sharing/publishing of retrieved data; no bulk collection; **no use of MCP data to train, test or
improve AI models**; no automated trading or broker actions; no working around limits. AI answers are not advice.
Lab policy (operator decision 2026-11-27): TradingView is used only to compile/run the operator's own scripts on demand,
for personal use. Probe results may be logged in full (including individual values read from the chart) as personal
test records. Not allowed: training/testing/improving AI models with MCP data, sharing or publishing retrieved data,
bulk collection of price series or datasets, automated trading.

## Pine tools (server "tv-mcp")
- validate_pine_script(code) → valid, errors[], warnings[]  (diagnostic shape: {message, start:{line,column}, end:{line,column}}, 1-based, end inclusive; warnings do not block)
- get_pine_script_info(code | script_id) → kind, title, overlay, inputs (in_0..), plots
- run_pine_indicator(code | script_id, symbol, timeframe, inputs, calc_bars_count=300, return_bars=50≤1000, format) → values of latest bars (t = bar open unix seconds UTC, null = no value), last_values, last_bar_forming
- run_pine_backtest(code | script_id, symbol, timeframe, inputs, date_from/date_to, include_trades≤200) → performance.all/long/short, trades, open_trades, report.range; equity curve never returned; *_percent are fractions
- search_pine_scripts / get_pine_script_source / create_pine_script / update_pine_script (write tools: only on explicit user request)
- Error codes: invalid_argument, compile_failed, compile_timeout (do NOT retry same script: repeats lead to a one-hour Pine block), compile_blocked, input_invalid, not_runnable/not_a_strategy, symbol_not_found, script_runtime_error, script_timeout, plan_limit, too_many_runs, access_denied/not_found/not_owner, name_taken/name_too_long, tv_not_connected.
- Quotas: plan 10/20/50/500 calls per day; AI subscription 500/day + 50/min on an active paid plan; every tool call counts.

## V5 design decision
The local CLI mirrors this contract (same diagnostic shape and analogous status codes) so that a session can switch
between LOCAL (PineTS + checker) and TV (official, quota-limited) backends without changing its loop.
