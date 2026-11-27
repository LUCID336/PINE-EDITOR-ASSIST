---
name: pine-backtester
description: Strategy validation with costs, fill model, independent Python replay, chronological out-of-sample and cost stress.
---
# pine-backtester
Responsibility: evidence-based strategy evaluation; default NO TRADE when evidence is inadequate.

## Commands
- `python tools/pinelab.py run_backtest FILE --data CSV --base-tf 60 --tf 60 --oos 0.3 --cost-stress 2 --pretty`
- Tests: `python -m pytest -q testing/backtesting`

## Contract
- Strategy must plot `sig_entry_long` and `sig_exit_long` (1/0, data window) for the independent replay (`testing/backtesting/backtester.py`).
- Fill model verified on TradingView (T9): market orders at next bar open, percent commission per side. Slippage and percent_of_equity sizing: PineTS = replay, TradingView UNVERIFIED.
- Report: engine vs replay parity (must be 0 mismatches), IS/OOS metrics, cost stress, buy-and-hold, trade count. Flag small samples (< 30 trades) and synthetic data. Never claim an edge from synthetic fixtures.
- Follow `.claude/skills/pine-script-engineering/operations/BACKTEST.md` (pre-registered hypothesis, all variants logged, final test untouched).

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
