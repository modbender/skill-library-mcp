/**
 * @module aggregator
 * Compute daily aggregate statistics from raw events.
 */

/**
 * Compute or recompute daily aggregates for a given date.
 * @param {import('better-sqlite3').Database} db
 * @param {string} [date] - YYYY-MM-DD; defaults to today (UTC)
 * @returns {{ date: string, total_tokens_in: number, total_tokens_out: number, total_cost: number, task_success: number, task_failure: number }}
 */
export function computeAggregate(db, date) {
  const d = date || new Date().toISOString().slice(0, 10);

  const tokens = db.prepare(`
    SELECT COALESCE(SUM(tokens_in), 0) AS total_in,
           COALESCE(SUM(tokens_out), 0) AS total_out,
           COALESCE(SUM(cost), 0) AS total_cost
    FROM token_events WHERE date(timestamp) = ?
  `).get(d);

  const tasks = db.prepare(`
    SELECT COALESCE(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END), 0) AS success,
           COALESCE(SUM(CASE WHEN status IN ('failure', 'timeout') THEN 1 ELSE 0 END), 0) AS failure
    FROM task_events WHERE date(timestamp) = ?
  `).get(d);

  const row = {
    date: d,
    total_tokens_in: tokens.total_in,
    total_tokens_out: tokens.total_out,
    total_cost: tokens.total_cost,
    task_success: tasks.success,
    task_failure: tasks.failure,
  };

  db.prepare(`
    INSERT OR REPLACE INTO daily_aggregates (date, total_tokens_in, total_tokens_out, total_cost, task_success, task_failure, computed_at)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
  `).run(row.date, row.total_tokens_in, row.total_tokens_out, row.total_cost, row.task_success, row.task_failure);

  return row;
}

/**
 * Compute aggregates for all dates that have events but no aggregate yet.
 * @param {import('better-sqlite3').Database} db
 * @returns {number} Number of dates aggregated
 */
export function computeAllMissing(db) {
  const dates = db.prepare(`
    SELECT DISTINCT date(timestamp) AS d FROM token_events
    UNION
    SELECT DISTINCT date(timestamp) AS d FROM task_events
    EXCEPT
    SELECT date FROM daily_aggregates
  `).all().map(r => r.d);

  for (const d of dates) computeAggregate(db, d);
  return dates.length;
}
