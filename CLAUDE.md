# Pine project instructions
For any TradingView/Pine task, load the `pine-script-engineering` skill (installed project-locally in `.claude/skills/`; five Pine subagents in `.claude/agents/`). Use the V3 instruction router and Academy as appropriate. All Pine source deliverables must be real complete UTF-8 TXT files in `releases/txt/` (export with `.claude/skills/pine-script-engineering/scripts/export_txt.py`), even for revisions. Apply the skill's validation, backtest and learning workflow. Delegate to specialized Pine subagents when useful. Work autonomously inside existing permissions; preserve user changes and require separate authorization for live orders, payments, publication or privileged access. Report unrun tests and uncertainty. Answer in German unless asked otherwise.

## Pine Engineering Lab V5 (local-first; see README.md)
- Main interface: `python tools/pinelab.py validate|run_indicator|run_backtest|get_capabilities|export_txt` (JSON; statuses LOCAL_VALIDATED / FAILED / BLOCKED). Optional local MCP server `pinelab` (.mcp.json).
- V5 skills: pine-compiler, pine-backtester, pine-debugger, pine-refactoring, pine-performance, pine-visual-designer, pine-data-engineer, pine-evaluation, pine-release-manager, pine-learning.
- Export finals with `pinelab export_txt` (validates first, never overwrites). Regression: `python -m pytest -q testing` + `python tools/selftest.py`.
- TradingView evidence only via pre-registered probes (`testing/regression/tv_probes/`); TradingView data is personal-use, never for AI training.

## Verified tooling (see `learning/V4_WORKSPACE_INVENTORY_2026-11-27.md`)
- API truth: `python tools/pine_api.py NAME` (official v6 reference snapshot). Never use a built-in that this lookup reports as NOT IN v6 SNAPSHOT without new official evidence.
- Before every delivery: `python tools/pine_static_check.py FILE` must be STATIC-PASS. This is not a compile.
- Local runtime: `tools/runtime/` (PineTS 0.13.1, AGPL, third-party; `python install.py` runs `npm ci --ignore-scripts`). With the LocalProvider, HTF/LTF are tested on a 24/7 UTC grid only (no sessions/DST); no realtime ticks or rollback. Never report PineTS as TradingView evidence.
- Signals/alerts from the current bar: gate with `barstate.isconfirmed` or label provisional; historical tests cannot reveal realtime flicker, so get a temporal review.
- Learning records: `learning/`; skill change proposals: `learning/proposals/`. The installed V3/V4 snapshot stays unmodified.
