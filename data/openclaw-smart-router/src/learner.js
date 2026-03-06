/**
 * OpenClaw Smart Router - Pattern Learning
 *
 * Learns from routing decisions to improve future model selection
 * Identifies patterns in successful/failed decisions
 * Tracks cost savings and model performance
 */

import { randomUUID } from 'crypto';

export class PatternLearner {
  constructor(storage) {
    this.storage = storage;

    // Model pricing (cost per 1M tokens - combined input/output estimate)
    this.modelPricing = {
      'claude-opus-4-6': 15.0,      // Premium: $15/M tokens
      'claude-opus-4-5': 15.0,
      'claude-sonnet-4-5': 3.0,     // Mid-tier: $3/M tokens
      'claude-sonnet-3-5': 3.0,
      'claude-haiku-4-5': 0.8,      // Budget: $0.80/M tokens
      'claude-haiku-3-5': 0.8,
      'gpt-4': 30.0,                // OpenAI premium
      'gpt-4-turbo': 10.0,
      'gpt-3.5-turbo': 0.5,
      'gemini-pro': 0.5,
      'gemini-flash': 0.1
    };

    // Pattern creation thresholds
    this.minSimilarTasks = 5;      // Need 5+ similar successful tasks to create pattern
    this.minPatternConfidence = 0.6; // Minimum confidence to use pattern
  }

  /**
   * Learn from a routing decision outcome
   * Called after request completes with actual results
   */
  async learnFromOutcome(decisionId, outcome) {
    try {
      // Get the original decision
      const decision = this.storage.db.prepare(`
        SELECT * FROM routing_decisions WHERE decision_id = ?
      `).get(decisionId);

      if (!decision) {
        throw new Error(`Decision ${decisionId} not found`);
      }

      // Update decision with outcome
      this.storage.db.prepare(`
        UPDATE routing_decisions
        SET
          was_successful = ?,
          actual_tokens = ?,
          actual_cost_usd = ?,
          response_quality = ?,
          response_time_ms = ?
        WHERE decision_id = ?
      `).run(
        outcome.success ? 1 : 0,
        outcome.actual_tokens || decision.context_length,
        outcome.actual_cost || this.estimateCost(decision.selected_model, outcome.actual_tokens),
        outcome.quality || (outcome.success ? 0.8 : 0.3),
        outcome.response_time_ms || null,
        decisionId
      );

      // Update model performance stats
      await this.updateModelPerformance(
        decision.agent_wallet,
        decision.selected_model,
        decision.selected_provider,
        decision.task_type,
        outcome
      );

      // If successful, look for patterns
      if (outcome.success) {
        await this.detectAndCreatePattern(decision);
      }

      // If pattern was used, update pattern stats
      if (decision.pattern_id) {
        await this.updatePatternStats(decision.pattern_id, outcome.success);
      }

      console.log(`[PatternLearner] Learned from decision ${decisionId}: ${outcome.success ? 'SUCCESS' : 'FAILURE'}`);
    } catch (error) {
      console.error('[PatternLearner] Error learning from outcome:', error.message);
      throw error;
    }
  }

  /**
   * Update model performance statistics
   */
  async updateModelPerformance(agentWallet, model, provider, taskType, outcome) {
    const existing = this.storage.db.prepare(`
      SELECT * FROM model_performance
      WHERE agent_wallet = ? AND model = ? AND provider = ? AND task_type = ?
    `).get(agentWallet, model, provider, taskType);

    if (existing) {
      // Update existing stats (incremental average)
      const totalRequests = existing.total_requests + 1;
      const successfulRequests = existing.successful_requests + (outcome.success ? 1 : 0);

      const avgQuality = existing.avg_quality_score
        ? (existing.avg_quality_score * existing.total_requests + (outcome.quality || 0.5)) / totalRequests
        : (outcome.quality || 0.5);

      const avgResponseTime = outcome.response_time_ms && existing.avg_response_time_ms
        ? (existing.avg_response_time_ms * existing.total_requests + outcome.response_time_ms) / totalRequests
        : (outcome.response_time_ms || existing.avg_response_time_ms);

      const costThisRequest = outcome.actual_cost || 0;
      const totalCost = (existing.total_cost_usd || 0) + costThisRequest;
      const avgCost = totalCost / totalRequests;

      this.storage.db.prepare(`
        UPDATE model_performance
        SET
          total_requests = ?,
          successful_requests = ?,
          avg_response_time_ms = ?,
          avg_quality_score = ?,
          avg_cost_per_request = ?,
          total_cost_usd = ?,
          last_updated = datetime('now')
        WHERE agent_wallet = ? AND model = ? AND provider = ? AND task_type = ?
      `).run(
        totalRequests,
        successfulRequests,
        avgResponseTime,
        avgQuality,
        avgCost,
        totalCost,
        agentWallet,
        model,
        provider,
        taskType
      );
    } else {
      // Create new performance record
      this.storage.db.prepare(`
        INSERT INTO model_performance
        (agent_wallet, model, provider, task_type, total_requests, successful_requests,
         avg_response_time_ms, avg_quality_score, avg_cost_per_request, total_cost_usd)
        VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
      `).run(
        agentWallet,
        model,
        provider,
        taskType,
        outcome.success ? 1 : 0,
        outcome.response_time_ms || null,
        outcome.quality || 0.5,
        outcome.actual_cost || 0,
        outcome.actual_cost || 0
      );
    }
  }

  /**
   * Detect patterns and create new pattern if threshold met
   */
  async detectAndCreatePattern(decision) {
    // Find similar successful decisions
    const similarDecisions = this.storage.db.prepare(`
      SELECT * FROM routing_decisions
      WHERE agent_wallet = ?
        AND task_type = ?
        AND was_successful = 1
        AND task_complexity BETWEEN ? AND ?
        AND context_length BETWEEN ? AND ?
      ORDER BY timestamp DESC
      LIMIT 20
    `).all(
      decision.agent_wallet,
      decision.task_type,
      decision.task_complexity - 0.1,
      decision.task_complexity + 0.1,
      Math.max(0, decision.context_length - 500),
      decision.context_length + 500
    );

    if (similarDecisions.length < this.minSimilarTasks) {
      return; // Not enough data to create pattern
    }

    // Check if pattern already exists
    const existingPattern = this.storage.db.prepare(`
      SELECT * FROM routing_patterns
      WHERE agent_wallet = ?
        AND task_type = ?
        AND complexity_min <= ?
        AND complexity_max >= ?
      ORDER BY confidence DESC
      LIMIT 1
    `).get(
      decision.agent_wallet,
      decision.task_type,
      decision.task_complexity,
      decision.task_complexity
    );

    if (existingPattern) {
      return; // Pattern already exists for this task type/complexity
    }

    // Determine most common successful model
    const modelCounts = {};
    for (const sd of similarDecisions) {
      const key = `${sd.selected_model}:${sd.selected_provider}`;
      modelCounts[key] = (modelCounts[key] || 0) + 1;
    }

    const mostCommon = Object.entries(modelCounts)
      .sort((a, b) => b[1] - a[1])[0];

    if (!mostCommon || mostCommon[1] < this.minSimilarTasks) {
      return; // No consistent pattern
    }

    const [model, provider] = mostCommon[0].split(':');
    const confidence = mostCommon[1] / similarDecisions.length;

    if (confidence < this.minPatternConfidence) {
      return; // Not confident enough
    }

    // Create new pattern
    const patternId = randomUUID();
    const complexityMin = Math.max(0, decision.task_complexity - 0.1);
    const complexityMax = Math.min(1.0, decision.task_complexity + 0.1);
    const contextMin = Math.max(0, decision.context_length - 500);
    const contextMax = decision.context_length + 500;

    this.storage.db.prepare(`
      INSERT INTO routing_patterns
      (pattern_id, agent_wallet, pattern_type, pattern_description,
       task_type, complexity_min, complexity_max, context_length_min, context_length_max,
       recommended_model, recommended_provider, success_count, confidence)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      patternId,
      decision.agent_wallet,
      'task_based',
      `Learned pattern for ${decision.task_type} tasks (complexity: ${complexityMin.toFixed(2)}-${complexityMax.toFixed(2)})`,
      decision.task_type,
      complexityMin,
      complexityMax,
      contextMin,
      contextMax,
      model,
      provider,
      similarDecisions.length,
      confidence
    );

    console.log(`[PatternLearner] Created new pattern ${patternId} for ${decision.task_type} -> ${model} (confidence: ${(confidence * 100).toFixed(1)}%)`);
  }

  /**
   * Update pattern statistics after use
   */
  async updatePatternStats(patternId, wasSuccessful) {
    const pattern = this.storage.db.prepare(`
      SELECT * FROM routing_patterns WHERE pattern_id = ?
    `).get(patternId);

    if (!pattern) return;

    const newSuccessCount = pattern.success_count + (wasSuccessful ? 1 : 0);
    const newFailureCount = pattern.failure_count + (wasSuccessful ? 0 : 1);
    const totalUses = newSuccessCount + newFailureCount;
    const newConfidence = newSuccessCount / totalUses;

    this.storage.db.prepare(`
      UPDATE routing_patterns
      SET
        success_count = ?,
        failure_count = ?,
        confidence = ?,
        last_used = datetime('now'),
        last_updated = datetime('now')
      WHERE pattern_id = ?
    `).run(newSuccessCount, newFailureCount, newConfidence, patternId);

    console.log(`[PatternLearner] Updated pattern ${patternId}: ${newSuccessCount}/${totalUses} success (${(newConfidence * 100).toFixed(1)}%)`);
  }

  /**
   * Analyze total savings for an agent over a timeframe
   */
  async analyzeSavings(agentWallet, timeframe = '30 days') {
    // Get all decisions in timeframe
    const decisions = this.storage.db.prepare(`
      SELECT * FROM routing_decisions
      WHERE agent_wallet = ?
        AND timestamp >= datetime('now', '-' || ? || ' days')
        AND was_successful = 1
        AND actual_cost_usd IS NOT NULL
    `).all(agentWallet, parseInt(timeframe));

    if (decisions.length === 0) {
      return {
        total_decisions: 0,
        total_cost: 0,
        estimated_default_cost: 0,
        total_savings: 0,
        savings_percentage: 0,
        avg_cost_per_decision: 0
      };
    }

    // Calculate actual cost
    const totalCost = decisions.reduce((sum, d) => sum + (d.actual_cost_usd || 0), 0);

    // Calculate what it would have cost with default (Opus)
    const estimatedDefaultCost = decisions.reduce((sum, d) => {
      return sum + this.estimateDefaultCost(d);
    }, 0);

    const totalSavings = estimatedDefaultCost - totalCost;
    const savingsPercentage = estimatedDefaultCost > 0
      ? (totalSavings / estimatedDefaultCost) * 100
      : 0;

    return {
      total_decisions: decisions.length,
      total_cost: totalCost,
      estimated_default_cost: estimatedDefaultCost,
      total_savings: totalSavings,
      savings_percentage: savingsPercentage,
      avg_cost_per_decision: totalCost / decisions.length,
      timeframe: `${timeframe} days`
    };
  }

  /**
   * Estimate cost if default model (Opus) was used
   */
  estimateDefaultCost(decision) {
    const defaultModel = 'claude-opus-4-6';
    const tokens = decision.actual_tokens || decision.context_length || 1000;
    return this.estimateCost(defaultModel, tokens);
  }

  /**
   * Estimate cost for a model and token count
   */
  estimateCost(model, tokens) {
    const pricePerMillion = this.modelPricing[model] || 15.0;
    return (tokens / 1000000) * pricePerMillion;
  }

  /**
   * Get top performing patterns for an agent
   */
  getTopPatterns(agentWallet, limit = 10) {
    return this.storage.db.prepare(`
      SELECT * FROM routing_patterns
      WHERE agent_wallet = ?
      ORDER BY confidence DESC, success_count DESC
      LIMIT ?
    `).all(agentWallet, limit);
  }

  /**
   * Get model performance comparison
   */
  getModelComparison(agentWallet, taskType = null) {
    let query = `
      SELECT
        model,
        provider,
        task_type,
        total_requests,
        successful_requests,
        avg_quality_score,
        avg_cost_per_request,
        total_cost_usd,
        (CAST(successful_requests AS REAL) / total_requests * 100) as success_rate
      FROM model_performance
      WHERE agent_wallet = ?
    `;

    const params = [agentWallet];

    if (taskType) {
      query += ` AND task_type = ?`;
      params.push(taskType);
    }

    query += ` ORDER BY success_rate DESC, avg_quality_score DESC`;

    return this.storage.db.prepare(query).all(...params);
  }

  /**
   * Get learning insights for an agent
   */
  async getLearningInsights(agentWallet) {
    const totalDecisions = this.storage.db.prepare(`
      SELECT COUNT(*) as count FROM routing_decisions WHERE agent_wallet = ?
    `).get(agentWallet).count;

    const successfulDecisions = this.storage.db.prepare(`
      SELECT COUNT(*) as count FROM routing_decisions
      WHERE agent_wallet = ? AND was_successful = 1
    `).get(agentWallet).count;

    const patternsLearned = this.storage.db.prepare(`
      SELECT COUNT(*) as count FROM routing_patterns WHERE agent_wallet = ?
    `).get(agentWallet).count;

    const savingsData = await this.analyzeSavings(agentWallet, '30');

    return {
      total_decisions: totalDecisions,
      successful_decisions: successfulDecisions,
      success_rate: totalDecisions > 0 ? (successfulDecisions / totalDecisions * 100) : 0,
      patterns_learned: patternsLearned,
      savings: savingsData,
      top_patterns: this.getTopPatterns(agentWallet, 5)
    };
  }
}
