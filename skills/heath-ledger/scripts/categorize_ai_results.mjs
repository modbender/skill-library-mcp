#!/usr/bin/env node
/**
 * Apply AI categorization results. Reads JSON from stdin or file argument.
 * Expected format: array of { transaction_id, category, subcategory, confidence }
 *
 * Usage: echo '[...]' | categorize_ai_results.mjs <entity_id>
 *    or: categorize_ai_results.mjs <entity_id> <results_file.json>
 */
import { readFileSync } from 'fs';
import { initSchema } from './lib/db.js';
import { normalizeCounterparty } from './lib/normalize.js';
import { CHART_OF_ACCOUNTS } from './lib/chart-of-accounts.js';

const entityId = process.argv[2];
const filePath = process.argv[3];

if (!entityId) {
  console.error('Usage: categorize_ai_results.mjs <entity_id> [results_file.json]');
  process.exit(1);
}

let input;
if (filePath) {
  input = readFileSync(filePath, 'utf-8');
} else {
  input = readFileSync('/dev/stdin', 'utf-8');
}

const results = JSON.parse(input);
if (!Array.isArray(results)) { console.error('Expected JSON array'); process.exit(1); }

const db = initSchema();
const allowedCategories = new Set(CHART_OF_ACCOUNTS);
const CONFIDENCE_THRESHOLD = 0.85;

const upsertCat = db.prepare(`
  INSERT INTO categorized_transactions (transaction_id, category, subcategory, method, confidence, notes)
  VALUES (?, ?, ?, ?, ?, ?)
  ON CONFLICT(transaction_id) DO UPDATE SET category=excluded.category, subcategory=excluded.subcategory,
    method=excluded.method, confidence=excluded.confidence, notes=excluded.notes, updated_at=datetime('now')
`);

// Partial unique index requires manual check-then-insert
const findRule = db.prepare('SELECT id FROM categorization_rules WHERE entity_id = ? AND counterparty_pattern_normalized = ?');
const insertRule = db.prepare(`
  INSERT INTO categorization_rules (entity_id, counterparty_pattern, counterparty_pattern_normalized, category, subcategory, confidence, source, usage_count)
  VALUES (?, ?, ?, ?, ?, ?, 'ai', 1)
`);
const updateRule = db.prepare(`
  UPDATE categorization_rules SET usage_count = usage_count + 1, confidence = MAX(confidence, ?),
    category = ?, subcategory = ?, updated_at = datetime('now') WHERE id = ?
`);

let categorized = 0, ambiguous = 0, invalid = 0;

for (const r of results) {
  const txId = parseInt(r.transaction_id, 10);
  if (!allowedCategories.has(r.category)) { invalid++; continue; }

  if (r.confidence >= CONFIDENCE_THRESHOLD) {
    upsertCat.run(txId, r.category, r.subcategory || null, 'ai', r.confidence, 'ai_inference');
    categorized++;

    // Create/update rule for future matching
    const tx = db.prepare('SELECT counterparty_name, counterparty_normalized FROM transactions WHERE id = ?').get(txId);
    if (tx) {
      const norm = tx.counterparty_normalized || normalizeCounterparty(tx.counterparty_name);
      if (norm) {
        const existing = findRule.get(entityId, norm);
        if (existing) {
          updateRule.run(r.confidence, r.category, r.subcategory || null, existing.id);
        } else {
          insertRule.run(entityId, tx.counterparty_name || norm, norm, r.category, r.subcategory || null, r.confidence);
        }
      }
    }
  } else {
    ambiguous++;
    const tx = db.prepare('SELECT counterparty_name, amount FROM transactions WHERE id = ?').get(txId);
    console.error(`  Low confidence (${(r.confidence*100).toFixed(0)}%): tx:${txId} $${Math.abs(tx?.amount||0).toFixed(2)} "${tx?.counterparty_name}" → ${r.category}`);
  }
}

console.error(`✓ Applied: ${categorized} categorized, ${ambiguous} low-confidence, ${invalid} invalid category`);
