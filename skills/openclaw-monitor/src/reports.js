/**
 * @module reports
 * Report generation for status, tokens, crons, tasks, and cost.
 */

/**
 * Parse a period string like '7d' or '30d' into a date string.
 * @param {string} period
 * @returns {string} ISO date string for the start of the period
 */
function periodToDate(period) {
  const match = period.match(/^(\d+)([dwm])$/);
  if (!match) throw new Error(`Invalid period: ${period}. Use e.g. 7d, 30d`);
  const n = parseInt(match[1], 10);
  const unit = match[2];
  const d = new Date();
  if (unit === 'd') d.setDate(d.getDate() - n);
  else if (unit === 'w') d.setDate(d.getDate() - n * 7);
  else if (unit === 'm') d.setMonth(d.getMonth() - n);
  return d.toISOString().slice(0, 10);
}

/**
 * Get system health status summary.
 * @param {import('better-sqlite3').Database} db
 * @returns {{ today_tokens_in: number, today_tokens_out: number, today_cost: number, task_success: number, task_failure: number, task_timeout: number, cron_ok: number, cron_fail: number, recent_errors: Array }}
 */
export function getStatus(db) {
  const today = new Date().toISOString().slice(0, 10);

  const tokens = db.prepare(`
    SELECT COALESCE(SUM(tokens_in), 0) AS ti, COALESCE(SUM(tokens_out), 0) AS to2, COALESCE(SUM(cost), 0) AS cost
    FROM token_events WHERE date(timestamp) = ?
  `).get(today);

  const tasks = db.prepare(`
    SELECT status, COUNT(*) AS cnt FROM task_events WHERE date(timestamp) = ? GROUP BY status
  `).all(today);
  const taskMap = Object.fromEntries(tasks.map(r => [r.status, r.cnt]));

  const crons = db.prepare(`
    SELECT status, COUNT(*) AS cnt FROM cron_runs WHERE date(started) = ? GROUP BY status
  `).all(today);
  const cronMap = Object.fromEntries(crons.map(r => [r.status, r.cnt]));

  const recentErrors = db.prepare(`
    SELECT command, error, timestamp FROM task_events WHERE status != 'success' AND timestamp > datetime('now', '-7 days') ORDER BY timestamp DESC LIMIT 5
  `).all();

  return {
    today_tokens_in: tokens.ti,
    today_tokens_out: tokens.to2,
    today_cost: tokens.cost,
    task_success: taskMap.success || 0,
    task_failure: taskMap.failure || 0,
    task_timeout: taskMap.timeout || 0,
    cron_ok: cronMap.success || 0,
    cron_fail: cronMap.failure || 0,
    recent_errors: recentErrors,
  };
}

/**
 * Get token usage report.
 * @param {import('better-sqlite3').Database} db
 * @param {{ period?: string, by?: 'model'|'skill' }} [opts]
 * @returns {Array<Record<string, any>>}
 */
export function getTokenReport(db, opts = {}) {
  const since = opts.period ? periodToDate(opts.period) : periodToDate('7d');
  const groupBy = opts.by || 'model';
  const col = groupBy === 'skill' ? 'COALESCE(skill, \'unknown\')' : 'model';

  return db.prepare(`
    SELECT ${col} AS group_key,
           SUM(tokens_in) AS tokens_in,
           SUM(tokens_out) AS tokens_out,
           SUM(cost) AS cost,
           COUNT(*) AS events
    FROM token_events
    WHERE date(timestamp) >= ?
    GROUP BY group_key
    ORDER BY cost DESC
  `).all(since);
}

/**
 * Get cron job health report.
 * @param {import('better-sqlite3').Database} db
 * @returns {Array<{ job_name: string, total: number, success: number, failure: number, last_run: string, avg_duration_ms: number }>}
 */
export function getCronReport(db) {
  return db.prepare(`
    SELECT job_name,
           COUNT(*) AS total,
           SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS success,
           SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) AS failure,
           MAX(started) AS last_run,
           CAST(AVG(duration_ms) AS INTEGER) AS avg_duration_ms
    FROM cron_runs GROUP BY job_name ORDER BY last_run DESC
  `).all();
}

/**
 * Get recent task history.
 * @param {import('better-sqlite3').Database} db
 * @param {{ failed?: boolean }} [opts]
 * @returns {Array}
 */
export function getTaskReport(db, opts = {}) {
  const where = opts.failed ? "WHERE status != 'success'" : '';
  return db.prepare(`
    SELECT command, status, duration_ms, error, timestamp FROM task_events ${where} ORDER BY timestamp DESC LIMIT 50
  `).all();
}

/**
 * Get cost breakdown report.
 * @param {import('better-sqlite3').Database} db
 * @param {{ period?: string }} [opts]
 * @returns {{ total: number, by_model: Array, by_day: Array }}
 */
export function getCostReport(db, opts = {}) {
  const periodMap = { month: '30d', week: '7d' };
  const since = periodToDate(periodMap[opts.period] || opts.period || '7d');

  const total = db.prepare(`SELECT COALESCE(SUM(cost), 0) AS total FROM token_events WHERE date(timestamp) >= ?`).get(since);

  const byModel = db.prepare(`
    SELECT model, SUM(cost) AS cost, SUM(tokens_in) AS tokens_in, SUM(tokens_out) AS tokens_out
    FROM token_events WHERE date(timestamp) >= ? GROUP BY model ORDER BY cost DESC
  `).all(since);

  const byDay = db.prepare(`
    SELECT date(timestamp) AS date, SUM(cost) AS cost, SUM(tokens_in) AS tokens_in, SUM(tokens_out) AS tokens_out
    FROM token_events WHERE date(timestamp) >= ? GROUP BY date(timestamp) ORDER BY date DESC
  `).all(since);

  return { total: total.total, by_model: byModel, by_day: byDay };
}
