// Re-extract the official Pine v6 reference (public page) into a structured ledger + example corpus.
// Usage: node refresh_reference.mjs OUT_DIR   (uses a local or the globally installed playwright)
// Produces OUT_DIR/v6_ledger_raw.json and OUT_DIR/examples.json. Then run build_ledger.py.
import { createRequire } from 'module';
import { execSync } from 'child_process';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const { chromium } = pw;
import fs from 'fs';
const out = process.argv[2] || '.';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('https://www.tradingview.com/pine-script-reference/v6/', { waitUntil: 'networkidle', timeout: 90000 });
await p.waitForTimeout(4000);
const data = await p.$$eval('div.tv-pine-reference-item[id]', els => els.map(el => {
  const id = el.id, kind = id.split('_')[0], name = id.slice(kind.length + 1);
  const q = s => [...el.querySelectorAll(s)];
  const sec = {}; let cur = null; const examples = [];
  for (const c of el.querySelector('.tv-pine-reference-item__content').children) {
    if (c.classList.contains('tv-pine-reference-item__sub-header')) { cur = c.innerText.trim(); sec[cur] = []; continue; }
    if (cur) { sec[cur].push(c.innerText.trim()); if (cur === 'EXAMPLE') examples.push(c.innerText); }
  }
  const lm = el.querySelector('.tv-pine-reference-item__learn-more-link');
  return { id, kind, name,
    syntax: q('pre.tv-pine-reference-item__syntax').map(e => e.innerText.trim()),
    args: q('.tv-pine-reference-item__arg-type').map(e => e.innerText.trim()),
    returns: (sec['RETURNS'] || []).join(' ').slice(0, 300), type: (sec['TYPE'] || []).join(' ').slice(0, 120),
    summary: ((el.querySelector('.tv-pine-reference-item__text') || {}).innerText || '').split(/(?<=\.)\s/)[0].slice(0, 220),
    learn_more: lm ? lm.getAttribute('href') : null, examples };
}));
await b.close();
fs.writeFileSync(`${out}/v6_ledger_raw.json`, JSON.stringify(data.map(({ examples, ...r }) => r), null, 1));
fs.writeFileSync(`${out}/examples.json`, JSON.stringify(data.flatMap(d => d.examples.map(code => ({ id: d.id, code })))));
console.log('entries', data.length);
