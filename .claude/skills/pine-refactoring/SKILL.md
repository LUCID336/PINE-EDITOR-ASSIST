---
name: pine-refactoring
description: Modular, readable Pine architecture without behaviour change, guarded by regression tests.
---
# pine-refactoring
Responsibility: improve structure while proving identical outputs.

## Procedure
1. Baseline: `pinelab run_indicator FILE --pretty` -> keep `result_ref` (all plot series) and source hash.
2. Refactor in small steps: typed declarations, named constants, input groups, pure helper functions (e.g. `safeRatio`), stateful calls unconditional, one shared feature core feeding human and AI outputs.
3. After each step re-run and compare every plot series bar-by-bar with the baseline (tolerance 1e-9); any difference is a behaviour change, not a refactor.
4. Re-run `pine_static_check` (warnings such as conditional `ta.*` calls must not appear).
Style reference: V3 sheet M45 (style guide) and `knowledge/candidates/` (Copilot candidate rules, verify before use).

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
