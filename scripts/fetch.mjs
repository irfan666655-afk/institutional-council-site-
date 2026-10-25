// Council data fetcher — runs on GitHub's runners (open internet).
// Dukascopy (Swiss bank ECN feed): hourly BID and ASK candles -> real spreads.
// Yahoo Finance: hourly + daily bars as an independent cross-check / fallback.
import fs from 'node:fs';
import { getHistoricRates } from 'dukascopy-node';
const req = JSON.parse(fs.readFileSync('request.json', 'utf8'));
const to = req.to ? new Date(req.to) : new Date();
const from = new Date(req.from);
fs.mkdirSync('data/duka', { recursive: true }); fs.mkdirSync('data/yahoo', { recursive: true });
const status = { requested_at: req.requested_at, ran_at: new Date().toISOString(), from: req.from, to: to.toISOString(), items: {} };
const toCsv = rows => 'time,open,high,low,close,volume\n' + rows.map(r => [new Date(r.timestamp).toISOString(), r.open, r.high, r.low, r.close, r.volume ?? ''].join(',')).join('\n') + '\n';

async function duka(inst, side) {
  const rows = await getHistoricRates({ instrument: inst.duka, dates: { from, to }, timeframe: 'h1', priceType: side,
    format: 'json', volumes: true, ignoreFlats: true, batchSize: 15, pauseBetweenBatchesMs: 400, retryCount: 3, retryOnEmpty: true });
  fs.writeFileSync(`data/duka/${inst.key}_h1_${side}.csv`, toCsv(rows));
  return rows.length;
}
async function yahoo(inst, interval) {
  const p1 = Math.floor((interval === '1h' ? Math.max(from.getTime(), Date.now() - 720 * 864e5) : from.getTime()) / 1000);
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(inst.yahoo)}?interval=${interval}&period1=${p1}&period2=${Math.floor(to.getTime() / 1000)}&includePrePost=false`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0 council-data' } });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  const j = await r.json(); const res = j.chart?.result?.[0];
  if (!res) throw new Error(JSON.stringify(j.chart?.error || 'no result'));
  const q = res.indicators.quote[0]; const rows = [];
  res.timestamp.forEach((t, i) => { if (q.open[i] != null && q.close[i] != null) rows.push({ timestamp: t * 1000, open: q.open[i], high: q.high[i], low: q.low[i], close: q.close[i], volume: q.volume?.[i] }); });
  fs.writeFileSync(`data/yahoo/${inst.key}_${interval === '1h' ? 'h1' : 'd1'}.csv`, toCsv(rows));
  return rows.length;
}
for (const inst of req.instruments) {
  const s = status.items[inst.key] = {};
  for (const [label, fn] of [['duka_bid', () => duka(inst, 'bid')], ['duka_ask', () => duka(inst, 'ask')],
                             ['yahoo_h1', () => yahoo(inst, '1h')], ['yahoo_d1', () => yahoo(inst, '1d')]]) {
    if ((label.startsWith('duka') && !inst.duka) || (label.startsWith('yahoo') && !inst.yahoo)) continue;
    try { s[label] = await fn(); } catch (e) { s[label] = 'ERROR: ' + String(e.message || e).slice(0, 200); }
    console.log(inst.key, label, s[label]);
  }
}
fs.writeFileSync('status.json', JSON.stringify(status, null, 1));
