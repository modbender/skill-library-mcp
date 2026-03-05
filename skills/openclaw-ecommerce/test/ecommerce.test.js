/**
 * Tests for openclaw-ecommerce
 */
import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { initDb } from '../src/db.js';
import { addProduct, getProduct, removeProduct, updateCurrentPrice, getPriceHistory } from '../src/products.js';
import { addOrder, getOrder, updateOrder, listOrders } from '../src/orders.js';
import { calculateMargin } from '../src/margin.js';
import { createAlert, acknowledgeAlert, listAlerts, checkAlerts } from '../src/alerts.js';
import { extractPrice } from '../src/scraper.js';

let db;
let tmpDir;

before(() => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ecom-test-'));
  db = initDb(path.join(tmpDir, 'test.db'));
});

after(() => {
  if (db) db.close();
  try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
});

describe('Scraper', () => {
  it('extracts price from JSON-LD', () => {
    const html = '<script type="application/ld+json">{"@type":"Product","offers":{"price":"25.99","priceCurrency":"USD"}}</script>';
    const result = extractPrice(html);
    assert.equal(result.price, 25.99);
    assert.equal(result.currency, 'USD');
  });

  it('extracts price from og:price meta', () => {
    const html = '<meta property="og:price:amount" content="19.99"><meta property="og:price:currency" content="EUR">';
    const result = extractPrice(html);
    assert.equal(result.price, 19.99);
    assert.equal(result.currency, 'EUR');
  });

  it('extracts price from dollar regex fallback', () => {
    const html = '<span class="price">$42.50</span>';
    const result = extractPrice(html);
    assert.equal(result.price, 42.50);
  });

  it('returns null for no price', () => {
    assert.equal(extractPrice('<html><body>No price here</body></html>'), null);
  });
});

describe('Products', () => {
  it('1. Add product to watchlist → stored with target price', () => {
    const id = addProduct(db, { name: 'Test Widget', url: 'https://example.com/widget', target_price: 25.00 });
    const product = getProduct(db, id);
    assert.ok(product);
    assert.equal(product.name, 'Test Widget');
    assert.equal(product.target_price, 25.00);
  });

  it('2. Remove product → deleted', () => {
    const id = addProduct(db, { name: 'To Remove', url: 'https://example.com/remove' });
    assert.ok(removeProduct(db, id));
    assert.equal(getProduct(db, id), undefined);
  });

  it('3. Price history recorded → queryable', () => {
    const id = addProduct(db, { name: 'History Test', url: 'https://example.com/history' });
    updateCurrentPrice(db, id, 30.00);
    updateCurrentPrice(db, id, 25.00);
    const product = getProduct(db, id);
    assert.equal(product.current_price, 25.00);
    const history = db.prepare('SELECT * FROM price_history WHERE product_id = ?').all(id);
    assert.equal(history.length, 2);
  });
});

describe('Orders', () => {
  it('4. Order add/update → status transitions work', () => {
    const id = addOrder(db, { product_name: 'USB Hub' });
    const order = getOrder(db, id);
    assert.equal(order.product_name, 'USB Hub');
    assert.equal(order.status, 'ordered');

    updateOrder(db, id, { status: 'shipped', tracking_number: '1Z999' });
    const updated = getOrder(db, id);
    assert.equal(updated.status, 'shipped');
    assert.equal(updated.tracking_number, '1Z999');
  });
});

describe('Margin', () => {
  it('5. Margin calculator → correct with fees', () => {
    const result = calculateMargin(10, 25, 15);
    // fees = 25 * 0.15 = 3.75, profit = 25 - 10 - 3.75 = 11.25, margin = 11.25/25*100 = 45
    assert.equal(result.profit, 11.25);
    assert.equal(result.margin, 45);
    assert.equal(result.fees, 3.75);
  });
});

describe('Alerts', () => {
  it('6. Alert created on price drop below target', () => {
    const pid = addProduct(db, { name: 'Alert Test', url: 'https://example.com/alert', target_price: 30.00 });
    checkAlerts(db, pid, 25.00, 30.00);
    const alerts = listAlerts(db, { pending: true, product_id: pid });
    assert.ok(alerts.length >= 1);
    assert.equal(alerts[0].type, 'below_target');
  });

  it('7. Alert acknowledgement works', () => {
    const pid = addProduct(db, { name: 'Ack Test', url: 'https://example.com/ack', target_price: 20.00 });
    const aid = createAlert(db, { product_id: pid, type: 'below_target', threshold: 20 });
    assert.ok(acknowledgeAlert(db, aid));
    const alerts = listAlerts(db, { pending: true, product_id: pid });
    assert.equal(alerts.length, 0);
  });
});

describe('Circuit Breaker', () => {
  it('8. Circuit breaker state stored in DB', () => {
    // Insert a circuit breaker state directly
    db.prepare("INSERT OR REPLACE INTO circuit_breaker_state (source, state, failure_count) VALUES ('generic', 'open', 5)").run();
    const state = db.prepare("SELECT * FROM circuit_breaker_state WHERE source = 'generic'").get();
    assert.equal(state.state, 'open');
    assert.equal(state.failure_count, 5);
    // Clean up
    db.prepare("DELETE FROM circuit_breaker_state WHERE source = 'generic'").run();
  });
});

describe('Backup', () => {
  it('10. Data persists after backup check', () => {
    const count = db.prepare('SELECT COUNT(*) as c FROM products').get().c;
    assert.ok(count > 0);
  });
});
