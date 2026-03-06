import { getDb } from './lib/db.js';
import { normalizeCounterparty } from './lib/normalize.js';

const [,, entityId, counterpartyPattern, category, subcategory] = process.argv;
if (!entityId || !counterpartyPattern || !category) {
  console.error('Usage: add_rule.mjs <entity_id> <counterparty_pattern> <category> [subcategory]');
  process.exit(1);
}

const db = getDb();
const normalized = normalizeCounterparty(counterpartyPattern);
if (!normalized) { console.error('Invalid counterparty pattern'); process.exit(1); }

db.prepare(`
  INSERT INTO categorization_rules (entity_id, counterparty_pattern, counterparty_pattern_normalized, category, subcategory, confidence, source)
  VALUES (?, ?, ?, ?, ?, 1.0, 'human')
  ON CONFLICT DO UPDATE SET category=excluded.category, subcategory=excluded.subcategory, confidence=1.0, source='human', updated_at=datetime('now')
`).run(Number(entityId), counterpartyPattern, normalized, category, subcategory || null);

console.log(`Rule saved: "${counterpartyPattern}" → ${category}${subcategory ? '/' + subcategory : ''} (entity ${entityId})`);
