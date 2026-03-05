/**
 * Add a follow-up for a deal.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {Object} data - {deal_id (required), due_date (required, YYYY-MM-DD), note?}
 * @returns {number} The generated follow-up ID.
 * @throws {Error} If deal_id or due_date missing.
 */
export function addFollowup(db, data) {
  if (!data.deal_id) {
    throw new Error('Deal ID is required');
  }
  if (!data.due_date) {
    throw new Error('Due date is required');
  }
  // Optional: validate date format, but assume valid
  const stmt = db.prepare(
    'INSERT INTO follow_ups (deal_id, due_date, note, completed) VALUES (?, ?, ?, 0)'
  );
  const info = stmt.run(data.deal_id, data.due_date, data.note || null);
  return info.lastInsertRowid;
}

/**
 * List due follow-ups (incomplete and due within specified days).
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {number} [days=0] - Days from now to consider due.
 * @returns {Array<Object>} Array of follow-up objects with deal and contact info.
 */
export function listDueFollowups(db, days = 0) {
  const cutoff = `datetime('now', '+${days} days')`;
  const sql = `
    SELECT f.*, d.title as deal_title, c.name as contact_name, c.company as contact_company
    FROM follow_ups f
    JOIN deals d ON f.deal_id = d.id
    LEFT JOIN contacts c ON d.contact_id = c.id
    WHERE f.completed = 0 AND f.due_date <= ${cutoff}
    ORDER BY f.due_date ASC
  `;
  const stmt = db.prepare(sql);
  return stmt.all();
}

/**
 * Complete a follow-up.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {number} id - The follow-up ID.
 * @returns {boolean} True if completed.
 * @throws {Error} If follow-up not found.
 */
export function completeFollowup(db, id) {
  const now = new Date().toISOString();
  const stmt = db.prepare(
    'UPDATE follow_ups SET completed = 1, completed_at = ? WHERE id = ?'
  );
  const info = stmt.run(now, id);
  if (info.changes === 0) {
    throw new Error(`Follow-up not found: ${id}`);
  }
  return true;
}

/**
 * Get a single follow-up by ID.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {number} id - The follow-up ID.
 * @returns {Object|null} The follow-up object or null.
 */
export function getFollowup(db, id) {
  const stmt = db.prepare('SELECT * FROM follow_ups WHERE id = ?');
  return stmt.get(id);
}