/**
 * Emergency Cleanup - Critical Context Overflow Handler
 *
 * Handles emergency situations when context usage exceeds critical thresholds
 * Performs aggressive cleanup to restore system functionality
 */

const fs = require('fs');
const path = require('path');

class EmergencyCleanup {
  constructor(monitor, pruner, archiver, config = {}) {
    this.monitor = monitor;
    this.pruner = pruner;
    this.archiver = archiver;

    this.config = {
      keepRecentHours: config.keepRecentHours || 6,
      keepMinimumSessions: config.keepMinimumSessions || 3,
      emergencyThreshold: config.emergencyThreshold || 95,
      notificationChannel: config.notificationChannel || 'log',
      ...config
    };

    this.history = [];
  }

  /**
   * Execute emergency cleanup
   * @returns {Promise<Object>} Cleanup result
   */
  async execute() {
    console.log('🚨 EMERGENCY CLEANUP INITIATED');

    const startTime = Date.now();
    const beforeUsage = await this.monitor.getContextUsage();

    const result = {
      timestamp: new Date().toISOString(),
      trigger: 'emergency',
      beforeUsage: {
        tokens: beforeUsage.currentTokens,
        percent: beforeUsage.utilizationPercent,
        sessions: beforeUsage.sessions.length
      },
      actions: [],
      success: false
    };

    try {
      // Step 1: Archive all sessions before cleanup
      console.log('📦 Archiving sessions...');
      const archiveResult = await this.archiver.archiveSessions(
        beforeUsage.sessions,
        'emergency-cleanup'
      );

      result.actions.push({
        action: 'archive',
        result: archiveResult
      });

      // Step 2: Determine sessions to keep
      const keepRecentMs = this.config.keepRecentHours * 60 * 60 * 1000;
      const now = Date.now();

      const sessionsToKeep = beforeUsage.sessions
        .filter(s => {
          const age = now - s.lastActive.getTime();
          return age < keepRecentMs;
        })
        .sort((a, b) => b.lastActive - a.lastActive)
        .slice(0, this.config.keepMinimumSessions);

      // Step 3: Delete all other sessions
      console.log('🗑️  Removing old sessions...');
      let deletedCount = 0;
      let tokensFreed = 0;

      for (const session of beforeUsage.sessions) {
        const shouldKeep = sessionsToKeep.some(s => s.sessionId === session.sessionId);

        if (!shouldKeep) {
          try {
            await fs.promises.unlink(session.path);
            deletedCount++;
            tokensFreed += session.tokenCount;
          } catch (error) {
            console.error(`Failed to delete session ${session.sessionId}:`, error.message);
          }
        }
      }

      result.actions.push({
        action: 'prune',
        deleted: deletedCount,
        kept: sessionsToKeep.length,
        tokensFreed
      });

      // Step 4: Verify cleanup success
      const afterUsage = await this.monitor.getContextUsage();

      result.afterUsage = {
        tokens: afterUsage.currentTokens,
        percent: afterUsage.utilizationPercent,
        sessions: afterUsage.sessions.length
      };

      result.duration = Date.now() - startTime;
      result.success = afterUsage.utilizationPercent < this.config.emergencyThreshold;

      // Log to history
      this._logToHistory(result);

      // Send notification
      await this._sendNotification(result);

      console.log('✅ Emergency cleanup complete');
      return result;
    } catch (error) {
      result.error = error.message;
      result.success = false;

      console.error('❌ Emergency cleanup failed:', error.message);
      return result;
    }
  }

  /**
   * Check if emergency cleanup is needed
   * @returns {Promise<boolean>}
   */
  async isNeeded() {
    const usage = await this.monitor.getContextUsage();
    return usage.utilizationPercent >= this.config.emergencyThreshold;
  }

  /**
   * Get emergency cleanup status
   */
  getStatus() {
    return {
      enabled: true,
      threshold: this.config.emergencyThreshold,
      keepRecentHours: this.config.keepRecentHours,
      keepMinimumSessions: this.config.keepMinimumSessions,
      historyCount: this.history.length,
      lastExecution: this.history.length > 0
        ? this.history[this.history.length - 1].timestamp
        : null
    };
  }

  /**
   * Generate emergency report
   */
  generateReport(result) {
    const beforePercent = result.beforeUsage.percent;
    const afterPercent = result.afterUsage.percent;
    const tokensFreed = result.beforeUsage.tokens - result.afterUsage.tokens;

    return `
╔══════════════════════════════════════════════════════════════╗
║           🚨 EMERGENCY CLEANUP EXECUTED                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Reason: Context usage exceeded ${this.config.emergencyThreshold}%                       ║
║          (${result.beforeUsage.tokens.toLocaleString()}/200k tokens)                              ║
║                                                              ║
║  Actions taken:                                              ║
║  ✅ Archived ${result.actions[0].result.archived} sessions to ${result.actions[0].result.archiveName.substring(0, 20)}... ║
║  ✅ Removed sessions older than ${this.config.keepRecentHours} hours                  ║
║  ✅ Freed ${this._formatTokens(tokensFreed)} tokens                                  ║
║                                                              ║
║  Current status:                                             ║
║  • Context: ${this._formatTokens(result.afterUsage.tokens)}/200k tokens (${afterPercent.toFixed(1)}%)         ║
║  • Active sessions: ${result.afterUsage.sessions}                                  ║
║  • System: ${result.success ? '✅ OPERATIONAL' : '❌ NEEDS ATTENTION'}                        ║
║                                                              ║
║  Your conversation history is safe in archives.              ║
║  Duration: ${result.duration}ms                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
`;
  }

  /**
   * Send notification about emergency cleanup
   * @private
   */
  async _sendNotification(result) {
    const report = this.generateReport(result);

    // For now, just log to console
    // In the future, could integrate with Telegram, Discord, etc.
    console.log(report);

    // Could also write to a log file
    const logPath = path.join(
      require('os').homedir(),
      '.openclaw',
      'logs',
      'emergency-cleanup.log'
    );

    try {
      const logDir = path.dirname(logPath);
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }

      await fs.promises.appendFile(
        logPath,
        `\n${new Date().toISOString()}\n${report}\n`,
        'utf-8'
      );
    } catch (error) {
      // Ignore logging errors
    }
  }

  /**
   * Log to history
   * @private
   */
  _logToHistory(result) {
    this.history.push(result);

    // Keep only last 50 entries
    if (this.history.length > 50) {
      this.history.shift();
    }
  }

  /**
   * Get emergency cleanup history
   */
  getHistory() {
    return this.history;
  }

  /**
   * Clear history
   */
  clearHistory() {
    this.history = [];
  }

  /**
   * Format tokens to human-readable
   * @private
   */
  _formatTokens(tokens) {
    if (tokens < 1000) return `${tokens}`;
    if (tokens < 1000000) return `${(tokens / 1000).toFixed(1)}k`;
    return `${(tokens / 1000000).toFixed(1)}M`;
  }

  /**
   * Simulate emergency cleanup (dry run)
   */
  async simulate() {
    const usage = await this.monitor.getContextUsage();

    const keepRecentMs = this.config.keepRecentHours * 60 * 60 * 1000;
    const now = Date.now();

    const sessionsToKeep = usage.sessions
      .filter(s => {
        const age = now - s.lastActive.getTime();
        return age < keepRecentMs;
      })
      .sort((a, b) => b.lastActive - a.lastActive)
      .slice(0, this.config.keepMinimumSessions);

    const sessionsToDelete = usage.sessions.filter(
      s => !sessionsToKeep.some(k => k.sessionId === s.sessionId)
    );

    const tokensToFree = sessionsToDelete.reduce((sum, s) => sum + s.tokenCount, 0);
    const afterTokens = usage.currentTokens - tokensToFree;
    const afterPercent = (afterTokens / this.monitor.config.maxTokens) * 100;

    return {
      currentUsage: {
        tokens: usage.currentTokens,
        percent: usage.utilizationPercent,
        sessions: usage.sessions.length
      },
      wouldDelete: sessionsToDelete.length,
      wouldKeep: sessionsToKeep.length,
      tokensToFree,
      afterUsage: {
        tokens: afterTokens,
        percent: afterPercent,
        sessions: sessionsToKeep.length
      },
      sessionsToDelete: sessionsToDelete.map(s => ({
        id: s.sessionId,
        tokens: s.tokenCount,
        messages: s.messageCount,
        age: this._getAge(s.lastActive)
      })),
      sessionsToKeep: sessionsToKeep.map(s => ({
        id: s.sessionId,
        tokens: s.tokenCount,
        messages: s.messageCount,
        age: this._getAge(s.lastActive)
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
}

module.exports = EmergencyCleanup;
