/**
 * Add a tag to a deal.
 * @param {import('better-sqlite3').Database} db
 * @param {string} dealId
 * @param {string} tag
 * @returns {boolean}
 */
export function addTag(db, dealId, tag) {
  if (!tag || tag.trim() === '') {
    throw new Error('Tag is required');
  }
  const cleanTag = tag.trim();
  const stmt = db.prepare('INSERT OR IGNORE INTO tags (deal_id, tag) VALUES (?, ?)');
  const info = stmt.run(dealId, cleanTag);
  if (info.changes === 0) {
    console.log(`Tag '${cleanTag}' already exists for deal ${dealId}`);
  }
  return true;
}

/**
 * Get tags for a deal.
 * @param {import('better-sqlite3').Database} db
 * @param {string} dealId
 * @returns {Array<string>}
 */
export function getTags(db, dealId) {
  const stmt = db.prepare('SELECT tag FROM tags WHERE deal_id = ? ORDER BY tag');
  return stmt.all(dealId).map(row => row.tag);
}

/**
 * Remove a tag from a deal.
 * @param {import('better-sqlite3').Database} db
 * @param {string} dealId
 * @param {string} tag
 * @returns {boolean}
 * @throws {Error} If tag not found.
 */
export function removeTag(db, dealId, tag) {
  const stmt = db.prepare('DELETE FROM tags WHERE deal_id = ? AND tag = ?');
  const info = stmt.run(dealId, tag.trim());
  if (info.changes === 0) {
    throw new Error(`Tag '${tag}' not found for deal ${dealId}`);
  }
  return true;
}