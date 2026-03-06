/**
 * Reinforced Learning System
 * Learns from past failures and automatically improves strategy parameters
 * Uses Q-learning principles on strategy execution outcomes
 */

const fs = require('fs');
const path = require('path');

class ReinforcedLearning {
  constructor(configFile = 'config.scheduler.json', logFile = 'execution-log.jsonl') {
    this.configFile = configFile;
    this.logFile = logFile;
    this.learnFile = 'learning-state.json';
    
    this.baseConfig = this.loadConfig();
    this.learnedState = this.loadLearningState();
    this.logs = this.loadLogs();
  }

  loadConfig() {
    if (!fs.existsSync(this.configFile)) {
      return this.getDefaultConfig();
    }
    try {
      return JSON.parse(fs.readFileSync(this.configFile, 'utf8'));
    } catch {
      return this.getDefaultConfig();
    }
  }

  getDefaultConfig() {
    return {
      agent: {
        min_apr_threshold: 5.0,
        max_slippage: 2.0,
        harvest_threshold_usd: 25,
        rebalance_apr_delta: 2.0,
        compound_confidence_threshold: 0.7,
      },
    };
  }

  loadLearningState() {
    if (!fs.existsSync(this.learnFile)) {
      return this.initializeLearnedState();
    }
    try {
      return JSON.parse(fs.readFileSync(this.learnFile, 'utf8'));
    } catch {
      return this.initializeLearnedState();
    }
  }

  initializeLearnedState() {
    return {
      version: 1,
      createdAt: Date.now(),
      strategies: {
        COMPOUND_YIELD: {
          attempts: 0,
          successes: 0,
          failures: 0,
          totalReward: 0,
          adjustedThreshold: 25, // USD
          confidenceLevel: 0.5,
          learningRate: 0.1,
        },
        REBALANCE: {
          attempts: 0,
          successes: 0,
          failures: 0,
          adjustedDelta: 2.0, // %
          confidenceLevel: 0.5,
          learningRate: 0.1,
        },
        DYNAMIC_HARVEST: {
          attempts: 0,
          successes: 0,
          failures: 0,
          totalReward: 0,
          gasRatioThreshold: 2.0,
          confidenceLevel: 0.5,
          learningRate: 0.1,
        },
      },
      improvements: [],
    };
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

  /**
   * Learn from execution history
   */
  learn() {
    console.log('\n🧠 Reinforced Learning: Analyzing history...');

    const recentLogs = this.logs.slice(-100); // Last 100 actions
    
    // Update strategy performance
    this._updateStrategyMetrics(recentLogs);

    // Analyze failure patterns
    this._analyzeFailurePatterns(recentLogs);

    // Generate parameter adjustments
    this._generateParameterAdjustments(recentLogs);

    // Save learning state
    this.saveLearnedState();

    return this.getOptimizedConfig();
  }

  /**
   * Track strategy performance metrics
   */
  _updateStrategyMetrics(logs) {
    logs.forEach(log => {
      const action = log.action;
      
      if (action?.includes('COMPOUND_YIELD')) {
        const strat = this.learnedState.strategies.COMPOUND_YIELD;
        strat.attempts += 1;
        if (!action.includes('ERROR')) {
          strat.successes += 1;
          strat.totalReward += log.rewards_usd || 0;
        } else {
          strat.failures += 1;
        }
      }

      if (action?.includes('REBALANCE')) {
        const strat = this.learnedState.strategies.REBALANCE;
        strat.attempts += 1;
        if (!action.includes('ERROR')) {
          strat.successes += 1;
        } else {
          strat.failures += 1;
        }
      }

      if (action?.includes('DYNAMIC_HARVEST')) {
        const strat = this.learnedState.strategies.DYNAMIC_HARVEST;
        strat.attempts += 1;
        if (!action.includes('ERROR')) {
          strat.successes += 1;
          strat.totalReward += log.rewards_usd || 0;
        } else {
          strat.failures += 1;
        }
      }
    });
  }

  /**
   * Analyze failure patterns to identify improvements
   */
  _analyzeFailurePatterns(logs) {
    const errors = logs.filter(l => l.action?.includes('ERROR'));
    const improvements = [];

    errors.forEach(error => {
      if (error.action?.includes('COMPOUND') && error.error?.includes('threshold')) {
        improvements.push({
          type: 'LOWER_THRESHOLD',
          strategy: 'COMPOUND_YIELD',
          reason: 'Threshold too high, missing opportunities',
          adjustment: 'reduce threshold by 10%',
        });
      }

      if (error.action?.includes('REBALANCE') && error.error?.includes('slippage')) {
        improvements.push({
          type: 'INCREASE_DELTA',
          strategy: 'REBALANCE',
          reason: 'APR delta too tight, causing slippage errors',
          adjustment: 'increase delta threshold by 0.5%',
        });
      }

      if (error.action?.includes('HARVEST') && error.error?.includes('gas')) {
        improvements.push({
          type: 'ADJUST_GAS_RATIO',
          strategy: 'DYNAMIC_HARVEST',
          reason: 'Gas estimation inaccurate',
          adjustment: 'increase ratio threshold from 2.0 to 2.5',
        });
      }
    });

    this.learnedState.improvements = improvements;
  }

  /**
   * Generate optimized parameters based on learning
   */
  _generateParameterAdjustments(logs) {
    const strategies = this.learnedState.strategies;

    // COMPOUND_YIELD: If success rate > 80%, lower threshold to capture more opportunities
    const compoundSuccess = strategies.COMPOUND_YIELD.successes / Math.max(strategies.COMPOUND_YIELD.attempts, 1);
    if (compoundSuccess > 0.8 && strategies.COMPOUND_YIELD.adjustedThreshold > 15) {
      const oldThreshold = strategies.COMPOUND_YIELD.adjustedThreshold;
      strategies.COMPOUND_YIELD.adjustedThreshold *= (1 - strategies.COMPOUND_YIELD.learningRate);
      strategies.COMPOUND_YIELD.confidenceLevel = Math.min(0.95, compoundSuccess);
      console.log(`  ✓ COMPOUND: Lowered threshold ${oldThreshold} → ${strategies.COMPOUND_YIELD.adjustedThreshold.toFixed(2)}`);
    }

    // REBALANCE: If failure rate > 20%, increase delta threshold
    const rebalanceFailure = strategies.REBALANCE.failures / Math.max(strategies.REBALANCE.attempts, 1);
    if (rebalanceFailure > 0.2 && strategies.REBALANCE.adjustedDelta < 5.0) {
      const oldDelta = strategies.REBALANCE.adjustedDelta;
      strategies.REBALANCE.adjustedDelta *= (1 + strategies.REBALANCE.learningRate);
      strategies.REBALANCE.confidenceLevel = Math.max(0.3, 1 - rebalanceFailure);
      console.log(`  ✓ REBALANCE: Increased delta ${oldDelta} → ${strategies.REBALANCE.adjustedDelta.toFixed(2)}`);
    }

    // DYNAMIC_HARVEST: Adjust gas ratio based on actual costs
    const harvestSuccess = strategies.DYNAMIC_HARVEST.successes / Math.max(strategies.DYNAMIC_HARVEST.attempts, 1);
    if (harvestSuccess < 0.6) {
      const oldRatio = strategies.DYNAMIC_HARVEST.gasRatioThreshold;
      strategies.DYNAMIC_HARVEST.gasRatioThreshold = Math.max(1.5, oldRatio * (1 - strategies.DYNAMIC_HARVEST.learningRate));
      console.log(`  ✓ HARVEST: Adjusted gas ratio ${oldRatio} → ${strategies.DYNAMIC_HARVEST.gasRatioThreshold.toFixed(2)}`);
    }
  }

  /**
   * Get optimized configuration
   */
  getOptimizedConfig() {
    const strats = this.learnedState.strategies;
    
    return {
      agent: {
        min_apr_threshold: this.baseConfig.agent.min_apr_threshold,
        max_slippage: this.baseConfig.agent.max_slippage,
        harvest_threshold_usd: strats.COMPOUND_YIELD.adjustedThreshold,
        rebalance_apr_delta: strats.REBALANCE.adjustedDelta,
        dynamic_harvest_gas_ratio: strats.DYNAMIC_HARVEST.gasRatioThreshold,
      },
      confidenceLevels: {
        COMPOUND_YIELD: strats.COMPOUND_YIELD.confidenceLevel,
        REBALANCE: strats.REBALANCE.confidenceLevel,
        DYNAMIC_HARVEST: strats.DYNAMIC_HARVEST.confidenceLevel,
      },
    };
  }

  /**
   * Save learned state
   */
  saveLearnedState() {
    this.learnedState.lastUpdated = new Date().toISOString();
    fs.writeFileSync(this.learnFile, JSON.stringify(this.learnedState, null, 2));
  }

  /**
   * Get learning summary
   */
  getLearningReport() {
    const strats = this.learnedState.strategies;

    return {
      timestamp: new Date().toISOString(),
      strategies: {
        COMPOUND_YIELD: {
          successRate: (strats.COMPOUND_YIELD.successes / Math.max(strats.COMPOUND_YIELD.attempts, 1) * 100).toFixed(1) + '%',
          threshold: strats.COMPOUND_YIELD.adjustedThreshold.toFixed(2),
          confidence: (strats.COMPOUND_YIELD.confidenceLevel * 100).toFixed(1) + '%',
          totalReward: strats.COMPOUND_YIELD.totalReward.toFixed(2),
        },
        REBALANCE: {
          successRate: (strats.REBALANCE.successes / Math.max(strats.REBALANCE.attempts, 1) * 100).toFixed(1) + '%',
          aprDelta: strats.REBALANCE.adjustedDelta.toFixed(2),
          confidence: (strats.REBALANCE.confidenceLevel * 100).toFixed(1) + '%',
        },
        DYNAMIC_HARVEST: {
          successRate: (strats.DYNAMIC_HARVEST.successes / Math.max(strats.DYNAMIC_HARVEST.attempts, 1) * 100).toFixed(1) + '%',
          gasRatio: strats.DYNAMIC_HARVEST.gasRatioThreshold.toFixed(2),
          confidence: (strats.DYNAMIC_HARVEST.confidenceLevel * 100).toFixed(1) + '%',
          totalReward: strats.DYNAMIC_HARVEST.totalReward.toFixed(2),
        },
      },
      improvements: this.learnedState.improvements.slice(0, 5),
    };
  }

  /**
   * Print learning report
   */
  printReport() {
    const report = this.getLearningReport();
    
    console.log(`
╔════════════════════════════════════════════════════════════╗
║              Reinforced Learning Report                    ║
╠════════════════════════════════════════════════════════════╣
║                                                             ║
║ COMPOUND_YIELD STRATEGY                                    ║
║   Success Rate:  ${report.strategies.COMPOUND_YIELD.successRate.padEnd(44)}║
║   Threshold:     $${report.strategies.COMPOUND_YIELD.threshold.padEnd(41)}║
║   Confidence:    ${report.strategies.COMPOUND_YIELD.confidence.padEnd(44)}║
║   Total Reward:  $${report.strategies.COMPOUND_YIELD.totalReward.padEnd(41)}║
║                                                             ║
║ REBALANCE STRATEGY                                         ║
║   Success Rate:  ${report.strategies.REBALANCE.successRate.padEnd(44)}║
║   APR Delta:     ${report.strategies.REBALANCE.aprDelta.padEnd(44)}%║
║   Confidence:    ${report.strategies.REBALANCE.confidence.padEnd(44)}║
║                                                             ║
║ DYNAMIC_HARVEST STRATEGY                                   ║
║   Success Rate:  ${report.strategies.DYNAMIC_HARVEST.successRate.padEnd(44)}║
║   Gas Ratio:     ${report.strategies.DYNAMIC_HARVEST.gasRatio.padEnd(44)}║
║   Confidence:    ${report.strategies.DYNAMIC_HARVEST.confidence.padEnd(44)}║
║   Total Reward:  $${report.strategies.DYNAMIC_HARVEST.totalReward.padEnd(41)}║
║                                                             ║
╚════════════════════════════════════════════════════════════╝
    `);

    if (report.improvements.length > 0) {
      console.log('\n🚀 Recent Improvements:');
      report.improvements.forEach((imp, i) => {
        console.log(`  ${i + 1}. [${imp.strategy}] ${imp.reason}`);
        console.log(`     → ${imp.adjustment}`);
      });
    }
  }
}

module.exports = ReinforcedLearning;
