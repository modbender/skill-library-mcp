#!/usr/bin/env node

/**
 * API Cost Tracker - Main Script
 * Track AI API costs across multiple providers
 */

import fs from 'fs/promises';
import path from 'path';

// Pricing per 1K tokens (USD)
const PRICING = {
  openai: {
    'gpt-4': { input: 0.03, output: 0.06 },
    'gpt-4-turbo': { input: 0.01, output: 0.03 },
    'gpt-3.5-turbo': { input: 0.0005, output: 0.0015 }
  },
  anthropic: {
    'claude-3-opus': { input: 0.015, output: 0.075 },
    'claude-3-sonnet': { input: 0.003, output: 0.015 },
    'claude-3-haiku': { input: 0.00025, output: 0.00125 }
  },
  google: {
    'gemini-pro': { input: 0.00025, output: 0.0005 },
    'gemini-ultra': { input: 0.0025, output: 0.0075 }
  }
};

class APICostTracker {
  constructor(config = {}) {
    this.config = config;
    this.dataDir = config.dataDir || './data';
    this.costs = {
      openai: { total: 0, models: {} },
      anthropic: { total: 0, models: {} },
      google: { total: 0, models: {} }
    };
    this.budgets = config.budgets || {
      daily: 10,
      weekly: 50,
      monthly: 200
    };
  }

  /**
   * Track API usage
   */
  async track(provider, model, inputTokens, outputTokens) {
    const pricing = PRICING[provider]?.[model];
    if (!pricing) {
      throw new Error(`Unknown provider/model: ${provider}/${model}`);
    }

    const inputCost = (inputTokens / 1000) * pricing.input;
    const outputCost = (outputTokens / 1000) * pricing.output;
    const totalCost = inputCost + outputCost;

    // Update costs
    if (!this.costs[provider].models[model]) {
      this.costs[provider].models[model] = {
        inputTokens: 0,
        outputTokens: 0,
        cost: 0
      };
    }

    this.costs[provider].models[model].inputTokens += inputTokens;
    this.costs[provider].models[model].outputTokens += outputTokens;
    this.costs[provider].models[model].cost += totalCost;
    this.costs[provider].total += totalCost;

    // Save to daily file
    await this.saveDailyCost({
      provider,
      model,
      inputTokens,
      outputTokens,
      cost: totalCost,
      timestamp: new Date().toISOString()
    });

    return {
      cost: totalCost,
      total: this.getTotalCost()
    };
  }

  /**
   * Get total cost across all providers
   */
  getTotalCost() {
    return Object.values(this.costs).reduce((sum, p) => sum + p.total, 0);
  }

  /**
   * Get cost breakdown
   */
  getBreakdown() {
    return {
      total: this.getTotalCost(),
      providers: Object.fromEntries(
        Object.entries(this.costs).map(([name, data]) => [name, data.total])
      ),
      models: Object.fromEntries(
        Object.entries(this.costs).flatMap(([provider, data]) =>
          Object.entries(data.models).map(([model, stats]) => [
            `${provider}/${model}`,
            stats.cost
          ])
        )
      )
    };
  }

  /**
   * Check budget status
   */
  checkBudget() {
    const total = this.getTotalCost();
    const status = {
      total,
      budgets: {}
    };

    for (const [period, limit] of Object.entries(this.budgets)) {
      const percentage = (total / limit) * 100;
      status.budgets[period] = {
        limit,
        used: total,
        percentage: percentage.toFixed(1),
        status: percentage >= 100 ? 'exceeded' : percentage >= 90 ? 'critical' : percentage >= 75 ? 'warning' : 'ok'
      };
    }

    return status;
  }

  /**
   * Save daily cost data
   */
  async saveDailyCost(costEntry) {
    const today = new Date().toISOString().split('T')[0];
    const filePath = path.join(this.dataDir, 'costs', `${today}.json`);

    try {
      await fs.mkdir(path.dirname(filePath), { recursive: true });

      let data = [];
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        data = JSON.parse(content);
      } catch {
        // File doesn't exist yet
      }

      data.push(costEntry);
      await fs.writeFile(filePath, JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error saving cost data:', error);
    }
  }

  /**
   * Load historical data
   */
  async loadHistory(days = 30) {
    const history = [];
    const today = new Date();

    for (let i = 0; i < days; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const filePath = path.join(this.dataDir, 'costs', `${dateStr}.json`);

      try {
        const content = await fs.readFile(filePath, 'utf-8');
        const data = JSON.parse(content);
        history.push({
          date: dateStr,
          entries: data,
          total: data.reduce((sum, entry) => sum + entry.cost, 0)
        });
      } catch {
        // File doesn't exist
      }
    }

    return history;
  }

  /**
   * Generate report
   */
  async generateReport(format = 'markdown') {
    const breakdown = this.getBreakdown();
    const budgetStatus = this.checkBudget();
    const history = await this.loadHistory(7);

    if (format === 'json') {
      return JSON.stringify({ breakdown, budgetStatus, history }, null, 2);
    }

    if (format === 'markdown') {
      let report = `# 💰 API Cost Report\n\n`;
      report += `**Generated:** ${new Date().toLocaleString()}\n\n`;

      report += `## 📊 Total Costs\n\n`;
      report += `**Total:** $${breakdown.total.toFixed(2)}\n\n`;

      report += `### By Provider\n\n`;
      for (const [provider, cost] of Object.entries(breakdown.providers)) {
        if (cost > 0) {
          report += `- **${provider}:** $${cost.toFixed(2)}\n`;
        }
      }

      report += `\n### By Model\n\n`;
      for (const [model, cost] of Object.entries(breakdown.models)) {
        if (cost > 0) {
          report += `- **${model}:** $${cost.toFixed(2)}\n`;
        }
      }

      report += `\n## 💵 Budget Status\n\n`;
      for (const [period, status] of Object.entries(budgetStatus.budgets)) {
        const emoji = status.status === 'exceeded' ? '❌' : status.status === 'critical' ? '⚠️' : status.status === 'warning' ? '🔶' : '✅';
        report += `${emoji} **${period}:** $${status.used.toFixed(2)} / $${status.limit} (${status.percentage}%)\n`;
      }

      if (history.length > 0) {
        report += `\n## 📈 Last 7 Days\n\n`;
        for (const day of history.slice(0, 7)) {
          report += `- **${day.date}:** $${day.total.toFixed(2)} (${day.entries.length} requests)\n`;
        }
      }

      return report;
    }

    if (format === 'csv') {
      let csv = 'Provider,Model,Input Tokens,Output Tokens,Cost\n';
      for (const [provider, data] of Object.entries(this.costs)) {
        for (const [model, stats] of Object.entries(data.models)) {
          csv += `${provider},${model},${stats.inputTokens},${stats.outputTokens},${stats.cost.toFixed(4)}\n`;
        }
      }
      return csv;
    }

    throw new Error(`Unknown format: ${format}`);
  }

  /**
   * Get optimization suggestions
   */
  getOptimizationTips() {
    const tips = [];
    const breakdown = this.getBreakdown();

    // Check for expensive model usage
    for (const [model, cost] of Object.entries(breakdown.models)) {
      if (model.includes('gpt-4') && cost > 10) {
        tips.push({
          type: 'model_switch',
          priority: 'high',
          message: `Consider using GPT-3.5 Turbo for simpler tasks. Current GPT-4 spend: $${cost.toFixed(2)}`,
          potential_savings: cost * 0.67 // ~67% cheaper
        });
      }

      if (model.includes('claude-3-opus') && cost > 10) {
        tips.push({
          type: 'model_switch',
          priority: 'high',
          message: `Consider using Claude-3 Sonnet or Haiku for faster responses. Current Opus spend: $${cost.toFixed(2)}`,
          potential_savings: cost * 0.8
        });
      }
    }

    // Check budget usage
    const budgetStatus = this.checkBudget();
    if (budgetStatus.budgets.monthly.status !== 'ok') {
      tips.push({
        type: 'budget_alert',
        priority: 'critical',
        message: `Monthly budget is at ${budgetStatus.budgets.monthly.percentage}% usage`,
        action: 'Review usage and consider rate limiting'
      });
    }

    return tips;
  }
}

// CLI Interface
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  const config = {
    dataDir: './data',
    budgets: {
      daily: 10,
      weekly: 50,
      monthly: 200
    }
  };

  const tracker = new APICostTracker(config);

  // Demo data for testing
  await tracker.track('openai', 'gpt-4', 50000, 25000);
  await tracker.track('openai', 'gpt-3.5-turbo', 200000, 100000);
  await tracker.track('anthropic', 'claude-3-sonnet', 30000, 15000);
  await tracker.track('google', 'gemini-pro', 40000, 20000);

  if (command === 'track') {
    console.log('💰 API Cost Tracker\n');
    const breakdown = tracker.getBreakdown();
    console.log('Total Cost:', `$${breakdown.total.toFixed(2)}`);
    console.log('\nBy Provider:');
    for (const [provider, cost] of Object.entries(breakdown.providers)) {
      if (cost > 0) {
        console.log(`  ${provider}: $${cost.toFixed(2)}`);
      }
    }
    console.log('\nBy Model:');
    for (const [model, cost] of Object.entries(breakdown.models)) {
      if (cost > 0) {
        console.log(`  ${model}: $${cost.toFixed(2)}`);
      }
    }
  } else if (command === 'budget') {
    const status = tracker.checkBudget();
    console.log('💵 Budget Status\n');
    for (const [period, info] of Object.entries(status.budgets)) {
      const emoji = info.status === 'exceeded' ? '❌' : info.status === 'critical' ? '⚠️' : info.status === 'warning' ? '🔶' : '✅';
      console.log(`${emoji} ${period}: $${info.used.toFixed(2)} / $${info.limit} (${info.percentage}%)`);
    }
  } else if (command === 'report') {
    const format = args.includes('--markdown') ? 'markdown' : args.includes('--csv') ? 'csv' : 'markdown';
    const report = await tracker.generateReport(format);
    console.log(report);
  } else if (command === 'optimize') {
    const tips = tracker.getOptimizationTips();
    console.log('💡 Optimization Tips\n');
    tips.forEach((tip, i) => {
      console.log(`${i + 1}. [${tip.priority.toUpperCase()}] ${tip.message}`);
      if (tip.potential_savings) {
        console.log(`   Potential savings: $${tip.potential_savings.toFixed(2)}`);
      }
    });
  } else {
    console.log(`
API Cost Tracker v1.0.0

Usage:
  node main.mjs track           - Show current costs
  node main.mjs budget          - Check budget status
  node main.mjs report          - Generate full report
  node main.mjs optimize        - Get optimization tips

Options:
  --format <markdown|csv|json>  - Report format
  --output <file>               - Save to file
    `);
  }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { APICostTracker, PRICING };
