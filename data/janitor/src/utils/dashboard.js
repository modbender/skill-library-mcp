/**
 * Dashboard Utility - Context Usage Visualization
 *
 * Provides beautiful CLI dashboard for monitoring context usage
 */

class Dashboard {
  constructor(monitor) {
    this.monitor = monitor;
  }

  /**
   * Generate full dashboard
   */
  async generate() {
    const usage = await this.monitor.getContextUsage();

    const output = this._buildDashboard(usage);
    console.log(output);

    return usage;
  }

  /**
   * Build dashboard content
   * @private
   */
  _buildDashboard(usage) {
    const lines = [];

    // Header
    lines.push('╔══════════════════════════════════════════════════════════════╗');
    lines.push('║           OPENCLAW CONTEXT USAGE DASHBOARD                   ║');
    lines.push('╠══════════════════════════════════════════════════════════════╣');
    lines.push('║                                                              ║');

    // Context usage bar
    const usageBar = this._buildProgressBar(usage.utilizationPercent, 50);
    const tokensDisplay = `${this.monitor.formatTokens(usage.currentTokens)} / 200k`;
    lines.push(`║  Context Usage                                               ║`);
    lines.push(`║  ${usageBar}  ║`);
    lines.push(`║  ${tokensDisplay.padEnd(58)} (${usage.utilizationPercent.toFixed(1)}%)  ║`);
    lines.push(`║  ${usage.status.emoji}  ${usage.status.message.padEnd(55)} ║`);
    lines.push('║                                                              ║');

    // Session table
    lines.push(`║  Active Sessions: ${usage.sessions.length.toString().padEnd(44)} ║`);
    lines.push('║  ┌─────────────────────────────────────────────────────┐   ║');
    lines.push('║  │ Session ID          | Tokens | Age      | Messages │   ║');
    lines.push('║  ├─────────────────────────────────────────────────────┤   ║');

    // Show top 5 sessions
    const topSessions = usage.sessions.slice(0, 5);
    for (const session of topSessions) {
      const id = this._truncate(session.sessionId, 19);
      const tokens = this.monitor.formatTokens(session.tokenCount).padStart(6);
      const age = this._getAge(session.lastActive).padEnd(8);
      const messages = session.messageCount.toString().padStart(8);

      lines.push(`║  │ ${id} | ${tokens} | ${age} | ${messages} │   ║`);
    }

    // Show count of remaining sessions
    if (usage.sessions.length > 5) {
      const remaining = usage.sessions.length - 5;
      const remainingTokens = usage.sessions
        .slice(5)
        .reduce((sum, s) => sum + s.tokenCount, 0);

      const remainingLine = `... (${remaining} more)`.padEnd(19);
      const remTokens = this.monitor.formatTokens(remainingTokens).padStart(6);
      lines.push(`║  │ ${remainingLine} | ${remTokens} | ${'...'.padEnd(8)} | ${'...'.padStart(8)} │   ║`);
    }

    lines.push('║  └─────────────────────────────────────────────────────┘   ║');
    lines.push('║                                                              ║');

    // Recommendations
    const recommendations = this._getRecommendations(usage);
    if (recommendations.length > 0) {
      lines.push('║  Recommendations:                                            ║');
      for (const rec of recommendations) {
        lines.push(`║  • ${rec.padEnd(58)} ║`);
      }
      lines.push('║                                                              ║');
    }

    // Footer (optional - if watcher is running)
    lines.push('║  Last Checked: ' + new Date().toLocaleString().padEnd(44) + ' ║');
    lines.push('║                                                              ║');
    lines.push('╚══════════════════════════════════════════════════════════════╝');

    return lines.join('\n');
  }

  /**
   * Build progress bar
   * @private
   */
  _buildProgressBar(percent, width = 50) {
    const filled = Math.round((percent / 100) * width);
    const empty = width - filled;

    const filledChar = '█';
    const emptyChar = '░';

    return filledChar.repeat(filled) + emptyChar.repeat(empty);
  }

  /**
   * Get age in human-readable short format
   * @private
   */
  _getAge(date) {
    const ageMs = Date.now() - date.getTime();
    const ageMinutes = ageMs / (1000 * 60);
    const ageHours = ageMinutes / 60;
    const ageDays = ageHours / 24;

    if (ageMinutes < 60) {
      return `${Math.round(ageMinutes)} mins`;
    } else if (ageHours < 24) {
      return `${Math.round(ageHours)} hours`;
    } else {
      return `${Math.round(ageDays)} days`;
    }
  }

  /**
   * Truncate string
   * @private
   */
  _truncate(str, maxLen) {
    if (str.length <= maxLen) {
      return str.padEnd(maxLen);
    }
    return str.substring(0, maxLen - 3) + '...';
  }

  /**
   * Get recommendations based on usage
   * @private
   */
  _getRecommendations(usage) {
    const recommendations = [];

    if (usage.utilizationPercent >= 95) {
      recommendations.push('CRITICAL: Run emergency cleanup immediately!');
    } else if (usage.utilizationPercent >= 85) {
      recommendations.push('Run cleanup to free tokens');
    } else if (usage.utilizationPercent >= 75) {
      recommendations.push('Consider archiving old sessions');
    }

    // Count old sessions (>7 days)
    const oldSessions = usage.sessions.filter(s => {
      const ageDays = (Date.now() - s.lastActive.getTime()) / (1000 * 60 * 60 * 24);
      return ageDays > 7;
    });

    if (oldSessions.length > 0) {
      const oldTokens = oldSessions.reduce((sum, s) => sum + s.tokenCount, 0);
      recommendations.push(
        `${oldSessions.length} sessions >7 days old (${this.monitor.formatTokens(oldTokens)} tokens)`
      );
    }

    return recommendations;
  }

  /**
   * Generate simple status line
   */
  async statusLine() {
    const usage = await this.monitor.getContextUsage();

    return `Context: ${this.monitor.formatTokens(usage.currentTokens)}/200k (${usage.utilizationPercent.toFixed(1)}%) | Sessions: ${usage.sessions.length} | ${usage.status.emoji} ${usage.status.level}`;
  }

  /**
   * Generate compact report
   */
  async compactReport() {
    const usage = await this.monitor.getContextUsage();

    console.log('\nContext Usage Report:');
    console.log(`  Tokens: ${this.monitor.formatTokens(usage.currentTokens)}/200k (${usage.utilizationPercent.toFixed(1)}%)`);
    console.log(`  Sessions: ${usage.sessions.length}`);
    console.log(`  Status: ${usage.status.emoji} ${usage.status.level} - ${usage.status.message}`);

    if (usage.sessions.length > 0) {
      const oldest = usage.sessions.reduce((old, s) =>
        s.lastActive < old.lastActive ? s : old
      );

      console.log(`  Oldest Session: ${this._getAge(oldest.lastActive)} ago`);
    }

    console.log('');

    return usage;
  }

  /**
   * Generate session list
   */
  async listSessions(sortBy = 'size') {
    const usage = await this.monitor.getContextUsage();

    let sorted;
    if (sortBy === 'age') {
      sorted = usage.sessions.sort((a, b) => a.lastActive - b.lastActive);
    } else if (sortBy === 'messages') {
      sorted = usage.sessions.sort((a, b) => b.messageCount - a.messageCount);
    } else {
      // default: size
      sorted = usage.sessions.sort((a, b) => b.tokenCount - a.tokenCount);
    }

    console.log('\nSession List:');
    console.log('  ID                      Tokens    Messages  Age         Priority');
    console.log('  ' + '─'.repeat(70));

    for (const session of sorted) {
      const id = this._truncate(session.sessionId, 22);
      const tokens = this.monitor.formatTokens(session.tokenCount).padStart(8);
      const messages = session.messageCount.toString().padStart(8);
      const age = this._getAge(session.lastActive).padEnd(11);
      const priority = session.priority.padEnd(8);

      console.log(`  ${id}  ${tokens}  ${messages}  ${age}  ${priority}`);
    }

    console.log('');

    return sorted;
  }
}

module.exports = Dashboard;
