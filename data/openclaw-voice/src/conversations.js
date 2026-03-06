import { v4 as uuidv4 } from 'uuid';

/**
 * Start a new conversation.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string|null} [summary=null] - Optional summary.
 * @returns {string} The conversation ID.
 */
export function startConversation(db, summary = null) {
  const id = uuidv4();
  const stmt = db.prepare('INSERT INTO conversations (id, summary) VALUES (?, ?)');
  stmt.run(id, summary);
  return id;
}

/**
 * End a conversation.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} id - The conversation ID.
 * @param {string|null} [summary=null] - Optional new summary.
 * @throws {Error} If conversation not found.
 */
export function endConversation(db, id, summary = null) {
  const exists = db.prepare('SELECT id FROM conversations WHERE id = ?').get(id);
  if (!exists) {
    throw new Error(`Conversation ${id} not found`);
  }
  let sql = "UPDATE conversations SET ended = datetime('now') WHERE id = ?";
  let params = [id];
  if (summary !== null) {
    sql = "UPDATE conversations SET ended = datetime('now'), summary = ? WHERE id = ?";
    params = [summary, id];
  }
  db.prepare(sql).run(...params);
}

/**
 * List conversations.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {Object} [options={}] - Options.
 * @param {boolean} [options.today=false] - Filter by today.
 * @param {string|null} [options.search=null] - Search in transcripts.
 * @param {number} [options.limit=10] - Limit results.
 * @returns {Array} Array of conversation objects.
 */
export function listConversations(db, options = {}) {
  const { today = false, search = null, limit = 10 } = options;
  let sql = 'SELECT c.* FROM conversations c';
  let whereClauses = [];
  let params = [];
  if (search) {
    sql += ' JOIN transcript_lines t ON c.id = t.conversation_id';
    whereClauses.push('t.text LIKE ?');
    params.push(`%${search}%`);
  }
  if (today) {
    whereClauses.push("c.started >= date('now')");
  }
  if (whereClauses.length > 0) {
    sql += ' WHERE ' + whereClauses.join(' AND ');
  }
  sql += ' ORDER BY c.started DESC LIMIT ?';
  params.push(limit);
  const stmt = db.prepare(sql);
  return stmt.all(...params);
}