// Pine Engineering Lab V5 -- PineTS execution adapter (called by tools/pinelab.py).
// Usage: node engine.mjs REQUEST.json RESPONSE.json
// REQUEST: {script, csv, base_timeframe, timeframe, symbol, inputs?, max_bars?, max_loops?}
// RESPONSE: {ok, engine, error?, time[], plots{}, strategy?, warnings[], alerts[], logs[], duration_ms}
// Never reports success for transpile/runtime/data errors; never approximates unsupported timeframes.
import fs from 'fs';
import { createRequire } from 'module';
import { PineTS, Indicator } from 'pinets';
import { LocalProvider, UnsupportedTimeframeError } from './local_provider.mjs';

const require = createRequire(import.meta.url);
const ENGINE = { name: 'PineTS', version: require('pinets/package.json').version, adapter: 'pinelab-engine/1' };
const [, , reqPath, outPath] = process.argv;
const req = JSON.parse(fs.readFileSync(reqPath, 'utf8'));
const logs = [];
const origLog = console.log;
console.log = (...a) => { if (logs.length < 2000) logs.push(a.map(String).join(' ')); };  // capture log.* output
const t0 = Date.now();

function classify(e) {
  const msg = String(e?.message ?? e);
  if (e instanceof UnsupportedTimeframeError || /finer than the local base timeframe|Unrecognized timeframe/.test(msg)) return 'UNSUPPORTED';
  if (/Failed to transpile|Unexpected token|Undeclared identifier/.test(msg)) return 'COMPILE_ERROR';
  if (/CSV/.test(msg)) return 'DATA_ERROR';
  return 'RUNTIME_ERROR';
}
const num = v => (typeof v === 'number' && !Number.isFinite(v)) ? null : v;
const clean = (o, depth = 0) => {
  if (depth > 4 || o === null || o === undefined) return o ?? null;
  if (Array.isArray(o)) return o.map(x => clean(x, depth + 1));
  if (typeof o === 'object') return Object.fromEntries(Object.entries(o).filter(([k]) => !k.startsWith('_')).map(([k, v]) => [k, clean(v, depth + 1)]));
  return num(o);
};

let out;
try {
  const provider = new LocalProvider({ csv: req.csv, baseTimeframe: String(req.base_timeframe) });
  const pine = new PineTS(provider, req.symbol || 'LOCAL:SYNTH', String(req.timeframe), req.max_bars || undefined);
  pine.setMaxLoops(req.max_loops || 100000);
  const src = fs.readFileSync(req.script, 'utf8');
  const res = await pine.run(req.inputs ? new Indicator(src, req.inputs) : src);
  const plots = {}; let time = null;
  for (const [k, v] of Object.entries(res.plots || {})) {
    if (k.startsWith('__')) continue;
    plots[k] = v.data.map(d => (d.value === undefined || d.value === null || (typeof d.value === 'number' && Number.isNaN(d.value))) ? null : d.value);
    time ??= v.data.map(d => d.time);
  }
  const s = res.strategy;
  const isStrategy = /^\s*strategy\s*\(/m.test(src);
  out = { ok: true, engine: ENGINE, time, plots,
    strategy: isStrategy && s ? clean({ config: s.config, netprofit: s.netprofit, grossprofit: s.grossprofit, grossloss: s.grossloss,
      max_drawdown: s.max_drawdown, equity: s.equity, initial_capital: s.initial_capital, position_size: s.position_size,
      wintrades: s.wintrades, losstrades: s.losstrades, closedtrades: s.closedtrades, opentrades: s.opentrades }) : null,
    warnings: clean(res.warnings || []), alerts: clean(res.alerts || []), logs,
    provider_requests: provider.requests };
} catch (e) {
  out = { ok: false, engine: ENGINE, error: { type: classify(e), message: String(e?.message ?? e).split('\n')[0].slice(0, 600) }, logs };
}
out.duration_ms = Date.now() - t0;
fs.writeFileSync(outPath, JSON.stringify(out));
console.log = origLog;
