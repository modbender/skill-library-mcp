import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import db from './db.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dbPath = path.join(__dirname, '../data/ecommerce.db');

export function backup(outputPath = null) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const defaultPath = path.join(__dirname, `../data/backup-${timestamp}.json`);
  const pathToUse = outputPath || defaultPath;

  // Backup to JSON for portability
  const products = db.initDb().prepare('SELECT * FROM products').all();
  const history = db.initDb().prepare('SELECT * FROM price_history').all();
  const orders = db.initDb().prepare('SELECT * FROM orders').all();
  const alerts = db.initDb().prepare('SELECT * FROM alerts').all();
  const breakers = db.initDb().prepare('SELECT * FROM circuit_breaker_state').all();

  const backupData = { products, history, orders, alerts, breakers, timestamp };

  fs.writeFileSync(pathToUse, JSON.stringify(backupData, null, 2));
  return pathToUse;
}

export function restore(backupFile) {
  if (!fs.existsSync(backupFile)) {
    throw new Error('Backup file not found');
  }

  const data = JSON.parse(fs.readFileSync(backupFile, 'utf8'));
  const dbInstance = db.initDb();

  // Clear tables
  dbInstance.exec('DELETE FROM products; DELETE FROM price_history; DELETE FROM orders; DELETE FROM alerts; DELETE FROM circuit_breaker_state;');

  // Restore
  const insertProduct = dbInstance.prepare(`
    INSERT INTO products (id, name, url, source, target_price, current_price, currency, last_checked, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  for (const p of data.products) {
    insertProduct.run(p.id, p.name, p.url, p.source, p.target_price, p.current_price, p.currency, p.last_checked, p.created_at);
  }

  const insertHistory = dbInstance.prepare(`
    INSERT INTO price_history (id, product_id, price, currency, timestamp)
    VALUES (?, ?, ?, ?, ?)
  `);
  for (const h of data.history) {
    insertHistory.run(h.id, h.product_id, h.price, h.currency, h.timestamp);
  }

  const insertOrder = dbInstance.prepare(`
    INSERT INTO orders (id, product_name, status, tracking_number, carrier, shipped_date, eta, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  for (const o of data.orders) {
    insertOrder.run(o.id, o.product_name, o.status, o.tracking_number, o.carrier, o.shipped_date, o.eta, o.notes, o.created_at);
  }

  const insertAlert = dbInstance.prepare(`
    INSERT INTO alerts (id, product_id, type, threshold, triggered_at, acknowledged)
    VALUES (?, ?, ?, ?, ?, ?)
  `);
  for (const a of data.alerts) {
    insertAlert.run(a.id, a.product_id, a.type, a.threshold, a.triggered_at, a.acknowledged);
  }

  const insertBreaker = dbInstance.prepare(`
    INSERT OR REPLACE INTO circuit_breaker_state (source, state, failure_count, last_failure, cooldown_until)
    VALUES (?, ?, ?, ?, ?)
  `);
  for (const b of data.breakers) {
    insertBreaker.run(b.source, b.state, b.failure_count, b.last_failure, b.cooldown_until);
  }

  console.log('Restore complete');
}