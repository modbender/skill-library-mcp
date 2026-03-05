/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║  YIELD — The Conversational Compounding Engine                          ║
 * ║                                                                         ║
 * ║  "Every message is an investment. Yield makes them compound."           ║
 * ║                                                                         ║
 * ║  Zero dependencies. Zero API calls. Zero cost. Maximum revenue lift.    ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * YIELD treats conversations like financial portfolios, tracking five
 * classes of psychological assets that compound, decay, and interact:
 *
 *   Trust       — Compounds slowly, like government bonds
 *   Commitment  — Stacks and locks, like real estate equity
 *   Urgency     — Decays rapidly, like options contracts
 *   Curiosity   — Pulls forward, like futures contracts
 *   Authority   — Grows with proof, like blue-chip stocks
 *
 * Usage:
 *   import { YieldEngine } from '@openbrawl/yield';
 *   const engine = new YieldEngine();
 *   const analysis = engine.processMessage('Tell me more!', 'conv-123');
 */

import { detectSignals, getSignalTypes, SIGNAL_PATTERNS } from './signals.js';
import { Portfolio } from './portfolio.js';
import {
  selectStrategy,
  generateContextualDirective,
  getStrategyNames,
  STRATEGIES,
} from './strategy.js';

// ─── Yield Engine ────────────────────────────────────────────────────────────

export class YieldEngine {
  /**
   * Create a new Yield Engine.
   *
   * @param {Object} [config={}] - Optional portfolio configuration overrides
   */
  constructor(config = {}) {
    this.config = config;
    this.conversations = new Map();  // conversationId → { portfolio, messageHistory }
  }

  /**
   * Process an inbound user message and return the full YIELD analysis.
   *
   * This is the main entry point. Call it on every user message.
   *
   * @param {string} message - The user's message text
   * @param {string} [conversationId='default'] - Unique conversation identifier
   * @returns {YieldAnalysis} Complete analysis with signals, portfolio, strategy
   */
  processMessage(message, conversationId = 'default') {
    // Get or create conversation state
    const conv = this._getConversation(conversationId);

    // Phase 1: Signal Detection
    const signals = detectSignals(message, conv.messageHistory);

    // Phase 2: Portfolio Update (compounding happens here)
    const portfolioState = conv.portfolio.applySignals(signals);

    // Phase 3: Strategy Selection
    const strategyResult = selectStrategy(portfolioState);
    const contextualDirective = generateContextualDirective(portfolioState);

    // Update message history for meta-signal detection
    conv.messageHistory.push(message);

    // Keep history bounded (last 20 messages)
    if (conv.messageHistory.length > 20) {
      conv.messageHistory = conv.messageHistory.slice(-20);
    }

    return {
      // Phase 1 output
      signals: signals.map(s => ({ type: s.type, category: s.category || 'meta', confidence: s.confidence })),
      signalCount: signals.length,

      // Phase 2 output
      portfolio: portfolioState.assets,
      totalYield: portfolioState.totalYield,
      peakYield: portfolioState.peakYield,
      messageCount: portfolioState.messageCount,

      // Phase 3 output
      strategy: strategyResult.strategy,
      directive: strategyResult.directive,
      contextualDirective,
      confidence: strategyResult.confidence,
      alternates: strategyResult.alternates || [],

      // Critical alerts
      inversion: portfolioState.inversion.inverted,
      inversionSeverity: portfolioState.inversion.severity,
      turnsUntilAbandon: portfolioState.inversion.turnsUntilAbandon,
      conversionWindow: portfolioState.conversionWindow.open,
      conversionStrength: portfolioState.conversionWindow.strength,
      conversionReason: portfolioState.conversionWindow.reason,
    };
  }

  /**
   * Get the current state of a conversation without processing a new message.
   *
   * @param {string} conversationId
   * @returns {Object|null} Portfolio state or null if conversation doesn't exist
   */
  peek(conversationId) {
    const conv = this.conversations.get(conversationId);
    if (!conv) return null;

    const state = conv.portfolio.getState();
    const strategy = selectStrategy(state);

    return {
      portfolio: state.assets,
      totalYield: state.totalYield,
      strategy: strategy.strategy,
      directive: strategy.directive,
      inversion: state.inversion,
      conversionWindow: state.conversionWindow,
      messageCount: state.messageCount,
    };
  }

  /**
   * Reset a conversation's portfolio to initial state.
   *
   * @param {string} conversationId
   */
  reset(conversationId) {
    this.conversations.delete(conversationId);
  }

  /**
   * Get all active conversation IDs.
   *
   * @returns {string[]}
   */
  getActiveConversations() {
    return Array.from(this.conversations.keys());
  }

  /**
   * Export a conversation's state for persistence.
   *
   * @param {string} conversationId
   * @returns {Object|null} Serializable state
   */
  exportConversation(conversationId) {
    const conv = this.conversations.get(conversationId);
    if (!conv) return null;

    return {
      conversationId,
      portfolio: conv.portfolio.toJSON(),
      messageHistory: conv.messageHistory,
      exportedAt: Date.now(),
    };
  }

  /**
   * Import a previously exported conversation state.
   *
   * @param {Object} data - Previously exported state
   */
  importConversation(data) {
    if (!data || !data.conversationId || !data.portfolio) {
      throw new Error('Invalid conversation data');
    }

    this.conversations.set(data.conversationId, {
      portfolio: Portfolio.fromJSON(data.portfolio, this.config),
      messageHistory: data.messageHistory || [],
    });
  }

  /**
   * Get aggregate statistics across all conversations.
   *
   * @returns {Object} Engine-wide statistics
   */
  getStats() {
    let totalConversations = 0;
    let totalMessages = 0;
    let totalConversions = 0;
    let totalInversions = 0;
    let avgYield = 0;

    for (const [, conv] of this.conversations) {
      totalConversations++;
      const state = conv.portfolio.getState();
      totalMessages += state.messageCount;
      avgYield += state.totalYield;
      if (state.conversionWindow.open) totalConversions++;
      if (state.inversion.inverted) totalInversions++;
    }

    return {
      totalConversations,
      totalMessages,
      conversionsOpen: totalConversions,
      inversionsActive: totalInversions,
      avgYield: totalConversations > 0
        ? Math.round((avgYield / totalConversations) * 1000) / 1000
        : 0,
    };
  }

  /** @private */
  _getConversation(conversationId) {
    if (!this.conversations.has(conversationId)) {
      this.conversations.set(conversationId, {
        portfolio: new Portfolio(this.config),
        messageHistory: [],
      });
    }
    return this.conversations.get(conversationId);
  }
}

// ─── Convenience: Standalone Functions ───────────────────────────────────────

/**
 * Quick one-shot analysis of a single message (no conversation tracking).
 * Useful for testing or stateless environments.
 *
 * @param {string} message
 * @returns {Object} Basic signal analysis
 */
export function analyzeMessage(message) {
  const signals = detectSignals(message);
  return {
    signals: signals.map(s => s.type),
    signalCount: signals.length,
    dominantSignal: signals.length > 0 ? signals[0].type : null,
  };
}

// ─── Re-exports ──────────────────────────────────────────────────────────────

export { detectSignals, getSignalTypes, SIGNAL_PATTERNS } from './signals.js';
export { Portfolio } from './portfolio.js';
export {
  selectStrategy,
  generateContextualDirective,
  getStrategyNames,
  STRATEGIES,
} from './strategy.js';
