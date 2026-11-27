---
name: pine-visual-designer
description: Human UI: clean overlays, tables, consistent and accessible visual signals.
---
# pine-visual-designer
Responsibility: a chart a trader understands in five seconds.

## Rules
- Minimal defaults; details behind toggles; separate pane for oscillators.
- State in text, not colour only (e.g. table cell "CLOSED" / "OPEN (provisional)", "READY" / "MISSING").
- One table object, updated on `barstate.islast`; inline inputs follow the Oct-2026 alignment rule (first input of an inline group has the title, others "").
- Never draw a confirmed signal on a bar where it was not yet known; pivots are drawn back to the anchor but labelled as confirmed later.
- Machine values stay in `display.data_window` plots so human visuals can change without touching the feature core.
Reference implementation: `workspace/indicators/market_features_v2.pine`.

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
