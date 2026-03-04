/**
 * Session Pruner - Intelligent Session Pruning Logic
 *
 * Implements multi-tier pruning strategy:
 * - Tier 1: Age-based (Conservative)
 * - Tier 2: Token-based (Aggressive)
 * - Tier 3: Smart pruning based on importance
 */

const fs = require('fs');
const path = require('path');

class SessionPruner {
  constructor(monitor, config = {}) {
    this.monitor = monitor;
    this.config = {
      maxSessionAge: config.maxSessionAge || 7, // days
      maxContextTokens: config.maxContextTokens || 160000,
      keepRecentHours: config.keepRecentHours || 24,
      keepMinimumSessions: config.keepMinimumSessions || 5,
      minMessagesForImportant: config.minMessagesForImportant || 10,
      preservePinned: config.preservePinned !== false,
      preserveHighEngagement: config.preserveHighEngagement !== false,
      ...config
    };

    this.pruneLog = [];
  }

  /**
   * Execute pruning based on current context usage
   * @param {string} strategy - 'conservative', 'moderate', 'aggressive', 'emergency'
   * @returns {Promise<Object>} Pruning results
   */
  async prune(strategy = 'moderate') {
    const usage = await this.monitor.getContextUsage();
    const sessions = usage.sessions;

    const pruneTargets = this._selectPruneTargets(sessions, strategy, usage.utilizationPercent);

    const results = {
      strategy,
      sessionsPruned: 0,
      tokensFreed: 0,
      sessionsPreserved: sessions.length - pruneTargets.length,
      prunedSessions: []
    };

    for (const session of pruneTargets) {
      try {
        // Delete session file
        await fs.promises.unlink(session.path);

        results.sessionsPruned++;
        results.tokensFreed += session.tokenCount;
        results.prunedSessions.push({
          id: session.sessionId,
          tokens: session.tokenCount,
          messages: session.messageCount,
          age: this._getAge(session.lastActive)
        });

        this._logPrune(session, strategy);
      } catch (error) {
        console.error(`Failed to prune session ${session.sessionId}:`, error.message);
      }
    }

    return results;
  }

  /**
   * Select sessions to prune based on strategy
   * @private
   */
  _selectPruneTargets(sessions, strategy, utilizationPercent) {
    // Filter out protected sessions
    const prunableSessions = sessions.filter(s => !this._isProtected(s));

    if (prunableSessions.length === 0) {
      return [];
    }

    switch (strategy) {
      case 'conservative':
        return this._conservativePrune(prunableSessions);

      case 'moderate':
        return this._moderatePrune(prunableSessions, utilizationPercent);

      case 'aggressive':
        return this._aggressivePrune(prunableSessions, utilizationPercent);

      case 'emergency':
        return this._emergencyPrune(prunableSessions);

      default:
        return this._moderatePrune(prunableSessions, utilizationPercent);
    }
  }

  /**
   * Conservative pruning: Only remove old sessions
   * @private
   */
  _conservativePrune(sessions) {
    const maxAgeMs = this.config.maxSessionAge * 24 * 60 * 60 * 1000;
    const now = Date.now();

    return sessions.filter(session => {
      const age = now - session.lastActive.getTime();
      return age > maxAgeMs;
    });
  }

  /**
   * Moderate pruning: Age + token-based
   * @private
   */
  _moderatePrune(sessions, utilizationPercent) {
    const targets = [];

    // First, remove sessions older than maxSessionAge
    const oldSessions = this._conservativePrune(sessions);
    targets.push(...oldSessions);

    // If still over threshold, remove based on utilization
    if (utilizationPercent > 80) {
      const sortedByScore = this._sortByPruneScore(sessions);
      const pruneCount = Math.ceil(sortedByScore.length * 0.25); // Remove lowest 25%

      for (let i = 0; i < pruneCount; i++) {
        if (!targets.find(t => t.sessionId === sortedByScore[i].sessionId)) {
          targets.push(sortedByScore[i]);
        }
      }
    }

    return targets;
  }

  /**
   * Aggressive pruning: Remove more sessions based on utilization
   * @private
   */
  _aggressivePrune(sessions, utilizationPercent) {
    const targets = [];
    const sortedByScore = this._sortByPruneScore(sessions);

    let prunePercent;
    if (utilizationPercent > 95) {
      prunePercent = 0.70; // Remove 70%
    } else if (utilizationPercent > 90) {
      prunePercent = 0.50; // Remove 50%
    } else if (utilizationPercent > 80) {
      prunePercent = 0.35; // Remove 35%
    } else {
      prunePercent = 0.25; // Remove 25%
    }

    const pruneCount = Math.ceil(sortedByScore.length * prunePercent);

    for (let i = 0; i < pruneCount; i++) {
      targets.push(sortedByScore[i]);
    }

    return targets;
  }

  /**
   * Emergency pruning: Keep only recent sessions
   * @private
   */
  _emergencyPrune(sessions) {
    const keepRecentMs = this.config.keepRecentHours * 60 * 60 * 1000;
    const now = Date.now();

    return sessions.filter(session => {
      const age = now - session.lastActive.getTime();
      return age > keepRecentMs;
    });
  }

  /**
   * Calculate prune score (lower = prune first)
   * @private
   */
  _sortByPruneScore(sessions) {
    return sessions
      .map(session => ({
        ...session,
        pruneScore: this._calculatePruneScore(session)
      }))
      .sort((a, b) => a.pruneScore - b.pruneScore);
  }

  /**
   * Calculate pruning score for a session
   * Higher score = more important to keep
   * @private
   */
  _calculatePruneScore(session) {
    let score = 0;

    // Recency score (0-100)
    const ageHours = (Date.now() - session.lastActive.getTime()) / (1000 * 60 * 60);
    const recencyScore = Math.max(0, 100 - ageHours);
    score += recencyScore * 0.4; // 40% weight

    // Message count score (0-100)
    const messageScore = Math.min(100, session.messageCount * 5);
    score += messageScore * 0.3; // 30% weight

    // Token count score (0-100) - Higher tokens might indicate important conversation
    const tokenScore = Math.min(100, (session.tokenCount / 10000) * 100);
    score += tokenScore * 0.2; // 20% weight

    // Priority bonus
    if (session.priority === 'high') score += 50;
    if (session.priority === 'medium') score += 25;

    return score;
  }

  /**
   * Check if session is protected from pruning
   * @private
   */
  _isProtected(session) {
    const now = Date.now();
    const ageHours = (now - session.lastActive.getTime()) / (1000 * 60 * 60);

    // Always keep recent sessions
    if (ageHours < this.config.keepRecentHours) {
      return true;
    }

    // Keep sessions with high engagement
    if (this.config.preserveHighEngagement &&
        session.messageCount >= this.config.minMessagesForImportant) {
      return true;
    }

    // Keep if below minimum session count
    // (This check should be done at a higher level)

    return false;
  }

  /**
   * Get recommended pruning strategy based on utilization
   */
  getRecommendedStrategy(utilizationPercent) {
    if (utilizationPercent >= 95) return 'emergency';
    if (utilizationPercent >= 85) return 'aggressive';
    if (utilizationPercent >= 75) return 'moderate';
    return 'conservative';
  }

  /**
   * Dry run - preview what would be pruned
   */
  async dryRun(strategy = 'moderate') {
    const usage = await this.monitor.getContextUsage();
    const sessions = usage.sessions;

    const pruneTargets = this._selectPruneTargets(
      sessions,
      strategy,
      usage.utilizationPercent
    );

    return {
      strategy,
      wouldPrune: pruneTargets.length,
      wouldFreeTokens: pruneTargets.reduce((sum, s) => sum + s.tokenCount, 0),
      wouldKeep: sessions.length - pruneTargets.length,
      sessions: pruneTargets.map(s => ({
        id: s.sessionId,
        tokens: s.tokenCount,
        messages: s.messageCount,
        age: this._getAge(s.lastActive),
        priority: s.priority,
        reason: this._getPruneReason(s)
      }))
    };
  }

  /**
   * Get age in human-readable format
   * @private
   */
  _getAge(date) {
    const ageMs = Date.now() - date.getTime();
    const ageHours = ageMs / (1000 * 60 * 60);

    if (ageHours < 1) {
      return `${Math.round(ageMs / (1000 * 60))} minutes`;
    } else if (ageHours < 24) {
      return `${Math.round(ageHours)} hours`;
    } else {
      return `${Math.round(ageHours / 24)} days`;
    }
  }

  /**
   * Get reason for pruning
   * @private
   */
  _getPruneReason(session) {
    const ageHours = (Date.now() - session.lastActive.getTime()) / (1000 * 60 * 60);
    const ageDays = ageHours / 24;

    if (ageDays > this.config.maxSessionAge) {
      return `Old session (${Math.round(ageDays)} days)`;
    }

    if (session.messageCount === 0) {
      return 'Empty session';
    }

    if (session.messageCount < 3) {
      return 'Low engagement';
    }

    return 'Low priority score';
  }

  /**
   * Log pruning action
   * @private
   */
  _logPrune(session, strategy) {
    this.pruneLog.push({
      timestamp: new Date(),
      sessionId: session.sessionId,
      tokens: session.tokenCount,
      messages: session.messageCount,
      age: this._getAge(session.lastActive),
      strategy
    });

    // Keep only last 100 entries
    if (this.pruneLog.length > 100) {
      this.pruneLog.shift();
    }
  }

  /**
   * Get pruning history
   */
  getHistory() {
    return this.pruneLog;
  }

  /**
   * Clear pruning history
   */
  clearHistory() {
    this.pruneLog = [];
  }
}

module.exports = SessionPruner;
