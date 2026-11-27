---
name: pine-evaluation
description: Test design, competence evidence and the evaluation rubric for Pine work and Academy labs.
---
# pine-evaluation
Responsibility: tests that can fail, evidence that can be audited.

## Rules
- Every test suite needs negative controls (mutation): see the reference-test mutations and backtest parity controls.
- Pre-register predictions before external (TradingView) runs.
- Academy: `python .claude/skills/pine-script-engineering/knowledge/PINE_AGENT/tools/pine_training.py next --progress academy/progress.json`; harness `python academy/lab_harness.py`; rubric `knowledge/PINE_AGENT/training/RUBRIC.md`. A lab is PASS only with official compile + all applicable checks; otherwise BLOCKED with evidence.
- Full regression: `python -m pytest -q testing` plus `python -m unittest discover -s testing/compiler`.
- Report each check as PASS / FAIL / NOT RUN / NOT APPLICABLE with reason.

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
