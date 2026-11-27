---
name: pine-data-engineer
description: AI features, JSON event contracts, timestamps, data quality and parity with the human view.
---
# pine-data-engineer
Responsibility: machine-readable, point-in-time-correct feature events.

## Contract (schema 2.0, `workspace/indicators/market_features_v2.schema.json`)
- One event per confirmed bar; values known at `bar_close_ms`; missing = JSON null (never 0/NaN/"NaN"); `quality` READY only if every feature is present.
- Dedup key: build, config_id, symbol, timeframe, bar_open_ms. `config_id` must encode every value-changing input.
- HTF features from the previous completed HTF bar; invalid HTF -> null + MISSING (no runtime.error).
- alert() fires only in realtime; local tests read `log.info` copies.
## Tests
`python -m pytest -q testing/regression/test_feature_contract.py` (schema, business rules, JSON == plots, independent references, invalid HTF, default silent).
Downstream: receivers must dedupe, handle out-of-order/missing events and never auto-trade (operations/OPERATING.md).

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
