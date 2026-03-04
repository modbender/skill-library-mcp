import { v4 as uuidv4 } from 'uuid';
import { getContact } from './contacts.js'; // for validation

const validStages = ['prospect', 'qualified', 'proposal', 'negotiation', 'closed-won', 'closed-lost'];

/**
 * Add a new deal.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {Object} data - Deal data: {title (required), contact_id, value (default 0), stage (default 'prospect'), source}
 * @returns {string} The generated deal ID.
 * @throws {Error} If title missing or invalid contact_id.
 */
export function addDeal(db, data) {
  if (!data.title) {
    throw new Error('Deal title is required');
  }
  if (data.contact_id) {
    const contact = getContact(db, data.contact_id);
    if (!contact) {
      throw new Error(`Contact not found: ${data.contact_id}`);
    }
  }
  const id = uuidv4();
  const now = new Date().toISOString();
  const defaults = { value: 0, stage: 'prospect', created_at: now, updated_at: now };
  const insertData = { ...defaults, ...data, id };
  const stmt = db.prepare(
    'INSERT INTO deals (id, contact_id, title, value, stage, source, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
  );
  const tx = db.transaction(() => {
    stmt.run(
      insertData.id,
      insertData.contact_id || null,
      insertData.title,
      insertData.value,
      insertData.stage,
      insertData.source || null,
      insertData.created_at,
      insertData.updated_at
    );
  });
  tx();
  return id;
}

/**
 * List deals, filtered by stage and/or tag.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {Object} filters - {stage?: string, tag?: string}
 * @returns {Array<Object>} Array of deal objects.
 */
export function listDeals(db, filters = {}) {
  let sql = 'SELECT * FROM deals d';
  let params = [];
  let where = [];
  if (filters.stage) {
    where.push('d.stage = ?');
    params.push(filters.stage);
  }
  if (filters.tag) {
    where.push('EXISTS (SELECT 1 FROM tags t WHERE t.deal_id = d.id AND t.tag = ?)');
    params.push(filters.tag);
  }
  if (where.length > 0) {
    sql += ' WHERE ' + where.join(' AND ');
  }
  sql += ' ORDER BY d.updated_at DESC NULLS LAST, d.created_at DESC';
  const stmt = db.prepare(sql);
  return stmt.all(...params);
}

/**
 * Update deal stage.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} id - The deal ID.
 * @param {string} stage - New stage.
 * @returns {boolean} True if updated.
 * @throws {Error} If deal not found or invalid stage.
 */
export function updateStage(db, id, stage) {
  if (!validStages.includes(stage)) {
    throw new Error(`Invalid stage: ${stage}. Must be one of ${validStages.join(', ')}`);
  }
  const now = new Date().toISOString();
  const updateStmt = db.prepare('UPDATE deals SET stage = ?, updated_at = ? WHERE id = ?');
  const closeStmt = db.prepare("UPDATE deals SET closed_at = ? WHERE id = ? AND stage LIKE 'closed-%' AND closed_at IS NULL");
  const tx = db.transaction(() => {
    const info = updateStmt.run(stage, now, id);
    if (info.changes === 0) {
      throw new Error(`Deal not found: ${id}`);
    }
    if (stage.startsWith('closed-')) {
      closeStmt.run(now, id);
    }
  });
  tx();
  return true;
}

/**
 * Get a single deal by ID, including contact if linked.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} id - The deal ID.
 * @returns {Object|null} The deal object with contact joined or null.
 */
export function getDeal(db, id) {
  const stmt = db.prepare(`
    SELECT d.*, c.name as contact_name, c.company, c.email, c.phone, c.notes
    FROM deals d
    LEFT JOIN contacts c ON d.contact_id = c.id
    WHERE d.id = ?
  `);
  return stmt.get(id);
}