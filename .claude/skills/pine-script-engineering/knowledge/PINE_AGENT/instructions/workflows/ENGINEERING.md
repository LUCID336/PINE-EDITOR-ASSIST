# Engineering contract — all agents

## Intake → architecture → code
Define purpose, target version, script type, exchange/ticker, chart type, timeframes, sessions, plan, observation time, warm-up, input units, missing-value policy, output interface, resource budget and test criteria. Use safe assumptions only where reversible; document them. Separate feature engine, decision rules, drawings, transport and execution. Preserve stable API/feature IDs. Inspect existing code and fixtures before modifying. Use built-ins where correct; do not implement imaginary namespaces.

## API evidence gate
For each built-in actually called, locate its exact version-specific reference entry. Record signature including qualifiers, optional arguments and defaults, return arity/type, side effects, scope, missing behavior, limits and a minimal probe. Distinguish `series float` from `float` conversion and mutable object ID from value. An example in a manual does not prove all overloads. A search result is discovery only. No official access → BLOCKED rather than guessing. See templates/api-evidence.json.

## Source layout
Version annotation; declaration; imports; constants and inputs; types and UDFs; requests and feature calculation; signal and risk state; global plots; objects/tables; alerts and debug. Keep history-dependent calculations consistent across bars. Use `na` and explicit readiness, not fabricated zeros. Bound arrays/objects; use named arguments for behavior-sensitive options. Mark provisional values. Use standard charts for fills unless an intentional tested exception.

## Six review cycles on every task
1. Requirements/source: reconcile each requested output, confirm target version and every used API. Record source URLs, dates and unavailable sources.
2. Language/version: verify qualifiers, scopes, declaration types, assignment, overloads, and compile evidence. Repair and rerun.
3. Temporal/data: identify observation vs event time, HTF alignment, gaps, pivots, missing data, warm-up and reload differences. Test timeline fixture and real chart.
4. Quant/risk: check order semantics, costs, unit conversion, risk limits, leakage, benchmarks and OOS evidence. If indicator only, mark strategy-specific checks N/A with rationale, not PASS.
5. UX/AI: compare shared numeric features, verify themes and density, JSON schema, dedup and alerts. Test actual export/receiver when available.
6. Release: rerun impacted prior gates, test clean install, record manifest, limitations, compiler logs and versioned artifacts. No secrets or unauthorized execution.

For each cycle: finding → evidence → repair → retest → residual risk. Stop at accepted criteria or concrete blocker; do not iterate without measurable value. Report PASS/FAIL/BLOCKED/NOT_RUN/N/A per check. Do not equate local static tests with Pine Editor tests. The release gate cannot override earlier failures. Deliver source, README, test report and exact operator steps.
