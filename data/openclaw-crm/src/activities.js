import { getDeal } from './deals.js'; // for validation if needed

const validTypes = ['call', 'email', 'meeting', 'note'];

/**
 * Add an activity to a deal.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {Object} data - {deal_id (required), type (required), content (required)}
 * @returns {number} The generated activity ID.
 * @throws {Error} If deal_id invalid, type invalid, or content missing.
 */
export function addActivity(db, data) {
  if (!data.deal_id) {
    throw new Error('Deal ID is required');
  }
  if (!validTypes.includes(data.type)) {
    throw new Error(`Invalid type: ${data.type}. Must be one of ${validTypes.join(', ')}`);
  }
  if (!data.content || data.content.trim() === '') {
    throw new Error('Content is required');
  }
  // Optional: check if deal exists
  // const deal = getDeal(db, data.deal_id);
  // if (!deal) throw new Error(`Deal not found: ${data.deal_id}`);
  const stmt = db.prepare(
    'INSERT INTO activities (deal_id, type, content) VALUES (?, ?, ?)'
  );
  const info = stmt.run(data.deal_id, data.type, data.content.trim());
  return info.lastInsertRowid;
}

/**
 * List activities for a deal.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} deal_id - The deal ID.
 * @returns {Array<Object>} Array of activity objects.
 */
export function listActivities(db, deal_id) {
  const stmt = db.prepare(
    'SELECT * FROM activities WHERE deal_id = ? ORDER BY timestamp DESC'
  );
  return stmt.all(deal_id);
}

/**
 * Get a single activity by ID.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {number} id - The activity ID.
 * @returns {Object|null} The activity object or null.
 */
export function getActivity(db, id) {
  const stmt = db.prepare('SELECT * FROM activities WHERE id = ?');
  return stmt.get(id);
}