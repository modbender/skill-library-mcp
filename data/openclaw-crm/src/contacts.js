import { v4 as uuidv4 } from 'uuid';

/**
 * Add a new contact.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {Object} data - Contact data: {name (required), company, email, phone, notes}
 * @returns {string} The generated contact ID.
 * @throws {Error} If name is missing.
 */
export function addContact(db, data) {
  if (!data.name) {
    throw new Error('Contact name is required');
  }
  const id = uuidv4();
  const stmt = db.prepare(
    'INSERT INTO contacts (id, name, company, email, phone, notes) VALUES (?, ?, ?, ?, ?, ?)'
  );
  const tx = db.transaction(() => {
    stmt.run(id, data.name, data.company || null, data.email || null, data.phone || null, data.notes || null);
  });
  tx();
  return id;
}

/**
 * List contacts, optionally filtered by search query using FTS.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} [search] - Search query for full-text search.
 * @returns {Array<Object>} Array of contact objects.
 */
export function listContacts(db, search = null) {
  let query, params = [];
  if (search) {
    const pattern = `%${search}%`;
    query = `SELECT * FROM contacts WHERE name LIKE ? OR company LIKE ? OR email LIKE ? ORDER BY created_at DESC`;
    params = [pattern, pattern, pattern];
  } else {
    query = 'SELECT * FROM contacts ORDER BY created_at DESC';
  }
  const stmt = db.prepare(query);
  return stmt.all(...params);
}

/**
 * Edit an existing contact.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} id - The contact ID.
 * @param {Object} updates - Fields to update: {company, email, phone, notes}
 * @returns {boolean} True if updated.
 * @throws {Error} If contact not found or no updates.
 */
export function editContact(db, id, updates) {
  const fields = Object.keys(updates).filter(key => updates[key] !== undefined);
  if (fields.length === 0) {
    throw new Error('No fields to update');
  }
  const setParts = fields.map(field => `${field} = ?`);
  const setClause = setParts.join(', ');
  const values = fields.map(field => updates[field]);
  const stmt = db.prepare(`UPDATE contacts SET ${setClause} WHERE id = ?`);
  const info = stmt.run(...values, id);
  if (info.changes === 0) {
    throw new Error(`Contact not found: ${id}`);
  }
  return true;
}

/**
 * Get a single contact by ID.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} id - The contact ID.
 * @returns {Object|null} The contact object or null if not found.
 */
export function getContact(db, id) {
  const stmt = db.prepare('SELECT * FROM contacts WHERE id = ?');
  return stmt.get(id);
}