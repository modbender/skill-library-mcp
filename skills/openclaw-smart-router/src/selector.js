/**
 * ModelSelector for OpenClaw Smart Router
 *
 * Selects the optimal model based on task analysis, budget constraints,
 * historical patterns, and performance data.
 */

import { randomUUID } from 'crypto';

/**
 * ModelSelector class
 * Intelligently selects models based on multiple factors
 */
export class ModelSelector {
  constructor(storage) {
    this.storage = storage;

    // Model definitions with capabilities and pricing
    this.models = {
      'claude-opus-4-5': {
        name: 'claude-opus-4-5',
        provider: 'anthropic',
        complexity_range: [0.7, 1.0],
        strengths: ['reasoning', 'code', 'debugging'],
        cost_per_1k_prompt: 0.015,
        cost_per_1k_completion: 0.075,
        max_tokens: 200000,
        quality_tier: 'premium'
      },
      'claude-sonnet-4-5': {
        name: 'claude-sonnet-4-5',
        provider: 'anthropic',
        complexity_range: [0.4, 0.8],
        strengths: ['code', 'reasoning', 'writing'],
        cost_per_1k_prompt: 0.003,
        cost_per_1k_completion: 0.015,
        max_tokens: 200000,
        quality_tier: 'balanced'
      },
      'claude-haiku-4-5': {
        name: 'claude-haiku-4-5',
        provider: 'anthropic',
        complexity_range: [0.0, 0.5],
        strengths: ['query', 'writing'],
        cost_per_1k_prompt: 0.0008,
        cost_per_1k_completion: 0.004,
        max_tokens: 200000,
        quality_tier: 'economy'
      },
      'gpt-5.2': {
        name: 'gpt-5.2',
        provider: 'openai',
        complexity_range: [0.5, 0.9],
        strengths: ['reasoning', 'code', 'writing'],
        cost_per_1k_prompt: 0.010,
        cost_per_1k_completion: 0.030,
        max_tokens: 128000,
        quality_tier: 'balanced'
      },
      'gemini-2.5-pro': {
        name: 'gemini-2.5-pro',
        provider: 'google',
        complexity_range: [0.5, 0.9],
        strengths: ['reasoning', 'code', 'data'],
        cost_per_1k_prompt: 0.005,
        cost_per_1k_completion: 0.015,
        max_tokens: 1000000,
        quality_tier: 'competitive'
      }
    };

    // Scoring weights (must sum to 1.0)
    this.weights = {
      complexity_match: 0.40,   // 40% - How well model matches task complexity
      budget_constraint: 0.30,  // 30% - Budget availability and cost
      pattern_match: 0.20,      // 20% - Historical pattern matching
      performance: 0.10         // 10% - Historical success rate
    };
  }

  /**
   * Select the best model for a task
   * @param {object} taskAnalysis - Task analysis from TaskAnalyzer
   * @param {string} agentWallet - Agent wallet address
   * @param {object} options - Additional options (force_model, max_cost, etc.)
   * @returns {Promise<object>} Selected model and selection details
   */
  async selectModel(taskAnalysis, agentWallet, options = {}) {
    try {
      // Check if model is forced
      if (options.force_model) {
        const forcedModel = this.models[options.force_model];
        if (forcedModel) {
          return {
            selection_id: randomUUID(),
            timestamp: new Date().toISOString(),
            model: forcedModel.name,
            provider: forcedModel.provider,
            reason: 'forced',
            confidence: 1.0,
            estimated_cost: this.estimateCost(forcedModel, taskAnalysis.estimated_tokens),
            model_details: forcedModel
          };
        }
      }

      // Get budget status
      const budgetStatus = await this.getBudgetStatus(agentWallet);

      // Get historical patterns
      const patterns = await this.getHistoricalPatterns(agentWallet, taskAnalysis);

      // Score all models
      const scores = await this.scoreModels(taskAnalysis, budgetStatus, patterns, options);

      // Select highest scoring model
      const selected = scores.reduce((best, current) =>
        current.total_score > best.total_score ? current : best
      );

      // Get selection reason
      const reason = this.getSelectionReason(selected, taskAnalysis, budgetStatus);

      // Create selection result
      const selection = {
        selection_id: randomUUID(),
        timestamp: new Date().toISOString(),
        model: selected.model.name,
        provider: selected.model.provider,
        reason: reason,
        confidence: selected.total_score,
        estimated_cost: selected.estimated_cost,
        model_details: selected.model,
        score_breakdown: {
          complexity_match: selected.complexity_score,
          budget_constraint: selected.budget_score,
          pattern_match: selected.pattern_score,
          performance: selected.performance_score,
          total: selected.total_score
        },
        alternatives: scores
          .filter(s => s.model.name !== selected.model.name)
          .slice(0, 2)
          .map(s => ({
            model: s.model.name,
            score: s.total_score,
            estimated_cost: s.estimated_cost
          }))
      };

      // Store selection for learning
      await this.storeSelection(agentWallet, taskAnalysis, selection);

      return selection;
    } catch (error) {
      console.error('[ModelSelector] Error selecting model:', error);
      // Fallback to safe default (Sonnet for balanced cost/quality)
      const fallback = this.models['claude-sonnet-4-5'];
      return {
        selection_id: randomUUID(),
        timestamp: new Date().toISOString(),
        model: fallback.name,
        provider: fallback.provider,
        reason: 'error_fallback',
        confidence: 0.5,
        estimated_cost: this.estimateCost(fallback, taskAnalysis.estimated_tokens || 1000),
        model_details: fallback
      };
    }
  }

  /**
   * Score all available models for the task
   * @param {object} taskAnalysis - Task analysis
   * @param {object} budgetStatus - Budget status
   * @param {object} patterns - Historical patterns
   * @param {object} options - Selection options
   * @returns {Promise<Array>} Array of scored models
   */
  async scoreModels(taskAnalysis, budgetStatus, patterns, options = {}) {
    const scores = [];

    for (const [modelName, model] of Object.entries(this.models)) {
      // Skip if model explicitly excluded
      if (options.exclude_models?.includes(modelName)) {
        continue;
      }

      // Calculate individual scores
      const complexityScore = this.scoreComplexityMatch(taskAnalysis, model);
      const budgetScore = this.scoreBudgetConstraint(taskAnalysis, model, budgetStatus, options);
      const patternScore = this.scorePatternMatch(taskAnalysis, model, patterns);
      const performanceScore = await this.scorePerformance(model, taskAnalysis.task_type);

      // Calculate weighted total score
      const totalScore =
        (complexityScore * this.weights.complexity_match) +
        (budgetScore * this.weights.budget_constraint) +
        (patternScore * this.weights.pattern_match) +
        (performanceScore * this.weights.performance);

      // Estimate cost
      const estimatedCost = this.estimateCost(model, taskAnalysis.estimated_tokens);

      scores.push({
        model,
        complexity_score: complexityScore,
        budget_score: budgetScore,
        pattern_score: patternScore,
        performance_score: performanceScore,
        total_score: totalScore,
        estimated_cost: estimatedCost
      });
    }

    // Sort by total score (descending)
    scores.sort((a, b) => b.total_score - a.total_score);

    return scores;
  }

  /**
   * Score how well a model matches task complexity
   * @param {object} taskAnalysis - Task analysis
   * @param {object} model - Model to score
   * @returns {number} Score from 0.0 to 1.0
   */
  scoreComplexityMatch(taskAnalysis, model) {
    const complexity = taskAnalysis.complexity_score;
    const [minRange, maxRange] = model.complexity_range;

    // Perfect match if complexity is within model's ideal range
    if (complexity >= minRange && complexity <= maxRange) {
      return 1.0;
    }

    // Calculate distance from ideal range
    let distance;
    if (complexity < minRange) {
      distance = minRange - complexity;
    } else {
      distance = complexity - maxRange;
    }

    // Convert distance to score (0.0 to 1.0)
    // Max penalty of 0.5 for being outside range
    const score = Math.max(0.0, 1.0 - (distance * 2));

    // Bonus for model strengths matching task type
    if (model.strengths.includes(taskAnalysis.task_type)) {
      return Math.min(1.0, score + 0.2);
    }

    return score;
  }

  /**
   * Score based on budget constraints
   * @param {object} taskAnalysis - Task analysis
   * @param {object} model - Model to score
   * @param {object} budgetStatus - Current budget status
   * @param {object} options - Selection options
   * @returns {number} Score from 0.0 to 1.0
   */
  scoreBudgetConstraint(taskAnalysis, model, budgetStatus, options = {}) {
    const estimatedCost = this.estimateCost(model, taskAnalysis.estimated_tokens);

    // If max_cost specified in options
    if (options.max_cost && estimatedCost > options.max_cost) {
      return 0.0; // Disqualify if over budget
    }

    // Check if we're near budget limits
    const budgetRemaining = budgetStatus.daily_remaining || Infinity;
    const budgetUtilization = budgetStatus.daily_utilization || 0;

    // If budget is very tight (>80% utilized), strongly prefer cheaper models
    if (budgetUtilization > 0.8) {
      const costEfficiency = 1.0 - (estimatedCost / (budgetRemaining + 0.01));
      return Math.max(0.0, costEfficiency);
    }

    // If budget is comfortable, use inverse cost as score
    // Cheaper models score higher, but not dramatically
    const maxCost = 0.10; // $0.10 as reference high cost
    const costScore = 1.0 - Math.min(1.0, estimatedCost / maxCost);

    // Blend cost efficiency with availability
    const availabilityScore = budgetRemaining > estimatedCost * 10 ? 1.0 : 0.5;

    return (costScore * 0.7) + (availabilityScore * 0.3);
  }

  /**
   * Score based on historical pattern matching
   * @param {object} taskAnalysis - Task analysis
   * @param {object} model - Model to score
   * @param {object} patterns - Historical patterns
   * @returns {number} Score from 0.0 to 1.0
   */
  scorePatternMatch(taskAnalysis, model, patterns) {
    if (!patterns || !patterns.similar_tasks || patterns.similar_tasks.length === 0) {
      return 0.5; // Neutral score if no patterns
    }

    // Count how often this model was successfully used for similar tasks
    const modelUsage = patterns.similar_tasks.filter(task =>
      task.model === model.name && task.success === true
    );

    const totalSimilar = patterns.similar_tasks.length;
    const successfulWithModel = modelUsage.length;

    // Calculate success rate
    if (totalSimilar === 0) {
      return 0.5;
    }

    const successRate = successfulWithModel / totalSimilar;

    // Boost if this model is preferred for this task type
    const preferredForType = patterns.preferred_models?.[taskAnalysis.task_type] === model.name;

    return Math.min(1.0, successRate + (preferredForType ? 0.3 : 0.0));
  }

  /**
   * Score based on historical performance
   * @param {object} model - Model to score
   * @param {string} taskType - Task type
   * @returns {Promise<number>} Score from 0.0 to 1.0
   */
  async scorePerformance(model, taskType) {
    try {
      // Query historical performance for this model and task type
      const stmt = this.storage.db.prepare(`
        SELECT
          COUNT(*) as total,
          SUM(CASE WHEN was_successful = 1 THEN 1 ELSE 0 END) as successful,
          AVG(response_quality) as avg_quality
        FROM routing_decisions
        WHERE selected_model = ? AND task_type = ?
        AND timestamp >= datetime('now', '-30 days')
      `);

      const stats = stmt.get(model.name, taskType);

      if (!stats || stats.total === 0) {
        return 0.6; // Slight positive bias for untested models
      }

      // Calculate success rate
      const successRate = stats.successful / stats.total;

      // Include quality score if available
      const qualityScore = stats.avg_quality || 0.7;

      // Weighted combination
      return (successRate * 0.6) + (qualityScore * 0.4);
    } catch (error) {
      console.error('[ModelSelector] Error scoring performance:', error);
      return 0.5; // Neutral score on error
    }
  }

  /**
   * Estimate cost for a request
   * @param {object} model - Model to estimate cost for
   * @param {number} estimatedTokens - Estimated token count
   * @returns {number} Estimated cost in USD
   */
  estimateCost(model, estimatedTokens) {
    // Assume input:output ratio of 3:1 for most tasks
    const promptTokens = estimatedTokens * 0.75;
    const completionTokens = estimatedTokens * 0.25;

    const promptCost = (promptTokens / 1000) * model.cost_per_1k_prompt;
    const completionCost = (completionTokens / 1000) * model.cost_per_1k_completion;

    return promptCost + completionCost;
  }

  /**
   * Get human-readable selection reason
   * @param {object} score - Scored model
   * @param {object} taskAnalysis - Task analysis
   * @param {object} budgetStatus - Budget status
   * @returns {string} Selection reason
   */
  getSelectionReason(score, taskAnalysis, budgetStatus) {
    const reasons = [];

    // Primary reason based on highest contributing factor
    const factors = {
      complexity_match: score.complexity_score * this.weights.complexity_match,
      budget_constraint: score.budget_score * this.weights.budget_constraint,
      pattern_match: score.pattern_score * this.weights.pattern_match,
      performance: score.performance_score * this.weights.performance
    };

    const primaryFactor = Object.entries(factors).reduce((a, b) =>
      b[1] > a[1] ? b : a
    );

    // Build reason string
    if (primaryFactor[0] === 'complexity_match') {
      if (taskAnalysis.complexity_score > 0.7) {
        reasons.push('high complexity task');
      } else if (taskAnalysis.complexity_score < 0.3) {
        reasons.push('simple query');
      } else {
        reasons.push('balanced complexity');
      }

      if (score.model.strengths.includes(taskAnalysis.task_type)) {
        reasons.push(`optimized for ${taskAnalysis.task_type}`);
      }
    }

    if (primaryFactor[0] === 'budget_constraint' || budgetStatus.daily_utilization > 0.7) {
      reasons.push('cost-efficient');
    }

    if (primaryFactor[0] === 'pattern_match') {
      reasons.push('learned from similar tasks');
    }

    if (primaryFactor[0] === 'performance') {
      reasons.push('proven performance');
    }

    // Add quality tier
    reasons.push(`${score.model.quality_tier} tier`);

    return reasons.join(', ');
  }

  /**
   * Get budget status for an agent
   * @param {string} agentWallet - Agent wallet address
   * @returns {Promise<object>} Budget status
   */
  async getBudgetStatus(agentWallet) {
    try {
      // This would integrate with Cost Governor
      // For now, return default values
      return {
        daily_limit: 10.0,
        daily_spent: 0.0,
        daily_remaining: 10.0,
        daily_utilization: 0.0,
        circuit_breaker_active: false
      };
    } catch (error) {
      console.error('[ModelSelector] Error getting budget status:', error);
      return {
        daily_limit: 10.0,
        daily_spent: 0.0,
        daily_remaining: 10.0,
        daily_utilization: 0.0,
        circuit_breaker_active: false
      };
    }
  }

  /**
   * Get historical patterns for similar tasks
   * @param {string} agentWallet - Agent wallet address
   * @param {object} taskAnalysis - Current task analysis
   * @returns {Promise<object>} Historical patterns
   */
  async getHistoricalPatterns(agentWallet, taskAnalysis) {
    try {
      // Find similar tasks based on type and complexity
      const stmt = this.storage.db.prepare(`
        SELECT *
        FROM routing_decisions
        WHERE agent_wallet = ?
          AND task_type = ?
          AND ABS(task_complexity - ?) < 0.2
          AND timestamp >= datetime('now', '-30 days')
        ORDER BY timestamp DESC
        LIMIT 20
      `);

      const similar = stmt.all(
        agentWallet,
        taskAnalysis.task_type,
        taskAnalysis.complexity_score
      );

      // Get preferred models by task type
      const preferredStmt = this.storage.db.prepare(`
        SELECT
          task_type,
          selected_model,
          COUNT(*) as usage_count
        FROM routing_decisions
        WHERE agent_wallet = ?
          AND was_successful = 1
          AND timestamp >= datetime('now', '-30 days')
        GROUP BY task_type, selected_model
        ORDER BY task_type, usage_count DESC
      `);

      const preferred = preferredStmt.all(agentWallet);

      // Build preferred models map
      const preferredModels = {};
      for (const row of preferred) {
        if (!preferredModels[row.task_type]) {
          preferredModels[row.task_type] = row.selected_model;
        }
      }

      return {
        similar_tasks: similar.map(s => ({
          model: s.selected_model,
          success: Boolean(s.was_successful),
          quality_score: s.response_quality
        })),
        preferred_models: preferredModels
      };
    } catch (error) {
      console.error('[ModelSelector] Error getting historical patterns:', error);
      return {
        similar_tasks: [],
        preferred_models: {}
      };
    }
  }

  /**
   * Store model selection for learning
   * @param {string} agentWallet - Agent wallet address
   * @param {object} taskAnalysis - Task analysis
   * @param {object} selection - Model selection
   * @returns {Promise<void>}
   */
  async storeSelection(agentWallet, taskAnalysis, selection) {
    try {
      const stmt = this.storage.db.prepare(`
        INSERT INTO routing_decisions (
          decision_id, agent_wallet, timestamp,
          task_complexity, context_length, task_type,
          has_code, has_errors, has_data,
          selected_model, selected_provider, selection_reason,
          confidence_score, alternatives_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run(
        selection.selection_id,
        agentWallet,
        selection.timestamp,
        taskAnalysis.complexity_score,
        taskAnalysis.estimated_tokens,
        taskAnalysis.task_type,
        taskAnalysis.has_code ? 1 : 0,
        taskAnalysis.has_errors ? 1 : 0,
        taskAnalysis.has_data || 0,
        selection.model,
        selection.provider,
        selection.reason,
        selection.confidence,
        JSON.stringify(selection.alternatives || [])
      );
    } catch (error) {
      console.error('[ModelSelector] Error storing selection:', error);
    }
  }

  /**
   * Update selection with actual results (for learning)
   * @param {string} selectionId - Selection ID (decision_id)
   * @param {object} results - Actual results
   * @returns {Promise<void>}
   */
  async updateSelectionResults(selectionId, results) {
    try {
      const stmt = this.storage.db.prepare(`
        UPDATE routing_decisions
        SET
          actual_tokens = ?,
          actual_cost_usd = ?,
          was_successful = ?,
          response_quality = ?,
          response_time_ms = ?
        WHERE decision_id = ?
      `);

      stmt.run(
        results.actual_tokens || null,
        results.actual_cost || null,
        results.success ? 1 : 0,
        results.quality_score || null,
        results.response_time_ms || null,
        selectionId
      );
    } catch (error) {
      console.error('[ModelSelector] Error updating selection results:', error);
    }
  }

  /**
   * Get model by name
   * @param {string} modelName - Model name
   * @returns {object|null} Model definition or null
   */
  getModel(modelName) {
    return this.models[modelName] || null;
  }

  /**
   * Get all available models
   * @returns {Array<object>} Array of model definitions
   */
  getAllModels() {
    return Object.values(this.models);
  }
}
