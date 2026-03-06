/**
 * @module queue
 * Task queue logic: create, list, claim, complete, fail, retry.
 */
import { v4 as uuidv4 } from 'uuid';

/**
 * Create a new task.
 * @param {import('better-sqlite3').Database} db
 * @param {object} opts
 * @param {string} opts.title
 * @param {string} [opts.description]
 * @param {string} [opts.priority]
 * @param {number} [opts.timeout]
 * @param {string[]} [opts.dependsOn]
 * @param {string} [opts.createdBy]
 * @param {number} [opts.maxRetries]
 * @returns {object} The created task
 */
export function createTask(db, opts) {
  const id = `task-${uuidv4().slice(0, 8)}`;
  const { title, description = '', priority = 'medium', timeout = 60, dependsOn = [], createdBy = 'unknown', maxRetries = 3 } = opts;

  db.prepare(`INSERT INTO tasks (id, title, description, priority, timeout_minutes, depends_on, created_by, max_retries)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`)
    .run(id, title, description, priority, timeout, JSON.stringify(dependsOn), createdBy, maxRetries);

  db.prepare(`INSERT INTO handoff_log (task_id, from_agent, action) VALUES (?, ?, 'created')`)
    .run(id, createdBy);

  return getTask(db, id);
}

/**
 * Get a single task by ID.
 * @param {import('better-sqlite3').Database} db
 * @param {string} id
 * @returns {object|null}
 */
export function getTask(db, id) {
  const row = db.prepare('SELECT * FROM tasks WHERE id = ?').get(id);
  if (row) row.depends_on = JSON.parse(row.depends_on);
  return row || null;
}

/**
 * List tasks with optional filters.
 * @param {import('better-sqlite3').Database} db
 * @param {object} [filters]
 * @param {string} [filters.status]
 * @param {string} [filters.agent]
 * @returns {object[]}
 */
export function listTasks(db, filters = {}) {
  let sql = 'SELECT * FROM tasks WHERE 1=1';
  const params = [];
  if (filters.status) { sql += ' AND status = ?'; params.push(filters.status); }
  if (filters.agent) { sql += ' AND assigned_agent = ?'; params.push(filters.agent); }
  sql += ' ORDER BY CASE priority WHEN \'high\' THEN 0 WHEN \'medium\' THEN 1 WHEN \'low\' THEN 2 END, created_at ASC';
  return db.prepare(sql).all(...params).map(r => ({ ...r, depends_on: JSON.parse(r.depends_on) }));
}

/**
 * Claim a task atomically. Returns the task if claimed, null if failed.
 * @param {import('better-sqlite3').Database} db
 * @param {string} taskId
 * @param {string} agentName
 * @returns {object|null}
 */
export function claimTask(db, taskId, agentName) {
  // Wrap everything in a transaction — no stale reads outside
  const doClaim = db.transaction(() => {
    const task = getTask(db, taskId);
    if (!task) throw new Error(`Task ${taskId} not found`);
    if (task.status !== 'pending') return null;

    // Check dependencies inside the transaction
    if (task.depends_on.length > 0) {
      const placeholders = task.depends_on.map(() => '?').join(',');
      const completed = db.prepare(
        `SELECT COUNT(*) as cnt FROM tasks WHERE id IN (${placeholders}) AND status = 'completed'`
      ).get(...task.depends_on);
      if (completed.cnt !== task.depends_on.length) {
        throw new Error(`Task ${taskId} has unmet dependencies`);
      }
    }

    const result = db.prepare(
      `UPDATE tasks SET status = 'claimed', assigned_agent = ?, claimed_at = datetime('now') WHERE id = ? AND status = 'pending'`
    ).run(agentName, taskId);

    if (result.changes === 0) return null;

    db.prepare(`INSERT INTO handoff_log (task_id, to_agent, action) VALUES (?, ?, 'claimed')`)
      .run(taskId, agentName);

    db.prepare(`UPDATE agents SET current_load = current_load + 1 WHERE name = ?`).run(agentName);

    return getTask(db, taskId);
  });

  return doClaim();
}

/**
 * Mark a task as completed.
 * @param {import('better-sqlite3').Database} db
 * @param {string} taskId
 * @param {object} [opts]
 * @param {string} [opts.resultPath]
 * @param {string} [opts.summary]
 * @returns {object}
 */
export function completeTask(db, taskId, opts = {}) {
  const doComplete = db.transaction(() => {
    const task = getTask(db, taskId);
    if (!task) throw new Error(`Task ${taskId} not found`);
    if (task.status !== 'claimed' && task.status !== 'in-progress') {
      throw new Error(`Task ${taskId} is ${task.status}, cannot complete`);
    }

    db.prepare(`UPDATE tasks SET status = 'completed', completed_at = datetime('now') WHERE id = ?`).run(taskId);

    if (opts.resultPath || opts.summary) {
      db.prepare(`INSERT OR REPLACE INTO results (task_id, output_path, summary) VALUES (?, ?, ?)`)
        .run(taskId, opts.resultPath || null, opts.summary || null);
    }

    db.prepare(`INSERT INTO handoff_log (task_id, from_agent, action) VALUES (?, ?, 'completed')`)
      .run(taskId, task.assigned_agent);

    if (task.assigned_agent) {
      db.prepare(`UPDATE agents SET current_load = MAX(0, current_load - 1) WHERE name = ?`).run(task.assigned_agent);
    }

    return getTask(db, taskId);
  });
  return doComplete();
}

/**
 * Mark a task as failed.
 * @param {import('better-sqlite3').Database} db
 * @param {string} taskId
 * @param {string} [reason]
 * @returns {object}
 */
export function failTask(db, taskId, reason) {
  const doFail = db.transaction(() => {
    const task = getTask(db, taskId);
    if (!task) throw new Error(`Task ${taskId} not found`);

    db.prepare(`UPDATE tasks SET status = 'failed', completed_at = datetime('now') WHERE id = ?`).run(taskId);

    // Store reason in handoff_log (from_agent + detail via action text)
    const actionDetail = reason ? `failed: ${reason}` : 'failed';
    db.prepare(`INSERT INTO handoff_log (task_id, from_agent, action) VALUES (?, ?, ?)`)
      .run(taskId, task.assigned_agent, actionDetail);

    if (task.assigned_agent) {
      db.prepare(`UPDATE agents SET current_load = MAX(0, current_load - 1) WHERE name = ?`).run(task.assigned_agent);
    }

    return getTask(db, taskId);
  });
  return doFail();
}

/**
 * Retry a failed task.
 * @param {import('better-sqlite3').Database} db
 * @param {string} taskId
 * @returns {object}
 */
export function retryTask(db, taskId) {
  const task = getTask(db, taskId);
  if (!task) throw new Error(`Task ${taskId} not found`);
  if (task.status !== 'failed') throw new Error(`Task ${taskId} is ${task.status}, cannot retry`);
  if (task.retry_count >= task.max_retries) throw new Error(`Task ${taskId} has exhausted retries (${task.retry_count}/${task.max_retries})`);

  db.prepare(`UPDATE tasks SET status = 'pending', assigned_agent = NULL, claimed_at = NULL, completed_at = NULL, retry_count = retry_count + 1 WHERE id = ?`)
    .run(taskId);

  db.prepare(`INSERT INTO handoff_log (task_id, action) VALUES (?, 'retried')`)
    .run(taskId);

  return getTask(db, taskId);
}
