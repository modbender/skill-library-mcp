#!/usr/bin/env node
import { initSchema, getDb } from './lib/db.js';
import { SEED_RULES } from './lib/seed-rules.js';

initSchema();
console.log('✓ Database initialized at data/heath.db');

// Seed global categorization rules (entity_id = NULL)
const db = getDb();
const insert = db.prepare(`
  INSERT OR IGNORE INTO categorization_rules
    (entity_id, counterparty_pattern, counterparty_pattern_normalized, patterns, category, subcategory, confidence, source)
  VALUES (NULL, ?, ?, '[]', ?, ?, ?, 'seed')
`);

let seeded = 0;
const seedTx = db.transaction(() => {
  for (const rule of SEED_RULES) {
    const pattern = rule.counterparty_pattern;
    const normalized = pattern.toLowerCase().replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, ' ').trim();
    const result = insert.run(pattern, normalized, rule.category, rule.subcategory ?? null, rule.confidence);
    if (result.changes > 0) seeded++;
  }
});
seedTx();
console.log(`✓ Seeded ${seeded} global categorization rules (${SEED_RULES.length - seeded} already existed)`);
