# Migration V4 workspace -> V5 lab layout (2026-11-27)

All moves via `git mv` (git history = backup; last pre-migration commit `07bcd3f`).
SHA-256 (first 12 hex) before migration vs. now. CHANGED = edited afterwards on purpose (path updates, review fixes, new results); details in `git log --follow`.

| old path | new path | status | sha before | sha now |
|---|---|---|---|---|
| `.pine-agent/README.md` | `learning/V4_WORKSPACE_INVENTORY_2026-11-27.md` | UNCHANGED | 97d3c8a6c278 | 97d3c8a6c278 |
| `.pine-agent/academy/evidence/L01.json` | `academy/evidence/L01.json` | CHANGED | 273f3a85817f | c487ee2d6df3 |
| `.pine-agent/academy/evidence/L02.json` | `academy/evidence/L02.json` | CHANGED | 4d46fe101d40 | 92ac948e9168 |
| `.pine-agent/academy/evidence/L03.json` | `academy/evidence/L03.json` | CHANGED | 381a1d37366a | df6a530b8ed5 |
| `.pine-agent/academy/evidence/L04.json` | `academy/evidence/L04.json` | CHANGED | 66023ba3ea9d | 263ab9535041 |
| `.pine-agent/academy/evidence/L05.json` | `academy/evidence/L05.json` | CHANGED | 83481b624816 | 0dc58c086d5f |
| `.pine-agent/academy/evidence/L08.json` | `academy/evidence/L08.json` | CHANGED | f50343e81cb5 | 1ed30b584477 |
| `.pine-agent/academy/evidence_own.json` | `academy/evidence_own.json` | UNCHANGED | bb673ba8fc78 | bb673ba8fc78 |
| `.pine-agent/academy/evidence_reference.json` | `academy/evidence_reference.json` | UNCHANGED | f6211febcca8 | f6211febcca8 |
| `.pine-agent/academy/lab_harness.py` | `academy/lab_harness.py` | CHANGED | 1334dde8ecb3 | 363f9d9618dc |
| `.pine-agent/academy/progress.json` | `academy/progress.json` | CHANGED | 425d63efbee2 | f521231e014a |
| `.pine-agent/academy/solutions/L01.pine` | `academy/solutions/L01.pine` | UNCHANGED | 8d1c76a6c3bb | 8d1c76a6c3bb |
| `.pine-agent/academy/solutions/L02.pine` | `academy/solutions/L02.pine` | UNCHANGED | 8403ee7357b5 | 8403ee7357b5 |
| `.pine-agent/academy/solutions/L03.pine` | `academy/solutions/L03.pine` | UNCHANGED | 0696e6522699 | 0696e6522699 |
| `.pine-agent/academy/solutions/L04.pine` | `academy/solutions/L04.pine` | UNCHANGED | bb56894aa0b3 | bb56894aa0b3 |
| `.pine-agent/academy/solutions/L05.pine` | `academy/solutions/L05.pine` | UNCHANGED | 597a11e6afac | 597a11e6afac |
| `.pine-agent/academy/solutions/L08.pine` | `academy/solutions/L08.pine` | UNCHANGED | ec48593fbbe5 | ec48593fbbe5 |
| `.pine-agent/learning/2026-11-27-release-delta-2025-2026.md` | `learning/2026-11-27-release-delta-2025-2026.md` | UNCHANGED | f20c2fd40eeb | f20c2fd40eeb |
| `.pine-agent/learning/2026-11-27-tooling-and-method-lessons.md` | `learning/2026-11-27-tooling-and-method-lessons.md` | CHANGED | f18e2106c9fb | c4f43bcb3f27 |
| `.pine-agent/proposals/P-2026-11-27-01-verified-tooling.md` | `learning/proposals/P-2026-11-27-01-verified-tooling.md` | CHANGED | 3d8ac8368bd9 | 2b745d72b550 |
| `.pine-agent/reference/catalog-diff-2026-11-27.json` | `knowledge/reference/catalog-diff-2026-11-27.json` | UNCHANGED | ca8f6df96417 | ca8f6df96417 |
| `.pine-agent/reference/v6-api-ledger.json` | `knowledge/reference/v6-api-ledger.json` | UNCHANGED | 627626ce2579 | 627626ce2579 |
| `.pine-agent/runtime/.gitignore` | `tools/runtime/.gitignore` | UNCHANGED | 4d56952b0fb1 | 4d56952b0fb1 |
| `.pine-agent/runtime/package-lock.json` | `tools/runtime/package-lock.json` | CHANGED | 27d2afae190e | 6c016539a51e |
| `.pine-agent/runtime/package.json` | `tools/runtime/package.json` | CHANGED | 3bf9456ebbaa | 6f5acc293ac8 |
| `.pine-agent/runtime/run_pine.mjs` | `tools/runtime/run_pine.mjs` | UNCHANGED | 5c0f2066e201 | 5c0f2066e201 |
| `.pine-agent/tests/test_static_check.py` | `testing/compiler/test_static_check.py` | CHANGED | cf2a7b14a911 | fd973e793de9 |
| `.pine-agent/tools/pine_api.py` | `tools/pine_api.py` | CHANGED | 08b1fcef6a13 | aeb7efc27b19 |
| `.pine-agent/tools/pine_static_check.py` | `tools/pine_static_check.py` | CHANGED | 93c7da71c824 | 93b11f99f815 |
| `.pine-agent/tools/refresh/README.md` | `tools/refresh/README.md` | CHANGED | 7d1f0502e457 | 0992090cfd50 |
| `.pine-agent/tools/refresh/build_ledger.py` | `tools/refresh/build_ledger.py` | CHANGED | dda39baf7529 | ff3b92ef6882 |
| `.pine-agent/tools/refresh/mutation_eval.py` | `tools/refresh/mutation_eval.py` | UNCHANGED | 32bfb972888e | 32bfb972888e |
| `.pine-agent/tools/refresh/refresh_reference.mjs` | `tools/refresh/refresh_reference.mjs` | UNCHANGED | dfde9fa4c3c8 | dfde9fa4c3c8 |
| `deliverables/academy_L01_sma_change_v01.txt` | `releases/txt/academy_L01_sma_change_v01.txt` | UNCHANGED | 8d1c76a6c3bb | 8d1c76a6c3bb |
| `deliverables/academy_L02_rsi_gate_v01.txt` | `releases/txt/academy_L02_rsi_gate_v01.txt` | UNCHANGED | 8403ee7357b5 | 8403ee7357b5 |
| `deliverables/academy_L03_confirmed_bull_state_v01.txt` | `releases/txt/academy_L03_confirmed_bull_state_v01.txt` | UNCHANGED | 0696e6522699 | 0696e6522699 |
| `deliverables/academy_L04_bounded_buffer_v01.txt` | `releases/txt/academy_L04_bounded_buffer_v01.txt` | UNCHANGED | bb56894aa0b3 | bb56894aa0b3 |
| `deliverables/academy_L05_safe_ratio_atr_pct_v01.txt` | `releases/txt/academy_L05_safe_ratio_atr_pct_v01.txt` | UNCHANGED | 597a11e6afac | 597a11e6afac |
| `deliverables/academy_L08_swing_high_breakout_v01.txt` | `releases/txt/academy_L08_swing_high_breakout_v01.txt` | UNCHANGED | ec48593fbbe5 | ec48593fbbe5 |

Summary: {'UNCHANGED': 22, 'CHANGED': 17}.
