# TradingView results — round 1 (2026-11-27)
Channel: user-operated TradingView AI Copilot (server-side compile = evidence A, chart readout = evidence B),
VANTAGE:XAUUSD, chart 1H, scripts unchanged. Relayed by the user as Copilot text; no screenshots/hashes.
Evidence label: TV_VERIFIED_RELAYED (official engine, second-hand report).

| Probe | PineTS 0.13.1 (pre-registered) | TradingView | Verdict |
|---|---|---|---|
| T1 first non-na bar of ta.ema(close,20) | 19 | 19 (B), compile A | MATCH → ta.ema is SMA-seeded. The reference's "same on pine" pseudocode (first-value seed) does NOT reproduce built-in warm-up (diff 8.48 on XAUUSD at bar 19). |
| T2 ta.rsi of constant series | 100 | 100.00 (B, last bar only) | MATCH |
| T3 global runtime.error + request.security("D") | RUNTIME_ERROR | compiled (A), no runtime error, daily_close = 3650.01 plotted (B) | DIVERGENCE (interpretation pending T3b: does in_seconds() = 86400 inside D context on TV?) |
| T4 once on realtime bar | not testable | compile A; counter 5 right after adding (B) | CONSISTENT with official docs ("can execute multiple times on one realtime bar"); exact tick count not interpretable |
| T5 2026 features (once, multiline string, aggressor_side, calc_on_every_history_tick) | COMPILE_ERROR aggressor_side | valid: true, no warnings (A) | PineTS GAP: 2026 features UNSUPPORTED locally |

Follow-ups (round 2): T3b built-in timeframe inside security context; T6 HTF non-repaint idiom historical check.
Local predictions round 2: T3b → 86400 (D ctx) / 3600 (main); T6 → mismatches 0 (29 days synthetic data).
Copilot self-report: claims no knowledge of 2026 features, cannot fetch Pine docs → use it as an execution channel only.

# Round 2 (2026-11-27), same channel and chart
| Probe | PineTS (pre-registered) | TradingView | Verdict |
|---|---|---|---|
| T3b in_seconds() inside request.security("D") | 86400 / main 3600 | 86400 / main 3600 (B) | MATCH. Combined with T3 (no error on TV): TradingView evaluates only the requested expression in the HTF context, NOT global side-effect code. PineTS re-executes the whole script → DIVERGENT (local false runtime.error). |
| T6 close[1]+lookahead_on vs prior D close at day change | 0 mismatches / 29 days (synthetic 24/7) | 7 mismatches / 234 days, realtime changes 0 (brief) (B) | OPEN: session/feed effect on XAUUSD vs flaw in probe; synthetic 24/7 data cannot reproduce. Diagnosis probe T6b. |
| L01–L05, L08 compile | STATIC-PASS | valid: true (A) | COMPILE TV_VERIFIED_RELAYED. Warnings channel not exposed by the tool → "no warnings" UNVERIFIED. |
Local prediction T6b (synthetic 24/7): 0 mismatches, all weekday counters 0.

# Round 3 (2026-11-27), same channel and chart
Channel notes: Copilot retyped T6b/T9/T10 for attaching (byte equality not guaranteed; compile of original passed).
Compile tool returned valid:true together with errors[] for T8a–c → judge by errors[], never by `valid` alone.
Messages come back as templates with unresolved placeholders; no `end` position returned.

| Probe | Local (pre-registered) | TradingView | Verdict |
|---|---|---|---|
| T7 ta.ema inside if | no warning concept in PineTS | warning 5:10 `The function "{functionName}" should be called on each calculation for consistency. It is recommended to extract the call from this scope` (A) | Warnings channel WORKS → absent warnings for L01–L08 mean "no warnings" (inference). |
| T8a plot(linewidth2=3) | checker ERROR L3; PineTS silent | error 3:13 `The "{signature}" function does not have an argument with the name "{name}"` (A) | checker MATCH (line); PineTS false success confirmed |
| T8b int x = "abc" | checker ERROR L3; PineTS silent | error 3:1 `Cannot assign a value of the "{assignedValueType}" type to the "{variableName}" variable. The variable is declared with the "{ownValueType}" type.` (A) | checker MATCH |
| T8c barstate.isclosed | checker ERROR L3; PineTS returns 0 | error 3:6 `Undeclared identifier "{identifier}"` (A) | checker MATCH |
| T6b mismatch diagnosis | 0 (synthetic 24/7) | 7 mismatches; Sun 2, Mon 4, Thu 1, others 0; last at 2026-11-26 23:00 UTC (US Thanksgiving), gap to previous bar 4 h; last_htfPrev 3566.39 = last_chart_close_prev_bar 3566.39, last_dClose_prev_bar 3588.61 (B) | Mismatches sit at session irregularities (weekend reopen, holiday). htfPrev equalled the actual last close; the REFERENCE dClose[1] (lookahead_off) was stale. → Probe artefact, not idiom repaint (strong indication for the last case, inference for the other 6). |
| T9 broker emulator | 0 / 0 / 0 (PineTS, synthetic) | 87 trades: entries_not_on_bar_after_signal 0, max entry-open diff 0, max commission error 0; netprofit −456.40 = report (B) | MATCH: market orders fill at next bar open; percent commission per side on fill value. Python backtester spec confirmed. |
| T10 pivot | 0/0/0, no ties (synthetic) | 728 pivots, value = high[2] always, higher neighbour 0, equal neighbour 1 (B) | MATCH for timing/value; ties allowed on at least one side (side unknown) → open item. |
| syminfo.session / timezone XAUUSD | – | unknown (not exposed) | open |
