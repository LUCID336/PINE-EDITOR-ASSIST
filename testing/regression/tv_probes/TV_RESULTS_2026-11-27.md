# TradingView results — round 1 (2026-11-27)
Channel: user-operated TradingView AI Copilot (server-side compile = evidence A, chart readout = evidence B),
VANTAGE:XAUUSD, chart 1H, scripts unchanged. Relayed by the user as Copilot text; no screenshots/hashes.
Evidence label: TV_VERIFIED_RELAYED (official engine, second-hand report).

| Probe | PineTS 0.13.1 (pre-registered) | TradingView | Verdict |
|---|---|---|---|
| T1 first non-na bar of ta.ema(close,20) | 19 | 19 (B), compile A | MATCH → ta.ema is SMA-seeded. The reference's "same on pine" pseudocode (first-value seed) does NOT reproduce built-in warm-up (diff 8.48 on XAUUSD at bar 19). |
| T2 ta.rsi of constant series | 100 | 100.00 (B, last bar only) | MATCH |
| T3 global runtime.error + request.security("D") | RUNTIME_ERROR | compiled (A), no runtime error, daily_close plotted (B) | DIVERGENCE (interpretation pending T3b: does in_seconds() = 86400 inside D context on TV?) |
| T4 once on realtime bar | not testable | compile A; counter 5 right after adding (B) | CONSISTENT with official docs ("can execute multiple times on one realtime bar"); exact tick count not interpretable |
| T5 2026 features (once, multiline string, aggressor_side, calc_on_every_history_tick) | COMPILE_ERROR aggressor_side | valid: true, no warnings (A) | PineTS GAP: 2026 features UNSUPPORTED locally |

Follow-ups (round 2): T3b built-in timeframe inside security context; T6 HTF non-repaint idiom historical check.
Local predictions round 2: T3b → 86400 (D ctx) / 3600 (main); T6 → mismatches 0 (29 days synthetic data).
Copilot self-report: claims no knowledge of 2026 features, cannot fetch Pine docs → use it as an execution channel only.
