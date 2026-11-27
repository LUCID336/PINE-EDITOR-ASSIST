---
name: pine-compiler
description: Local Pine v6 validation: parser/runtime adapter, diagnostics with line/column, capability check. Use before any delivery or when a script fails.
---
# pine-compiler
Responsibility: decide whether a script is LOCAL_VALIDATED, FAILED or BLOCKED and explain every diagnostic.

## Commands
- `python tools/pinelab.py validate FILE [--no-runtime] [--data CSV --base-tf 15 --tf 60] --pretty`
- `python tools/pine_static_check.py FILE` (API/named-arg/type-literal/consistency-warning check)
- `python tools/pinelab.py get_capabilities --pretty`

## Stages and meaning
1. package: one `//@version=6`, declaration, no fences, UTF-8.
2. static_api: built-ins, named arguments, namespace members vs the official ledger; literal type mismatches; TradingView-equivalent consistency warning for `ta.*` in conditional blocks. Positions match TradingView for the probed cases (T7, T8a-c).
3. capability: UNSUPPORTED-local APIs (e.g. `aggressor_side`, fundamental `request.*`) -> BLOCKED, never silently approximated.
4. runtime: PineTS on local data. PineTS silently accepts wrong named args, literal type errors and unknown variables, therefore stage 2 is mandatory.
Known divergence: global `runtime.error` + `request.security` raises locally only -> BLOCKED with `runtime_error_divergent`.
Compiler message templates seen on TradingView: `knowledge/reference/tv_compiler_messages_2026-11-27.json`.

## Lab rules (all Pine skills)
- Local results are LOCAL_VALIDATED at best. TV_VERIFIED only with real TradingView evidence (editor or user-operated MCP/Copilot), recorded in `testing/regression/tv_probes/`.
- Never invent APIs: `python tools/pine_api.py NAME` (official v6 snapshot). Statuses per API: `compatibility.json`.
- Deliver complete Pine source as TXT via `python tools/pinelab.py export_txt FILE --name NAME --version NN` (no overwrite).
- No paid service, API key, live order, publication or bulk TradingView data. TradingView data is personal-use only and never used for AI training.
- Record durable lessons in `learning/` (claim, evidence, scope, status).
