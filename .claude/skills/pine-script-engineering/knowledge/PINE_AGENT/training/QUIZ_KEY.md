# Answer key
1. Implicit prior bar series vs explicit position in a collection, whose layout you control.
2. It is skipped; history-dependent computations may become inconsistent. Hoist them.
3. var persists across bars but follows realtime rollback; varip escapes rollback within a bar.
4. A missing measurement becomes indistinguishable from measured zero, contaminating features.
5. Inside the HTF expression, e.g. close[1] with lookahead_on, only for strictly higher TF with the intended semantics.
6. Only that requested intrabars are unavailable in that returned array; not proof of no trades.
7. 103, assuming three subsequent bars exist and confirmation is taken at close.
8. Its historical calculation must run on each bar, not just the latest one.
9. No; use numeric plots/exports/alerts with explicit observation times.
10. Recreate alert to capture the new configuration; verify build and config IDs.
11. No; reconcile, deduplicate and handle missing or delayed delivery.
12. No; order and emulator settings determine simulated fill timing.
13. If the amounts are actual per-side total cash costs in matching units; gross minus all four costs = 7.
14. No; consult the version-specific reference and migration guide.
15. Actual official compiler evidence for exact source/build and context, not a local regex or other parser.
16. They share inputs and can be correlated; measure incremental OOS information.
17. Actual resting order book, hidden orders or real stop clusters.
18. Mark missing/BLOCKED, consult official evidence, use no trade by default; do not fabricate.
