# Six review and repair passes
These are six distinct review angles over this deliverable, not six exhaustive repetitions of the entire TradingView reference. Evidence: source register, file content, `tools/audit.py` and generated `LOCAL_RESULTS.txt`. No claims of independent agent review.

| Pass | Inspect / challenge | Repair implemented | Retest / remaining scope |
|---|---|---|---|
| 1 — coverage & sources | Manual navigation, dynamic reference access, community mirrors; claimed 100% not supportable | 78-topic index, curated symbol catalog, exact verification ledger, open-items register | check count and uniqueness; full per-symbol coverage OPEN |
| 2 — language & versions | v1/v2 security, v3 lookahead change, v5 namespaces, v6 bool and lazy semantics | sequential migration policy, global calculations, v6 examples, API lookup rules | static header and declaration checks; compiler and migration runtime OPEN |
| 3 — causality & data | HTF future leak, stale values, pivot backdating, footprint vs true orderflow | HTF guard + confirmed offset, null handling, per-feature provenance rules, distinct provisional/confirmed | static assertions; chart reload/feeds OPEN |
| 4 — quantitative validity | cost assumptions, fill timing, parameter selection, non-independent confluence | explicit cost settings, baseline not production strategy, OOS/DSR/PBO, NO TRADE gate | static checks for settings and policy; actual backtest OPEN |
| 5 — UX and AI | duplicate logic, unreliable screenshot parsing, null/NaN, ambiguous dedup, alert snapshots | single hybrid script, stable plots, strict event schema, config in key, validator, 9 tests | run unit tests, schema/plots consistency; actual webhook/UX OPEN |
| 6 — release & reproducibility | misleading certification, missing handoff, version drift | README, AGENTS, skill, source register, open items, reproducible audit and package checksum | verify archive, rerun local checks; all outstanding gates documented |

Retest scope is local and reproducible, not a substitute for Pine's compiler, licensed live data, or strategy validation. Full recursive completion remains blocked by the open items. Static PASS means only that named check passed.
