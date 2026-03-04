/**
 * Analytics - Track token savings and statistics
 */

const fs = require('fs');
const path = require('path');

class Analytics {
  constructor(options = {}) {
    this.enabled = options.tracking !== false && process.env.OKTK_DISABLE !== 'true';
    this.logFile = options.logFile || process.env.OKTK_LOG_FILE ||
                   path.join(process.env.HOME, '.oktk', 'savings.log');
    this.statsFile = options.statsFile || process.env.OKTK_STATS_FILE ||
                     path.join(process.env.HOME, '.oktk', 'stats.json');
    this.debug = options.debug || process.env.OKTK_DEBUG === '1';

    // Ensure directory exists
    this.ensureDirs();
  }

  /**
   * Ensure analytics directory exists
   */
  async ensureDirs() {
    try {
      const dir = path.dirname(this.logFile);
      await fs.promises.mkdir(dir, { recursive: true });
    } catch (error) {
      console.error('Failed to create analytics directory:', error.message);
    }
  }

  /**
   * Track a filter operation
   */
  async track(cacheKey, command, originalLength, filteredLength, filterName) {
    if (!this.enabled) return;

    const timestamp = Date.now();
    const savings = originalLength - filteredLength;
    const savingsPercent = originalLength > 0
      ? (savings / originalLength * 100).toFixed(1)
      : 0;

    const entry = {
      timestamp,
      cacheKey,
      command: this.sanitizeCommand(command),
      original: originalLength,
      filtered: filteredLength,
      saved: savings,
      savedPercent: parseFloat(savingsPercent),
      filterName,
      method: 'filtered' // or 'cache' for cache hits
    };

    // Append to log
    await this.appendLog(entry);

    // Update stats
    await this.updateStats(entry);
  }

  /**
   * Track cache hit
   */
  async trackCacheHit(cacheKey, command, originalLength, filteredLength) {
    if (!this.enabled) return;

    const timestamp = Date.now();
    const savings = originalLength - filteredLength;

    const entry = {
      timestamp,
      cacheKey,
      command: this.sanitizeCommand(command),
      original: originalLength,
      filtered: filteredLength,
      saved: savings,
      savedPercent: 100, // Cache saves everything
      filterName: 'cache',
      method: 'cache'
    };

    await this.appendLog(entry);
    await this.updateStats(entry);
  }

  /**
   * Append entry to log file
   */
  async appendLog(entry) {
    try {
      const logLine = JSON.stringify(entry) + '\n';
      await fs.promises.appendFile(this.logFile, logLine, 'utf8');
    } catch (error) {
      console.error('Analytics log error:', error.message);
    }
  }

  /**
   * Update aggregate statistics
   */
  async updateStats(entry) {
    try {
      let stats;

      try {
        const data = await fs.promises.readFile(this.statsFile, 'utf8');
        stats = JSON.parse(data);
      } catch {
        // Initialize new stats
        stats = {
          total: 0,
          filtered: 0,
          cacheHits: 0,
          raw: 0,
          errors: 0,
          totalOriginal: 0,
          totalFiltered: 0,
          totalSaved: 0,
          filters: {},
          commands: []
        };
      }

      // Update counts
      stats.total++;

      if (entry.method === 'cache') {
        stats.cacheHits++;
      } else if (entry.filterName !== 'none') {
        stats.filtered++;
      } else {
        stats.raw++;
      }

      if (entry.filterName === 'passthrough' || entry.filterName === 'none') {
        stats.errors++;
      }

      // Update token counts
      stats.totalOriginal += entry.original;
      stats.totalFiltered += entry.filtered;
      stats.totalSaved += entry.saved;

      // Track by filter
      if (!stats.filters[entry.filterName]) {
        stats.filters[entry.filterName] = {
          count: 0,
          saved: 0,
          original: 0,
          filtered: 0
        };
      }

      stats.filters[entry.filterName].count++;
      stats.filters[entry.filterName].saved += entry.saved;
      stats.filters[entry.filterName].original += entry.original;
      stats.filters[entry.filterName].filtered += entry.filtered;

      // Keep last 100 commands
      stats.commands.push({
        command: entry.command,
        filterName: entry.filterName,
        savedPercent: entry.savedPercent,
        timestamp: entry.timestamp
      });

      if (stats.commands.length > 100) {
        stats.commands.shift();
      }

      // Write stats
      await fs.promises.writeFile(
        this.statsFile,
        JSON.stringify(stats, null, 2),
        'utf8'
      );

    } catch (error) {
      console.error('Analytics stats error:', error.message);
    }
  }

  /**
   * Generate savings report
   */
  async report() {
    try {
      const data = await fs.promises.readFile(this.statsFile, 'utf8');
      const stats = JSON.parse(data);

      const totalSavingsPercent = stats.totalOriginal > 0
        ? (stats.totalSaved / stats.totalOriginal * 100).toFixed(1)
        : 0;

      const filteredRate = stats.total > 0
        ? (stats.filtered / stats.total * 100).toFixed(1)
        : 0;

      const errorRate = stats.total > 0
        ? (stats.errors / stats.total * 100).toFixed(1)
        : 0;

      let report = '';

      report += `📊 Token Savings (All time)\n`;
      report += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      report += `\n`;
      report += `Total commands:  ${stats.total}\n`;
      report += `Filtered:        ${stats.filtered} (${filteredRate}%)\n`;
      report += `Cache hits:      ${stats.cacheHits}\n`;
      report += `Raw (no filter): ${stats.raw}\n`;
      report += `\n`;
      report += `💰 Tokens Saved:  ${stats.totalSaved.toLocaleString()} (${totalSavingsPercent}%)\n`;
      report += `  - Original:    ${stats.totalOriginal.toLocaleString()}\n`;
      report += `  - Filtered:    ${stats.totalFiltered.toLocaleString()}\n`;
      report += `\n`;

      // Cost savings estimation (based on common model prices)
      // Assuming ~4 chars per token
      const tokensSaved = Math.round(stats.totalSaved / 4);
      const costSavings = this.calculateCostSavings(tokensSaved);
      report += `💵 Estimated Cost Savings:\n`;
      report += `  - GPT-4o:      $${costSavings.gpt4o.toFixed(4)}\n`;
      report += `  - Claude 3.5:  $${costSavings.claude35.toFixed(4)}\n`;
      report += `  - GPT-4:       $${costSavings.gpt4.toFixed(4)}\n`;
      report += `\n`;

      // Breakdown by filter
      report += `📊 By Filter:\n`;
      const sortedFilters = Object.entries(stats.filters)
        .sort((a, b) => b[1].saved - a[1].saved);

      for (const [name, data] of sortedFilters) {
        const filterPercent = data.original > 0
          ? (data.saved / data.original * 100).toFixed(1)
          : 0;

        report += `  ${name.padEnd(15)} ${data.saved.toLocaleString().padStart(10)} (${filterPercent}%)\n`;
      }

      report += `\n`;

      // Error rate
      report += `❌ Errors:         ${errorRate}%\n`;

      return report;

    } catch (error) {
      if (error.code === 'ENOENT') {
        return '📊 No analytics data yet. Run some commands first!';
      }
      return `Error loading analytics: ${error.message}`;
    }
  }

  /**
   * Get statistics for a time period
   */
  async getStats(days = 7) {
    try {
      const data = await fs.promises.readFile(this.statsFile, 'utf8');
      const stats = JSON.parse(data);

      const cutoff = Date.now() - (days * 24 * 60 * 60 * 1000);

      // Filter commands by time
      const recentCommands = stats.commands.filter(c => c.timestamp > cutoff);

      return {
        ...stats,
        period: `${days} days`,
        recentCommands: recentCommands.length
      };

    } catch (error) {
      return null;
    }
  }

  /**
   * Reset all analytics
   */
  async reset() {
    try {
      await fs.promises.unlink(this.logFile);
      await fs.promises.unlink(this.statsFile);
      return true;
    } catch (error) {
      console.error('Analytics reset error:', error.message);
      return false;
    }
  }

  /**
   * Calculate cost savings based on model prices
   * Prices per 1M input tokens (2024 rates)
   */
  calculateCostSavings(tokensSaved) {
    const prices = {
      gpt4o: 2.50,      // $2.50 per 1M input tokens
      claude35: 3.00,   // $3.00 per 1M input tokens  
      gpt4: 30.00,      // $30 per 1M input tokens
      opus: 15.00,      // $15 per 1M input tokens
      sonnet: 3.00,     // $3 per 1M input tokens
    };

    const millionTokens = tokensSaved / 1_000_000;

    return {
      gpt4o: millionTokens * prices.gpt4o,
      claude35: millionTokens * prices.claude35,
      gpt4: millionTokens * prices.gpt4,
      opus: millionTokens * prices.opus,
      sonnet: millionTokens * prices.sonnet,
    };
  }

  /**
   * Sanitize command (remove secrets, shorten)
   */
  sanitizeCommand(command) {
    // Remove sensitive patterns
    let sanitized = command
      .replace(/api[_-]?key[=:]\s*[^\s]+/gi, 'api_key=***')
      .replace(/secret[=:]\s*[^\s]+/gi, 'secret=***')
      .replace(/token[=:]\s*[^\s]+/gi, 'token=***')
      .replace(/password[=:]\s*[^\s]+/gi, 'password=***')
      .replace(/bearer\s+[^\s]+/gi, 'bearer ***');

    // Truncate if too long
    if (sanitized.length > 200) {
      sanitized = sanitized.substring(0, 200) + '...';
    }

    return sanitized;
  }

  /**
   * Get log entries for analysis
   */
  async getLogs(limit = 100, filter = null) {
    try {
      const data = await fs.promises.readFile(this.logFile, 'utf8');
      const lines = data.trim().split('\n');

      let entries = lines
        .map(line => {
          try {
            return JSON.parse(line);
          } catch {
            return null;
          }
        })
        .filter(e => e !== null);

      // Apply filter if provided
      if (filter) {
        entries = entries.filter(e => {
          if (filter.filterName && e.filterName !== filter.filterName) return false;
          if (filter.command && !e.command.includes(filter.command)) return false;
          if (filter.since && e.timestamp < filter.since) return false;
          return true;
        });
      }

      // Sort by timestamp descending
      entries.sort((a, b) => b.timestamp - a.timestamp);

      // Limit
      return entries.slice(0, limit);

    } catch (error) {
      if (error.code === 'ENOENT') {
        return [];
      }
      throw error;
    }
  }
}

module.exports = Analytics;
