/**
 * Session Monitor - Real-time Context Monitoring
 *
 * Monitors OpenClaw's active context token usage in real-time
 * Tracks per-session token counts and alerts when approaching limits
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class SessionMonitor {
  constructor(config = {}) {
    this.config = {
      maxTokens: config.maxTokens || 200000,
      sessionPath: config.sessionPath || path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions'),
      alertThreshold: config.alertThreshold || 80, // percentage
      emergencyThreshold: config.emergencyThreshold || 95, // percentage
      ...config
    };

    this.lastCheck = null;
    this.currentUsage = null;
  }

  /**
   * Get current context usage across all sessions
   * @returns {Object} Context usage information
   */
  async getContextUsage() {
    const sessions = await this.getAllSessions();

    let totalTokens = 0;
    const sessionInfo = [];

    for (const session of sessions) {
      const tokens = await this.countSessionTokens(session.path);
      const messages = await this.getMessageCount(session.path);

      totalTokens += tokens;
      sessionInfo.push({
        sessionId: session.id,
        path: session.path,
        tokenCount: tokens,
        messageCount: messages,
        lastActive: session.lastModified,
        priority: this._calculatePriority(tokens, messages, session.lastModified)
      });
    }

    const utilizationPercent = (totalTokens / this.config.maxTokens) * 100;

    this.currentUsage = {
      currentTokens: totalTokens,
      maxTokens: this.config.maxTokens,
      utilizationPercent: Math.round(utilizationPercent * 100) / 100,
      sessions: sessionInfo.sort((a, b) => b.tokenCount - a.tokenCount),
      lastChecked: new Date(),
      status: this._getStatus(utilizationPercent)
    };

    this.lastCheck = new Date();
    return this.currentUsage;
  }

  /**
   * Count tokens in a session file
   * @param {string} sessionPath - Path to session file
   * @returns {Promise<number>} Estimated token count
   */
  async countSessionTokens(sessionPath) {
    try {
      const content = await fs.promises.readFile(sessionPath, 'utf-8');
      const session = JSON.parse(content);

      let totalChars = 0;

      // Count characters in all messages
      if (session.messages && Array.isArray(session.messages)) {
        for (const message of session.messages) {
          if (message.content) {
            totalChars += typeof message.content === 'string'
              ? message.content.length
              : JSON.stringify(message.content).length;
          }

          // Include tool calls and results
          if (message.tool_calls) {
            totalChars += JSON.stringify(message.tool_calls).length;
          }

          if (message.tool_results) {
            totalChars += JSON.stringify(message.tool_results).length;
          }
        }
      }

      // Estimate tokens: ~4 characters per token (average)
      return Math.ceil(totalChars / 4);
    } catch (error) {
      // If can't parse, estimate from file size
      try {
        const stats = await fs.promises.stat(sessionPath);
        // Roughly 1 byte = 0.25 tokens after JSON compression
        return Math.ceil(stats.size / 4);
      } catch (e) {
        return 0;
      }
    }
  }

  /**
   * Get message count from session
   * @param {string} sessionPath - Path to session file
   * @returns {Promise<number>} Number of messages
   */
  async getMessageCount(sessionPath) {
    try {
      const content = await fs.promises.readFile(sessionPath, 'utf-8');
      const session = JSON.parse(content);
      return session.messages ? session.messages.length : 0;
    } catch (error) {
      return 0;
    }
  }

  /**
   * Get all session files
   * @returns {Promise<Array>} Array of session information
   */
  async getAllSessions() {
    const sessions = [];

    if (!fs.existsSync(this.config.sessionPath)) {
      return sessions;
    }

    try {
      const files = await fs.promises.readdir(this.config.sessionPath);

      for (const file of files) {
        if (file.endsWith('.json')) {
          const filePath = path.join(this.config.sessionPath, file);
          const stats = await fs.promises.stat(filePath);

          sessions.push({
            id: file.replace('.json', ''),
            path: filePath,
            lastModified: stats.mtime,
            size: stats.size
          });
        }
      }
    } catch (error) {
      console.error('Error reading sessions:', error.message);
    }

    return sessions;
  }

  /**
   * Calculate session priority for pruning decisions
   * @private
   */
  _calculatePriority(tokens, messages, lastModified) {
    const ageHours = (Date.now() - lastModified.getTime()) / (1000 * 60 * 60);

    // High priority: Recent sessions with many messages
    if (ageHours < 24 && messages > 10) return 'high';

    // Medium priority: Recent sessions or sessions with some activity
    if (ageHours < 168 || messages > 5) return 'medium';

    // Low priority: Old sessions with few messages
    return 'low';
  }

  /**
   * Get status based on utilization percentage
   * @private
   */
  _getStatus(utilizationPercent) {
    if (utilizationPercent >= this.config.emergencyThreshold) {
      return {
        level: 'CRITICAL',
        emoji: '🚨',
        message: 'Emergency cleanup required'
      };
    } else if (utilizationPercent >= this.config.alertThreshold) {
      return {
        level: 'WARNING',
        emoji: '⚠️',
        message: 'High usage - cleanup recommended'
      };
    } else if (utilizationPercent >= 60) {
      return {
        level: 'MODERATE',
        emoji: '⚡',
        message: 'Moderate usage'
      };
    } else {
      return {
        level: 'OK',
        emoji: '✅',
        message: 'Normal usage'
      };
    }
  }

  /**
   * Check if cleanup is needed based on current usage
   * @returns {Promise<Object>} Cleanup recommendation
   */
  async needsCleanup() {
    const usage = await this.getContextUsage();

    return {
      required: usage.utilizationPercent >= this.config.alertThreshold,
      emergency: usage.utilizationPercent >= this.config.emergencyThreshold,
      recommendation: usage.utilizationPercent >= this.config.emergencyThreshold
        ? 'EMERGENCY_CLEANUP'
        : usage.utilizationPercent >= this.config.alertThreshold
        ? 'ROUTINE_CLEANUP'
        : 'NO_ACTION',
      currentUsage: usage
    };
  }

  /**
   * Get sessions sorted by age
   * @returns {Promise<Array>} Sessions sorted oldest first
   */
  async getSessionsByAge() {
    const usage = await this.getContextUsage();
    return usage.sessions.sort((a, b) => a.lastActive - b.lastActive);
  }

  /**
   * Get sessions sorted by token count
   * @returns {Promise<Array>} Sessions sorted by token count (descending)
   */
  async getSessionsBySize() {
    const usage = await this.getContextUsage();
    return usage.sessions.sort((a, b) => b.tokenCount - a.tokenCount);
  }

  /**
   * Format bytes to human-readable
   * @private
   */
  _formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Format tokens to human-readable
   */
  formatTokens(tokens) {
    if (tokens < 1000) return `${tokens}`;
    if (tokens < 1000000) return `${(tokens / 1000).toFixed(1)}k`;
    return `${(tokens / 1000000).toFixed(1)}M`;
  }
}

module.exports = SessionMonitor;
