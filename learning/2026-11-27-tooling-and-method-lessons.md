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
