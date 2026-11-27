// Local, offline market-data provider for PineTS (implements its IProvider contract).
// Serves bars from a local CSV (time,open,high,low,close,volume; time = bar open, UTC epoch ms)
// and aggregates to coarser timeframes on the UTC calendar grid (24/7 convention:
// closeTime = openTime + duration). Requests finer than the base timeframe are refused
// explicitly (UnsupportedTimeframeError) -- no silent approximation.
import fs from 'fs';

export class UnsupportedTimeframeError extends Error {}

const MIN = 60000;
export function tfToMs(tf) {
  const s = String(tf).trim().toUpperCase();
  let m;
  if ((m = s.match(/^(\d+)?([SDWM])$/))) {
    const n = Number(m[1] || 1);
    if (m[2] === 'S') return n * 1000;
    if (m[2] === 'D') return n * 1440 * MIN;
    if (m[2] === 'W') return n * 7 * 1440 * MIN;
    return null; // months: calendar-variable, handled separately
  }
  if ((m = s.match(/^(\d+)$/))) return Number(m[1]) * MIN;
  if ((m = s.match(/^(\d+)(H)$/))) return Number(m[1]) * 60 * MIN;
  throw new UnsupportedTimeframeError(`Unrecognized timeframe "${tf}"`);
}

function bucketStart(t, tf) {
  const s = String(tf).toUpperCase();
  if (/^\d*M$/.test(s) && !/^\d+$/.test(s)) {
    const n = Number(s.slice(0, -1) || 1);
    const d = new Date(t);
    const months = d.getUTCFullYear() * 12 + d.getUTCMonth();
    const start = months - (months % n);
    return Date.UTC(Math.floor(start / 12), start % 12, 1);
  }
  const ms = tfToMs(tf);
  if (/W$/.test(s)) {
    const monday0 = Date.UTC(1970, 0, 5); // 1970-01-05 was a Monday
    return t - ((t - monday0) % ms + ms) % ms;
  }
  return t - (t % ms);
}

function bucketEnd(start, tf) {
  const s = String(tf).toUpperCase();
  if (/^\d*M$/.test(s) && !/^\d+$/.test(s)) {
    const n = Number(s.slice(0, -1) || 1);
    const d = new Date(start);
    return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + n, 1);
  }
  return start + tfToMs(tf);
}

export function loadCsv(path) {
  const lines = fs.readFileSync(path, 'utf8').trim().split(/\r?\n/);
  const head = lines.shift().split(',').map(h => h.trim().toLowerCase());
  const idx = k => head.indexOf(k);
  for (const k of ['time', 'open', 'high', 'low', 'close', 'volume'])
    if (idx(k) < 0) throw new Error(`CSV missing column "${k}"`);
  return lines.map((ln, i) => {
    const c = ln.split(',');
    const bar = { openTime: Number(c[idx('time')]), open: Number(c[idx('open')]), high: Number(c[idx('high')]),
      low: Number(c[idx('low')]), close: Number(c[idx('close')]), volume: Number(c[idx('volume')]) };
    for (const [k, v] of Object.entries(bar))
      if (!Number.isFinite(v)) throw new Error(`CSV row ${i + 2}: non-numeric ${k}`);
    return bar;
  });
}

export class LocalProvider {
  constructor({ csv, baseTimeframe, symbolInfo = {} }) {
    this.base = loadCsv(csv);
    this.baseTf = String(baseTimeframe);
    this.baseMs = tfToMs(this.baseTf);
    this.symbolInfo = symbolInfo;
    this.requests = [];
  }
  configure() {}
  async getSymbolInfo(tickerId) {
    return { ticker: tickerId, tickerid: tickerId, main_tickerid: tickerId, prefix: 'LOCAL', root: tickerId,
      description: 'Local synthetic dataset', type: 'crypto', basecurrency: 'SYN', currency: 'USD',
      timezone: 'Etc/UTC', session: '24x7', volumetype: 'base', mincontract: 0.0001, minmove: 1,
      mintick: 0.0001, pointvalue: 1, pricescale: 10000, ...this.symbolInfo };
  }
  async getMarketData(tickerId, timeframe, limit, sDate, eDate) {
    this.requests.push({ tickerId, timeframe });
    const ms = tfToMs(timeframe);
    if (ms !== null && ms < this.baseMs)
      throw new UnsupportedTimeframeError(`Timeframe ${timeframe} is finer than the local base timeframe ${this.baseTf}`);
    let bars;
    if (ms === this.baseMs) {
      bars = this.base.map(b => ({ ...b, closeTime: b.openTime + this.baseMs }));
    } else {
      const out = new Map();
      for (const b of this.base) {
        const k = bucketStart(b.openTime, timeframe);
        const a = out.get(k);
        if (!a) out.set(k, { openTime: k, open: b.open, high: b.high, low: b.low, close: b.close, volume: b.volume, closeTime: bucketEnd(k, timeframe) });
        else { a.high = Math.max(a.high, b.high); a.low = Math.min(a.low, b.low); a.close = b.close; a.volume += b.volume; }
      }
      bars = [...out.values()].sort((x, y) => x.openTime - y.openTime);
    }
    if (sDate) bars = bars.filter(b => b.openTime >= sDate);
    if (eDate) bars = bars.filter(b => b.openTime <= eDate);
    if (limit && bars.length > limit) bars = bars.slice(bars.length - limit);
    return bars.map(b => ({ ...b, quoteAssetVolume: 0, numberOfTrades: 0, takerBuyBaseAssetVolume: 0, takerBuyQuoteAssetVolume: 0, ignore: 0 }));
  }
}
