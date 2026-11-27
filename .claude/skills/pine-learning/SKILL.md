---
name: pine-learning
description: Verified knowledge, error journal and controlled skill improvement.
---
# pine-learning
Responsibility: turn observations into durable, verified knowledge - and keep candidates separate.

## Where
- `learning/` dated records (claim, source, evidence, scope, status, superseded IDs).
- `knowledge/reference/` verified official data (ledger, TradingView contract, compiler messages).
- `knowledge/candidates/` unverified material (e.g. Copilot AGENTS.md) until each claim is checked.
- `learning/proposals/` skill changes with diff, evidence and rollback; the installed V3/V4 snapshot stays unmodified.
## Loop
observe -> root cause -> bounded change -> isolated test -> regression -> promote or reject -> log. Max six improvement passes per task; stop on no progress. Re-validate after Pine release notes change (refresh: `tools/refresh/`).

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
