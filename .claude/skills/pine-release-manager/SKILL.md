---
name: pine-release-manager
description: Versioning, TXT delivery, provenance, checksums and release packaging.
---
# pine-release-manager
Responsibility: reproducible, verifiable releases.

## Steps
1. `python -m pytest -q testing` and compiler unit tests green; record counts in TEST_REPORT.md.
2. TXT: `python tools/pinelab.py export_txt FILE --name NAME --version NN` (validation must not be FAILED; no overwrite).
3. `python tools/build_compatibility.py` -> compatibility.json.
4. `python tools/make_release.py` -> `releases/dist/PINE_ENGINEERING_LAB_V5.zip` + `SHA256SUMS.txt` (excludes node_modules; installer restores the pinned runtime).
5. Provenance per file: source hash, engine version, data hash, evidence level (LOCAL_VALIDATED / TV_VERIFIED_RELAYED / BLOCKED).
Never publish to TradingView or share data without separate operator authorisation.

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
