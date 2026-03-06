#!/usr/bin/env node

/**
 * API Cost Tracker - Tests
 */

import { APICostTracker, PRICING } from '../scripts/main.mjs';

console.log('🧪 Running API Cost Tracker Tests\n');

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`✅ ${message}`);
    passed++;
  } else {
    console.log(`❌ ${message}`);
    failed++;
  }
}

// Test 1: Basic tracking
console.log('Test 1: Basic Cost Tracking');
const tracker = new APICostTracker();

const result1 = await tracker.track('openai', 'gpt-4', 1000, 500);
const expectedCost = (1000/1000 * 0.03) + (500/1000 * 0.06);
assert(
  Math.abs(result1.cost - expectedCost) < 0.0001,
  `GPT-4 cost calculation correct ($${result1.cost.toFixed(4)})`
);

// Test 2: Multiple tracks
console.log('\nTest 2: Multiple API Calls');
await tracker.track('openai', 'gpt-3.5-turbo', 5000, 2500);
await tracker.track('anthropic', 'claude-3-sonnet', 3000, 1500);

const breakdown = tracker.getBreakdown();
assert(breakdown.total > 0, 'Total cost calculated');
assert(breakdown.providers.openai > 0, 'OpenAI costs tracked');
assert(breakdown.providers.anthropic > 0, 'Anthropic costs tracked');

// Test 3: Budget checking
console.log('\nTest 3: Budget Monitoring');
const budgetStatus = tracker.checkBudget();
assert(budgetStatus.total > 0, 'Budget status returns total');
assert(budgetStatus.budgets.daily !== undefined, 'Daily budget exists');
assert(budgetStatus.budgets.monthly !== undefined, 'Monthly budget exists');

// Test 4: Pricing reference
console.log('\nTest 4: Pricing Reference');
assert(PRICING.openai['gpt-4'] !== undefined, 'GPT-4 pricing exists');
assert(PRICING.anthropic['claude-3-opus'] !== undefined, 'Claude-3 Opus pricing exists');
assert(PRICING.google['gemini-pro'] !== undefined, 'Gemini Pro pricing exists');

// Test 5: Optimization tips
console.log('\nTest 5: Optimization Tips');
const expensiveTracker = new APICostTracker();
await expensiveTracker.track('openai', 'gpt-4', 500000, 250000); // Expensive!
const tips = expensiveTracker.getOptimizationTips();
assert(tips.length > 0, 'Optimization tips generated');
assert(tips[0].potential_savings > 0, 'Savings calculated');

// Summary
console.log('\n' + '='.repeat(50));
console.log(`Total: ${passed + failed}`);
console.log(`✅ Passed: ${passed}`);
console.log(`❌ Failed: ${failed}`);
console.log('='.repeat(50));

if (failed > 0) {
  process.exit(1);
}
