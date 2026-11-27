// Probe which official v6 functions exist in the installed PineTS (presence only, not correctness).
// Usage: node probe_functions.mjs LEDGER.json OUT.json
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { PineTS } from 'pinets';
// Methods shipped by PineTS per namespace (authoritative for receiver-style functions like array.avg)
const NS_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), 'node_modules', 'pinets', 'dist', 'types', 'namespaces');
const shipped = ns => { try { return new Set(fs.readdirSync(path.join(NS_DIR, ns, 'methods')).map(f => f.replace(/\.d\.ts$/, ''))); } catch { return null; } };
const [, , ledgerPath, outPath] = process.argv;
const ledger = JSON.parse(fs.readFileSync(ledgerPath, 'utf8'));
const bars = Array.from({ length: 5 }, (_, i) => ({ open: 10 + i, high: 11 + i, low: 9 + i, close: 10.5 + i, volume: 100, openTime: 1704067200000 + i * 86400000 }));
const origLog = console.log; console.log = () => {};
const out = {};
for (const e of ledger.entries.filter(e => e.kind === 'fun')) {
  const name = e.name.replace(/<[^>]*>/g, '');
  if (['indicator', 'strategy', 'library'].includes(name)) { out[e.name] = 'PRESENT'; continue; }
  const src = `//@version=6\nindicator("p")\nvar _x = ${name}()\nplot(0)\n`;
  try { await new PineTS(bars, 'P', 'D').run(src); out[e.name] = 'PRESENT'; }
  catch (err) {
    const m = String(err?.message ?? err);
    const first = m.split('\n')[0];
    if (/is not a function|Undeclared identifier|is not defined/.test(first)) out[e.name] = 'ABSENT';
    else if (/Cannot read properties of undefined/.test(first)) {
      const [ns, ...rest] = name.split('.');
      const set = shipped(ns);
      out[e.name] = set ? (set.has(rest.join('_')) || set.has(rest.join('.')) ? 'PRESENT' : 'ABSENT') : 'UNCERTAIN';
    } else out[e.name] = 'PRESENT';
    if (out[e.name] !== 'PRESENT') out[e.name + '__msg'] = m.split('\n')[0].slice(0, 160);
  }
}
console.log = origLog;
fs.writeFileSync(outPath, JSON.stringify(out, null, 1));
const vals = Object.entries(out).filter(([k]) => !k.endsWith('__msg')).map(([, v]) => v);
console.log('functions', vals.length, 'present', vals.filter(v => v === 'PRESENT').length, 'absent', vals.filter(v => v === 'ABSENT').length, 'uncertain', vals.filter(v => v === 'UNCERTAIN').length);
