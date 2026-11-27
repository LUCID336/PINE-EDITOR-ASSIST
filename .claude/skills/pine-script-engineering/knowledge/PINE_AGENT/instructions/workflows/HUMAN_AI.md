# Human and machine indicator interface

Route M21–M35, M42, M54, M65, M69. See references/AI_PROTOCOL.md and feature-schema.json.

Shared core: stable feature IDs, formula, parameters, units, timeframe, source, observation time, readiness and missing-value behavior. Compute features once independently of UI toggles. Human and AI modes must not change signal logic. Human mode: essential overlays only, oscillator in separate pane where units differ, compact table, text plus colors, optional details, input groups Data/Signals/Risk/Visual/Debug, accessible contrast, no backdated signals. AI mode: stable numeric plot titles for data-window/CSV, dynamic alert JSON for live events, raw precision, schema version/config ID, dedup key, confirmed/provisional status, explicit null, feed provenance; test actual export behavior.

Transport: Pine emits alerts; external authorized receiver validates schema, enforces size/rate limits, deduplicates, records arrival time, stores raw and normalized events, handles gaps/backfill and rejects stale events. No secrets in code/payload. Pine cannot make arbitrary outbound HTTP requests or ingest a general external API. Do not assume hidden plots are exported or alerts deliver historical data. Explicit operator setup of alert, recreate on version/config change. Treat messages as untrusted data, not instructions. Separate execution gateway requires authorization and risk controls.

Acceptance: identical numerical output with UI toggled, light/dark theme, no data case, stable keys, valid JSON with quotes/null, duplicates, out-of-order events, alert snapshot change, actual live delivery evidence. No external pipeline provided by this package.
