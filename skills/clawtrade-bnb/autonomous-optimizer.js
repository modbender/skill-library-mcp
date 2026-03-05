#!/usr/bin/env node
/**
 * Autonomous Optimizer
 * Makes intelligent decisions automatically to maximize yield
 * Runs independently of strategy scheduler
 */

const fs = require('fs');
const path = require('path');
const PerformanceAnalytics = require('./performance-analytics');
const ReinforcedLearning = require('./reinforced-learning');

class AutonomousOptimizer {
  constructor() {
    this.analytics = new PerformanceAnalytics();
    this.learning = new ReinforcedLearning();
    this.decisionLog = path.join(__dirname, 'autonomous-decisions.jsonl');
    this.lastOptimization = Date.now();
  }

  /**
   * Make autonomous decisions based on data
   */
  async makeDecisions() {
    console.log(`\n${'═'.repeat(70)}`);
    console.log(`🤖 AUTONOMOUS DECISION MAKER`);
    console.log(`${new Date().toISOString()}`);
    console.log(`${'═'.repeat(70)}`);

    try {
      // 1. Analyze current performance
      const summary = this.analytics.getPerformanceSummary();
      const vaults = this.analytics.getVaultPerformance();
      const strategies = this.analytics.getStrategyAnalysis();

      console.log('\n📊 CURRENT STATUS');
      console.log(`  Success Rate: ${(summary.successRate * 100).toFixed(1)}%`);
      console.log(`  Realized APR: ${summary.realizedAPR.toFixed(2)}%`);
      console.log(`  Total Harvested: $${summary.totalHarvested.toFixed(2)}`);

      // 2. Learn from history
      console.log('\n🧠 LEARNING CYCLE');
      const optimizedConfig = this.learning.learn();
      console.log(`  ✓ Analyzed ${summary.totalActions} actions`);
      console.log(`  ✓ Generated ${this.learning.learnedState.improvements.length} improvements`);

      // 3. Make strategic decisions
      const decisions = this.generateStrategicDecisions(summary, vaults, strategies, optimizedConfig);

      // 4. Log decisions
      this.logDecisions(decisions);

      // 5. Report recommendations
      this.reportRecommendations(decisions);

      return decisions;
    } catch (error) {
      console.error('❌ Decision error:', error.message);
      return [];
    }
  }

  /**
   * Generate strategic decisions
   */
  generateStrategicDecisions(summary, vaults, strategies, optimizedConfig) {
    const decisions = [];

    // DECISION 1: Success rate below 90%?
    if (summary.successRate < 0.9) {
      decisions.push({
        type: 'REDUCE_RISK',
        reason: `Success rate ${(summary.successRate * 100).toFixed(1)}% < 90%`,
        action: 'Increase thresholds to reduce failed attempts',
        impact: 'More conservative, safer execution',
      });
    }

    // DECISION 2: APR dropping?
    if (summary.realizedAPR < 5) {
      decisions.push({
        type: 'INCREASE_YIELD',
        reason: `Realized APR ${summary.realizedAPR.toFixed(2)}% is low`,
        action: 'Rebalance to higher-yield vaults',
        impact: 'Shift capital to better performers',
      });
    }

    // DECISION 3: High-performing vault found?
    const vaultEntries = Object.entries(vaults);
    const topVault = vaultEntries.sort((a, b) => (b[1].rewards || 0) - (a[1].rewards || 0))[0];
    if (topVault && topVault[1].rewards > summary.totalHarvested / 3) {
      decisions.push({
        type: 'CONCENTRATE_CAPITAL',
        reason: `${topVault[0]} outperforming (${topVault[1].rewards.toFixed(2)} of total)`,
        action: `Increase allocation to ${topVault[0]}`,
        impact: `Focus on best performer`,
      });
    }

    // DECISION 4: Strategy optimization opportunity?
    const bestStrategy = Object.entries(strategies).sort((a, b) => (b[1].success / Math.max(b[1].count, 1)) - (a[1].success / Math.max(a[1].count, 1)))[0];
    if (bestStrategy && (bestStrategy[1].success / Math.max(bestStrategy[1].count, 1)) > 0.95) {
      decisions.push({
        type: 'SCALE_BEST_STRATEGY',
        reason: `${bestStrategy[0]} has 95%+ success rate`,
        action: `Increase frequency of ${bestStrategy[0]} cycles`,
        impact: 'Maximize high-confidence operations',
      });
    }

    // DECISION 5: Harvest opportunities?
    const totalYield = Object.values(vaults).reduce((sum, v) => sum + (v.rewards || 0), 0);
    if (totalYield > 100) {
      decisions.push({
        type: 'EXECUTE_HARVEST',
        reason: `Significant yield available ($${totalYield.toFixed(2)})`,
        action: 'Execute harvest across all vaults',
        impact: 'Capture gains, refresh pool',
      });
    }

    // DECISION 6: Compounding optimization?
    if (summary.totalHarvested > 0 && summary.totalCompounded / summary.totalHarvested < 0.7) {
      decisions.push({
        type: 'INCREASE_COMPOUNDING',
        reason: `Only ${((summary.totalCompounded / summary.totalHarvested) * 100).toFixed(1)}% being compounded`,
        action: 'Lower compound thresholds',
        impact: 'More frequent compounding = exponential growth',
      });
    }

    return decisions;
  }

  /**
   * Log decisions for audit trail
   */
  logDecisions(decisions) {
    decisions.forEach(decision => {
      const record = {
        timestamp: Math.floor(Date.now() / 1000),
        type: decision.type,
        reason: decision.reason,
        action: decision.action,
        impact: decision.impact,
      };
      fs.appendFileSync(this.decisionLog, JSON.stringify(record) + '\n');
    });
  }

  /**
   * Report recommendations
   */
  reportRecommendations(decisions) {
    if (decisions.length === 0) {
      console.log('\n✅ All systems optimal - no changes recommended');
      return;
    }

    console.log(`\n🎯 AUTONOMOUS RECOMMENDATIONS (${decisions.length})`);
    console.log('─'.repeat(70));

    decisions.forEach((d, i) => {
      console.log(`\n${i + 1}. ${d.type}`);
      console.log(`   Reason: ${d.reason}`);
      console.log(`   Action: ${d.action}`);
      console.log(`   Impact: ${d.impact}`);
    });

    console.log('\n' + '─'.repeat(70));
    console.log('📋 These decisions have been logged to: autonomous-decisions.jsonl');
  }

  /**
   * Get decision history
   */
  getDecisionHistory() {
    if (!fs.existsSync(this.decisionLog)) return [];
    
    const lines = fs.readFileSync(this.decisionLog, 'utf8').split('\n').filter(l => l);
    return lines.map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    }).filter(l => l);
  }

  /**
   * Print decision history
   */
  printDecisionHistory() {
    const history = this.getDecisionHistory();
    if (history.length === 0) {
      console.log('No decision history yet');
      return;
    }

    console.log(`\n📋 AUTONOMOUS DECISION HISTORY (${history.length})`);
    console.log('─'.repeat(70));

    const byType = {};
    history.forEach(d => {
      if (!byType[d.type]) byType[d.type] = 0;
      byType[d.type] += 1;
    });

    Object.entries(byType).forEach(([type, count]) => {
      console.log(`  ${type}: ${count} times`);
    });

    console.log('\nRecent 5 decisions:');
    history.slice(-5).forEach(d => {
      console.log(`  • ${new Date(d.timestamp * 1000).toISOString()}: ${d.type}`);
    });
  }
}

// Main
async function runAutonomous() {
  const optimizer = new AutonomousOptimizer();

  console.log(`
╔═══════════════════════════════════════════════════════════════════╗
║  Autonomous Optimizer - Continuous Improvement Loop               ║
╠═══════════════════════════════════════════════════════════════════╣
║  Mode: AUTONOMOUS (no manual intervention needed)                 ║
║  Decision Interval: Every 100 cycles (~100 minutes)               ║
║  Learning: Continuous (improves every cycle)                      ║
║  Logging: All decisions to autonomous-decisions.jsonl             ║
╚═══════════════════════════════════════════════════════════════════╝
  `);

  // Run immediately
  await optimizer.makeDecisions();

  // Then every 100 cycles (~100 minutes)
  const DECISION_INTERVAL = 100 * 60 * 1000; // 100 cycles * 60s
  setInterval(async () => {
    await optimizer.makeDecisions();
  }, DECISION_INTERVAL);

  console.log(`\n✅ Autonomous optimizer running`);
  console.log(`   Next decision cycle in ${(DECISION_INTERVAL / 1000 / 60).toFixed(0)} minutes`);
}

if (require.main === module) {
  runAutonomous().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}

module.exports = AutonomousOptimizer;
