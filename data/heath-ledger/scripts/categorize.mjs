#!/usr/bin/env node
/**
 * Categorize transactions using rules first, then outputs uncategorized ones
 * as a JSON prompt for the host agent to process with AI.
 *
 * Usage: categorize.mjs <entity_id> [max_transactions]
 *
 * For AI categorization, pipe the output JSON to your AI model and feed results back
 * via set_category.mjs or by running categorize_ai_results.mjs with the JSON response.
 */
import { initSchema } from './lib/db.js';
import { normalizeCounterparty } from './lib/normalize.js';
import { CHART_OF_ACCOUNTS } from './lib/chart-of-accounts.js';

const entityId = process.argv[2];
const maxTx = parseInt(process.argv[3] || '5000', 10);

if (!entityId) {
  console.error('Usage: categorize.mjs <entity_id> [max_transactions]');
  process.exit(1);
}

const db = initSchema();
const MIN_PATTERN_LENGTH = 3;

// Load connections -> accounts -> transactions
const connections = db.prepare('SELECT id FROM connections WHERE entity_id = ?').all(entityId);
const connectionIds = connections.map(c => c.id);
if (connectionIds.length === 0) { console.error('✗ No connections for entity', entityId); process.exit(1); }

const cph = connectionIds.map(() => '?').join(',');
const accounts = db.prepare(`SELECT id FROM accounts WHERE connection_id IN (${cph})`).all(...connectionIds);
const accountIds = accounts.map(a => a.id);
if (accountIds.length === 0) { console.error('✗ No accounts found'); process.exit(1); }

const aph = accountIds.map(() => '?').join(',');
const transactions = db.prepare(`
  SELECT id, account_id, posted_at, amount, counterparty_name, counterparty_normalized, bank_description
  FROM transactions WHERE account_id IN (${aph})
  ORDER BY posted_at DESC LIMIT ?
`).all(...accountIds, maxTx);

if (transactions.length === 0) { console.error('✗ No transactions found'); process.exit(1); }

// Already categorized
const txIds = transactions.map(t => t.id);
const catExisting = db.prepare(`SELECT transaction_id FROM categorized_transactions WHERE transaction_id IN (${txIds.map(() => '?').join(',')})`).all(...txIds);
const categorizedSet = new Set(catExisting.map(r => r.transaction_id));

// Load rules
const rules = db.prepare('SELECT * FROM categorization_rules WHERE entity_id = ? OR entity_id IS NULL').all(entityId);

const entityRules = [];
const globalRules = [];
const humanEntityPatternSet = new Set();
const entityRuleByPattern = new Map();

for (const rule of rules) {
  const basePattern = rule.counterparty_pattern_normalized || normalizeCounterparty(rule.counterparty_pattern);
  let patterns = [];
  try { patterns = JSON.parse(rule.patterns || '[]'); } catch {}
  const normalizedPatterns = [basePattern, ...patterns]
    .map(p => normalizeCounterparty(p))
    .filter(p => p && p.length >= MIN_PATTERN_LENGTH);

  const nr = { ...rule, normalizedPatterns, normalizedBase: basePattern };
  if (rule.entity_id) {
    entityRules.push(nr);
    if (rule.source === 'human' && basePattern) humanEntityPatternSet.add(basePattern);
    if (basePattern) entityRuleByPattern.set(basePattern, rule);
  } else {
    globalRules.push(nr);
  }
}

const pickMatch = (rulesToCheck, norm) => {
  let best = null;
  let bestMatchLen = 0;
  for (const rule of rulesToCheck) {
    const matched = rule.normalizedPatterns.find(p => norm === p || norm.includes(p));
    if (matched) {
      // Prefer longer pattern matches (more specific)
      const matchLen = matched.length;
      if (!best || matchLen > bestMatchLen) {
        best = rule;
        bestMatchLen = matchLen;
      } else if (matchLen === bestMatchLen) {
        // If same length, prefer higher confidence/usage
        const bestScore = (best.confidence || 0) + (best.usage_count || 0) / 1000;
        const nextScore = (rule.confidence || 0) + (rule.usage_count || 0) / 1000;
        if (nextScore > bestScore) best = rule;
      }
    }
  }
  return best;
};

const upsertCat = db.prepare(`
  INSERT INTO categorized_transactions (transaction_id, category, subcategory, method, confidence, notes)
  VALUES (?, ?, ?, ?, ?, ?)
  ON CONFLICT(transaction_id) DO UPDATE SET category=excluded.category, subcategory=excluded.subcategory,
    method=excluded.method, confidence=excluded.confidence, notes=excluded.notes, updated_at=datetime('now')
`);

const updateRuleUsage = db.prepare('UPDATE categorization_rules SET usage_count = usage_count + 1 WHERE id = ?');

let ruleMatched = 0;
const ambiguous = [];
const needsAi = [];

for (const tx of transactions) {
  if (categorizedSet.has(tx.id)) continue;
  const norm = tx.counterparty_normalized || normalizeCounterparty(tx.counterparty_name);
  if (!norm) {
    ambiguous.push({ id: tx.id, counterparty: tx.counterparty_name, amount: tx.amount, description: tx.bank_description });
    continue;
  }

  const entityMatch = pickMatch(entityRules, norm);
  const globalMatch = entityMatch ? null : pickMatch(globalRules, norm);
  const match = entityMatch || globalMatch;

  if (match) {
    let category = match.category;
    // Special case: Stripe debits are fees (COGS), not revenue
    if (norm === 'stripe' && tx.amount < 0) {
      category = 'Stripe Fees';
    }
    const confidence = match.source === 'human' && match.entity_id ? 1.0 : (match.confidence || 0.9);
    upsertCat.run(tx.id, category, match.subcategory || null, 'rule', confidence, match.entity_id ? 'entity_rule' : 'global_rule');
    if (match.id) updateRuleUsage.run(match.id);
    ruleMatched++;
  } else {
    needsAi.push({
      transaction_id: String(tx.id),
      counterparty_name: tx.counterparty_name,
      bank_description: tx.bank_description,
      amount: tx.amount,
      type: tx.amount < 0 ? 'debit' : 'credit',
    });
  }
}

console.error(`✓ Rule-matched: ${ruleMatched}`);
console.error(`  Needs AI: ${needsAi.length}`);
console.error(`  Ambiguous (no counterparty): ${ambiguous.length}`);

if (needsAi.length > 0) {
  // Output AI categorization prompt as JSON to stdout
  const prompt = {
    action: 'categorize_transactions',
    instructions: `Categorize each transaction into one of these categories: ${CHART_OF_ACCOUNTS.join(', ')}. Return JSON array with objects: { transaction_id, category, subcategory, confidence (0-1) }`,
    chart_of_accounts: CHART_OF_ACCOUNTS,
    transactions: needsAi,
  };
  console.log(JSON.stringify(prompt, null, 2));
} else {
  console.error('✓ All transactions categorized by rules');
}

if (ambiguous.length > 0) {
  console.error('\nAmbiguous transactions (need manual review):');
  for (const a of ambiguous) {
    console.error(`  tx:${a.id} — $${Math.abs(a.amount).toFixed(2)} to "${a.counterparty || 'Unknown'}" — ${a.description || 'no description'}`);
  }
}
