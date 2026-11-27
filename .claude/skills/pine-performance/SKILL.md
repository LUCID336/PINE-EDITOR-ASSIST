---
name: pine-performance
description: Profiling, resource limits and optimisation of Pine scripts with measured evidence.
---
# pine-performance
Responsibility: measured improvements only; no claimed speed-up without numbers.

## Tools
- `pinelab run_indicator` reports `duration_ms` and engine time; repeat >= 3 runs and report median.
- Local limits (tools/pinelab_core.py LIMITS): 60 s timeout, 1024 MB Node heap, CPU rlimit, 100000 loop iterations, script <= 512 KB, CSV <= 200 MB.
## Rules
- Prefer built-ins over loops; bound collections (`array.shift` after push); avoid per-bar drawing churn; minimise `request.*` calls (each is a separate context).
- TradingView limits (max_bars_back, drawing counts, request counts, timeouts) must be taken from the official Limitations page and the ledger, not from memory; PineTS timing is not TradingView timing.
- TradingView Profiler evidence is TV-only; mark local timings as LOCAL.

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
