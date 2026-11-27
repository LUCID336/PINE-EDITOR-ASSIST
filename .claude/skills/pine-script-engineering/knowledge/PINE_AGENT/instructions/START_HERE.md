# Agent entrypoint — Pine Script v2 instruction system

Use progressive disclosure. Read this file and root AGENTS.md/SKILL.md, not every sheet at once. The instructions are original operational guidance, not a verbatim TradingView manual. Official version-specific documentation overrides any local claim. All 78 currently indexed v6 topics have a sheet, but full chapter-body and API-overload coverage is not established.

## Routing

1. Determine task: new indicator, strategy, library, migration, debugging, optimization, human UI, AI features or research. Establish Pine version; default v6 only for new work.
2. Use `python tools/pine_lookup.py topic <query>` or `api <identifier>` from the package root. `route <task>` returns suggested sheets for common tasks. Use `--json` for agents. Load only relevant sheets and their sources. If no match, consult the official manual; do not conclude the API is absent.
3. Read `instructions/workflows/ENGINEERING.md` and the relevant specialized workflow. Complete `instructions/templates/task-spec.json` in the task workspace. No secrets.
4. Open official reference matching target version; record exact overloads using `instructions/templates/api-evidence.json`. The 612 identifiers are discovery candidates, not approved signatures. Never fabricate a missing signature; use an authorized Pine Editor reference lookup if the interactive page is not accessible.
5. Implement, compile in official Pine Editor if available, verify chart behavior, compare expected/actual. For legacy code use sequential migration and preserve baseline.
6. Run six review gates in ENGINEERING.md. Return source, source ledger, evidence, and unresolved blockers. No claim of compiler success without a real compile; no claim of market edge without empirical data.

## Required distinctions
- Documented claim vs inference vs hypothesis vs unverified candidate.
- Historical bar vs realtime tick vs closed bar, observed time vs visual location.
- Source feed vs heuristic proxy vs external data.
- Pine compilation vs runtime behavior vs quantitative validity.
- Human visualization vs machine features, shared calculation core.

Read `instructions/topic-index.json` for chapter paths and `instructions/api-index.json` for candidate-level lookup. `instructions/manifest.json` summarizes coverage. Original v1 research is retained in RESEARCH.md. `audit/OPEN_ITEMS.md` remains authoritative for unresolved work.

Four high-priority signatures observed in official manual text are in `instructions/api-signature-evidence.json`; these are partial evidence, not complete overload/qualifier verification.

## V3 learning route
For requests about training, tutorials, skill gaps or continuous learning, open `training/START_HERE.md`, then use `tools/pine_training.py`. During normal coding tasks search the tips catalog as relevant. This extension does not alter V2 API verification status.
