# TradingView probe pre-registration (written BEFORE TradingView results), 2026-11-27
Local engine: PineTS 0.13.1 via tools/runtime/engine.mjs, dataset testing/synthetic_data/synth_15m_seed7.csv, chart TF 60.
TradingView channel: user-operated AI Copilot (server-side compile + chart readout), chart VANTAGE:XAUUSD 1H.

| Probe | PineTS observation | Question for TradingView |
|---|---|---|
| T1 ta.ema warm-up | first non-na bar = 19 (SMA seed); ta.ema - pine_ema at bar 19 = 0.1704 (non-zero) | first non-na bar 0 or 19? difference at bar 19 zero or not? |
| T2 ta.rsi constant series | 100 | 100 / 50 / 0 / na (-1)? |
| T3 global runtime.error in request.security context | RUNTIME_ERROR fired (global code executed in D context) | does TradingView fire it too? |
| T4 once on realtime bar | NOT TESTABLE locally (no ticks) | counter > 1 after several ticks? |
| T5 2026 features compile | COMPILE_ERROR: aggressor_side undeclared (PineTS predates Nov 2026) | compiles? plan restriction for calc_on_every_history_tick? |
Status after results: each probe → TV_VERIFIED (with A/B evidence) or UNVERIFIED.

## Round 3 local predictions (PineTS 0.13.1 + static checker), written before TradingView results
| Probe | Local result | Question |
|---|---|---|
| T6b mismatch diagnosis | 0 mismatches (synthetic 24/7) | weekday pattern / gap hours of TV mismatches |
| T7 ta.ema inside if | PineTS: no warning concept (warnings []) | does validate return a warnings[] entry (consistency warning)? |
| T8a plot(linewidth2=3) | checker ERROR; PineTS runs silently | exact compiler error text + line/col |
| T8b int x = "abc" | checker ERROR; PineTS runs silently | exact compiler error text + line/col |
| T8c barstate.isclosed | checker ERROR; PineTS returns 0 silently | exact compiler error text + line/col |
| T9 broker emulator self-check | entries_not_on_bar_after_signal 0, max entry-open diff 0, max commission error 0 | same on TV? (fill at next bar open, percent commission per side) |
| T10 pivot self-check | value mismatch 0, higher neighbour 0, equal neighbour 0 (synthetic data, no ties) | tie handling on real data |
