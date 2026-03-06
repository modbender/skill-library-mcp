/**
 * @module products
 * Product watchlist CRUD operations.
 */
import { v4 as uuidv4 } from 'uuid';

/**
 * Add a product to the watchlist.
 * @param {import('better-sqlite3').Database} db
 * @param {{ name: string, url: string, target_price?: number, source?: string, currency?: string }} opts
 * @returns {string} Product ID
 */
export function addProduct(db, opts) {
  if (!opts.name) throw new Error('Product name is required');
  if (!opts.url) throw new Error('Product URL is required');
  const id = uuidv4();
  db.prepare(`INSERT INTO products (id, name, url, source, target_price, currency) VALUES (?, ?, ?, ?, ?, ?)`)
    .run(id, opts.name, opts.url, opts.source || 'generic', opts.target_price || null, opts.currency || 'USD');
  return id;
}

/**
 * Get a product by ID.
 * @param {import('better-sqlite3').Database} db
 * @param {string} id
 * @returns {object|undefined}
 */
export function getProduct(db, id) {
  return db.prepare('SELECT * FROM products WHERE id = ?').get(id);
}

/**
 * List products with optional filters.
 * @param {import('better-sqlite3').Database} db
 * @param {{ source?: string, belowTarget?: boolean }} [filters]
 * @returns {object[]}
 */
export function listProducts(db, filters = {}) {
  let sql = 'SELECT * FROM products';
  const params = [];
  const where = [];
  if (filters.source) { where.push('source = ?'); params.push(filters.source); }
  if (filters.belowTarget) { where.push('current_price IS NOT NULL AND target_price IS NOT NULL AND current_price < target_price'); }
  if (where.length) sql += ' WHERE ' + where.join(' AND ');
  sql += ' ORDER BY created_at DESC';
  return db.prepare(sql).all(...params);
}

/**
 * Remove a product from the watchlist.
 * @param {import('better-sqlite3').Database} db
 * @param {string} id
 * @returns {boolean}
 */
export function removeProduct(db, id) {
  return db.prepare('DELETE FROM products WHERE id = ?').run(id).changes > 0;
}

/**
 * Update current price and record in history.
 * @param {import('better-sqlite3').Database} db
 * @param {string} id
 * @param {number} price
 * @param {string} [currency]
 */
export function updateCurrentPrice(db, id, price, currency = 'USD') {
  const update = db.transaction(() => {
    db.prepare('UPDATE products SET current_price = ?, currency = ?, last_checked = datetime(\'now\') WHERE id = ?')
      .run(price, currency, id);
    db.prepare('INSERT INTO price_history (product_id, price, currency) VALUES (?, ?, ?)')
      .run(id, price, currency);
  });
  update();
}

/**
 * Get price history for a product.
 * @param {import('better-sqlite3').Database} db
 * @param {string} productId
 * @param {number} [days=30]
 * @returns {object[]}
 */
export function getPriceHistory(db, productId, days = 30) {
  return db.prepare(`SELECT * FROM price_history WHERE product_id = ? AND timestamp > datetime('now', '-' || ? || ' days') ORDER BY timestamp DESC`)
    .all(productId, days);
}
