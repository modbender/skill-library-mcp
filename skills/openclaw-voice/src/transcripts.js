/**
 * Add a transcript line to a conversation.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} conversationId - The conversation ID.
 * @param {string} speaker - 'user' or 'assistant'.
 * @param {string} text - The text.
 * @param {number} [confidence=1.0] - Confidence score.
 * @throws {Error} If invalid speaker or conversation not found.
 */
export function addTranscriptLine(db, conversationId, speaker, text, confidence = 1.0) {
  if (!['user', 'assistant'].includes(speaker)) {
    throw new Error('Speaker must be "user" or "assistant"');
  }
  const exists = db.prepare('SELECT id FROM conversations WHERE id = ?').get(conversationId);
  if (!exists) {
    throw new Error(`Conversation ${conversationId} not found`);
  }
  const insertStmt = db.prepare('INSERT INTO transcript_lines (conversation_id, speaker, text, confidence) VALUES (?, ?, ?, ?)');
  insertStmt.run(conversationId, speaker, text, confidence);
  if (speaker === 'assistant') {
    const updateStmt = db.prepare('UPDATE conversations SET turn_count = turn_count + 1 WHERE id = ?');
    updateStmt.run(conversationId);
  }
}

/**
 * Show transcript lines for a conversation.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} conversationId - The conversation ID.
 * @returns {Array} Array of transcript lines.
 * @throws {Error} If conversation not found.
 */
export function showTranscript(db, conversationId) {
  const exists = db.prepare('SELECT id FROM conversations WHERE id = ?').get(conversationId);
  if (!exists) {
    throw new Error(`Conversation ${conversationId} not found`);
  }
  const stmt = db.prepare('SELECT * FROM transcript_lines WHERE conversation_id = ? ORDER BY id ASC');
  return stmt.all(conversationId);
}