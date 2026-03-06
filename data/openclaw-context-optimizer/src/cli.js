#!/usr/bin/env node
/**
 * OpenClaw Context Optimizer - CLI Interface
 *
 * Commands:
 * - compress: Test compression on text
 * - stats: Show compression statistics
 * - patterns: List learned patterns
 * - license: Check license status
 * - subscribe: Subscribe to Pro tier
 */

import { Command } from 'commander';
import { getContextOptimizer } from './index.js';

const program = new Command();

program
  .name('openclaw-context-optimizer')
  .description('Intelligent context compression for OpenClaw agents')
  .version('1.0.0');

// Compress command
program
  .command('compress <text>')
  .description('Test compression on provided text')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .option('--strategy <strategy>', 'Compression strategy (deduplication, pruning, summarization, template, hybrid)', 'hybrid')
  .action(async (text, options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const optimizer = getContextOptimizer();
      const result = await optimizer.compress(text, options.wallet, options.strategy);

      console.log('\nCompression Results:\n');
      console.log(`${'='.repeat(70)}`);
      console.log(`Strategy: ${result.strategy}`);
      console.log(`${'='.repeat(70)}`);
      console.log(`\nOriginal Tokens: ${result.metrics.originalTokens}`);
      console.log(`Compressed Tokens: ${result.metrics.compressedTokens}`);
      console.log(`Tokens Saved: ${result.metrics.tokensRemoved}`);
      console.log(`Compression Ratio: ${(result.metrics.compressionRatio * 100).toFixed(1)}%`);
      console.log(`Quality Score: ${result.metrics.qualityScore.toFixed(2)}`);

      // Cost savings estimate
      const costSaved = (result.metrics.tokensRemoved / 1000) * 0.002;
      console.log(`Estimated Cost Saved: $${costSaved.toFixed(6)}`);

      console.log(`\n${'='.repeat(70)}`);
      console.log('Compressed Text:\n');
      console.log(result.compressed);
      console.log(`\n${'='.repeat(70)}\n`);

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

// Stats command
program
  .command('stats')
  .description('Show compression statistics')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const optimizer = getContextOptimizer();
      const stats = await optimizer.getStats(options.wallet);

      console.log('\nCompression Statistics:\n');
      console.log(`${'='.repeat(70)}`);
      console.log(`  Agent: ${options.wallet.substring(0, 10)}...`);
      console.log(`  Tier: ${stats.tier.toUpperCase()}`);
      console.log(`${'='.repeat(70)}`);
      console.log(`\n  Total Compressions: ${stats.total_compressions.toLocaleString()}`);
      console.log(`  Total Tokens Saved: ${stats.total_tokens_saved.toLocaleString()}`);
      console.log(`  Total Cost Saved: $${stats.total_cost_saved.toFixed(4)}`);
      console.log(`  Average Compression: ${(stats.avg_compression_ratio * 100).toFixed(1)}%`);

      if (stats.quota_remaining !== -1) {
        console.log(`\n  Quota Today: ${stats.quota_remaining} remaining`);
      } else {
        console.log(`\n  Quota: Unlimited (Pro tier)`);
      }

      if (stats.learned_patterns && stats.learned_patterns.length > 0) {
        console.log(`\n  Top Learned Patterns (${stats.learned_patterns.length}):`);
        for (const pattern of stats.learned_patterns.slice(0, 5)) {
          const patternPreview = pattern.pattern_text.substring(0, 50);
          console.log(`    [${pattern.pattern_type}] ${patternPreview}...`);
          console.log(`    └─ Impact: ${pattern.token_impact} tokens, Importance: ${pattern.importance_score.toFixed(2)}`);
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
  .description('List learned compression patterns')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .option('--type <type>', 'Filter by pattern type (redundant, high_value, low_value, template)')
  .option('--limit <n>', 'Number of patterns to show', '20')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const optimizer = getContextOptimizer();
      const patterns = await optimizer.getPatterns(options.wallet, options.type);
      const limit = parseInt(options.limit);

      if (!patterns || patterns.length === 0) {
        console.log(`\nNo patterns found${options.type ? ` for type: ${options.type}` : ''}\n`);
        return;
      }

      console.log(`\nLearned Compression Patterns (${patterns.length}):\n`);
      console.log(`${'='.repeat(70)}`);

      for (const pattern of patterns.slice(0, limit)) {
        console.log(`\n  [${'─'.repeat(66)}]`);
        console.log(`  Type: ${pattern.pattern_type.toUpperCase()}`);
        console.log(`  Text: ${pattern.pattern_text.substring(0, 80)}...`);
        console.log(`  Frequency: ${pattern.frequency} times`);
        console.log(`  Token Impact: ${pattern.token_impact} tokens`);
        console.log(`  Importance: ${pattern.importance_score.toFixed(2)}`);
        console.log(`  Last Seen: ${new Date(pattern.last_seen).toLocaleString()}`);
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

      const optimizer = getContextOptimizer();
      const license = optimizer.checkLicense(options.wallet);

      console.log('\nLicense Status:\n');
      console.log(`${'='.repeat(70)}`);
      console.log(`  Agent: ${options.wallet.substring(0, 10)}...`);
      console.log(`  Tier: ${license.tier.toUpperCase()}`);

      if (license.valid) {
        console.log(`  Status: Active`);
        console.log(`  Expires: ${new Date(license.expires).toLocaleDateString()}`);
        console.log(`  Days Remaining: ${license.days_remaining}`);
        console.log('\n  Pro Features:');
        console.log('    - Unlimited daily compressions');
        console.log('    - Advanced compression strategies');
        console.log('    - Pattern learning optimization');
        console.log('    - Priority support');
      } else if (license.expired) {
        console.log(`  Status: EXPIRED`);
        console.log('\n  Your Pro license has expired.');
        console.log('  Run "openclaw context-optimizer subscribe" to renew.');
      } else {
        console.log(`  Status: FREE TIER`);
        console.log('\n  Free Tier Limits:');
        console.log('    - 100 compressions per day');
        console.log('    - Basic compression strategies');
        console.log('    - Limited pattern learning');
        console.log('\n  Upgrade to Pro:');
        console.log('    - Unlimited compressions');
        console.log('    - Advanced strategies');
        console.log('    - Full pattern learning');
        console.log('    - Priority support');
        console.log('\n  Price: 0.5 USDT/month on Base');
        console.log('  Run "openclaw context-optimizer subscribe" to upgrade.');
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
  .description('Subscribe to Pro tier (unlimited compressions)')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('Error: --wallet is required');
        process.exit(1);
      }

      const optimizer = getContextOptimizer();
      const paymentRequest = await optimizer.createPaymentRequest(options.wallet);

      console.log('\nSubscribe to Context Optimizer Pro\n');
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
      console.log(`     curl -X POST http://localhost:9092/api/x402/verify \\`);
      console.log(`       -H "Content-Type: application/json" \\`);
      console.log(`       -d '{`);
      console.log(`         "request_id": "${paymentRequest.request_id}",`);
      console.log(`         "tx_hash": "YOUR_TX_HASH",`);
      console.log(`         "agent_wallet": "${options.wallet}"`);
      console.log(`       }'\n`);

      console.log('  Or use the dashboard at: http://localhost:9092\n');

    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse();
