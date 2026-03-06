/**
 * @module alerts
 * Price alert creation, checking, and acknowledgement.
 */

/**
 * Create a price alert.
 * @param {import('better-sqlite3').Database} db
 * @param {{ product_id: string, type: string, threshold?: number }} opts
 * @returns {number} Alert ID
 */
export function createAlert(db, opts) {
  const result = db.prepare(
    "INSERT INTO alerts (product_id, type, threshold, triggered_at) VALUES (?, ?, ?, datetime('now'))"
  ).run(opts.product_id, opts.type, opts.threshold || null);
  return result.lastInsertRowid;
}

/**
 * List alerts with optional filters.
 * @param {import('better-sqlite3').Database} db
 * @param {{ pending?: boolean, product_id?: string }} [filters]
 * @returns {object[]}
 */
export function listAlerts(db, filters = {}) {
  let sql = 'SELECT a.*, p.name as product_name FROM alerts a LEFT JOIN products p ON a.product_id = p.id';
  const params = [];
  const where = [];
  if (filters.pending) { where.push('a.acknowledged = 0'); }
  if (filters.product_id) { where.push('a.product_id = ?'); params.push(filters.product_id); }
  if (where.length) sql += ' WHERE ' + where.join(' AND ');
  sql += ' ORDER BY a.triggered_at DESC';
  return db.prepare(sql).all(...params);
}

/**
 * Acknowledge an alert.
 * @param {import('better-sqlite3').Database} db
 * @param {number} id
 * @returns {boolean}
 */
export function acknowledgeAlert(db, id) {
  return db.prepare('UPDATE alerts SET acknowledged = 1 WHERE id = ?').run(id).changes > 0;
}

/**
 * Check if price drop below target should trigger an alert.
 * @param {import('better-sqlite3').Database} db
 * @param {string} productId
 * @param {number} currentPrice
 * @param {number} targetPrice
 */
export function checkAlerts(db, productId, currentPrice, targetPrice) {
  if (targetPrice && currentPrice <= targetPrice) {
    // Check no unacknowledged alert of same type exists
    const existing = db.prepare(
      "SELECT id FROM alerts WHERE product_id = ? AND type = 'below_target' AND acknowledged = 0"
    ).get(productId);
    if (!existing) {
      createAlert(db, { product_id: productId, type: 'below_target', threshold: targetPrice });
    }
  }
}
