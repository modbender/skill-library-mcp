import { readFileSync, readdirSync, statSync, existsSync } from 'fs';
import { join } from 'path';
import { initDb, getDb } from './db.mjs';
import { calculateCost } from './pricing.mjs';
import { config } from './config.mjs';

export async function ingestAll(agentsDir) {
  const db = getDb();

  const agents = readdirSync(agentsDir).filter(d => {
    const sessDir = join(agentsDir, d, 'sessions');
    return existsSync(sessDir) && statSync(sessDir).isDirectory();
  });

  let totalNew = 0;
  for (const agent of agents) {
    const sessDir = join(agentsDir, agent, 'sessions');
    const files = readdirSync(sessDir).filter(f => f.endsWith('.jsonl'));
    for (const file of files) {
      totalNew += ingestFile(join(sessDir, file), agent);
    }
  }

  rebuildDailyAggregates();
  return totalNew;
}

export function ingestFile(filePath, agent = 'main') {
  const db = getDb();
  const stat = statSync(filePath);
  const stateRow = db.prepare('SELECT last_line, last_modified FROM ingest_state WHERE file_path = ?').get(filePath);

  const lastLine = stateRow?.last_line || 0;
  const lastMod = stateRow?.last_modified;

  if (lastMod && stat.mtimeMs <= parseFloat(lastMod) && lastLine > 0) return 0;

  const content = readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter(Boolean);

  let sessionId = null, sessionModel = null, sessionProvider = null;
  let newEvents = 0;

  const run = db.transaction(() => {
    for (let i = 0; i < lines.length; i++) {
      let p;
      try { p = JSON.parse(lines[i]); } catch { continue; }

      if (p.type === 'session') {
        sessionId = p.id;
        db.prepare('INSERT OR IGNORE INTO sessions (id, agent, started_at) VALUES (?, ?, ?)').run(sessionId, agent, p.timestamp);
      }
      if (p.type === 'model_change') { sessionModel = p.modelId; sessionProvider = p.provider; }

      if (p.type === 'message' && p.message?.role === 'assistant' && p.message?.usage) {
        if (i < lastLine) continue;
        const msg = p.message, usage = msg.usage;
        const model = msg.model || sessionModel;
        const provider = msg.provider || sessionProvider;
        const cost = calculateCost(usage, model);

        const r = db.prepare(`INSERT OR IGNORE INTO usage_events
          (session_id, event_id, timestamp, model, provider, input_tokens, output_tokens,
           cache_read, cache_write, cost_input, cost_output, cost_cache_read, cost_cache_write, cost_total, stop_reason)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(
          sessionId, p.id, p.timestamp, model, provider,
          usage.input || 0, usage.output || 0, usage.cacheRead || 0, usage.cacheWrite || 0,
          cost.input, cost.output, cost.cacheRead || 0, cost.cacheWrite || 0, cost.total,
          msg.stopReason || null
        );
        if (r.changes > 0) newEvents++;
      }
    }

    if (sessionId) {
      db.prepare(`UPDATE sessions SET
        total_cost = (SELECT COALESCE(SUM(cost_total), 0) FROM usage_events WHERE session_id = ?),
        total_input_tokens = (SELECT COALESCE(SUM(input_tokens), 0) FROM usage_events WHERE session_id = ?),
        total_output_tokens = (SELECT COALESCE(SUM(output_tokens), 0) FROM usage_events WHERE session_id = ?),
        total_cache_read = (SELECT COALESCE(SUM(cache_read), 0) FROM usage_events WHERE session_id = ?),
        total_cache_write = (SELECT COALESCE(SUM(cache_write), 0) FROM usage_events WHERE session_id = ?),
        message_count = (SELECT COUNT(*) FROM usage_events WHERE session_id = ?),
        model = COALESCE(?, model), provider = COALESCE(?, provider), last_ingested_line = ?
        WHERE id = ?`).run(sessionId, sessionId, sessionId, sessionId, sessionId, sessionId, sessionModel, sessionProvider, lines.length, sessionId);
    }

    db.prepare('INSERT OR REPLACE INTO ingest_state (file_path, last_line, last_modified) VALUES (?, ?, ?)').run(filePath, lines.length, String(stat.mtimeMs));
  });

  run();
  return newEvents;
}

export function rebuildDailyAggregates() {
  const db = getDb();
  db.exec('DELETE FROM daily_aggregates');
  db.exec(`INSERT INTO daily_aggregates (date, model, provider, total_cost, total_input_tokens, total_output_tokens, session_count, message_count)
    SELECT DATE(timestamp), COALESCE(model,'unknown'), COALESCE(provider,'unknown'),
      SUM(cost_total), SUM(input_tokens), SUM(output_tokens), COUNT(DISTINCT session_id), COUNT(*)
    FROM usage_events GROUP BY DATE(timestamp), model, provider`);
}

// CLI
if (process.argv[1]?.endsWith('ingest.mjs')) {
  await initDb(config.dbPath);
  const count = await ingestAll(config.agentsDir);
  console.log(`✅ Ingested ${count} new usage events`);
}
