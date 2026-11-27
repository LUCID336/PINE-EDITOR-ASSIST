// Usage: node run_pine.mjs SCRIPT.pine CANDLES.json TIMEFRAME OUT.json
// Executes Pine source in PineTS on a supplied OHLCV array and writes non-internal plot series.
// Known limits (calibrated 2026-11-27): request.security HTF on custom arrays is NOT aggregated;
// request.security_lower_tf unsupported on custom arrays; no realtime ticks / rollback.
import { PineTS } from 'pinets';
import fs from 'fs';
const [, , file, data, tf = 'D', out] = process.argv;
try {
  const res = await new PineTS(JSON.parse(fs.readFileSync(data, 'utf8')), 'FIXTURE', tf).run(fs.readFileSync(file, 'utf8'));
  const plots = {};
  for (const [k, v] of Object.entries(res.plots)) {
    if (k.startsWith('__')) continue;
    plots[k] = v.data.map(d => (d.value === undefined || d.value === null || Number.isNaN(d.value)) ? null : d.value);
  }
  fs.writeFileSync(out, JSON.stringify({ ok: true, plots }));
} catch (e) {
  fs.writeFileSync(out, JSON.stringify({ ok: false, error: String(e?.message ?? e).slice(0, 500) }));
}
