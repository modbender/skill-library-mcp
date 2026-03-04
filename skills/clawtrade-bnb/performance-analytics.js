/**
 * Performance Analytics
 * Tracks strategy performance, calculates real APR, identifies failures
 */

const fs = require('fs');
const path = require('path');

class PerformanceAnalytics {
  constructor(logFile = 'execution-log.jsonl', metricsFile = 'performance-metrics.json') {
    this.logFile = logFile;
    this.metricsFile = metricsFile;
    this.logs = this.loadLogs();
    this.metrics = this.loadMetrics();
  }

  loadLogs() {
    if (!fs.existsSync(this.logFile)) return [];
    const lines = fs.readFileSync(this.logFile, 'utf8').split('\n').filter(l => l);
    return lines.map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    }).filter(l => l);
  }

  loadMetrics() {
    if (!fs.existsSync(this.metricsFile)) return {};
    try {
      return JSON.parse(fs.readFileSync(this.metricsFile, 'utf8'));
    } catch {
      return {};
    }
  }

  /**
   * Calculate realized APR based on historical performance
   */
  calculateRealizedAPR() {
    if (this.metrics.totalDeposited === 0) return 0;

    const timeElapsed = (Date.now() - this.metrics.startTime) / (1000 * 60 * 60 * 24); // Days
    const harvested = this.metrics.totalHarvested || 0;
    const deposited = this.metrics.totalDeposited || 1;

    const dailyYield = harvested / Math.max(timeElapsed, 1);
    const apr = (dailyYield / deposited) * 365 * 100;

    return Math.max(0, apr);
  }

  /**
   * Get performance summary
   */
  getPerformanceSummary() {
    const failures = this.logs.filter(l => l.action?.includes('ERROR')).length;
    const successes = this.logs.filter(l => !l.action?.includes('ERROR')).length;

    return {
      totalActions: this.logs.length,
      successfulActions: successes,
      failedActions: failures,
      successRate: successes / Math.max(this.logs.length, 1),
      totalHarvested: this.metrics.totalHarvested || 0,
      totalCompounded: this.metrics.totalCompounded || 0,
      realizedAPR: this.calculateRealizedAPR(),
      startTime: new Date(this.metrics.startTime || Date.now()).toISOString(),
      uptime: this.getUptime(),
    };
  }

  /**
   * Identify failing strategies
   */
  identifyFailures() {
    const failures = {};
    
    this.logs.filter(l => l.action?.includes('ERROR')).forEach(log => {
      const key = log.action || 'UNKNOWN';
      if (!failures[key]) {
        failures[key] = { count: 0, examples: [] };
      }
      failures[key].count += 1;
      if (failures[key].examples.length < 3) {
        failures[key].examples.push({
          timestamp: new Date(log.timestamp * 1000).toISOString(),
          vault: log.vault,
          error: log.error,
        });
      }
    });

    return failures;
  }

  /**
   * Vault performance breakdown
   */
  getVaultPerformance() {
    const vaultStats = {};

    this.logs.forEach(log => {
      const vault = log.vault_id || log.vault;
      if (!vault) return;

      if (!vaultStats[vault]) {
        vaultStats[vault] = {
          actions: 0,
          harvested: 0,
          compounded: 0,
          errors: 0,
        };
      }

      vaultStats[vault].actions += 1;
      if (log.action?.includes('HARVEST')) vaultStats[vault].harvested += log.rewards_usd || 0;
      if (log.action?.includes('COMPOUND')) vaultStats[vault].compounded += log.rewards_usd || 0;
      if (log.action?.includes('ERROR')) vaultStats[vault].errors += 1;
    });

    return vaultStats;
  }

  /**
   * Strategy effectiveness analysis
   */
  getStrategyAnalysis() {
    const strategies = {
      COMPOUND_YIELD: { count: 0, rewards: 0 },
      REBALANCE: { count: 0, success: 0 },
      DYNAMIC_HARVEST: { count: 0, rewards: 0 },
    };

    this.logs.forEach(log => {
      Object.keys(strategies).forEach(strat => {
        if (log.action?.includes(strat)) {
          strategies[strat].count += 1;
          if (log.action?.includes('ERROR')) {
            strategies[strat].success = strategies[strat].success || 0;
          } else {
            strategies[strat].success = (strategies[strat].success || 0) + 1;
            if (log.rewards_usd) strategies[strat].rewards += log.rewards_usd;
          }
        }
      });
    });

    return strategies;
  }

  /**
   * Generate full performance report
   */
  generateReport() {
    console.log(`
╔════════════════════════════════════════════════════════════╗
║               Performance Analytics Report                 ║
╚════════════════════════════════════════════════════════════╝

📊 OVERALL PERFORMANCE
─────────────────────────────────────────────────────────────
${this.formatReportSection(this.getPerformanceSummary())}

💰 VAULT PERFORMANCE
─────────────────────────────────────────────────────────────
${this.formatVaultTable(this.getVaultPerformance())}

🎯 STRATEGY EFFECTIVENESS
─────────────────────────────────────────────────────────────
${this.formatStrategyTable(this.getStrategyAnalysis())}

⚠️  FAILURE ANALYSIS
─────────────────────────────────────────────────────────────
${this.formatFailures(this.identifyFailures())}
    `);
  }

  formatReportSection(summary) {
    return `
Total Actions:      ${summary.totalActions}
Success Rate:       ${(summary.successRate * 100).toFixed(1)}%
Total Harvested:    $${summary.totalHarvested.toFixed(2)}
Total Compounded:   $${summary.totalCompounded.toFixed(2)}
Realized APR:       ${summary.realizedAPR.toFixed(2)}%
Uptime:             ${summary.uptime}
`;
  }

  formatVaultTable(vaults) {
    let table = 'Vault ID                    | Actions | Harvested | Compounded | Errors\n';
    table += '─'.repeat(70) + '\n';
    
    Object.entries(vaults).forEach(([vault, stats]) => {
      const vaultName = vault.slice(0, 26).padEnd(26);
      table += `${vaultName} | ${stats.actions.toString().padStart(7)} | $${stats.harvested.toFixed(2).padStart(8)} | $${stats.compounded.toFixed(2).padStart(9)} | ${stats.errors}\n`;
    });

    return table;
  }

  formatStrategyTable(strategies) {
    let table = 'Strategy             | Executed | Success Rate | Total Value\n';
    table += '─'.repeat(60) + '\n';

    Object.entries(strategies).forEach(([strat, stats]) => {
      const successRate = stats.count > 0 ? ((stats.success / stats.count) * 100).toFixed(1) : '0.0';
      table += `${strat.padEnd(20)} | ${stats.count.toString().padStart(8)} | ${successRate.padStart(11)}% | $${stats.rewards.toFixed(2)}\n`;
    });

    return table;
  }

  formatFailures(failures) {
    if (Object.keys(failures).length === 0) {
      return 'No failures detected ✓';
    }

    let text = '';
    Object.entries(failures).forEach(([action, data]) => {
      text += `\n${action} (${data.count} occurrences):\n`;
      data.examples.forEach(ex => {
        text += `  • ${ex.timestamp} - ${ex.vault}: ${ex.error}\n`;
      });
    });

    return text;
  }

  getUptime() {
    const totalCycles = this.logs.length;
    const elapsed = (Date.now() - (this.metrics.startTime || Date.now())) / (1000 * 60);
    const cyclesPerMin = totalCycles / Math.max(elapsed, 1);
    return `${(cyclesPerMin * 60).toFixed(1)} cycles/hour (${totalCycles} total)`;
  }

  /**
   * Export metrics to JSON
   */
  exportMetrics() {
    return {
      generated: new Date().toISOString(),
      performance: this.getPerformanceSummary(),
      vaults: this.getVaultPerformance(),
      strategies: this.getStrategyAnalysis(),
      failures: this.identifyFailures(),
    };
  }
}

module.exports = PerformanceAnalytics;
