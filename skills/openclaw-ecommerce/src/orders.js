/**
 * @module orders
 * Order tracking CRUD operations.
 */
import { v4 as uuidv4 } from 'uuid';

/**
 * Add an order.
 * @param {import('better-sqlite3').Database} db
 * @param {{ product_name: string, tracking_number?: string, carrier?: string }} opts
 * @returns {string} Order ID
 */
export function addOrder(db, opts) {
  if (!opts.product_name) throw new Error('Product name is required');
  const id = uuidv4();
  db.prepare('INSERT INTO orders (id, product_name, tracking_number, carrier) VALUES (?, ?, ?, ?)')
    .run(id, opts.product_name, opts.tracking_number || null, opts.carrier || null);
  return id;
}

/**
 * Get an order by ID.
 * @param {import('better-sqlite3').Database} db
 * @param {string} id
 * @returns {object|undefined}
 */
export function getOrder(db, id) {
  return db.prepare('SELECT * FROM orders WHERE id = ?').get(id);
}

/**
 * List orders with optional status filter.
 * @param {import('better-sqlite3').Database} db
 * @param {{ status?: string }} [filters]
 * @returns {object[]}
 */
export function listOrders(db, filters = {}) {
  let sql = 'SELECT * FROM orders';
  const params = [];
  if (filters.status) { sql += ' WHERE status = ?'; params.push(filters.status); }
  sql += ' ORDER BY created_at DESC';
  return db.prepare(sql).all(...params);
}

/**
 * Update an order's fields.
 * @param {import('better-sqlite3').Database} db
 * @param {string} id
 * @param {{ status?: string, tracking_number?: string, carrier?: string, shipped_date?: string, eta?: string }} updates
 * @returns {boolean}
 */
export function updateOrder(db, id, updates) {
  const allowed = ['status', 'tracking_number', 'carrier', 'shipped_date', 'eta', 'notes'];
  const fields = [];
  const values = [];
  for (const [key, value] of Object.entries(updates)) {
    if (allowed.includes(key)) { fields.push(`${key} = ?`); values.push(value); }
  }
  if (fields.length === 0) return false;
  values.push(id);
  return db.prepare(`UPDATE orders SET ${fields.join(', ')} WHERE id = ?`).run(...values).changes > 0;
}
