# LR-2026-11-27-02..07 — Tooling, verification method and lessons (session 2026-11-27)

Status legend: VERIFIED = observed in this session with reproducible command; HYPOTHESIS = unproven.

## LR-02 Official v6 reference is extractable (closes V3 FULL_REFERENCE for v6) — VERIFIED
- Claim: the interactive reference https://www.tradingview.com/pine-script-reference/v6/ is a JS shell for curl,
  but a single headless-Chromium render exposes all 948 entries (475 fun incl. 121 multi-overload, 163 var,
  243 const, 20 type, 16 kw, 21 op, 10 annotations; 758 syntax lines).
- Evidence: `knowledge/reference/v6-api-ledger.json` (signatures, arg type labels, return/type, learn-more URL).
- Result: all 612 V3 candidate identifiers exist in v6 (`map.new` = `map.new<type,type>`); 312 official entries were
  missing from the V3 catalog (`knowledge/reference/catalog-diff-2026-11-27.json`).
- Scope: v6 only. v3–v5 reference pages not extracted yet. Re-extract after each release-note change.

## LR-03 Static API checker — VERIFIED (static only)
- Tool: `tools/pine_static_check.py` (built-ins, named args per overload, namespace members, v6 pitfalls).
- False positives: 0 / 478 official example scripts (414 reference examples + 64 manual examples).
- Mutation detection (3 seeds): unknown function 100 %, wrong named argument 99.3 %, unknown member 99.3–100 %.
- Root causes fixed during calibration: (a) regex backtracking flagged `strategy.risk`; (b) named arguments
  (`color = …`) were mistaken for declarations, masking namespaces; (c) a blanket "member of built-in object"
  exemption let every `color.<typo>` pass because `color` is also a type. Lesson: measure a checker with
  mutation tests, not only with clean inputs; the first fix of (b) did not raise var detection — diagnosis by
  probing beat guessing.
- Not covered: types, qualifiers (simple vs series), scope, runtime. STATIC-PASS ≠ compile PASS.

## LR-04 PineTS 0.13.1 as third-party runtime — VERIFIED profile
- Exact matches vs independent Python on 300 bars: ta.sma, ta.rma, ta.rsi, ta.atr, ta.pivothigh, user `:=`/`[1]`/`na`.
- `ta.ema` in PineTS is SMA-seeded (na for first length-1 bars) while the reference "same on pine" pseudocode seeds with
  the first value. Real TradingView warm-up: HYPOTHESIS (SMA-seeded) — must be checked in the Pine Editor.
- Seed difference of EMA(20) decays below 1e-7 only after ~117 bars → warm-up/quality flags matter for AI features.
- Limits: custom-array data needs explicit timeframe arg (default 86400 s while `timeframe.isintraday` reports true);
  `request.security` HTF on custom arrays returns the lagged chart series (NOT aggregated) → unusable for MTF tests;
  `request.security_lower_tf` unsupported; no realtime ticks/rollback; whole script re-executed in security context
  (a global `runtime.error` guard fires there).
- Use: deterministic single-timeframe calculation tests only. Never report PineTS results as TradingView compile/runtime.

## LR-05 Fixture realism — VERIFIED
- My first L08 fixture put a close above the pivot candidate before confirmation; that necessarily raises the bar's
  high and invalidates the candidate. Runtime was right, fixture wrong. Rule: build fixtures from OHLC constraints
  (low ≤ open/close ≤ high) and re-derive pivot expectations from highs, not from intent.

## LR-06 Historical tests are blind to realtime flicker — VERIFIED (by review)
- My L02/L08 signals lacked `barstate.isconfirmed`; all historical bars are confirmed, so tests passed. Reference
  solutions gate signals. Rule: every alert/trade signal derived from the current bar must be gated by
  `barstate.isconfirmed` (or explicitly labeled provisional), and this must be checked by review because the
  available runtime has no ticks.

## LR-07 Official example corpus as regression set — VERIFIED
- 478 TradingView-authored v6 examples are a free regression corpus for any static tool change. Extraction scripts in
  `tools/refresh/`; the corpus itself is regenerated locally, not committed (copyright).

## LR-08 TradingView ground truth via AI Copilot (round 1) — TV_VERIFIED_RELAYED
- ta.ema warm-up: first non-na at bar length-1 (SMA seed) on TradingView = PineTS. The v6 reference
  "same on pine" pseudocode for ta.ema is NOT warm-up-equivalent; never use it as a parity oracle for early bars.
- ta.rsi of a constant series = 100 on TradingView (last bar) = PineTS.
- `once` executes repeatedly on an open realtime bar (counter 5 seen) — matches official docs; gate side effects
  with `barstate.isconfirmed`.
- 2026 features compile on TradingView; PineTS 0.13.1 rejects aggressor_side → UNSUPPORTED locally.
- Global `runtime.error` guard + request.security: PineTS fires it, TradingView did not → local false alarm; pending T3b.
- Method: pre-register local predictions before each TradingView round (testing/regression/tv_probes/PREREGISTRATION.md).

## LR-09 TradingView round 2 — TV_VERIFIED_RELAYED
- Built-ins inside request.security reflect the requested context (in_seconds() = 86400 for "D") on TV and PineTS.
- TradingView does not execute global side-effect code (runtime.error) in the security context; PineTS does →
  local runtime must flag scripts combining global runtime.error with request.security as DIVERGENT, not FAIL.
- Six academy scripts compile on TradingView (valid:true). Copilot compile channel exposes no warnings field.
- Synthetic 24/7 UTC data showed 0 HTF day-boundary mismatches, TradingView XAUUSD 7/234 → session/feed effects
  are invisible to local synthetic tests; need session-shaped fixtures (weekend gaps, holidays, DST) — open item.

## LR-10 TradingView round 3 — TV_VERIFIED_RELAYED
- Broker emulator (87 trades, XAUUSD 1h): market orders fill at the NEXT bar open; percent commission = rate · qty ·
  (entry + exit). Identical to PineTS → spec for the independent Python backtester.
- Pivots: value = high[right], reported `right` bars later (728 cases); ties with an equal neighbour occur (side unknown).
- HTF idiom close[1]+lookahead_on was right at all mismatch points examined; the lookahead_off comparison series was stale at
  weekend reopen and US Thanksgiving (2026-11-26 23:00 UTC, 4 h gap). Lesson: lookahead_off HTF values on the last chart bar
  of an irregular session can lag → never use them as a reference; test with session-shaped fixtures.
- Compiler: warnings[] is returned when present (T7) → absent warnings mean none. `valid` can be true while errors[] is
  filled (relay quirk) → judge by errors[]. Message templates stored in knowledge/reference/tv_compiler_messages_2026-11-27.json.
- Static checker now emits the T7-equivalent consistency warning (same line as TradingView; 0 false warnings on 414 examples).
- Copilot AGENTS.md stored as CANDIDATE (knowledge/candidates/); one [D] claim corrected via ledger
  (ta.sma/ta.highest accept series int length; ta.ema/ta.rsi/ta.atr require simple int).

## LR-11 V5 build lessons (independent reviews) — VERIFIED locally / by official docs
- v6: `na()`, `nz()`, `fixnan()` reject bool; bool cannot be na (official v6 migration guide). Neither PineTS nor the old
  checker caught `na(boolVar)`; new static rule added (0 false positives on 414 official examples).
- A backtest report without statistical caveats is misleading even with exact engine parity: pinelab now attaches
  bootstrap CI, concentration, sample-size and benchmark flags and a "NO EDGE CLAIM" verdict.
- Parity between two implementations proves bookkeeping only; shared assumptions (slippage units, sizing rule) stay
  UNVERIFIED_TV until probed on TradingView. Signals are now recomputed independently in tests.
- Feature quality must be derived from exactly the exported field list; presence is not freshness (STALE state).
- Reference tests that never fail need mutation checks: the pivot tie rule was invisible without dedicated fixtures.

## LR-12 Gold Multi-Setup v7 overhaul (user script) — VERIFIED locally
- Regression method for refactors of user scripts: instrument old and new copies identically (engine state as
  data-window plots, alert() -> log.info) and compare bar-by-bar on the same data. v7 with legacy statistics = v6 exactly
  (26 state series + every webhook JSON), 32 tests (testing/regression/gold/).
- "Realistic exits" must follow the user's execution path: with webhook execution the BE stop is moved only at the
  close of the TP1 bar, so an open beyond the stop on the next bar exits at the open. My first "gap-only" rule
  (prev close on this side) was too optimistic - found by independent temporal review, test kept.
- The original drew stop/TP lines at spread-adjusted simulation levels while tooltip and webhook used broker levels
  (0.20 $ apart): draw what the user trades (broker levels) and say where spread is applied.
- PineTS silently ignores unknown input titles (a renamed input invalidated a test run) -> pinelab now returns
  INPUT_INVALID, mirroring the TradingView MCP code input_invalid.
- UI: secret inputs need display = display.none (status line); white text on light setup colours fails contrast.
