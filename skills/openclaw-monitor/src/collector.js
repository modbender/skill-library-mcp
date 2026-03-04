/**
 * @module collector
 * Ingest functions for token events, task events, and cron runs.
 * All inserts use INSERT OR IGNORE for idempotency via event_id.
 */

import crypto from 'node:crypto';

/**
 * Generate a unique event ID.
 * @returns {string}
 */
export function generateEventId() {
  return crypto.randomUUID();
}

/**
 * Add a token usage event.
 * @param {import('better-sqlite3').Database} db
 * @param {{ model: string, tokens_in: number, tokens_out: number, cost: number, skill?: string, event_source?: string, event_id?: string, timestamp?: string }} event
 * @returns {{ inserted: boolean, event_id: string }}
 */
export function addTokenEvent(db, event) {
  if (event.tokens_in < 0 || event.tokens_out < 0) throw new Error('Tokens must be non-negative');
  if (event.cost < 0) throw new Error('Cost must be non-negative');
  if (!event.model) throw new Error('Model is required');
  const eventId = event.event_id || generateEventId();
  const stmt = db.prepare(`
    INSERT OR IGNORE INTO token_events (model, tokens_in, tokens_out, cost, skill, event_source, event_id, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE(?, datetime('now')))
  `);
  const result = stmt.run(
    event.model, event.tokens_in, event.tokens_out, event.cost,
    event.skill || null, event.event_source || 'manual', eventId, event.timestamp || null
  );
  return { inserted: result.changes > 0, event_id: eventId };
}

/**
 * Add a task event.
 * @param {import('better-sqlite3').Database} db
 * @param {{ command: string, status: 'success'|'failure'|'timeout', duration_ms: number, error?: string, event_id?: string, timestamp?: string }} event
 * @returns {{ inserted: boolean, event_id: string }}
 */
const VALID_TASK_STATUSES = new Set(['success', 'failure', 'timeout']);
const VALID_CRON_STATUSES = new Set(['success', 'failure']);

export function addTaskEvent(db, event) {
  if (!VALID_TASK_STATUSES.has(event.status)) throw new Error(`Invalid task status: ${event.status}. Must be one of: ${[...VALID_TASK_STATUSES].join(', ')}`);
  if (event.duration_ms < 0) throw new Error('Duration must be non-negative');
  const eventId = event.event_id || generateEventId();
  const stmt = db.prepare(`
    INSERT OR IGNORE INTO task_events (command, status, duration_ms, error, event_id, timestamp)
    VALUES (?, ?, ?, ?, ?, COALESCE(?, datetime('now')))
  `);
  const result = stmt.run(
    event.command, event.status, event.duration_ms, event.error || null, eventId, event.timestamp || null
  );
  return { inserted: result.changes > 0, event_id: eventId };
}

/**
 * Add a cron run event.
 * @param {import('better-sqlite3').Database} db
 * @param {{ job_name: string, status: 'success'|'failure', duration_ms: number, error?: string, event_id?: string, started?: string }} event
 * @returns {{ inserted: boolean, event_id: string }}
 */
export function addCronRun(db, event) {
  if (!VALID_CRON_STATUSES.has(event.status)) throw new Error(`Invalid cron status: ${event.status}. Must be one of: ${[...VALID_CRON_STATUSES].join(', ')}`);
  if (event.duration_ms < 0) throw new Error('Duration must be non-negative');
  const eventId = event.event_id || generateEventId();
  const stmt = db.prepare(`
    INSERT OR IGNORE INTO cron_runs (job_name, status, duration_ms, error, event_id, started)
    VALUES (?, ?, ?, ?, ?, COALESCE(?, datetime('now')))
  `);
  const result = stmt.run(
    event.job_name, event.status, event.duration_ms, event.error || null, eventId, event.started || null
  );
  return { inserted: result.changes > 0, event_id: eventId };
}
