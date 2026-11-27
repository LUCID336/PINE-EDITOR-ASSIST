# Six documented improvement cycles (V5 build, 2026-11-27)

Each cycle: hypothesis → test → result → finding → repair → retest. Only events that actually happened are listed.

## 1. Requirements, licence and cost check
- **Hypothesis:** the local core can run without any paid service; TradingView MCP is usable as an optional reference.
- **Test:** read the TradingView MCP docs/terms; inspect PineTS manifest (no install hooks, 3 MIT deps, AGPL-3.0); check PyneCore (automatic Pine translation needs its cloud compiler + API key).
- **Result/finding:** the TradingView connector failed with "A paid plan is required" (AI add-on alone is not enough); MCP terms forbid using MCP data to train/test/improve AI models and bulk data export.
- **Repair:** PineTS (pinned, `--ignore-scripts`) as local runtime; PyneCore not adopted; TradingView only via the operator's Copilot for pre-registered probes; data-use policy written (`knowledge/reference/tradingview_mcp_pine_contract_2026-11-27.md`), operator decision recorded.
- **Retest:** offline self-test with blocked network → PASS (`tools/selftest.py`).

## 2. Architecture and API compatibility
- **Hypothesis:** PineTS can serve as the local runtime for indicators, MTF and strategies.
- **Test:** probes for syntax errors, unknown functions, wrong named args, type errors, unknown variables; function-presence probe over all 475 v6 functions with 17 negative controls; custom-array HTF test.
- **Result:** PineTS rejects syntax/unknown functions but silently accepts wrong named args, literal type errors and unknown variables; HTF on custom arrays was NOT aggregated; 474/475 functions present; `aggressor_side` missing.
- **Repair:** layered `validate` (package → static ledger check → capability → runtime); own `LocalProvider` with UTC-grid aggregation; capability stage turns unsupported APIs into BLOCKED; compatibility matrix.
- **Retest:** HTF (D, 240) and LTF arrays match an independent aggregation bar-for-bar (`test_indicator_reference.py`).

## 3. Numerics, time series and error cases
- **Hypothesis:** local indicator values equal TradingView semantics.
- **Test:** 25 reference tests incl. warm-up; mutation of the references; TradingView probes T1–T11.
- **Result/findings:** all references matched on first run → mutation showed the pivot test could not detect tie semantics (no ties in data); TradingView showed EMA is SMA-seeded (official pseudocode is not warm-up-equivalent); PineTS executes global code inside `request.security` contexts (TradingView does not).
- **Repair:** tie fixtures (local rule >= left, > right; TradingView side open, probe T11 prepared); divergence reclassified as BLOCKED; T6b proved the earlier 7/234 HTF "mismatches" were a probe artefact at session irregularities.
- **Retest:** mutation detection 4/5 → tie case covered by dedicated fixtures; T3 now BLOCKED instead of FAILED.

## 4. Quantitative backtests and bias check
- **Hypothesis:** engine and independent replay agree, and the report is fit for decisions.
- **Test:** parity on 15 trades + 4 negative controls; independent quant review (pine-quant-reviewer).
- **Findings:** parity exact, but the report said `OK` without statistical caveats (bootstrap CI of mean trade includes 0, 3 trades > net profit, underperforms buy-and-hold); Sharpe annualisation fixed to 1h; drawdown definitions differ; `na()` on a bool in the strategy (found by the temporal reviewer) would not compile on TradingView v6.
- **Repair:** evidence block with flags and verdict "NO EDGE CLAIM"; timeframe-aware annualisation; drawdown note; OOS bounds; cost stress rounding; new static rule for na/nz/fixnan on bool; strategy HTF guard; independent signal recomputation test.
- **Retest:** 19 backtest tests green; checker flags the old strategy at 21:41, 0 false positives on 414 official examples.

## 5. Agent routing, UX and AI data contract
- **Hypothesis:** the Human+AI indicator exports correct, complete, point-in-time features.
- **Test:** JSON schema + parity tests; independent temporal and UI/data reviews.
- **Findings:** READY possible with a null feature; stale swing/HTF values reported as READY; `NaN` possible in JSON on non-standard charts; table unreadable in dark theme; editable build id breaks dedup.
- **Repair:** v2.1 with quality derived from the exported list, `missing[]`, STALE state + meta timestamps, export only on standard charts, theme colours, constant BUILD, schema 2.1 with if/then rule.
- **Retest:** 9 contract tests incl. independent references for all 8 features, flat-price and staleness fixtures.

## 6. Reproducibility, regression and release
- **Hypothesis:** a fresh extraction installs and passes offline.
- **Test:** deterministic ZIP from git-tracked files, fresh unzip into an empty directory, `install.py` (npm ci from lockfile), self-test with network blocked; ledger re-extraction compared byte-for-byte.
- **Result:** see `TEST_REPORT.md` (fresh-install section) and `releases/dist/SHA256SUMS.txt`.
- **Open:** Windows install path documented but not executed (no Windows host available) → NOT RUN.
