#!/usr/bin/env node
/**
 * OpenClaw Smart Router - CLI Interface
 *
 * Commands:
 * - stats: Show routing statistics
 * - patterns: List learned patterns
 * - savings: Analyze cost savings vs Opus baseline
 * - test <query>: Test model selection for a query
 * - license: Check license status
 * - subscribe: Subscribe to Pro tier
 */

import { Command } from 'commander';
import { getSmartRouter } from './index.js';

const program = new Command();

program
  .name('openclaw-smart-router')
  .description('Intelligent model selection for OpenClaw agents')
  .version('1.0.0');

// Stats command
program
  .command('stats')
  .description('Show routing statistics')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .option('--timeframe <days>', 'Timeframe in days', '30')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const router = getSmartRouter();
      const stats = await router.getStats(options.wallet, `${options.timeframe} days`);

      console.log('\nSmart Router Statistics:\n');
      console.log(`${'='.repeat(70)}`);
      console.log(`  Agent: ${options.wallet.substring(0, 10)}...`);
      console.log(`  Timeframe: ${stats.timeframe}`);
      console.log(`${'='.repeat(70)}`);
      console.log(`\n  Routing Statistics:`);
      console.log(`    Total Decisions: ${stats.routing.total_decisions}`);
      console.log(`    Success Rate: ${(stats.routing.success_rate * 100).toFixed(1)}%`);
      console.log(`    Avg Complexity: ${stats.routing.avg_complexity.toFixed(2)}`);
      console.log(`\n  Cost Analysis:`);
      console.log(`    Total Cost: $${stats.savings.total_cost.toFixed(4)}`);
      console.log(`    Baseline (Opus): $${stats.savings.estimated_default_cost.toFixed(4)}`);
      console.log(`    Total Savings: $${stats.savings.total_savings.toFixed(4)}`);
      console.log(`    Savings Rate: ${stats.savings.savings_percentage.toFixed(1)}%`);
      console.log(`\n  Quota Status:`);
      console.log(`    Tier: ${stats.quota.tier.toUpperCase()}`);
      console.log(`    Today: ${stats.quota.decisions_today} decisions`);
      if (stats.quota.decisions_limit === -1) {
        console.log(`    Limit: Unlimited`);
      } else {
        console.log(`    Remaining: ${stats.quota.remaining}/${stats.quota.decisions_limit}`);
      }

      if (stats.patterns && stats.patterns.length > 0) {
        console.log(`\n  Top Learned Patterns (${stats.patterns.length}):`);
        for (const pattern of stats.patterns.slice(0, 3)) {
          console.log(`    ${pattern.pattern_type}: ${pattern.optimal_model} (${(pattern.confidence_score * 100).toFixed(0)}%)`);
        }
      }

      console.log(`\n${'='.repeat(70)}\n`);

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

// Patterns command
program
  .command('patterns')
  .description('List learned patterns')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .option('--limit <n>', 'Number of patterns to show', '20')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const router = getSmartRouter();
      const patterns = router.getPatterns(options.wallet);
      const limit = parseInt(options.limit);

      if (!patterns || patterns.length === 0) {
        console.log(`\nNo patterns learned yet\n`);
        return;
      }

      console.log(`\nLearned Routing Patterns (${patterns.length}):\n`);
      console.log(`${'='.repeat(70)}`);

      for (const pattern of patterns.slice(0, limit)) {
        console.log(`\n  [${'─'.repeat(66)}]`);
        console.log(`  Type: ${pattern.pattern_type.toUpperCase()}`);
        console.log(`  Optimal Model: ${pattern.optimal_model}`);
        console.log(`  Confidence: ${(pattern.confidence_score * 100).toFixed(1)}%`);
        console.log(`  Usage Count: ${pattern.usage_count || 0}`);
        console.log(`  Success Rate: ${(pattern.success_rate * 100).toFixed(1)}%`);
        console.log(`  Avg Cost: $${(pattern.avg_cost || 0).toFixed(6)}`);
        console.log(`  Created: ${new Date(pattern.created_at).toLocaleString()}`);
      }

      console.log(`\n${'='.repeat(70)}\n`);

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

// Savings command
program
  .command('savings')
  .description('Analyze cost savings vs Opus baseline')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .option('--timeframe <days>', 'Timeframe in days', '30')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const router = getSmartRouter();
      const stats = await router.getStats(options.wallet, `${options.timeframe} days`);
      const savings = stats.savings;

      console.log('\nCost Savings Analysis:\n');
      console.log(`${'='.repeat(70)}`);
      console.log(`  Agent: ${options.wallet.substring(0, 10)}...`);
      console.log(`  Timeframe: ${stats.timeframe}`);
      console.log(`${'='.repeat(70)}`);
      console.log(`\n  Baseline (All Opus 4):`);
      console.log(`    Total Cost: $${savings.estimated_default_cost.toFixed(4)}`);
      console.log(`    Decisions: ${savings.total_decisions}`);
      console.log(`    Avg per decision: $${savings.avg_default_cost_per_decision.toFixed(6)}`);

      console.log(`\n  Smart Router (Optimized):`);
      console.log(`    Total Cost: $${savings.total_cost.toFixed(4)}`);
      console.log(`    Decisions: ${savings.total_decisions}`);
      console.log(`    Avg per decision: $${savings.avg_cost_per_decision.toFixed(6)}`);

      console.log(`\n  Savings:`);
      console.log(`    Total Saved: $${savings.total_savings.toFixed(4)}`);
      console.log(`    Percentage: ${savings.savings_percentage.toFixed(1)}%`);

      // Extrapolate savings
      if (savings.total_decisions > 0) {
        const savingsPerDecision = savings.total_savings / savings.total_decisions;
        const monthlyProjection = savingsPerDecision * 1000; // Assume 1000 decisions/month
        const yearlyProjection = monthlyProjection * 12;

        console.log(`\n  Projected Savings:`);
        console.log(`    Monthly (1K decisions): $${monthlyProjection.toFixed(2)}`);
        console.log(`    Yearly (12K decisions): $${yearlyProjection.toFixed(2)}`);
      }

      console.log(`\n  Quality Maintained: ${(stats.routing.avg_quality || 0.5).toFixed(2)}`);
      console.log(`  ROI: ${savings.total_savings > 0.5 ? 'POSITIVE ✓' : 'Building...'}`);
      console.log(`${'='.repeat(70)}\n`);

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

// Test command
program
  .command('test <query>')
  .description('Test model selection for a query')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .action(async (query, options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const router = getSmartRouter();
      const result = await router.testSelection(query, options.wallet);

      console.log('\nModel Selection Test:\n');
      console.log(`${'='.repeat(70)}`);
      console.log(`  Query: "${result.query}"`);
      console.log(`${'='.repeat(70)}`);
      console.log(`\n  Task Analysis:`);
      console.log(`    Complexity: ${result.task_analysis.complexity_score.toFixed(2)} / 1.0`);
      console.log(`    Task Type: ${result.task_analysis.task_type}`);
      console.log(`    Estimated Tokens: ${result.task_analysis.estimated_tokens}`);
      console.log(`    Has Code: ${result.task_analysis.has_code ? 'Yes' : 'No'}`);
      console.log(`    Has Errors: ${result.task_analysis.has_errors ? 'Yes' : 'No'}`);

      console.log(`\n  Selection Decision:`);
      console.log(`    Selected Model: ${result.model_selection.model}`);
      console.log(`    Provider: ${result.model_selection.provider}`);
      console.log(`    Reason: ${result.model_selection.reason}`);
      console.log(`    Confidence: ${(result.model_selection.confidence * 100).toFixed(1)}%`);

      if (result.model_selection.alternatives && result.model_selection.alternatives.length > 0) {
        console.log(`\n  Alternatives Considered:`);
        for (const alt of result.model_selection.alternatives.slice(0, 3)) {
          console.log(`    ${alt.model}: Score ${alt.score.toFixed(2)}`);
        }
      }

      console.log(`\n${'='.repeat(70)}\n`);

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

// License command
program
  .command('license')
  .description('Check license status')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const router = getSmartRouter();
      const license = router.checkLicense(options.wallet);

      console.log('\nLicense Status:\n');
      console.log(`${'='.repeat(70)}`);
      console.log(`  Agent: ${options.wallet.substring(0, 10)}...`);
      console.log(`  Tier: ${license.tier.toUpperCase()}`);

      if (license.valid) {
        console.log(`  Status: Active`);
        console.log(`  Expires: ${new Date(license.expires).toLocaleDateString()}`);
        console.log(`  Days Remaining: ${license.days_remaining}`);
        console.log('\n  Pro Features:');
        console.log('    - Unlimited routing decisions');
        console.log('    - Advanced ML-enhanced routing');
        console.log('    - Custom model preferences');
        console.log('    - Priority support');
      } else if (license.expired) {
        console.log(`  Status: EXPIRED`);
        console.log('\n  Your Pro license has expired.');
        console.log('  Run "openclaw smart-router subscribe --wallet <wallet>" to renew.');
      } else {
        console.log(`  Status: FREE TIER`);
        console.log('\n  Free Tier Features:');
        console.log('    - 100 routing decisions per day');
        console.log('    - Basic complexity analysis');
        console.log('    - Standard model routing');
        console.log('\n  Upgrade to Pro for:');
        console.log('    - Unlimited routing decisions');
        console.log('    - Advanced ML-enhanced routing');
        console.log('    - Custom model preferences');
        console.log('    - Priority support');
        console.log('\n  Price: 0.5 USDT/month on Base');
        console.log('  Run "openclaw smart-router subscribe --wallet <wallet>" to upgrade.');
      }

      console.log(`${'='.repeat(70)}\n`);

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

// Subscribe command
program
  .command('subscribe')
  .description('Subscribe to Pro tier')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const router = getSmartRouter();
      const paymentRequest = await router.createPaymentRequest(options.wallet);

      console.log('\nSubscribe to Smart Router Pro\n');
      console.log(`${'='.repeat(70)}`);
      console.log('  Price: 0.5 USDT/month');
      console.log('  Chain: Base');
      console.log('  Protocol: x402');
      console.log(`${'='.repeat(70)}\n`);

      console.log('Payment Request Details:\n');
      console.log(`  Request ID: ${paymentRequest.request_id}`);
      console.log(`  Recipient: ${paymentRequest.recipient}`);
      console.log(`  Amount: ${paymentRequest.amount} ${paymentRequest.token}`);
      console.log(`  Chain: ${paymentRequest.chain}`);
      console.log(`  Expires: ${new Date(paymentRequest.expires_at).toLocaleString()}\n`);

      console.log('Instructions:\n');
      console.log('  1. Send 0.5 USDT to the recipient address via x402 protocol');
      console.log('  2. After payment, verify with your transaction hash:\n');
      console.log(`     curl -X POST http://localhost:9093/api/x402/verify \\`);
      console.log(`       -H "Content-Type: application/json" \\`);
      console.log(`       -d '{`);
      console.log(`         "request_id": "${paymentRequest.request_id}",`);
      console.log(`         "tx_hash": "YOUR_TX_HASH",`);
      console.log(`         "agent_wallet": "${options.wallet}"`);
      console.log(`       }'\n`);

      console.log('  Or use the dashboard at: http://localhost:9093\n');

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse();
