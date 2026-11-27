# Pine Engineering Cookbook — 40 field rules

Original actionable synthesis. Source IDs refer to `training/SOURCES.md`; project-derived rules are explicitly labeled. These are engineering checks, not empirically demonstrated trading edges.

## T01 — Pin version before coding (language)
**How:** Use explicit version and verify each overload against same-version reference; if unavailable mark blocked.

**Why:** Legacy and current signatures differ.

**Verify:** Compile in target version and record evidence.

**Evidence:** S02 S17 S33.

## T02 — Think in series (language)
**How:** Treat close[1] as preceding bar history, not an array element; handle initial missing values.

**Why:** Pine executes across bars, with separate realtime updates.

**Verify:** Synthetic warm-up and closed-bar comparison.

**Evidence:** S15 S16.

## T03 — Respect qualifiers (language)
**How:** Trace strongest qualifier of an expression before passing lengths, symbols or plot titles; do not cast blindly.

**Why:** Many APIs require weaker qualifiers.

**Verify:** Read exact overload and test dynamic inputs.

**Evidence:** S16 S36.

## T04 — Hoist stateful calls (language)
**How:** Compute moving averages, RSI and crosses on each bar, then apply gating.

**Why:** v6 lazy boolean evaluation can skip evaluations needed for history.

**Verify:** Compare gated and ungated feature series.

**Evidence:** S17 S15.

## T05 — Use typed missing values (language)
**How:** Declare initial na with explicit type and check na(x), not numeric substitutes.

**Why:** Missing and zero have different meanings.

**Verify:** Zero and missing fixture.

**Evidence:** S16.

## T06 — Choose var deliberately (state)
**How:** Use var for cross-bar persistence; use ordinary declarations for per-execution values.

**Why:** Persistent state must not reset inadvertently.

**Verify:** Reload and compare known closed-bar events.

**Evidence:** S15 S22.

## T07 — Treat varip as intrabar-only unless proved (state)
**How:** Describe what cannot be reconstructed after reload; never infer historical tick sequence.

**Why:** Realtime intrabar state differs from history.

**Verify:** Live log versus reload; do not expect identity for tick-only state.

**Evidence:** S15 S21.

## T08 — Guard collection reads (state)
**How:** Check size before get, pop or shift; cap growth.

**Why:** Empty arrays and unbounded memory break scripts.

**Verify:** Empty, one element and capacity tests.

**Evidence:** S18 S32.

## T09 — Use functions with clear contracts (state)
**How:** Specify units, na behavior and qualifiers; avoid hidden state unless needed.

**Why:** Simplifies parity and tests.

**Verify:** Verify caller behavior across chart contexts.

**Evidence:** S36 S16.

## T10 — Confirm chart signals (temporal)
**How:** Separate provisional values from confirmed signals; barstate.isconfirmed at chart scope only for this purpose.

**Why:** Open-bar values can change.

**Verify:** Compare realtime close versus reload.

**Evidence:** S15 S21 S34.

## T11 — Use confirmed HTF pattern (temporal)
**How:** For strictly higher TF, request the previous expression value with lookahead_on and guard timeframe.

**Why:** Unshifted lookahead_on may expose future history.

**Verify:** Test HTF boundary, same/lower rejection, reload.

**Evidence:** S19 S20 S21.

## T12 — Do not confuse offsets (temporal)
**How:** Offset expression inside request context, not result after request, when retrieving prior HTF expression.

**Why:** A chart-bar shift is not an HTF-bar shift.

**Verify:** Compare against native HTF close.

**Evidence:** S19 S20.

## T13 — Request lower timeframe arrays (temporal)
**How:** Use security_lower_tf for available intrabars when needed; check counts and missingness.

**Why:** One LTF sample is not all intrabars.

**Verify:** Test low-liquidity periods and empty arrays.

**Evidence:** S19 S20.

## T14 — Separate pivot anchor from discovery (temporal)
**How:** Store confirmation time and original pivot time separately; never backdate tradable signal.

**Why:** Right-side pivot confirmation requires later observations.

**Verify:** Replay right-strength delay.

**Evidence:** S21 S22.

## T15 — Use actual timestamps (temporal)
**How:** Store exchange/timezone/session assumptions; distinguish event, receipt and availability timestamps.

**Why:** A feature may not be observable at its chart anchor.

**Verify:** DST, overnight and session-boundary tests.

**Evidence:** S15 S19.

## T16 — Tag feed and units (data)
**How:** Use venue-qualified symbols, quote currency, contract type, units and feature source.

**Why:** Spot, perpetual and aggregated values are not interchangeable.

**Verify:** Cross-feed and missing-data comparison.

**Evidence:** S19 S30.

## T17 — Reject synthetic orderflow claims (data)
**How:** Label OHLCV-derived delta or liquidity as proxy; use verified footprint/feed features only when supported.

**Why:** A bar-derived estimate is not an exchange L2/L3 book.

**Verify:** Compare availability and provenance; do not claim hidden orders.

**Evidence:** S19 S32.

## T18 — Check footprint availability (data)
**How:** Verify current signature, plan, feed, na handling and request-count restrictions; test on supported symbol.

**Why:** Footprint may be unavailable or request composition may exceed restrictions.

**Verify:** Missing-feed and single-request probe.

**Evidence:** S19 S32 S33.

## T19 — Distinguish RVOL definitions (data)
**How:** Specify baseline (including/excluding current bar, session-adjusted or not) and zero-volume policy.

**Why:** Different definitions produce different numbers.

**Verify:** Known window fixture and no-volume case.

**Evidence:** S16 S22.

## T20 — Separate calculation from rendering (human)
**How:** Compute features regardless of display mode; toggle only presentation.

**Why:** Mode changes must not alter underlying signals.

**Verify:** Export parity with toggles.

**Evidence:** S25 S31.

## T21 — Use one persistent dashboard (human)
**How:** Allocate table once and update on last bar; calculate rolling values on all bars.

**Why:** Avoid unnecessary object allocations and missing series history.

**Verify:** Profiler and mode toggle check.

**Evidence:** S24 S35 S34.

## T22 — Keep overlays sparse (human)
**How:** Use grouped inputs, optional layers, stable color meaning and text/shape cues.

**Why:** Readability is not the same as more information.

**Verify:** Review dark/light themes, dense charts and mobile.

**Evidence:** S25 S02.

## T23 — Reuse drawings (human)
**How:** Update persistent objects and delete expired ones instead of creating every bar.

**Why:** Drawings have limits and cost.

**Verify:** Check object count and profiling.

**Evidence:** S22 S24 S32.

## T24 — Stable feature IDs (ai)
**How:** Define names, units, schema version, build, effective config, feed and times.

**Why:** Agents need stable numeric contracts rather than screenshots.

**Verify:** Compare exported data and alert payload.

**Evidence:** S28 S30 S31.

## T25 — Serialize missing as JSON null (ai)
**How:** Use explicit null token and validate at receiver; reject NaN/Infinity and unescaped strings.

**Why:** Invalid JSON and fake zeros contaminate models.

**Verify:** Offline JSON tests and actual alert check.

**Evidence:** S28 S29.

## T26 — Respect alert snapshot (ai)
**How:** Recreate the alert when source, inputs or context change; include config/build ID.

**Why:** Server-side alert uses saved context.

**Verify:** Test new and old configurations separately.

**Evidence:** S28.

## T27 — Separate ingestion from execution (ai)
**How:** Use sink-only HTTPS endpoint, durable queue and reconciliation; no credentials in payload; acknowledge within documented timeout.

**Why:** Delivery can fail and alerts are not a guaranteed execution API.

**Verify:** Duplicate, missing, late and malformed messages.

**Evidence:** S29 S37.

## T28 — Use CSV for historical samples (ai)
**How:** Export chart/indicator data where permitted; verify actual columns, history coverage and time alignment.

**Why:** Realtime alert stream is not historical export.

**Verify:** Compare exact row timestamps and plot IDs.

**Evidence:** S30 S31.

## T29 — Separate signal and fill time (strategy)
**How:** Record order generation, actual simulated fill, and settings; do not assume signal close fills.

**Why:** Broker emulator execution differs by order type and settings.

**Verify:** Strategy Tester trade list vs plotted event.

**Evidence:** S26 S27.

## T30 — Explicit transaction friction (strategy)
**How:** Set commission, slippage and size; model spreads/funding externally when necessary; test costs per side.

**Why:** Gross edge can vanish after friction.

**Verify:** Stress costs and compare net baseline.

**Evidence:** S26 S27.

## T31 — Use standard chart prices for baseline (strategy)
**How:** Prefer ordinary candles for fill realism; document any synthetic chart use and emulator configuration.

**Why:** Synthetic OHLC may not be executable prices.

**Verify:** Repeat on standard candles.

**Evidence:** S26.

## T32 — Stop semantics matter (strategy)
**How:** Distinguish absolute price from tick distance, stop from limit and trailing activation from offset; verify API per version.

**Why:** Unit errors distort orders and results.

**Verify:** Known-price trade fixture and fill review.

**Evidence:** S26 S27.

## T33 — Check sizing units (strategy)
**How:** For linear instrument cash risk divided by stop distance times point value, then round down; include costs, conversion and margin separately.

**Why:** Different instruments have different payoff geometry.

**Verify:** Synthetic sizing fixture plus exchange metadata.

**Evidence:** S26 S16.

## T34 — Do not optimize holdout (quant)
**How:** Separate chronological development/validation/test, record trials, compare baseline and test robustness.

**Why:** Selection bias inflates apparent performance.

**Verify:** Review split boundaries and trial ledger.

**Evidence:** S26; project RESEARCH.md.

## T35 — Confluence is not independent by default (quant)
**How:** Group correlated momentum/trend features; require incremental out-of-sample benefit.

**Why:** Multiple transforms of same price are redundant evidence.

**Verify:** Ablation and cost stress tests.

**Evidence:** project RESEARCH.md; derived engineering rule.

## T36 — Reduce to minimal reproducible script (debug)
**How:** Isolate one compiler warning or runtime failure with same version and inputs; use logs selectively.

**Why:** Smaller state space reveals root cause.

**Verify:** Save original error and corrected result.

**Evidence:** S23 S25.

## T37 — Profile then optimize (debug)
**How:** Measure hot paths on same context; prefer built-ins when semantics match; update drawings; reduce repeated requests where valid.

**Why:** Shorter code is not necessarily faster.

**Verify:** Repeated before/after profiling and parity checks.

**Evidence:** S24 S32.

## T38 — Track resource budgets (debug)
**How:** Read current plot, object, execution and request limitations; prototype worst-case inputs.

**Why:** Limits can vary by plan and release.

**Verify:** Worst-case stress and controlled failure.

**Evidence:** S32 S33.

## T39 — Migrate one version at a time (migration)
**How:** Snapshot baseline and follow ordered migration guides, especially v5→v6 lazy eval and bool changes.

**Why:** Silent changes may alter signals, not just syntax.

**Verify:** Compile and compare every intermediate where supported.

**Evidence:** S17 S33.

## T40 — Use independent reconstruction (learning)
**How:** Predict, code, test, then read reference; record one counterexample and verify correction.

**Why:** Reading alone does not demonstrate competence.

**Verify:** Evidence rubric and regression checks.

**Evidence:** S03; derived training protocol.
