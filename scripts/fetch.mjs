// Council data fetcher — runs on GitHub's runners (open internet).
// Dukascopy (Swiss bank ECN feed): hourly BID and ASK candles -> real spreads.
// Yahoo Finance: hourly + daily bars as an independent cross-check / fallback.
import fs from 'node:fs';
import { getHistoricRates } from 'dukascopy-node';
const req = JSON.parse(fs.readFileSync('request.json', 'utf8'));
const to = req.to ? new Date(req.to) : new Date();
const from = new Date(req.from);
fs.mkdirSync('data/duka', { recursive: true }); fs.mkdirSync('data/yahoo', { recursive: true });
const t0 = Date.now();
const status = { requested_at: req.requested_at, ran_at: new Date().toISOString(), from: req.from, to: to.toISOString(), items: {} };
// Incremental: each file is extended from its last stored bar (minus a 2-day overlap) unless request.full is true.
const readCsv = p => { if (!fs.existsSync(p)) return []; return fs.readFileSync(p, 'utf8').trim().split('\n').slice(1).filter(Boolean).map(l => { const [t, o, h, lo, c, v] = l.split(','); return { timestamp: Date.parse(t), open: +o, high: +h, low: +lo, close: +c, volume: v === '' ? undefined : +v }; }); };
const startFor = p => { if (req.full) return from; const old = readCsv(p); if (!old.length) return from; return new Date(Math.max(from.getTime(), old[old.length - 1].timestamp - 2 * 864e5)); };
const merge = (p, rows) => { const m = new Map(readCsv(p).map(r => [r.timestamp, r])); for (const r of rows) m.set(r.timestamp, r); const all = [...m.values()].sort((a, b) => a.timestamp - b.timestamp); fs.writeFileSync(p, toCsv(all)); return rows.length; };
const toCsv = rows => 'time,open,high,low,close,volume\n' + rows.map(r => [new Date(r.timestamp).toISOString(), r.open, r.high, r.low, r.close, r.volume ?? ''].join(',')).join('\n') + '\n';

async function duka(inst, side) {
  const p = `data/duka/${inst.key}_h1_${side}.csv`;
  const rows = await getHistoricRates({ instrument: inst.duka, dates: { from: startFor(p), to }, timeframe: 'h1', priceType: side,
    format: 'json', volumes: true, ignoreFlats: true, batchSize: 15, pauseBetweenBatchesMs: 400, retryCount: 3, retryOnEmpty: true });
  return merge(p, rows);
}
async function yahoo(inst, interval) {
  const p = `data/yahoo/${inst.key}_${interval === '1h' ? 'h1' : 'd1'}.csv`;
  const st0 = startFor(p).getTime();
  const p1 = Math.floor((interval === '1h' ? Math.max(st0, Date.now() - 720 * 864e5) : st0) / 1000);
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(inst.yahoo)}?interval=${interval}&period1=${p1}&period2=${Math.floor(to.getTime() / 1000)}&includePrePost=false`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0 council-data' } });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  const j = await r.json(); const res = j.chart?.result?.[0];
  if (!res) throw new Error(JSON.stringify(j.chart?.error || 'no result'));
  const q = res.indicators.quote[0]; const rows = [];
  res.timestamp.forEach((t, i) => { if (q.open[i] != null && q.close[i] != null) rows.push({ timestamp: t * 1000, open: q.open[i], high: q.high[i], low: q.low[i], close: q.close[i], volume: q.volume?.[i] }); });
  return merge(p, rows);
}
async function one(inst) {
  const s = status.items[inst.key] = {};
  for (const [label, fn] of [['duka_bid', () => duka(inst, 'bid')], ['duka_ask', () => duka(inst, 'ask')],
                             ['yahoo_h1', () => yahoo(inst, '1h')], ['yahoo_d1', () => yahoo(inst, '1d')]]) {
    if ((label.startsWith('duka') && !inst.duka) || (label.startsWith('yahoo') && !inst.yahoo)) continue;
    try { s[label] = await fn(); } catch (e) { s[label] = 'ERROR: ' + String(e.message || e).slice(0, 200); }
    console.log(inst.key, label, s[label]);
  }
}
const queue = req.instruments.filter(i => !req.only || req.only.includes(i.key));
await Promise.all(Array.from({ length: 4 }, async () => { while (queue.length) await one(queue.shift()); }));
status.seconds = Math.round((Date.now() - t0) / 1000);
fs.writeFileSync('status.json', JSON.stringify(status, null, 1));
