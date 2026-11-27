# Pine Engineering Lab V5 — local-first, no mandatory subscription

Local Pine Script v6 coding and test environment for Claude Code. Claude writes Pine, validates it against the
official v6 reference, runs indicators and backtests strategies on local data, compares against independent Python
references and delivers every final script as a complete TXT file. TradingView is **optional** (manual reference
checks only); local results are labelled `LOCAL_VALIDATED`, never `TV_VERIFIED`.

## What is inside
| Path | Content |
|---|---|
| `.claude/skills/` | `pine-script-engineering` (V4 incl. full V3 knowledge base, unmodified) + 10 V5 skills (compiler, backtester, debugger, refactoring, performance, visual-designer, data-engineer, evaluation, release-manager, learning) |
| `.claude/agents/` | 5 V4 subagents (lead, api-researcher, temporal-, quant-, ui-data-reviewer) |
| `tools/pinelab.py` | CLI: `validate`, `run_indicator`, `run_backtest`, `get_capabilities`, `export_txt` (JSON out) |
| `tools/pinelab_mcp.py`, `.mcp.json` | optional local MCP wrapper (stdio, no secrets, no remote endpoint) |
| `tools/runtime/` | pinned PineTS 0.13.1 runtime + offline LocalProvider (CSV, UTC-grid HTF aggregation, LTF arrays) |
| `knowledge/reference/` | official v6 API ledger (948 entries), TradingView MCP contract summary, compiler message catalog |
| `knowledge/candidates/` | unverified material (TradingView Copilot AGENTS.md) - verify before use |
| `academy/` | Academy harness, own lab solutions, evidence, progress |
| `workspace/` | `indicators/` (Market Features v2.1 Human+AI), `strategies/` (EMA long/flat example), `libraries/`, `experiments/` |
| `testing/` | `compiler/` (checker + CLI contract), `regression/` (indicator reference, feature contract, TradingView probes), `backtesting/` (independent backtester + parity), `synthetic_data/` |
| `learning/` | dated lessons, migration log, proposals |
| `releases/txt/` | delivered Pine sources (TXT, no Markdown) |
| `compatibility.json`, `TEST_REPORT.md`, `LICENSES.md`, `COSTS.md`, `OPEN_ITEMS.md`, `LOOPS.md` | release documents |

## Requirements
- Python 3.10+ (`pytest`, `jsonschema` for the test suites: `python -m pip install pytest jsonschema`)
- Node.js 20+ LTS with npm (runtime). Internet only once for `npm ci` (pinned package-lock).
- Optional: Playwright + Chromium only to refresh the API ledger (`tools/refresh/`).

## Windows setup (PowerShell)
```powershell
# 1) install Python 3.12+ (python.org, tick "Add to PATH") and Node.js LTS (nodejs.org), then open a NEW terminal
py --version; node --version; npm --version
# 2) extract PINE_ENGINEERING_LAB_V5.zip, e.g. to C:\PineLab, and enter the folder
cd C:\PineLab\PINE_ENGINEERING_LAB_V5
py -m pip install pytest jsonschema
py install.py            # npm ci (pinned), .mcp.json, offline self-test
# optional: py install.py --claude-user   (copies skills/agents to %USERPROFILE%\.claude with backups)
```
macOS/Linux: same with `python3 install.py`.

## Start commands
```bash
python tools/pinelab.py get_capabilities --pretty
python tools/pinelab.py validate workspace/indicators/market_features_v2.pine --pretty
python tools/pinelab.py run_indicator testing/regression/fixtures/ema_poc.pine --pretty
python tools/pinelab.py run_backtest workspace/strategies/ema_trend_longflat_v1.pine --data testing/synthetic_data/synth_60m_seed11.csv --base-tf 60 --tf 60 --pretty
python tools/pinelab.py export_txt MY_SCRIPT.pine --name my_script --version 1
python tools/pine_api.py request.security          # official signature lookup
python tools/selftest.py                            # offline self-test (network blocked)
python -m pytest -q testing                          # full regression
```
In Claude Code: open the folder, run `/pine-script-engineering` or ask for a Pine task; approve the local `pinelab` MCP server if prompted.

## Status vocabulary
`LOCAL_VALIDATED` (local checks passed) · `FAILED` (explicit errors with line/column) · `BLOCKED` (unsupported locally or known
local divergence) · `TV_VERIFIED_RELAYED` (real TradingView evidence via the operator's TradingView AI Copilot, see
`testing/regression/tv_probes/`). Exit codes: 0 ok, 1 code errors, 2 usage/data, 3 blocked, 4 timeout/resource limit.

## Own data
CSV columns `time,open,high,low,close,volume`, `time` = bar open in UTC milliseconds, one fixed base timeframe
(`--base-tf`). Chart timeframe `--tf` must be >= base. Only use data you have the right to use; TradingView MCP data
must not be exported into datasets (TradingView terms).

## Troubleshooting
| Symptom | Fix |
|---|---|
| `node not found on PATH` | install Node.js LTS, reopen terminal; Windows: check "Add to PATH" |
| `npm ci` fails behind a proxy | set `npm config set proxy ...` once, or copy `tools/runtime/node_modules` from another installation and use `install.py --skip-npm` |
| `engine_installed: false` | run `python install.py` (or `npm ci --ignore-scripts` in `tools/runtime`) |
| `BLOCKED` with `unsupported_local` | feature not available locally (e.g. `aggressor_side`, fundamentals); verify on TradingView |
| `BLOCKED` with `runtime_error_divergent` | global `runtime.error` + `request.security`: PineTS-only error; guard with a bool instead |
| HTF values differ from TradingView | local data has no sessions/holidays; see `compatibility.json` note for `request.security` |
| `.mcp.json` uses wrong Python | re-run `python install.py --skip-npm` (rewrites it with the current interpreter, backup kept) |
| Windows `python` opens Microsoft Store | use `py` launcher or disable the App Execution Alias |

## Limits (honest)
Not a TradingView compiler. Type/qualifier checking is partial (literal types, bool-na rule). No realtime ticks/rollback,
no sessions/DST in local data, slippage/percent-of-equity sizing not TradingView-verified. See `OPEN_ITEMS.md`.
