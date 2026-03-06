import { getDb } from './lib/db.js';
import { normalizeCounterparty } from './lib/normalize.js';

const [,, transactionId, category, subcategory] = process.argv;
if (!transactionId || !category) {
  console.error('Usage: set_category.mjs <transaction_id> <category> [subcategory]');
  process.exit(1);
}

const db = getDb();

// Verify transaction exists
const tx = db.prepare('SELECT t.*, a.connection_id FROM transactions t JOIN accounts a ON a.id = t.account_id WHERE t.id = ?').get(transactionId);
if (!tx) { console.error(`Transaction ${transactionId} not found`); process.exit(1); }

// Upsert categorized_transactions
db.prepare(`
  INSERT INTO categorized_transactions (transaction_id, category, subcategory, method, confidence)
  VALUES (?, ?, ?, 'human', 1.0)
  ON CONFLICT(transaction_id) DO UPDATE SET category=excluded.category, subcategory=excluded.subcategory, method='human', confidence=1.0, updated_at=datetime('now')
`).run(transactionId, category, subcategory || null);

// Find entity_id
const conn = db.prepare('SELECT entity_id FROM connections WHERE id = ?').get(tx.connection_id);
const entityId = conn?.entity_id || null;

// Upsert categorization rule if counterparty exists
if (tx.counterparty_name) {
  const normalized = normalizeCounterparty(tx.counterparty_name);
  if (normalized) {
    db.prepare(`
      INSERT INTO categorization_rules (entity_id, counterparty_pattern, counterparty_pattern_normalized, category, subcategory, confidence, source)
      VALUES (?, ?, ?, ?, ?, 1.0, 'human')
      ON CONFLICT DO UPDATE SET category=excluded.category, subcategory=excluded.subcategory, confidence=1.0, source='human', updated_at=datetime('now')
    `).run(entityId, tx.counterparty_name, normalized, category, subcategory || null);
    console.log(`Rule created/updated for "${tx.counterparty_name}" → ${category}${subcategory ? '/' + subcategory : ''}`);
  }
}

console.log(`Transaction ${transactionId} categorized as ${category}${subcategory ? '/' + subcategory : ''}`);
