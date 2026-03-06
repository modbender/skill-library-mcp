#!/usr/bin/env node
import { initSchema } from './lib/db.js';
import { stripeRequest } from './lib/stripe-client.js';

const entityId = process.argv[2];
const apiKey = process.argv[3];

if (!entityId || !apiKey) {
  console.error('Usage: connect_stripe.mjs <entity_id> <stripe_api_key>');
  process.exit(1);
}

const db = initSchema();

// Verify entity exists
const entity = db.prepare('SELECT id, name FROM entities WHERE id = ?').get(Number(entityId));
if (!entity) {
  console.error(`✗ Entity ${entityId} not found. Create it first via connect_mercury.mjs.`);
  process.exit(1);
}

try {
  // Test connection
  const balance = await stripeRequest(apiKey, '/balance');
  console.log(`✓ Stripe API connection successful`);

  // Check for existing Stripe connection
  const existing = db.prepare('SELECT id FROM connections WHERE entity_id = ? AND provider = ?').get(Number(entityId), 'stripe');
  
  let connectionId;
  if (existing) {
    db.prepare('UPDATE connections SET access_token = ?, updated_at = datetime(\'now\') WHERE id = ?').run(apiKey, existing.id);
    connectionId = existing.id;
    console.log(`  Updated existing Stripe connection (id: ${connectionId})`);
  } else {
    const result = db.prepare('INSERT INTO connections (entity_id, provider, access_token) VALUES (?, ?, ?) RETURNING id').get(Number(entityId), 'stripe', apiKey);
    connectionId = result.id;
    console.log(`  Created new Stripe connection (id: ${connectionId})`);
  }

  console.log(`  Entity: ${entity.name} (id: ${entity.id})`);
  
  // Show available balance
  const available = balance.available || [];
  for (const b of available) {
    console.log(`  Balance: ${(b.amount / 100).toFixed(2)} ${b.currency.toUpperCase()}`);
  }
} catch (err) {
  console.error('✗ Failed to connect:', err.message);
  process.exit(1);
}
