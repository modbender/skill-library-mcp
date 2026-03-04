/**
 * @module search
 * Search across contacts and deals using LIKE-based queries.
 * Simple and reliable with TEXT UUID primary keys.
 */

/**
 * Search across contacts and deals.
 * @param {import('better-sqlite3').Database} db
 * @param {string} query
 * @returns {Array<{type: string, id: string, title: string, company?: string, email?: string}>}
 */
export function search(db, query) {
  if (!query || query.trim() === '') throw new Error('Search query is required');
  const pattern = `%${query.trim()}%`;
  const results = db.prepare(`
    SELECT 'contact' as type, id, name as title, company, email, created_at
    FROM contacts
    WHERE name LIKE ? OR company LIKE ? OR email LIKE ? OR notes LIKE ?
    UNION ALL
    SELECT 'deal' as type, id, title, NULL as company, NULL as email, created_at
    FROM deals
    WHERE title LIKE ?
    ORDER BY created_at DESC
  `).all(pattern, pattern, pattern, pattern, pattern);
  return results;
}
