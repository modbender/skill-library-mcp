/**
 * OpenClaw Smart Router - Main Orchestrator
 *
 * Intelligent model selection for OpenClaw agents
 * Automatically routes to optimal models based on complexity, budget, and learned patterns
 *
 * Features:
 * - Task complexity analysis
 * - Intelligent model selection (cost vs. quality optimization)
 * - Pattern learning from successful decisions
 * - Cost savings tracking & ROI analysis
 * - Quota management (free: 100/day, pro: unlimited)
 * - x402 payment protocol (0.5 USDT/month for Pro tier)
 */

import { homedir } from 'os';
import { join } from 'path';
import { mkdirSync, existsSync } from 'fs';
import { randomUUID } from 'crypto';
import { RouterStorage } from './storage.js';
import { TaskAnalyzer } from './analyzer.js';
import { ModelSelector } from './selector.js';
import { PatternLearner } from './learner.js';
import { X402PaymentHandler } from './x402.js';

export class SmartRouter {
  constructor(options = {}) {
    this.dataDir = options.dataDir || join(homedir(), '.openclaw', 'openclaw-smart-router');
    if (!existsSync(this.dataDir)) {
      mkdirSync(this.dataDir, { recursive: true });
    }

    this.dbPath = join(this.dataDir, 'smart-router.db');
    this.storage = new RouterStorage(this.dbPath);
    this.analyzer = new TaskAnalyzer(this.storage);
    this.selector = new ModelSelector(this.storage);
    this.learner = new PatternLearner(this.storage);
    this.x402 = new X402PaymentHandler(this.storage);

    console.log(`[SmartRouter] Initialized at ${this.dataDir}`);
  }

  /**
   * Before request hook - analyze task and select optimal model
   * Called BEFORE sending request to provider
   *
   * @param {string} requestId - Unique request ID
   * @param {string} agentWallet - Agent wallet address
   * @param {object} requestData - Request data (prompt, context, etc.)
   * @returns {Promise<object>} Selected model and routing decision
   */
  async beforeRequest(requestId, agentWallet, requestData) {
    try {
      // Check quota availability
      const quotaCheck = this.x402.checkAndIncrementQuota(agentWallet);
      if (!quotaCheck.available) {
        console.log(`[SmartRouter] Quota exceeded for ${agentWallet}`);
        throw new Error(quotaCheck.message || 'Daily quota exceeded. Upgrade to Pro for unlimited routing.');
      }

      // Analyze the task
      const taskAnalysis = await this.analyzer.analyzeTask(requestData);

      // Select optimal model
      const modelSelection = await this.selector.selectModel(taskAnalysis, agentWallet, {
        max_cost: requestData.max_cost,
        force_model: requestData.force_model,
        exclude_models: requestData.exclude_models
      });

      // Record routing decision
      const decisionId = randomUUID();
      this.storage.recordDecision({
        decision_id: decisionId,
        agent_wallet: agentWallet,
        task_complexity: taskAnalysis.complexity_score,
        context_length: taskAnalysis.estimated_tokens,
        task_type: taskAnalysis.task_type,
        has_code: taskAnalysis.has_code,
        has_errors: taskAnalysis.has_errors,
        has_data: taskAnalysis.has_reasoning, // Using has_reasoning for has_data
        selected_model: modelSelection.model,
        selected_provider: modelSelection.provider,
        selection_reason: modelSelection.reason,
        confidence_score: modelSelection.confidence,
        alternatives_json: JSON.stringify(modelSelection.alternatives || []),
        pattern_id: null // Will be linked later if pattern is created
      });

      // Update requestData with selected model
      requestData.model = modelSelection.model;
      requestData.provider = modelSelection.provider;

      // Store decision ID for later use in afterRequest
      requestData._routing_decision_id = decisionId;
      requestData._routing_analysis = taskAnalysis;

      console.log(`[SmartRouter] Selected ${modelSelection.model} for request ${requestId}`);
      console.log(`  Complexity: ${taskAnalysis.complexity_score.toFixed(2)}, Task: ${taskAnalysis.task_type}`);
      console.log(`  Reason: ${modelSelection.reason}`);
      console.log(`  Quota remaining: ${quotaCheck.remaining === -1 ? 'unlimited' : quotaCheck.remaining}`);

      return {
        decision_id: decisionId,
        selected_model: modelSelection.model,
        selected_provider: modelSelection.provider,
        task_analysis: taskAnalysis,
        selection_details: modelSelection,
        quota_status: quotaCheck
      };
    } catch (error) {
      console.error('[SmartRouter] Error in beforeRequest:', error.message);
      throw error;
    }
  }

  /**
   * After request hook - learn from outcome
   * Called AFTER receiving response from provider
   *
   * @param {string} requestId - Request ID
   * @param {string} agentWallet - Agent wallet address
   * @param {object} request - Original request data
   * @param {object} response - Provider response
   * @returns {Promise<void>}
   */
  async afterRequest(requestId, agentWallet, request, response) {
    try {
      const decisionId = request._routing_decision_id;
      if (!decisionId) {
        console.log('[SmartRouter] No routing decision found for request');
        return;
      }

      // Determine success
      const wasSuccessful = response.status !== 'error' &&
                          (response.content || response.text || response.message);

      // Extract actual token usage
      const actualTokens = response.usage?.total_tokens ||
                          response.usage?.prompt_tokens + response.usage?.completion_tokens ||
                          request._routing_analysis?.estimated_tokens || 0;

      // Calculate actual cost
      const actualCost = this.calculateActualCost(
        request.model || request._routing_decision?.selected_model,
        response.usage
      );

      // Assess quality
      const quality = this.assessResponseQuality(response, wasSuccessful);

      // Extract response time if available
      const responseTime = response.response_time_ms ||
                          response.latency ||
                          response.elapsed_ms ||
                          null;

      // Create outcome object
      const outcome = {
        success: wasSuccessful,
        actual_tokens: actualTokens,
        actual_cost: actualCost,
        quality: quality,
        response_time_ms: responseTime
      };

      // Learn from the outcome
      await this.learner.learnFromOutcome(decisionId, outcome);

      console.log(`[SmartRouter] Learned from request ${requestId}`);
      console.log(`  Success: ${wasSuccessful}, Quality: ${quality.toFixed(2)}, Cost: $${actualCost.toFixed(4)}`);
    } catch (error) {
      console.error('[SmartRouter] Error in afterRequest:', error.message);
    }
  }

  /**
   * Session end hook - analyze and report savings
   * Called at the end of an agent session
   *
   * @param {string} sessionId - Session ID
   * @param {string} agentWallet - Agent wallet address
   * @returns {Promise<void>}
   */
  async sessionEnd(sessionId, agentWallet) {
    try {
      // Analyze savings over last 30 days
      const savingsAnalysis = await this.learner.analyzeSavings(agentWallet, '30');

      // Get license status
      const license = this.x402.hasValidLicense(agentWallet);

      // Get quota status
      const quotaStatus = this.x402.getQuotaStatus(agentWallet);

      console.log(`\n========================================`);
      console.log(`[SmartRouter] Session ${sessionId} ended`);
      console.log(`========================================`);
      console.log(`  Agent: ${agentWallet.substring(0, 10)}...`);
      console.log(`  Timeframe: ${savingsAnalysis.timeframe}`);
      console.log(``);
      console.log(`  📊 Routing Statistics:`);
      console.log(`    Total decisions: ${savingsAnalysis.total_decisions}`);
      console.log(`    Actual cost: $${savingsAnalysis.total_cost.toFixed(4)}`);
      console.log(`    Default cost (Opus): $${savingsAnalysis.estimated_default_cost.toFixed(4)}`);
      console.log(`    Avg cost per decision: $${savingsAnalysis.avg_cost_per_decision.toFixed(4)}`);
      console.log(``);
      console.log(`  💰 Cost Savings:`);
      console.log(`    Total saved: $${savingsAnalysis.total_savings.toFixed(4)}`);
      console.log(`    Savings rate: ${savingsAnalysis.savings_percentage.toFixed(1)}%`);
      console.log(`    ROI: ${savingsAnalysis.total_savings > 0.5 ? 'POSITIVE ✓' : 'Building...'}`);
      console.log(``);
      console.log(`  📋 Quota Status:`);
      console.log(`    Tier: ${quotaStatus.tier.toUpperCase()}`);
      console.log(`    Today: ${quotaStatus.decisions_today} decisions`);
      if (quotaStatus.decisions_limit === -1) {
        console.log(`    Limit: Unlimited`);
      } else {
        console.log(`    Remaining: ${quotaStatus.remaining}/${quotaStatus.decisions_limit}`);
      }

      if (license.valid) {
        console.log(``);
        console.log(`  🎫 License:`);
        console.log(`    Status: Pro (Active)`);
        console.log(`    Expires: ${license.expires}`);
        console.log(`    Days remaining: ${license.days_remaining}`);
      } else {
        console.log(``);
        console.log(`  🎫 License:`);
        console.log(`    Status: Free tier`);
        console.log(`    Upgrade to Pro: 0.5 USDT/month`);
        console.log(`    Benefits: Unlimited decisions + ML-enhanced routing`);
      }

      console.log(`========================================\n`);
    } catch (error) {
      console.error('[SmartRouter] Error in sessionEnd:', error.message);
    }
  }

  /**
   * Calculate actual cost from usage data
   */
  calculateActualCost(model, usage) {
    if (!usage || !model) {
      return 0;
    }

    const pricing = this.storage.getPricing(this.getProviderForModel(model), model);

    const inputTokens = usage.prompt_tokens || usage.input_tokens || 0;
    const outputTokens = usage.completion_tokens || usage.output_tokens || 0;

    const inputCost = (inputTokens / 1000) * (pricing.cost_per_1k_prompt || 0);
    const outputCost = (outputTokens / 1000) * (pricing.cost_per_1k_completion || 0);

    return inputCost + outputCost;
  }

  /**
   * Assess response quality (0.0 to 1.0)
   */
  assessResponseQuality(response, wasSuccessful) {
    if (!wasSuccessful) {
      return 0.3; // Base quality for failed responses
    }

    let score = 0.5; // Base quality

    const content = response.content || response.text || response.message || '';

    // Has meaningful content
    if (content.length > 50) {
      score += 0.2;
    }

    // Content is substantial but not excessively long
    if (content.length > 200 && content.length < 10000) {
      score += 0.2;
    }

    // No error indicators
    if (!response.error && response.status !== 'error') {
      score += 0.1;
    }

    return Math.min(1.0, score);
  }

  /**
   * Get provider for a model name
   */
  getProviderForModel(model) {
    if (model.includes('claude')) return 'anthropic';
    if (model.includes('gpt')) return 'openai';
    if (model.includes('gemini')) return 'google';
    return 'unknown';
  }

  /**
   * Get routing statistics for an agent
   */
  async getStats(agentWallet, timeframe = '30 days') {
    try {
      const routingStats = this.storage.getRoutingStats(agentWallet, timeframe);
      const quotaStatus = this.x402.getQuotaStatus(agentWallet);
      const savingsAnalysis = await this.learner.analyzeSavings(agentWallet, timeframe);
      const patterns = this.learner.getTopPatterns(agentWallet, 10);
      const modelComparison = this.learner.getModelComparison(agentWallet);

      return {
        routing: routingStats,
        quota: quotaStatus,
        savings: savingsAnalysis,
        patterns: patterns,
        models: modelComparison,
        timeframe: timeframe
      };
    } catch (error) {
      throw new Error(`Failed to get stats: ${error.message}`);
    }
  }

  /**
   * Get learning insights for an agent
   */
  async getInsights(agentWallet) {
    try {
      return await this.learner.getLearningInsights(agentWallet);
    } catch (error) {
      throw new Error(`Failed to get insights: ${error.message}`);
    }
  }

  /**
   * Test model selection for a query (without recording)
   */
  async testSelection(query, agentWallet) {
    try {
      const requestData = { prompt: query };
      const taskAnalysis = await this.analyzer.analyzeTask(requestData);
      const modelSelection = await this.selector.selectModel(taskAnalysis, agentWallet);

      return {
        query: query,
        task_analysis: taskAnalysis,
        model_selection: modelSelection
      };
    } catch (error) {
      throw new Error(`Failed to test selection: ${error.message}`);
    }
  }

  /**
   * x402 Payment Methods
   */

  async createPaymentRequest(agentWallet) {
    try {
      return await this.x402.createPaymentRequest(agentWallet);
    } catch (error) {
      throw new Error(`Failed to create payment request: ${error.message}`);
    }
  }

  async verifyPayment(requestId, txHash, agentWallet) {
    try {
      return await this.x402.verifyPayment(requestId, txHash, agentWallet);
    } catch (error) {
      throw new Error(`Failed to verify payment: ${error.message}`);
    }
  }

  checkLicense(agentWallet) {
    try {
      return this.x402.hasValidLicense(agentWallet);
    } catch (error) {
      throw new Error(`Failed to check license: ${error.message}`);
    }
  }

  getQuotaStatus(agentWallet) {
    try {
      return this.x402.getQuotaStatus(agentWallet);
    } catch (error) {
      throw new Error(`Failed to get quota status: ${error.message}`);
    }
  }

  /**
   * Get all patterns for an agent
   */
  getPatterns(agentWallet) {
    try {
      return this.storage.getPatterns(agentWallet);
    } catch (error) {
      throw new Error(`Failed to get patterns: ${error.message}`);
    }
  }

  /**
   * Get model performance data
   */
  getModelPerformance(agentWallet, taskType = null) {
    try {
      return this.storage.getModelPerformanceAll(agentWallet, taskType);
    } catch (error) {
      throw new Error(`Failed to get model performance: ${error.message}`);
    }
  }

  /**
   * Cleanup and close database
   */
  close() {
    if (this.storage) {
      this.storage.close();
    }
  }
}

// Singleton instance management
let instance;

export function getSmartRouter(options = {}) {
  if (!instance) {
    instance = new SmartRouter(options);
  }
  return instance;
}

export function resetSmartRouter() {
  if (instance) {
    instance.close();
    instance = null;
  }
}

// Export all modules for direct use
export { RouterStorage } from './storage.js';
export { TaskAnalyzer } from './analyzer.js';
export { ModelSelector } from './selector.js';
export { PatternLearner } from './learner.js';
export { X402PaymentHandler } from './x402.js';

export default SmartRouter;
