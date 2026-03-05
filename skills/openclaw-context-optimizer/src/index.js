/**
 * OpenClaw Context Optimizer - Main Orchestrator
 *
 * Intelligent context compression for OpenClaw agents
 * Reduces token usage by 40-60% through smart summarization,
 * deduplication, and pattern learning.
 *
 * Features:
 * - Context compression (summary, dedup, prune, hybrid strategies)
 * - Token usage tracking & savings analytics
 * - Pattern learning (redundant/high-value detection)
 * - Quality feedback & adaptive optimization
 * - Quota management (free: 100/day, pro: unlimited)
 * - x402 payment protocol (0.5 USDT/month for Pro tier)
 */

import { homedir } from 'os';
import { join } from 'path';
import { mkdirSync, existsSync } from 'fs';
import { randomUUID } from 'crypto';
import { ContextStorage } from './storage.js';
import { ContextCompressor } from './compressor.js';
import { ContextAnalyzer } from './analyzer.js';
import { X402PaymentHandler } from './x402.js';

export class ContextOptimizer {
  constructor(options = {}) {
    this.dataDir = options.dataDir || join(homedir(), '.openclaw', 'openclaw-context-optimizer');
    if (!existsSync(this.dataDir)) {
      mkdirSync(this.dataDir, { recursive: true });
    }

    this.dbPath = join(this.dataDir, 'context-optimizer.db');
    this.storage = new ContextStorage(this.dbPath);
    this.compressor = new ContextCompressor(this.storage);
    this.analyzer = new ContextAnalyzer(this.storage);
    this.x402 = new X402PaymentHandler(this.storage);

    console.log(`[ContextOptimizer] Initialized`);
  }

  async beforeRequest(requestId, agentWallet, requestData) {
    try {
      const context = requestData.context || requestData.prompt || requestData.query || '';
      if (!context || typeof context !== 'string') return;

      // Check quota
      const quotaCheck = this.storage.checkQuotaAvailable(agentWallet);
      if (!quotaCheck.available) {
        console.log(`[ContextOptimizer] Quota exceeded for ${agentWallet}`);
        return;
      }

      // Compress context
      const result = await this.compressor.compress(context, 'hybrid');

      if (result && result.compressed) {
        // Update request data with compressed context
        if (typeof requestData.context === 'string') {
          requestData.context = result.compressed;
        } else if (requestData.prompt) {
          requestData.prompt = result.compressed;
        }

        // Store compression metrics for later use
        requestData._compression_metrics = {
          original_length: result.metrics.originalTokens,
          compressed_length: result.metrics.compressedTokens,
          tokens_saved: result.metrics.tokensRemoved,
          compression_ratio: result.metrics.compressionRatio
        };

        // Record compression session
        this.storage.recordCompressionSession({
          session_id: randomUUID(),
          agent_wallet: agentWallet,
          original_tokens: result.metrics.originalTokens,
          compressed_tokens: result.metrics.compressedTokens,
          compression_ratio: result.metrics.compressionRatio,
          tokens_saved: result.metrics.tokensRemoved,
          cost_saved_usd: (result.metrics.tokensRemoved / 1000) * 0.002,
          strategy_used: result.strategy,
          quality_score: result.metrics.qualityScore
        });

        // Increment compression count
        this.storage.incrementCompressionCount(agentWallet);

        console.log(`[ContextOptimizer] Compressed context for request ${requestId}`);
        console.log(`  Tokens saved: ${result.metrics.tokensRemoved} (${result.metrics.percentageReduction}%)`);
      }
    } catch (error) {
      console.error('[ContextOptimizer] Error in beforeRequest:', error.message);
    }
  }

  async afterRequest(requestId, agentWallet, request, response) {
    try {
      const metrics = request._compression_metrics;
      if (!metrics) return;

      const responseText = response.content || response.text || response.message || '';
      const wasSuccessful = response.status !== 'error' && responseText.length > 0;

      // Record quality feedback
      const sessionId = randomUUID();
      this.storage.recordFeedback(
        sessionId,
        wasSuccessful ? 'success' : 'failure',
        wasSuccessful ? 0.8 : 0.3,
        null
      );

      // Update token stats
      this.storage.updateTokenStats(
        agentWallet,
        metrics.original_length,
        metrics.compressed_length,
        (metrics.tokens_saved / 1000) * 0.002
      );

      console.log(`[ContextOptimizer] Recorded feedback for request ${requestId}`);
    } catch (error) {
      console.error('[ContextOptimizer] Error in afterRequest:', error.message);
    }
  }

  async sessionEnd(sessionId, agentWallet) {
    try {
      const stats = this.storage.getTotalSavings(agentWallet);
      const license = this.x402.hasValidLicense(agentWallet);

      console.log(`\n[ContextOptimizer] Session ${sessionId} complete`);
      console.log(`  Total compressions: ${stats.total_compressions || 0}`);
      console.log(`  Total tokens saved: ${(stats.total_tokens_saved || 0).toLocaleString()}`);
      console.log(`  Estimated cost saved: $${(stats.total_cost_saved || 0).toFixed(4)}`);

      if (license.valid) {
        console.log(`  License: Pro (${license.days_remaining} days remaining)`);
      } else {
        console.log(`  License: Free tier`);
      }
    } catch (error) {
      console.error('[ContextOptimizer] Error in sessionEnd:', error.message);
    }
  }

  async compress(text, agentWallet, strategy = 'hybrid') {
    try {
      const quotaCheck = this.storage.checkQuotaAvailable(agentWallet);
      if (!quotaCheck.available) {
        throw new Error('Compression quota exceeded. Upgrade to Pro for unlimited compressions.');
      }

      const result = await this.compressor.compress(text, strategy);
      this.storage.incrementCompressionCount(agentWallet);

      // Map to expected return format (matches CLI expectations)
      return {
        session_id: randomUUID(),
        strategy: strategy,
        compressed: result.compressed,
        metrics: {
          originalTokens: result.metrics.originalTokens,
          compressedTokens: result.metrics.compressedTokens,
          tokensRemoved: result.metrics.tokensRemoved,
          compressionRatio: result.metrics.compressionRatio,
          qualityScore: result.metrics.qualityScore,
          percentageReduction: result.metrics.percentageReduction
        }
      };
    } catch (error) {
      throw new Error(`Failed to compress: ${error.message}`);
    }
  }

  async compressContext(agentWallet, context, strategy = 'hybrid') {
    return await this.compress(context, agentWallet, strategy);
  }

  async getCompressionStats(agentWallet, timeframe = '30 days') {
    try {
      const stats = this.storage.getCompressionStats(agentWallet, timeframe);
      const quota = this.storage.getQuota(agentWallet);
      const strategyStats = this.storage.getStrategyStats(agentWallet, timeframe);

      return {
        ...stats,
        quota: {
          tier: quota.tier,
          compressions_today: quota.compressions_today,
          compression_limit: quota.compression_limit,
          remaining: quota.compression_limit === -1 ? -1 : quota.compression_limit - quota.compressions_today
        },
        strategies: strategyStats
      };
    } catch (error) {
      throw new Error(`Failed to get compression stats: ${error.message}`);
    }
  }

  async recordFeedback(sessionId, feedbackType, score, notes = null) {
    try {
      this.storage.recordFeedback(sessionId, feedbackType, score, notes);
      return { success: true };
    } catch (error) {
      throw new Error(`Failed to record feedback: ${error.message}`);
    }
  }

  async getStats(agentWallet) {
    try {
      const total = this.storage.getTotalSavings(agentWallet);
      const quota = this.storage.getQuota(agentWallet);
      const patterns = this.storage.getTopPatterns(agentWallet, 10);

      return {
        total_compressions: total.total_compressions || 0,
        total_tokens_saved: total.total_tokens_saved || 0,
        total_cost_saved: total.total_cost_saved || 0,
        avg_compression_ratio: total.overall_avg_ratio || 0,
        tier: quota.tier,
        quota_remaining: quota.compression_limit === -1 ? -1 : (quota.compression_limit - quota.compressions_today),
        learned_patterns: patterns
      };
    } catch (error) {
      throw new Error(`Failed to get stats: ${error.message}`);
    }
  }

  async getPatterns(agentWallet) {
    try {
      return this.storage.getPatterns(agentWallet);
    } catch (error) {
      throw new Error(`Failed to get patterns: ${error.message}`);
    }
  }

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

  close() {
    if (this.storage) {
      this.storage.close();
    }
  }
}

let instance;

export function getContextOptimizer(options = {}) {
  if (!instance) {
    instance = new ContextOptimizer(options);
  }
  return instance;
}

export function resetContextOptimizer() {
  if (instance) {
    instance.close();
    instance = null;
  }
}

export { ContextStorage } from './storage.js';
export { ContextCompressor } from './compressor.js';
export { ContextAnalyzer } from './analyzer.js';
export { X402PaymentHandler } from './x402.js';
export { setup } from './setup.js';

export default ContextOptimizer;
