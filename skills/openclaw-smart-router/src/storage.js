import Database from 'better-sqlite3';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * RouterStorage - SQLite storage for smart model routing
 * Handles routing decisions, learned patterns, model performance, and quotas
 */
export class RouterStorage {
  constructor(dbPath) {
    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
  }

  /**
   * Initialize database with migrations
   * Run this separately via setup.js
   */
  initialize() {
    // Run core routing schema
    const migration1 = readFileSync(
      join(__dirname, '../migrations/001-init.sql'),
      'utf-8'
    );
    this.db.exec(migration1);

    // Run x402 payment tables
    const migration2 = readFileSync(
      join(__dirname, '../migrations/002-x402-payments.sql'),
      'utf-8'
    );
    this.db.exec(migration2);
  }

  // ============================================
  // Routing Decision Management
  // ============================================

  /**
   * Record a routing decision
   * @param {Object} decisionData - Routing decision details
   */
  recordDecision(decisionData) {
    const stmt = this.db.prepare(`
      INSERT INTO routing_decisions (
        decision_id, agent_wallet, task_complexity, context_length,
        task_type, has_code, has_errors, has_data,
        selected_model, selected_provider, selection_reason,
        confidence_score, alternatives_json, pattern_id
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    return stmt.run(
      decisionData.decision_id,
      decisionData.agent_wallet || null,
      decisionData.task_complexity || 0.5,
      decisionData.context_length || 0,
      decisionData.task_type || 'query',
      decisionData.has_code ? 1 : 0,
      decisionData.has_errors ? 1 : 0,
      decisionData.has_data ? 1 : 0,
      decisionData.selected_model,
      decisionData.selected_provider,
      decisionData.selection_reason || null,
      decisionData.confidence_score || 0.5,
      decisionData.alternatives_json || null,
      decisionData.pattern_id || null
    );
  }

  /**
   * Record outcome for a routing decision
   * @param {string} decisionId - Decision ID
   * @param {Object} outcomeData - Outcome details (success, cost, quality, etc.)
   */
  recordOutcome(decisionId, outcomeData) {
    const stmt = this.db.prepare(`
      UPDATE routing_decisions
      SET was_successful = ?,
          actual_tokens = ?,
          actual_cost_usd = ?,
          response_quality = ?,
          response_time_ms = ?
      WHERE decision_id = ?
    `);

    return stmt.run(
      outcomeData.was_successful ? 1 : 0,
      outcomeData.actual_tokens || 0,
      outcomeData.actual_cost_usd || 0.0,
      outcomeData.response_quality || 0.5,
      outcomeData.response_time_ms || 0,
      decisionId
    );
  }

  /**
   * Get a single routing decision
   */
  getDecision(decisionId) {
    const stmt = this.db.prepare(`
      SELECT * FROM routing_decisions WHERE decision_id = ?
    `);

    const decision = stmt.get(decisionId);

    if (decision && decision.alternatives_json) {
      decision.alternatives_json = JSON.parse(decision.alternatives_json);
    }

    return decision;
  }

  /**
   * Get routing decisions for an agent
   * @param {string} agentWallet - Agent wallet address
   * @param {string} timeframe - SQL timeframe (e.g., '7 days', '30 days')
   */
  getDecisions(agentWallet, timeframe = '30 days') {
    const stmt = this.db.prepare(`
      SELECT * FROM routing_decisions
      WHERE agent_wallet = ?
        AND timestamp >= datetime('now', '-' || ?)
      ORDER BY timestamp DESC
    `);

    const decisions = stmt.all(agentWallet, timeframe);

    return decisions.map(d => ({
      ...d,
      alternatives_json: d.alternatives_json ? JSON.parse(d.alternatives_json) : null
    }));
  }

  /**
   * Get routing statistics for an agent
   */
  getRoutingStats(agentWallet, timeframe = '30 days') {
    const stmt = this.db.prepare(`
      SELECT
        COUNT(*) as total_decisions,
        SUM(CASE WHEN was_successful = 1 THEN 1 ELSE 0 END) as successful_decisions,
        AVG(task_complexity) as avg_complexity,
        AVG(actual_cost_usd) as avg_cost,
        SUM(actual_cost_usd) as total_cost,
        AVG(response_quality) as avg_quality,
        AVG(confidence_score) as avg_confidence
      FROM routing_decisions
      WHERE agent_wallet = ?
        AND timestamp >= datetime('now', '-' || ?)
    `);

    return stmt.get(agentWallet, timeframe);
  }

  // ============================================
  // Pattern Management
  // ============================================

  /**
   * Get a matching pattern
   * @param {Object} criteria - Search criteria (agent_wallet, task_type, complexity, etc.)
   */
  getPattern(criteria) {
    let query = 'SELECT * FROM routing_patterns WHERE 1=1';
    const params = [];

    if (criteria.agent_wallet) {
      query += ' AND agent_wallet = ?';
      params.push(criteria.agent_wallet);
    }

    if (criteria.task_type) {
      query += ' AND task_type = ?';
      params.push(criteria.task_type);
    }

    if (criteria.complexity_min !== undefined && criteria.complexity_max !== undefined) {
      query += ' AND ? BETWEEN complexity_min AND complexity_max';
      params.push((criteria.complexity_min + criteria.complexity_max) / 2);
    }

    if (criteria.context_length_min !== undefined && criteria.context_length_max !== undefined) {
      query += ' AND ? BETWEEN context_length_min AND context_length_max';
      params.push((criteria.context_length_min + criteria.context_length_max) / 2);
    }

    query += ' ORDER BY confidence DESC, success_count DESC LIMIT 1';

    const stmt = this.db.prepare(query);
    const pattern = stmt.get(...params);

    if (pattern && pattern.keywords_json) {
      pattern.keywords_json = JSON.parse(pattern.keywords_json);
    }

    return pattern;
  }

  /**
   * Get all patterns for an agent
   */
  getPatterns(agentWallet, patternType = null) {
    let query = 'SELECT * FROM routing_patterns WHERE agent_wallet = ?';
    const params = [agentWallet];

    if (patternType) {
      query += ' AND pattern_type = ?';
      params.push(patternType);
    }

    query += ' ORDER BY confidence DESC, success_count DESC';

    const stmt = this.db.prepare(query);
    const patterns = stmt.all(...params);

    return patterns.map(p => ({
      ...p,
      keywords_json: p.keywords_json ? JSON.parse(p.keywords_json) : null
    }));
  }

  /**
   * Create a new routing pattern
   * @param {Object} patternData - Pattern details
   */
  createPattern(patternData) {
    const stmt = this.db.prepare(`
      INSERT INTO routing_patterns (
        pattern_id, agent_wallet, pattern_type, pattern_description,
        task_type, complexity_min, complexity_max,
        context_length_min, context_length_max, keywords_json,
        recommended_model, recommended_provider
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    return stmt.run(
      patternData.pattern_id,
      patternData.agent_wallet || null,
      patternData.pattern_type,
      patternData.pattern_description || null,
      patternData.task_type || null,
      patternData.complexity_min || null,
      patternData.complexity_max || null,
      patternData.context_length_min || null,
      patternData.context_length_max || null,
      patternData.keywords_json ? JSON.stringify(patternData.keywords_json) : null,
      patternData.recommended_model,
      patternData.recommended_provider
    );
  }

  /**
   * Update pattern statistics
   * @param {string} patternId - Pattern ID
   * @param {boolean} success - Whether the routing was successful
   * @param {number} cost - Actual cost
   * @param {number} quality - Response quality (0.0-1.0)
   */
  updatePatternStats(patternId, success, cost, quality) {
    const stmt = this.db.prepare(`
      UPDATE routing_patterns
      SET success_count = success_count + ?,
          failure_count = failure_count + ?,
          avg_cost_saved = (avg_cost_saved * (success_count + failure_count) + ?) / (success_count + failure_count + 1),
          avg_quality = (avg_quality * (success_count + failure_count) + ?) / (success_count + failure_count + 1),
          confidence = CAST(success_count + ? AS REAL) / (success_count + failure_count + 1),
          last_used = CURRENT_TIMESTAMP,
          last_updated = CURRENT_TIMESTAMP
      WHERE pattern_id = ?
    `);

    return stmt.run(
      success ? 1 : 0,
      success ? 0 : 1,
      cost || 0.0,
      quality || 0.5,
      success ? 1 : 0,
      patternId
    );
  }

  // ============================================
  // Model Performance Tracking
  // ============================================

  /**
   * Get model performance stats
   * @param {string} agentWallet - Agent wallet address
   * @param {string} model - Model name
   * @param {string} taskType - Task type (optional)
   */
  getModelPerformance(agentWallet, model, taskType = null) {
    let query = `
      SELECT * FROM model_performance
      WHERE agent_wallet = ? AND model = ?
    `;
    const params = [agentWallet, model];

    if (taskType) {
      query += ' AND task_type = ?';
      params.push(taskType);
    }

    query += ' LIMIT 1';

    const stmt = this.db.prepare(query);
    return stmt.get(...params);
  }

  /**
   * Get all model performance stats for an agent
   */
  getModelPerformanceAll(agentWallet, taskType = null) {
    let query = 'SELECT * FROM model_performance WHERE agent_wallet = ?';
    const params = [agentWallet];

    if (taskType) {
      query += ' AND task_type = ?';
      params.push(taskType);
    }

    query += ' ORDER BY total_requests DESC';

    const stmt = this.db.prepare(query);
    return stmt.all(...params);
  }

  /**
   * Update model performance metrics
   * @param {string} agentWallet - Agent wallet address
   * @param {string} model - Model name
   * @param {string} provider - Provider name
   * @param {string} taskType - Task type
   * @param {Object} outcome - Outcome data (success, cost, quality, time)
   */
  updateModelPerformance(agentWallet, model, provider, taskType, outcome) {
    const stmt = this.db.prepare(`
      INSERT INTO model_performance (
        agent_wallet, model, provider, task_type,
        total_requests, successful_requests,
        avg_response_time_ms, avg_quality_score,
        avg_cost_per_request, total_cost_usd
      ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
      ON CONFLICT(agent_wallet, model, provider, task_type) DO UPDATE SET
        total_requests = total_requests + 1,
        successful_requests = successful_requests + ?,
        avg_response_time_ms = (avg_response_time_ms * total_requests + ?) / (total_requests + 1),
        avg_quality_score = (avg_quality_score * total_requests + ?) / (total_requests + 1),
        avg_cost_per_request = (avg_cost_per_request * total_requests + ?) / (total_requests + 1),
        total_cost_usd = total_cost_usd + ?,
        last_updated = CURRENT_TIMESTAMP
    `);

    return stmt.run(
      agentWallet,
      model,
      provider,
      taskType || 'unknown',
      outcome.was_successful ? 1 : 0,
      outcome.response_time_ms || 0,
      outcome.response_quality || 0.5,
      outcome.actual_cost_usd || 0.0,
      outcome.actual_cost_usd || 0.0,
      outcome.was_successful ? 1 : 0,
      outcome.response_time_ms || 0,
      outcome.response_quality || 0.5,
      outcome.actual_cost_usd || 0.0,
      outcome.actual_cost_usd || 0.0
    );
  }

  // ============================================
  // Quota Management
  // ============================================

  /**
   * Get agent's routing quota
   */
  getQuota(agentWallet) {
    const stmt = this.db.prepare(`
      SELECT * FROM agent_router_quotas WHERE agent_wallet = ?
    `);
    let quota = stmt.get(agentWallet);

    // Initialize quota if doesn't exist
    if (!quota) {
      quota = this.initializeQuota(agentWallet);
    }

    // Reset daily counter if needed
    quota = this.resetDailyQuotaIfNeeded(quota);

    return quota;
  }

  /**
   * Initialize default quota for new agent
   */
  initializeQuota(agentWallet) {
    const stmt = this.db.prepare(`
      INSERT INTO agent_router_quotas (
        agent_wallet, tier, decisions_limit, decisions_today, last_reset_date
      ) VALUES (?, 'free', 100, 0, DATE('now'))
    `);
    stmt.run(agentWallet);

    return this.getQuota(agentWallet);
  }

  /**
   * Reset daily quota if date has changed
   */
  resetDailyQuotaIfNeeded(quota) {
    const today = new Date().toISOString().split('T')[0];

    if (quota.last_reset_date !== today) {
      const stmt = this.db.prepare(`
        UPDATE agent_router_quotas
        SET decisions_today = 0,
            last_reset_date = DATE('now'),
            updated_at = CURRENT_TIMESTAMP
        WHERE agent_wallet = ?
      `);
      stmt.run(quota.agent_wallet);

      // Refresh quota
      return this.db.prepare(`
        SELECT * FROM agent_router_quotas WHERE agent_wallet = ?
      `).get(quota.agent_wallet);
    }

    return quota;
  }

  /**
   * Check if agent has quota available
   * @returns {Object} { available: boolean, remaining: number, limit: number, tier: string }
   */
  checkQuotaAvailable(agentWallet) {
    const quota = this.getQuota(agentWallet);

    // Pro tier has unlimited quota
    if (quota.tier === 'pro' && quota.decisions_limit === -1) {
      return {
        available: true,
        remaining: -1,
        limit: -1,
        tier: 'pro'
      };
    }

    const remaining = quota.decisions_limit - quota.decisions_today;
    return {
      available: remaining > 0,
      remaining: Math.max(0, remaining),
      limit: quota.decisions_limit,
      tier: quota.tier
    };
  }

  /**
   * Increment decision count for agent
   */
  incrementDecisionCount(agentWallet) {
    const quota = this.getQuota(agentWallet);

    const stmt = this.db.prepare(`
      UPDATE agent_router_quotas
      SET decisions_today = decisions_today + 1,
          updated_at = CURRENT_TIMESTAMP
      WHERE agent_wallet = ?
    `);

    return stmt.run(agentWallet);
  }

  /**
   * Update agent tier and paid_until date
   * @param {string} agentWallet - Agent wallet address
   * @param {string} tier - 'free' or 'pro'
   * @param {string} paidUntil - ISO date string
   */
  updateAgentTier(agentWallet, tier, paidUntil) {
    const stmt = this.db.prepare(`
      UPDATE agent_router_quotas
      SET tier = ?,
          paid_until = ?,
          decisions_limit = ?,
          updated_at = CURRENT_TIMESTAMP
      WHERE agent_wallet = ?
    `);

    // Pro tier gets unlimited decisions
    const decisionsLimit = tier === 'pro' ? -1 : 100;

    return stmt.run(tier, paidUntil, decisionsLimit, agentWallet);
  }

  // ============================================
  // Cost Governor Integration
  // ============================================

  /**
   * Get pricing for a model (would normally come from Cost Governor)
   * @param {string} provider - Provider name
   * @param {string} model - Model name
   */
  getPricing(provider, model) {
    // Placeholder: In production, this would call Cost Governor's storage
    // For now, return static pricing data
    const pricingData = {
      anthropic: {
        'claude-opus-4-5': { cost_per_1k_prompt: 0.015, cost_per_1k_completion: 0.075 },
        'claude-sonnet-4-5': { cost_per_1k_prompt: 0.003, cost_per_1k_completion: 0.015 },
        'claude-haiku-4-5': { cost_per_1k_prompt: 0.00025, cost_per_1k_completion: 0.00125 }
      },
      openai: {
        'gpt-5.2': { cost_per_1k_prompt: 0.01, cost_per_1k_completion: 0.03 },
        'gpt-4.5': { cost_per_1k_prompt: 0.005, cost_per_1k_completion: 0.015 }
      },
      google: {
        'gemini-2.5-pro': { cost_per_1k_prompt: 0.00125, cost_per_1k_completion: 0.005 }
      }
    };

    return pricingData[provider]?.[model] || { cost_per_1k_prompt: 0.001, cost_per_1k_completion: 0.003 };
  }

  // ============================================
  // x402 Payment Methods
  // ============================================

  /**
   * Record a payment request
   * @param {string} requestId - Unique request ID
   * @param {string} agentWallet - Agent wallet address
   * @param {number} amount - Payment amount
   * @param {string} token - Token type (USDT, USDC, SOL)
   */
  recordPaymentRequest(requestId, agentWallet, amount, token) {
    const stmt = this.db.prepare(`
      INSERT INTO payment_requests (request_id, agent_wallet, amount_requested, token, status)
      VALUES (?, ?, ?, ?, 'pending')
    `);

    return stmt.run(requestId, agentWallet, amount, token);
  }

  /**
   * Get payment request
   */
  getPaymentRequest(requestId) {
    const stmt = this.db.prepare(`
      SELECT * FROM payment_requests WHERE request_id = ?
    `);

    return stmt.get(requestId);
  }

  /**
   * Update payment request status
   */
  updatePaymentRequest(requestId, status, txHash = null) {
    const stmt = this.db.prepare(`
      UPDATE payment_requests
      SET status = ?,
          completed_at = CURRENT_TIMESTAMP,
          tx_hash = ?
      WHERE request_id = ?
    `);

    return stmt.run(status, txHash, requestId);
  }

  /**
   * Record a completed payment transaction
   * @param {Object} data - Transaction data
   */
  recordPaymentTransaction(data) {
    const stmt = this.db.prepare(`
      INSERT INTO payment_transactions (
        agent_wallet, tx_hash, amount, token, chain,
        verified, tier_granted, duration_months
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);

    return stmt.run(
      data.agent_wallet,
      data.tx_hash,
      data.amount,
      data.token,
      data.chain,
      data.verified ? 1 : 0,
      data.tier_granted,
      data.duration_months || 1
    );
  }

  /**
   * Get payment transactions for an agent
   */
  getPaymentTransactions(agentWallet) {
    const stmt = this.db.prepare(`
      SELECT * FROM payment_transactions
      WHERE agent_wallet = ?
      ORDER BY timestamp DESC
    `);

    return stmt.all(agentWallet);
  }

  /**
   * Get latest payment transaction
   */
  getLatestPayment(agentWallet) {
    const stmt = this.db.prepare(`
      SELECT * FROM payment_transactions
      WHERE agent_wallet = ?
      ORDER BY timestamp DESC
      LIMIT 1
    `);

    return stmt.get(agentWallet);
  }

  /**
   * Verify if transaction hash exists
   */
  hasTransaction(txHash) {
    const stmt = this.db.prepare(`
      SELECT COUNT(*) as count FROM payment_transactions WHERE tx_hash = ?
    `);

    return stmt.get(txHash).count > 0;
  }

  // ============================================
  // Utility Methods
  // ============================================

  /**
   * Get decision statistics by model
   */
  getDecisionsByModel(agentWallet, timeframe = '30 days') {
    const stmt = this.db.prepare(`
      SELECT
        selected_model,
        selected_provider,
        COUNT(*) as count,
        AVG(actual_cost_usd) as avg_cost,
        AVG(response_quality) as avg_quality,
        SUM(CASE WHEN was_successful = 1 THEN 1 ELSE 0 END) as success_count
      FROM routing_decisions
      WHERE agent_wallet = ?
        AND timestamp >= datetime('now', '-' || ?)
      GROUP BY selected_model, selected_provider
      ORDER BY count DESC
    `);

    return stmt.all(agentWallet, timeframe);
  }

  /**
   * Get decision statistics by task type
   */
  getDecisionsByTaskType(agentWallet, timeframe = '30 days') {
    const stmt = this.db.prepare(`
      SELECT
        task_type,
        COUNT(*) as count,
        AVG(task_complexity) as avg_complexity,
        AVG(actual_cost_usd) as avg_cost,
        AVG(response_quality) as avg_quality
      FROM routing_decisions
      WHERE agent_wallet = ?
        AND timestamp >= datetime('now', '-' || ?)
      GROUP BY task_type
      ORDER BY count DESC
    `);

    return stmt.all(agentWallet, timeframe);
  }

  /**
   * Clean up old routing decisions (keep last 90 days)
   */
  cleanupOldDecisions(days = 90) {
    const stmt = this.db.prepare(`
      DELETE FROM routing_decisions
      WHERE timestamp < datetime('now', '-' || ? || ' days')
    `);

    return stmt.run(days);
  }

  /**
   * Vacuum database to reclaim space
   */
  vacuum() {
    this.db.exec('VACUUM');
  }

  /**
   * Close database connection
   */
  close() {
    this.db.close();
  }
}
