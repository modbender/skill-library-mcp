/**
 * Swarm Metrics & Performance Tracking
 * Collects data over time for analysis and improvement
 */

const fs = require('fs');
const path = require('path');

const METRICS_DIR = path.join(process.env.HOME, '.config/clawdbot/swarm-metrics');
const METRICS_FILE = path.join(METRICS_DIR, 'performance.jsonl');
const DAILY_SUMMARY_FILE = path.join(METRICS_DIR, 'daily-summary.json');

class SwarmMetrics {
  constructor() {
    this.ensureMetricsDir();
    this.sessionStart = Date.now();
    this.sessionId = `${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
  }

  ensureMetricsDir() {
    if (!fs.existsSync(METRICS_DIR)) {
      fs.mkdirSync(METRICS_DIR, { recursive: true });
    }
  }

  /**
   * Log a Swarm execution
   */
  logExecution(data) {
    const entry = {
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
      type: data.type || 'orchestration', // orchestration, parallel, code-gen
      
      // Task info
      taskCount: data.taskCount || 0,
      phases: data.phases || 1,
      nodeTypes: data.nodeTypes || [],
      
      // Performance
      durationMs: data.durationMs,
      successCount: data.successCount || 0,
      failureCount: data.failureCount || 0,
      
      // Speedup estimation
      estimatedSequentialMs: data.estimatedSequentialMs || null,
      speedup: data.speedup || null,
      
      // Resource usage
      nodesUsed: data.nodesUsed || 0,
      maxNodesHit: data.maxNodesHit || false,
      
      // Cost tracking
      estimatedCost: data.estimatedCost || null,
      tokensUsed: data.tokensUsed || null,
      
      // Context
      taskDescription: data.taskDescription || null,
      
      // Issues/observations
      warnings: data.warnings || [],
      errors: data.errors || [],
    };

    // Append to JSONL file
    fs.appendFileSync(METRICS_FILE, JSON.stringify(entry) + '\n');
    
    // Update daily summary
    this.updateDailySummary(entry);
    
    return entry;
  }

  /**
   * Log an edge case or issue
   */
  logEdgeCase(data) {
    const edgeCaseFile = path.join(METRICS_DIR, 'edge-cases.jsonl');
    const entry = {
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
      type: data.type, // timeout, failure, unexpected, slow, etc.
      description: data.description,
      context: data.context || {},
      suggestedFix: data.suggestedFix || null,
    };
    
    fs.appendFileSync(edgeCaseFile, JSON.stringify(entry) + '\n');
    return entry;
  }

  /**
   * Update daily summary statistics
   */
  updateDailySummary(entry) {
    let summary = {};
    
    if (fs.existsSync(DAILY_SUMMARY_FILE)) {
      try {
        summary = JSON.parse(fs.readFileSync(DAILY_SUMMARY_FILE, 'utf8'));
      } catch (e) {
        summary = {};
      }
    }

    const today = new Date().toISOString().split('T')[0];
    
    if (!summary[today]) {
      summary[today] = {
        executions: 0,
        totalTasks: 0,
        totalDurationMs: 0,
        successCount: 0,
        failureCount: 0,
        avgSpeedup: 0,
        speedupSamples: [],
        nodeTypesUsed: {},
        edgeCases: 0,
      };
    }

    const day = summary[today];
    day.executions++;
    day.totalTasks += entry.taskCount;
    day.totalDurationMs += entry.durationMs;
    day.successCount += entry.successCount;
    day.failureCount += entry.failureCount;
    
    if (entry.speedup) {
      day.speedupSamples.push(entry.speedup);
      day.avgSpeedup = day.speedupSamples.reduce((a, b) => a + b, 0) / day.speedupSamples.length;
    }
    
    (entry.nodeTypes || []).forEach(type => {
      day.nodeTypesUsed[type] = (day.nodeTypesUsed[type] || 0) + 1;
    });

    fs.writeFileSync(DAILY_SUMMARY_FILE, JSON.stringify(summary, null, 2));
  }

  /**
   * Update daily cost tracking (called by daemon after each request)
   * 
   * costSummary contains SESSION-cumulative totals. We track the last
   * snapshot we wrote so we can compute the delta and add it to the
   * daily total — surviving daemon restarts without double-counting.
   */
  updateDailyCost(costSummary) {
    let summary = {};
    
    if (fs.existsSync(DAILY_SUMMARY_FILE)) {
      try {
        summary = JSON.parse(fs.readFileSync(DAILY_SUMMARY_FILE, 'utf8'));
      } catch (e) {
        summary = {};
      }
    }

    const today = new Date().toISOString().split('T')[0];
    if (!summary[today]) {
      summary[today] = {
        executions: 0, totalTasks: 0, totalDurationMs: 0,
        successCount: 0, failureCount: 0, avgSpeedup: 0,
        speedupSamples: [], nodeTypesUsed: {}, edgeCases: 0,
      };
    }

    const prev = summary[today].cost || {
      inputTokens: 0, outputTokens: 0,
      swarmCost: '0', opusEquivalent: '0', saved: '0',
    };

    // Compute delta from last snapshot this session wrote
    if (!this._lastCostSnapshot) {
      this._lastCostSnapshot = { inputTokens: 0, outputTokens: 0, swarmCost: 0 };
    }

    const deltaInput = costSummary.inputTokens - this._lastCostSnapshot.inputTokens;
    const deltaOutput = costSummary.outputTokens - this._lastCostSnapshot.outputTokens;
    const deltaSwarm = parseFloat(costSummary.swarmCost) - this._lastCostSnapshot.swarmCost;

    // Accumulate into daily total
    const newInput = (prev.inputTokens || 0) + deltaInput;
    const newOutput = (prev.outputTokens || 0) + deltaOutput;
    const newSwarm = parseFloat(prev.swarmCost || 0) + deltaSwarm;

    // Recalculate Opus equivalent from accumulated totals
    const opusCost = (newInput / 1_000_000) * 15.00 + (newOutput / 1_000_000) * 75.00;
    const saved = opusCost - newSwarm;

    summary[today].cost = {
      inputTokens: newInput,
      outputTokens: newOutput,
      swarmCost: newSwarm.toFixed(6),
      opusEquivalent: opusCost.toFixed(4),
      saved: saved.toFixed(4),
      savingsMultiplier: newSwarm > 0 ? (opusCost / newSwarm).toFixed(0) + 'x' : 'N/A',
    };

    // Update snapshot
    this._lastCostSnapshot = {
      inputTokens: costSummary.inputTokens,
      outputTokens: costSummary.outputTokens,
      swarmCost: parseFloat(costSummary.swarmCost),
    };

    fs.writeFileSync(DAILY_SUMMARY_FILE, JSON.stringify(summary, null, 2));
  }

  /**
   * Get monthly savings report
   */
  getMonthlySavings() {
    if (!fs.existsSync(DAILY_SUMMARY_FILE)) {
      return { error: 'No metrics collected yet' };
    }

    const summary = JSON.parse(fs.readFileSync(DAILY_SUMMARY_FILE, 'utf8'));
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];

    let totalSwarmCost = 0;
    let totalOpusCost = 0;
    let totalTasks = 0;
    let totalTokens = 0;
    let daysActive = 0;

    for (const [date, day] of Object.entries(summary)) {
      if (date >= monthStart && day.cost) {
        totalSwarmCost += parseFloat(day.cost.swarmCost || 0);
        totalOpusCost += parseFloat(day.cost.opusEquivalent || 0);
        totalTokens += (day.cost.inputTokens || 0) + (day.cost.outputTokens || 0);
        totalTasks += day.totalTasks || 0;
        daysActive++;
      }
    }

    const saved = totalOpusCost - totalSwarmCost;

    return {
      month: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`,
      daysActive,
      totalTasks,
      totalTokens,
      swarmCost: `$${totalSwarmCost.toFixed(4)}`,
      opusEquivalent: `$${totalOpusCost.toFixed(2)}`,
      saved: `$${saved.toFixed(2)}`,
      savingsMultiplier: totalSwarmCost > 0 ? `${(totalOpusCost / totalSwarmCost).toFixed(0)}x` : 'N/A',
    };
  }

  /**
   * Get performance report
   */
  getReport(days = 7) {
    if (!fs.existsSync(DAILY_SUMMARY_FILE)) {
      return { error: 'No metrics collected yet' };
    }

    const summary = JSON.parse(fs.readFileSync(DAILY_SUMMARY_FILE, 'utf8'));
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    
    const relevantDays = Object.entries(summary)
      .filter(([date]) => new Date(date) >= cutoff)
      .sort(([a], [b]) => b.localeCompare(a));

    const totals = {
      days: relevantDays.length,
      executions: 0,
      tasks: 0,
      durationMs: 0,
      success: 0,
      failures: 0,
      avgSpeedup: 0,
    };

    const speedups = [];
    
    relevantDays.forEach(([, day]) => {
      totals.executions += day.executions;
      totals.tasks += day.totalTasks;
      totals.durationMs += day.totalDurationMs;
      totals.success += day.successCount;
      totals.failures += day.failureCount;
      speedups.push(...(day.speedupSamples || []));
    });

    if (speedups.length > 0) {
      totals.avgSpeedup = speedups.reduce((a, b) => a + b, 0) / speedups.length;
    }

    return {
      period: `Last ${days} days`,
      ...totals,
      successRate: totals.tasks > 0 ? ((totals.success / totals.tasks) * 100).toFixed(1) + '%' : 'N/A',
      avgSpeedup: totals.avgSpeedup.toFixed(2) + 'x',
      dailyBreakdown: Object.fromEntries(relevantDays),
    };
  }

  /**
   * Get edge cases for review
   */
  getEdgeCases(limit = 20) {
    const edgeCaseFile = path.join(METRICS_DIR, 'edge-cases.jsonl');
    
    if (!fs.existsSync(edgeCaseFile)) {
      return [];
    }

    const lines = fs.readFileSync(edgeCaseFile, 'utf8').trim().split('\n');
    return lines
      .slice(-limit)
      .map(line => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      })
      .filter(Boolean);
  }
}

// Singleton instance
const metrics = new SwarmMetrics();

module.exports = { SwarmMetrics, metrics };
