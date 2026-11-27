# Pine project instructions
For any TradingView/Pine task, load the `pine-script-engineering` skill (installed project-locally in `.claude/skills/`; five Pine subagents in `.claude/agents/`). Use the V3 instruction router and Academy as appropriate. All Pine source deliverables must be real complete UTF-8 TXT files in `deliverables/` (export with `.claude/skills/pine-script-engineering/scripts/export_txt.py`), even for revisions. Apply the skill's validation, backtest and learning workflow. Delegate to specialized Pine subagents when useful. Work autonomously inside existing permissions; preserve user changes and require separate authorization for live orders, payments, publication or privileged access. Report unrun tests and uncertainty. Answer in German unless asked otherwise.

## Verified tooling added 2026-11-27 (see `.pine-agent/README.md`)
- API truth: `python .pine-agent/tools/pine_api.py NAME` (official v6 reference snapshot). Never use a built-in that this lookup reports as NOT IN v6 SNAPSHOT without new official evidence.
- Before every delivery: `python .pine-agent/tools/pine_static_check.py FILE` must be STATIC-PASS. This is not a compile.
- Deterministic single-timeframe runtime tests: `.pine-agent/runtime/` (PineTS 0.13.1, third-party; run `npm install --ignore-scripts` there first). Not valid for `request.security` HTF/LTF, realtime ticks or rollback. Never report PineTS as TradingView evidence.
- Signals/alerts from the current bar: gate with `barstate.isconfirmed` or label provisional; historical tests cannot reveal realtime flicker, so get a temporal review.
- Learning records: `.pine-agent/learning/`; skill change proposals: `.pine-agent/proposals/`. The installed V3/V4 snapshot stays unmodified.
