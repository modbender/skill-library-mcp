/**
 * @module sweep
 * Timeout detection and retry logic.
 */

/**
 * Sweep stale tasks: mark timed-out tasks as failed, retry eligible ones.
 * @param {import('better-sqlite3').Database} db
 * @returns {{ timedOut: number, retried: number }}
 */
export function sweep(db) {
  let timedOut = 0;
  let retried = 0;

  // Find claimed tasks past their timeout
  const stale = db.prepare(`
    SELECT * FROM tasks
    WHERE status = 'claimed'
      AND claimed_at IS NOT NULL
      AND (julianday('now') - julianday(claimed_at)) * 24 * 60 > timeout_minutes
  `).all();

  // Process each stale task in a transaction (fail + optional retry atomically)
  const processStale = db.transaction((task) => {
    db.prepare(`UPDATE tasks SET status = 'failed', completed_at = datetime('now') WHERE id = ?`)
      .run(task.id);

    db.prepare(`INSERT INTO handoff_log (task_id, from_agent, action) VALUES (?, ?, 'timed-out')`)
      .run(task.id, task.assigned_agent);

    if (task.assigned_agent) {
      db.prepare(`UPDATE agents SET current_load = MAX(0, current_load - 1) WHERE name = ?`)
        .run(task.assigned_agent);
    }

    // Retry if eligible
    if (task.retry_count < task.max_retries) {
      db.prepare(`UPDATE tasks SET status = 'pending', assigned_agent = NULL, claimed_at = NULL, completed_at = NULL, retry_count = retry_count + 1 WHERE id = ?`)
        .run(task.id);

      db.prepare(`INSERT INTO handoff_log (task_id, action) VALUES (?, 'retried')`)
        .run(task.id);

      return { timedOut: true, retried: true };
    }
    return { timedOut: true, retried: false };
  });

  for (const task of stale) {
    const result = processStale(task);
    if (result.timedOut) timedOut++;
    if (result.retried) retried++;
  }

  return { timedOut, retried };
}
