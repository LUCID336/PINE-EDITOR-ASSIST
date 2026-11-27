# Proposal P-2026-11-27-01 — wire verified tooling into the skill workflow

Status: PROPOSED (not applied to the installed skill snapshot; project CLAUDE.md already references the tools).

## Change
In `operations/OPERATING.md` add:
1. Resolve every built-in via `.pine-agent/tools/pine_api.py` (official v6 snapshot) instead of the 612-name discovery catalog.
2. Require STATIC-PASS from `pine_static_check.py` before TXT export; report it separately from compile status.
3. For single-timeframe logic, run deterministic fixtures in PineTS and record them as THIRD_PARTY_RUNTIME evidence.
4. Gate every current-bar signal with `barstate.isconfirmed` or mark it provisional; require temporal review.

## Evidence
- `learning/2026-11-27-tooling-and-method-lessons.md` (LR-02 to LR-07), `academy/evidence/*.json`.
- Regression: skill unit tests 19/19 still pass (snapshot untouched); checker tests 12/12; 0/478 false positives.

## Rollback
Remove the four lines from OPERATING.md; the tools are additive and do not modify the V3 snapshot.
