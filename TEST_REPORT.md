# TEST REPORT — Pine Engineering Lab V5 (2026-11-27)

Environment: Linux container, Python 3.13.18, Node v22.23.5, PineTS 0.13.1, pytest 9.1.1, jsonschema 4.26.0.
Evidence levels: **LOCAL** (this lab) · **TV_VERIFIED_RELAYED** (operator-run TradingView AI Copilot, see
`testing/regression/tv_probes/`) · **NOT RUN**. No local result is a TradingView compilation.

## 1. Test suites (final run)
| Suite | Result |
|---|---|
| `pytest testing/` (indicator reference 25, feature contract 9, backtester 9, strategy parity 10, CLI contract 8, misc) | **78 passed** |
| `unittest testing/compiler` (static checker incl. TradingView positions T7/T8a-c, bool-na rule) | **18 OK** |
| V3/V4 knowledge base tests + `audit_instructions.py` + 226 SHA-256 checksums | **19 OK, all gates PASS, 226 OK** |
| Academy harness L01–L05, L08 (own solutions, PineTS) | **6/6 PASS (LOCAL)** |
| Static checker on 414 official TradingView v6 examples | **0 false positives** |
| Mutation test (unknown function / named argument / member) | **100 % / 100 % / 100 %** (seed 7) |
| Offline self-test (`tools/selftest.py`, network blocked) | **PASS, 11/11 steps** |
| MCP wrapper over stdio and live in Claude Code (`mcp__pinelab__validate`) | **PASS** (valid → LOCAL_VALIDATED; T8b → FAILED at 3:1) |

## 2. Phase acceptance
| Phase | Criterion | Status | Evidence |
|---|---|---|---|
| 01 PoC | pinned runtime, licence/API coverage, EMA on local synthetic OHLCV, JSON result | **PASS (LOCAL)** | `selftest` step "EMA indicator" (first non-na bar 19); function probe 474/475 present, 17/17 negative controls; LICENSES.md |
| 02 Interface | CLI with status, timeout, resource limits, explicit errors | **PASS (LOCAL)** | `testing/compiler/test_cli_contract.py` (syntax error, missing function, invalid input, unsupported → BLOCKED, timeout, loop limit, size limit) |
| 03 Indicators | SMA, EMA, RSI, ATR, crossing, state, arrays, MTF vs independent references; warm-up/na | **PASS (LOCAL)**, MTF **PARTIAL** (24/7 UTC grid) | `test_indicator_reference.py` 25 tests incl. D/240 HTF, LTF arrays, tie fixtures; mutation controls |
| 04 Strategies | long/flat example; fees, slippage, sizing, fill time, equity, drawdown; chronological OOS | **PASS (LOCAL)** with evidence verdict **NO EDGE CLAIM** | `test_backtester.py`, `test_strategy_parity.py` (15/15 trades identical, 4 negative controls, independent signal recomputation); fills + commission TV_VERIFIED_RELAYED (T9) |
| 05 Human & AI | shared core, chart UI, JSON feature vectors (symbol, TF, UTC, confirmed, quality); TXT | **PASS (LOCAL)** | `test_feature_contract.py` (schema 2.1, JSON == plots, all 8 features vs independent references, flat/stale/invalid-HTF fixtures) |
| 06 Integration | V4 knowledge + skills, fresh install, offline test, regression, backup/update, reproducible release | **PASS (LOCAL, Linux)**; Windows **NOT RUN** | fresh install from ZIP + update/backup run: `releases/dist/FRESH_INSTALL_LOG.txt`; checksums `releases/dist/SHA256SUMS.txt` |

## 3. Deliverables (Pine TXT)
| File | Local | TradingView |
|---|---|---|
| `releases/txt/academy_L01…L08_*_v01.txt` (6) | LOCAL_VALIDATED | compile PASS, no warnings (TV_VERIFIED_RELAYED); realtime/reload NOT RUN |
| `releases/txt/ema_trend_longflat_v01.txt` | LOCAL_VALIDATED; backtest parity 0 mismatches; verdict NO EDGE CLAIM | NOT RUN (pre-review version had a v6 compile error `na(bool)`, fixed) |
| `releases/txt/market_features_v21.txt` | LOCAL_VALIDATED; contract tests 9/9 | NOT RUN |

## 4. TradingView ground truth used (TV_VERIFIED_RELAYED, 3 rounds, ~40 calls)
EMA SMA-seeded warm-up · RSI of constant series = 100 · built-ins inside `request.security` reflect the requested
context; TradingView does not run global side effects there (PineTS does → BLOCKED locally) · `once` repeats on open
realtime bars (per docs) · 2026 features compile · broker emulator next-bar-open fills + per-side percent commission ·
pivot timing/value · compiler message templates and positions · HTF idiom correct at session irregularities.

## 5. Critical checks (V5 order) — status
| Check | Status |
|---|---|
| Repainting / lookahead | LOCAL tests + temporal review; HTF idiom TV_VERIFIED_RELAYED |
| HTF/LTF mapping | PASS on 24/7 UTC grid; sessions NOT MODELLED |
| Pivot detection time | PASS (LOCAL + TV T10); tie side UNVERIFIED (probe T11) |
| Missing bars | PARTIAL (null/MISSING paths tested; no gap fixtures for HTF) |
| DST / time zones | NOT RUN (UTC-only data) |
| Intrabar assumptions | NOT TESTABLE locally (no ticks); strategy uses closed-bar signals |
| Order execution | fills/commission verified; slippage, sizing, drawdown definition UNVERIFIED_TV |

## 6. Not run / limits
Windows installation · TradingView compile of the two new scripts · realtime/replay checks · real market data and
walk-forward · v5 scripts · 886 API entries without local tests. See `OPEN_ITEMS.md`.
