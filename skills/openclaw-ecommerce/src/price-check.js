// Use built-in fetch
import { extractPrice } from './scraper.js';
import { updateCurrentPrice } from './products.js';
import { addToHistory } from './price-history.js'; // I'll create this later, but for now assume.
import db from './db.js';
import CircuitBreaker from '../../../interchange/src/circuit-breaker.js'; // Adjust path

const dbInstance = db.initDb();

const circuitBreaker = new CircuitBreaker({
  threshold: 5,
  timeout: 300000, // 5 min
  db: dbInstance, // Pass db for persistence
  table: 'circuit_breaker_state'
});

// Assume CircuitBreaker handles persistence via db.

export async function checkPrice(productId, url) {
  import { getProduct, listProducts } from './products.js';
import { createAlert } from './alerts.js';
  if (!product) return null;

  const source = product.source || 'generic';
  const cb = circuitBreaker.get(source);

  try {
    const html = await cb.call(async () => {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.text();
    });

    const priceData = extractPrice(html);
    if (!priceData) throw new Error('No price extracted');

    // Update product
    updateCurrentPrice(productId, priceData.price, priceData.currency);

    // Add to history
    addToHistory(productId, priceData.price, priceData.currency);

    // Check for alerts
    checkAlerts(productId, priceData.price, product.target_price);

    return priceData;
  } catch (error) {
    // Circuit breaker handles state
    console.error(`Price check failed for ${productId}: ${error.message}`);
    return null;
  }
}

export async function checkAllPrices() {
  const products = listProducts();
  const results = [];
  for (const product of products) {
    results.push(await checkPrice(product.id, product.url));
  }
  return results;
}

// Stub for addToHistory
export function addToHistory(productId, price, currency) {
  const stmt = dbInstance.prepare(`
    INSERT INTO price_history (product_id, price, currency, timestamp)
    VALUES (?, ?, ?, datetime('now'))
  `);
  stmt.run(productId, price, currency);
}

// Stub for checkAlerts, will be in alerts.js
export function checkAlerts(productId, currentPrice, targetPrice) {
  if (targetPrice && currentPrice < targetPrice) {
    // Create alert
    createAlert(productId, 'below_target', targetPrice);
  }
  // Price drop logic would need previous price, etc.
}

// Need getProduct and listProducts from products
import { getProduct, listProducts } from './products.js';
import { createAlert } from './alerts.js'; // Forward ref