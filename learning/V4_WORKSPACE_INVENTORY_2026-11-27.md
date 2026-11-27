# Pine agent workspace — capability inventory (2026-11-27)

## Installed
| Component | Location | Status |
|---|---|---|
| Skill `pine-script-engineering` V4 (incl. V3 knowledge, 227 files) | `.claude/skills/pine-script-engineering/` | Installed with bundled `install.py --target .claude`; byte-identical to upload; 226/226 SHA-256 OK; 19/19 unit tests, V1/V2/V3 audits PASS. Discovery by the Skill tool requires a new session. |
| Subagents pine-lead, pine-api-researcher, pine-temporal-reviewer, pine-quant-reviewer, pine-ui-data-reviewer | `.claude/agents/` | Installed; registered only after session restart. In this session one review ran via a general-purpose agent with the temporal-reviewer brief. |
| Official v6 API ledger (948 entries, 758 syntax lines) | `reference/v6-api-ledger.json` | VERIFIED snapshot of the official reference, 2026-11-27. Reproducible: `tools/refresh/`. |
| Static API checker | `tools/pine_static_check.py` + `tests/` | 0 false positives on 478 official examples; mutation detection ≥ 99.3 %. Not a compiler. |
| API lookup | `tools/pine_api.py` | Reads the ledger. |
| Local runtime | `runtime/` (PineTS 0.13.1, AGPL-3.0, LuxAlgo) | Calibrated exact for sma/rma/rsi/atr/pivothigh and history semantics; unusable for MTF/LTF/realtime. |
| Academy harness | `academy/` | 6 labs executed (L01–L05, L08); evidence + progress (`BLOCKED`: official compile missing). |

## Not available (blockers)
- TradingView Pine Editor compile, Strategy Tester, realtime/replay: no account/authorization in this environment. Automation of the TradingView chart UI was not attempted (requires the user's authorized account; unofficial compile endpoints are prohibited by the skill).
- Real market data / licensed OHLCV for backtests: none supplied.
- v3–v5 reference ledgers: not yet extracted.

## Remaining knowledge gaps (prioritized)
1. Real TradingView behavior for: `ta.ema` warm-up seed; `ta.rsi` on flat prices; whether a global `runtime.error` fires inside `request.security` contexts; `once` on realtime bars (documented, not observed). → needs Pine Editor run.
2. Labs L06/L07 (MTF/LTF), L09–L16 not yet executed; L06/L07 need TradingView (PineTS cannot aggregate custom data).
3. Qualifier/type checking (simple vs series) is not covered by any local tool.
4. Strategy backtesting with realistic costs: no data, no Strategy Tester.
