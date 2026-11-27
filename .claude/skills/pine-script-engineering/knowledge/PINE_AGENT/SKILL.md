---
name: pine-script-engineering
description: Develop, migrate, audit and test TradingView Pine Script indicators, strategies, libraries and machine-readable market feature pipelines. Use for Pine v1–v6, repainting, MTF, footprint, alerts, strategy validation and TradingView UX.
---
# Pine Script Engineering Skill

Start with `instructions/START_HERE.md` and its task router; retrieve relevant sheets, then consult `RESEARCH.md` for detailed context; use `references/manual-index.csv` for topic retrieval, `references/symbol-catalog.csv` for discovery (not an authoritative signature database), and `references/SOURCES.md` for source hierarchy. New scripts use v6 unless the task demands another version. Every built-in, argument, overload, type qualifier and availability must be checked against the matching official reference before use. Never invent functions. If unavailable, record BLOCKED. The reference catalog is deliberately partial; do not infer that missing symbols do not exist.

## Operating loop
1. Understand: specify symbol/feed, market, timezone, timeframe, historical versus live, indicator/strategy/library, HUMAN/AI mode, data source, trade hypothesis, execution and costs, user settings.
2. Research: retrieve official reference entries for every API used, including types and restrictions; compare release notes; record URLs, date, exact signature in a project-local ledger. Older versions require their own reference and sequential migration.
3. Design: define observation time, feature schema, confirmed/provisional semantics, warm-up, missing data policy, risk rules, tests and resource budget. Separate feature logic, signals, visuals, alerts, external ingestion and execution.
4. Implement: typed functions, explicit state, versioned schema, global plots, bounded collections, input validation, no unconfirmed HTF signal unless labeled; no hidden historical future knowledge. Use source-level reuse or a version-pinned library; avoid duplicated business logic.
5. Validate: static review, Pine Editor compilation, chart tests, reload vs live/replay comparison, alert payload tests, and strategy tester with costs and realistic fills. External tests do not replace Pine compilation. Track compile logs and configuration. No tool? state NOT RUN.
6. Challenge: investigate data leakage, false positives, regime dependence, sample size, optimizer selection, missing feeds, order sizing and limits. Repair, rerun affected checks; compare against baseline. Stop with explicit residual blockers.

## Mandatory gates
- No lookahead misuse, pivot backdating, unqualified intrabar promises, or fabricated market data. Historical and realtime differences must be explained.
- Human: uncluttered overlay, separate oscillator pane if useful, optional details, accessible color + text/shape, stable labels, no fake confidence.
- AI: stable feature IDs, numeric values and units, event time vs observation time, source, timeframe, quality flags, null for missing, schema version, dedup key, no trade by default. See `references/AI_PROTOCOL.md`.
- Backtests: record all variants, use chronological splits, realistic transaction costs, benchmark, stress tests, multiple-testing awareness, forward validation. No performance guarantee. Do not execute live orders without separate user authorization and external risk controls.
- Deliver source, requirements, source ledger, test results, deployment instructions, limitations and a coverage report. Never mark a compiler or live test PASS without evidence. Use `tools/audit.py` for local checks.

## V3 training and continuous learning
For onboarding, skill gaps, failed tasks, or idle learning, load `training/START_HERE.md`. Use `tools/pine_training.py` to select labs and tips. Persist progress and evidence in the task workspace; reading is not training completion. Source/compile/runtime gates remain mandatory. Never interpret training examples as trade recommendations.
