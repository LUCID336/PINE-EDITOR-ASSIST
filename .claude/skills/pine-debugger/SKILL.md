---
name: pine-debugger
description: Root-cause analysis of Pine runtime/logic errors and local-vs-TradingView divergences.
---
# pine-debugger
Responsibility: reproduce, isolate, explain and fix - one hypothesis at a time.

## Method
1. Reproduce with `pinelab validate` / `run_indicator` on the smallest fixture; record source and data SHA-256.
2. Build a probe script that prints the suspect values as plots or `log.info` (captured in the run result).
3. Compare with an independent Python reference (`testing/regression/test_indicator_reference.py` patterns).
4. If local and TradingView may differ, pre-register the local prediction in `testing/regression/tv_probes/PREREGISTRATION.md`, then ask the operator for a TradingView probe run.
5. Distinguish probe artefacts from script bugs (lesson T6b: the reference series was stale, not the idiom).
Known traps: EMA warm-up (SMA seed, first value at length-1), pivot tie rule (local: >= left, > right; TradingView side unverified, probe T11), `once` re-executing on open realtime bars, HTF lookahead_off values at irregular sessions.

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
