import express from 'express';
import { join, resolve } from 'path';
import { watch } from 'chokidar';
import { initDb, getDb } from './db.mjs';
import { config } from './config.mjs';
import { ingestAll, ingestFile, rebuildDailyAggregates } from './ingest.mjs';
import { checkBudgetAlerts } from './alerts.mjs';

const db = await initDb(config.dbPath);
const app = express();

console.log('🔄 Ingesting existing session logs...');
const count = await ingestAll(config.agentsDir);
console.log(`✅ Ingested ${count} new usage events`);

// Watch for changes
const watcher = watch(join(config.agentsDir, '**', 'sessions', '*.jsonl'), { ignoreInitial: true, persistent: true });
watcher.on('change', (fp) => {
  const parts = fp.split('/'); const ai = parts.indexOf('agents');
  const n = ingestFile(fp, ai >= 0 ? parts[ai + 1] : 'main');
  if (n > 0) { rebuildDailyAggregates(); console.log(`📥 ${n} new events`); checkBudgetAlerts().catch(console.error); }
});
watcher.on('add', (fp) => {
  const parts = fp.split('/'); const ai = parts.indexOf('agents');
  const n = ingestFile(fp, ai >= 0 ? parts[ai + 1] : 'main');
  if (n > 0) { rebuildDailyAggregates(); console.log(`📥 ${n} new events`); }
});

app.use(express.static(resolve(import.meta.dirname, '..', 'web')));

app.get('/api/summary', (req, res) => {
  const today = new Date().toISOString().slice(0, 10);
  const monthStart = today.slice(0, 7) + '-01';
  const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);

  res.json({
    today: db.prepare('SELECT COALESCE(SUM(total_cost),0) as t FROM daily_aggregates WHERE date=?').get(today)?.t || 0,
    week: db.prepare('SELECT COALESCE(SUM(total_cost),0) as t FROM daily_aggregates WHERE date>=?').get(weekAgo)?.t || 0,
    month: db.prepare('SELECT COALESCE(SUM(total_cost),0) as t FROM daily_aggregates WHERE date>=?').get(monthStart)?.t || 0,
    allTime: db.prepare('SELECT COALESCE(SUM(total_cost),0) as t FROM daily_aggregates').get()?.t || 0,
    sessions: db.prepare('SELECT COUNT(*) as c FROM sessions').get()?.c || 0,
    messages: db.prepare('SELECT COUNT(*) as c FROM usage_events').get()?.c || 0,
    budgetDaily: config.budgetDaily,
    budgetMonthly: config.budgetMonthly,
  });
});

app.get('/api/daily', (req, res) => {
  const days = parseInt(req.query.days || '30', 10);
  const since = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  res.json(db.prepare(`SELECT date, SUM(total_cost) as cost, SUM(total_input_tokens) as input_tokens,
    SUM(total_output_tokens) as output_tokens, SUM(message_count) as messages
    FROM daily_aggregates WHERE date>=? GROUP BY date ORDER BY date`).all(since));
});

app.get('/api/sessions', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit || '50', 10), 200);
  const offset = parseInt(req.query.offset || '0', 10);
  res.json(db.prepare(`SELECT id, agent, started_at, model, provider, total_cost,
    total_input_tokens, total_output_tokens, total_cache_read, total_cache_write, message_count
    FROM sessions ORDER BY started_at DESC LIMIT ? OFFSET ?`).all(limit, offset));
});

app.get('/api/models', (req, res) => {
  res.json(db.prepare(`SELECT model, provider, SUM(cost_total) as total_cost,
    SUM(input_tokens) as input_tokens, SUM(output_tokens) as output_tokens, COUNT(*) as message_count
    FROM usage_events GROUP BY model, provider ORDER BY total_cost DESC`).all());
});

app.get('/api/top-sessions', (req, res) => {
  const limit = Math.min(parseInt(req.query.limit || '10', 10), 50);
  res.json(db.prepare('SELECT id, agent, started_at, model, total_cost, message_count FROM sessions ORDER BY total_cost DESC LIMIT ?').all(limit));
});

app.get('/api/alerts', (req, res) => {
  res.json(db.prepare('SELECT * FROM alerts_log ORDER BY sent_at DESC LIMIT 50').all());
});

app.post('/api/ingest', async (req, res) => {
  const n = await ingestAll(config.agentsDir);
  res.json({ ingested: n });
});

app.listen(config.port, () => console.log(`🔥 ClawMeter running at http://localhost:${config.port}`));
