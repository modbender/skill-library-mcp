/**
 * Categorization Engine
 * 
 * Handles automatic categorization with:
 * - Global rules (entity_id = NULL) that apply across all entities
 * - Entity-specific rules that override global rules
 * - Confidence scoring based on confirmation/override history
 * - Rule promotion from entity-specific to global when patterns are consistent
 */

import { getDb } from './db.js';
import { normalizeCounterparty } from './normalize.js';

/**
 * Ensure the categorization schema supports the enhanced rule system
 */
export function initCategorizationSchema(db) {
  // Add columns for enhanced tracking if they don't exist
  const columns = db.prepare("PRAGMA table_info(categorization_rules)").all();
  const columnNames = columns.map(c => c.name);
  
  if (!columnNames.includes('confirmed_count')) {
    db.exec(`ALTER TABLE categorization_rules ADD COLUMN confirmed_count INTEGER DEFAULT 0`);
  }
  if (!columnNames.includes('overridden_count')) {
    db.exec(`ALTER TABLE categorization_rules ADD COLUMN overridden_count INTEGER DEFAULT 0`);
  }
  if (!columnNames.includes('last_confirmed_at')) {
    db.exec(`ALTER TABLE categorization_rules ADD COLUMN last_confirmed_at TEXT`);
  }
  if (!columnNames.includes('promoted_from_entity_id')) {
    db.exec(`ALTER TABLE categorization_rules ADD COLUMN promoted_from_entity_id INTEGER`);
  }
  
  // Create index for efficient global rule lookup
  db.exec(`
    CREATE INDEX IF NOT EXISTS idx_rules_global 
    ON categorization_rules(counterparty_pattern_normalized) 
    WHERE entity_id IS NULL
  `);
}

/**
 * Find the best matching rule for a counterparty
 * Priority: Entity-specific > Global
 * Within same scope: Higher confidence > Lower confidence
 */
export function findMatchingRule(db, entityId, counterpartyName) {
  const normalized = normalizeCounterparty(counterpartyName);
  if (!normalized) return null;
  
  // Try entity-specific rule first
  const entityRule = db.prepare(`
    SELECT * FROM categorization_rules 
    WHERE entity_id = ? AND counterparty_pattern_normalized = ?
    ORDER BY confidence DESC
    LIMIT 1
  `).get(entityId, normalized);
  
  if (entityRule) return { ...entityRule, scope: 'entity' };
  
  // Try global rule
  const globalRule = db.prepare(`
    SELECT * FROM categorization_rules 
    WHERE entity_id IS NULL AND counterparty_pattern_normalized = ?
    ORDER BY confidence DESC
    LIMIT 1
  `).get(normalized);
  
  if (globalRule) return { ...globalRule, scope: 'global' };
  
  // Try fuzzy match on global rules
  const fuzzyGlobal = db.prepare(`
    SELECT * FROM categorization_rules 
    WHERE entity_id IS NULL AND ? LIKE '%' || counterparty_pattern_normalized || '%'
    ORDER BY confidence DESC, length(counterparty_pattern_normalized) DESC
    LIMIT 1
  `).get(normalized);
  
  if (fuzzyGlobal) return { ...fuzzyGlobal, scope: 'global', matchType: 'fuzzy' };
  
  return null;
}

/**
 * Categorize a transaction using the rule hierarchy
 */
export function categorizeTransaction(db, entityId, transactionId, counterpartyName) {
  const rule = findMatchingRule(db, entityId, counterpartyName);
  
  if (!rule) return null;
  
  // Apply the categorization
  const existing = db.prepare('SELECT id FROM categorized_transactions WHERE transaction_id = ?').get(transactionId);
  
  if (existing) {
    db.prepare(`
      UPDATE categorized_transactions 
      SET category = ?, subcategory = ?, method = ?, confidence = ?, updated_at = datetime('now')
      WHERE transaction_id = ?
    `).run(rule.category, rule.subcategory, rule.scope === 'global' ? 'global_rule' : 'entity_rule', rule.confidence, transactionId);
  } else {
    db.prepare(`
      INSERT INTO categorized_transactions (transaction_id, category, subcategory, method, confidence)
      VALUES (?, ?, ?, ?, ?)
    `).run(transactionId, rule.category, rule.subcategory, rule.scope === 'global' ? 'global_rule' : 'entity_rule', rule.confidence);
  }
  
  // Increment usage count
  db.prepare('UPDATE categorization_rules SET usage_count = usage_count + 1 WHERE id = ?').run(rule.id);
  
  return rule;
}

/**
 * Set or update a category for a transaction (manual override)
 * This also updates or creates rules and tracks confirmation/override
 */
export function setTransactionCategory(db, entityId, transactionId, category, subcategory = null, options = {}) {
  const { createGlobalRule = false, source = 'manual' } = options;
  
  // Get the transaction
  const tx = db.prepare(`
    SELECT t.*, ct.category as existing_category, ct.method as existing_method
    FROM transactions t
    LEFT JOIN categorized_transactions ct ON ct.transaction_id = t.id
    WHERE t.id = ?
  `).get(transactionId);
  
  if (!tx) throw new Error(`Transaction ${transactionId} not found`);
  
  const normalized = normalizeCounterparty(tx.counterparty_name);
  const isOverride = tx.existing_category && tx.existing_category !== category;
  
  // Update the categorized_transactions table
  const existing = db.prepare('SELECT id FROM categorized_transactions WHERE transaction_id = ?').get(transactionId);
  
  if (existing) {
    db.prepare(`
      UPDATE categorized_transactions 
      SET category = ?, subcategory = ?, method = ?, confidence = 1.0, updated_at = datetime('now')
      WHERE transaction_id = ?
    `).run(category, subcategory, source, transactionId);
  } else {
    db.prepare(`
      INSERT INTO categorized_transactions (transaction_id, category, subcategory, method, confidence)
      VALUES (?, ?, ?, ?, 1.0)
    `).run(transactionId, category, subcategory, source);
  }
  
  // Find existing rule to update
  const ruleEntityId = createGlobalRule ? null : entityId;
  const existingRule = db.prepare(`
    SELECT * FROM categorization_rules 
    WHERE (entity_id = ? OR (entity_id IS NULL AND ? IS NULL))
    AND counterparty_pattern_normalized = ?
  `).get(ruleEntityId, ruleEntityId, normalized);
  
  if (existingRule) {
    if (existingRule.category === category) {
      // Confirmation - same category
      db.prepare(`
        UPDATE categorization_rules 
        SET confirmed_count = confirmed_count + 1, 
            usage_count = usage_count + 1,
            last_confirmed_at = datetime('now'),
            confidence = MIN(1.0, confidence + 0.01),
            updated_at = datetime('now')
        WHERE id = ?
      `).run(existingRule.id);
    } else {
      // Override - different category
      db.prepare(`
        UPDATE categorization_rules 
        SET overridden_count = overridden_count + 1,
            category = ?,
            subcategory = ?,
            confidence = MAX(0.5, confidence - 0.05),
            updated_at = datetime('now')
        WHERE id = ?
      `).run(category, subcategory, existingRule.id);
    }
  } else {
    // Create new rule
    db.prepare(`
      INSERT INTO categorization_rules 
      (entity_id, counterparty_pattern, counterparty_pattern_normalized, category, subcategory, confidence, source, usage_count, confirmed_count)
      VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)
    `).run(ruleEntityId, tx.counterparty_name, normalized, category, subcategory, 0.9, source);
  }
  
  // Check if we should promote to global rule
  if (!createGlobalRule && entityId) {
    checkForRulePromotion(db, normalized, category);
  }
  
  return { transactionId, category, subcategory, isOverride };
}

/**
 * Check if a rule should be promoted to global
 * Promotes when 3+ entities have the same category for a counterparty
 */
export function checkForRulePromotion(db, normalizedCounterparty, category) {
  // Count how many entities have this rule with the same category
  const entityCount = db.prepare(`
    SELECT COUNT(DISTINCT entity_id) as cnt
    FROM categorization_rules
    WHERE counterparty_pattern_normalized = ?
    AND category = ?
    AND entity_id IS NOT NULL
  `).get(normalizedCounterparty, category);
  
  if (entityCount.cnt >= 3) {
    // Check if global rule already exists
    const globalExists = db.prepare(`
      SELECT id, category FROM categorization_rules
      WHERE counterparty_pattern_normalized = ?
      AND entity_id IS NULL
    `).get(normalizedCounterparty);
    
    if (!globalExists) {
      // Get the first entity rule to copy pattern from
      const sampleRule = db.prepare(`
        SELECT counterparty_pattern, subcategory
        FROM categorization_rules
        WHERE counterparty_pattern_normalized = ?
        AND category = ?
        AND entity_id IS NOT NULL
        LIMIT 1
      `).get(normalizedCounterparty, category);
      
      // Create global rule
      db.prepare(`
        INSERT INTO categorization_rules 
        (entity_id, counterparty_pattern, counterparty_pattern_normalized, category, subcategory, confidence, source, usage_count)
        VALUES (NULL, ?, ?, ?, ?, 0.95, 'promoted', ?)
      `).run(sampleRule.counterparty_pattern, normalizedCounterparty, category, sampleRule.subcategory, entityCount.cnt);
      
      console.log(`Promoted rule to global: ${normalizedCounterparty} → ${category} (${entityCount.cnt} entities)`);
    } else if (globalExists.category !== category) {
      // Conflict - different entities disagree on category
      console.warn(`Rule conflict: ${normalizedCounterparty} has different categories across entities`);
    }
  }
}

/**
 * Get rules that may need review (high override count, low confidence)
 */
export function getRulesNeedingReview(db, limit = 20) {
  return db.prepare(`
    SELECT *, 
           CAST(overridden_count AS REAL) / MAX(confirmed_count + overridden_count, 1) as override_rate
    FROM categorization_rules
    WHERE overridden_count > 0
    ORDER BY override_rate DESC, overridden_count DESC
    LIMIT ?
  `).all(limit);
}

/**
 * Get global rules with high confidence (good candidates for defaults)
 */
export function getHighConfidenceGlobalRules(db, minConfidence = 0.9) {
  return db.prepare(`
    SELECT *
    FROM categorization_rules
    WHERE entity_id IS NULL
    AND confidence >= ?
    ORDER BY usage_count DESC, confidence DESC
  `).all(minConfidence);
}

/**
 * Seed well-known global rules (common vendors)
 */
export function seedGlobalRules(db) {
  const knownRules = [
    // Software
    { pattern: 'twilio', category: 'Software expenses' },
    { pattern: 'github', category: 'Software expenses' },
    { pattern: 'slack', category: 'Software expenses' },
    { pattern: 'hubspot', category: 'Software expenses' },
    { pattern: 'intercom', category: 'Software expenses' },
    { pattern: 'monday', category: 'Software expenses' },
    { pattern: 'notion', category: 'Software expenses' },
    { pattern: 'figma', category: 'Software expenses' },
    { pattern: 'zoom', category: 'Software expenses' },
    { pattern: 'dropbox', category: 'Software expenses' },
    { pattern: 'gsuite', category: 'Software expenses' },
    { pattern: 'google cloud', category: 'Software expenses' },
    { pattern: 'google workspace', category: 'Software expenses' },
    
    // Advertising
    { pattern: 'google ads', category: 'Advertising' },
    { pattern: 'facebook ads', category: 'Advertising' },
    { pattern: 'meta ads', category: 'Advertising' },
    { pattern: 'linkedin ads', category: 'Advertising' },
    { pattern: 'twitter ads', category: 'Advertising' },
    
    // Hosting
    { pattern: 'aws', category: 'Servers & Hosting' },
    { pattern: 'amazon web services', category: 'Servers & Hosting' },
    { pattern: 'digitalocean', category: 'Servers & Hosting' },
    { pattern: 'heroku', category: 'Servers & Hosting' },
    { pattern: 'vercel', category: 'Servers & Hosting' },
    { pattern: 'netlify', category: 'Servers & Hosting' },
    { pattern: 'cloudflare', category: 'Servers & Hosting' },
    
    // Revenue
    { pattern: 'stripe', category: 'Sales/Service Revenue', isCredit: true },
    
    // Bank
    { pattern: 'wire fee', category: 'Bank Service Charges' },
    { pattern: 'intl wire', category: 'Bank Service Charges' },
    { pattern: 'mercury', category: 'Bank Service Charges' },
  ];
  
  initCategorizationSchema(db);
  
  let added = 0;
  for (const rule of knownRules) {
    const exists = db.prepare(`
      SELECT 1 FROM categorization_rules 
      WHERE entity_id IS NULL AND counterparty_pattern_normalized = ?
    `).get(rule.pattern);
    
    if (!exists) {
      db.prepare(`
        INSERT INTO categorization_rules 
        (entity_id, counterparty_pattern, counterparty_pattern_normalized, category, confidence, source)
        VALUES (NULL, ?, ?, ?, 0.85, 'seed')
      `).run(rule.pattern, rule.pattern, rule.category);
      added++;
    }
  }
  
  return added;
}

/**
 * Batch categorize all uncategorized transactions for an entity
 */
export function categorizeAllUncategorized(db, entityId) {
  initCategorizationSchema(db);
  
  const uncategorized = db.prepare(`
    SELECT t.id, t.counterparty_name
    FROM transactions t
    JOIN accounts a ON t.account_id = a.id
    JOIN connections c ON a.connection_id = c.id
    LEFT JOIN categorized_transactions ct ON ct.transaction_id = t.id
    WHERE c.entity_id = ?
    AND ct.id IS NULL
  `).all(entityId);
  
  let categorized = 0;
  for (const tx of uncategorized) {
    const result = categorizeTransaction(db, entityId, tx.id, tx.counterparty_name);
    if (result) categorized++;
  }
  
  return { total: uncategorized.length, categorized };
}
