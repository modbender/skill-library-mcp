#!/usr/bin/env node
/**
 * OpenClaw Memory System - CLI Interface
 *
 * Commands:
 * - add: Store a memory manually
 * - search: Semantic search for memories
 * - list: List recent memories
 * - delete: Delete a memory
 * - stats: Show memory statistics
 * - license: Check license status
 * - subscribe: Subscribe to Pro tier
 */

import { Command } from 'commander';
import { getMemoryManager } from './index.js';

const program = new Command();

program
  .name('openclaw-memory')
  .description('Persistent memory system for OpenClaw agents')
  .version('1.0.0');

// Add memory command
program
  .command('add <content>')
  .description('Store a new memory')
  .option('--type <type>', 'Memory type (fact, conversation, preference, pattern)', 'fact')
  .option('--importance <score>', 'Importance score (0.0-1.0)', '0.5')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .option('--session <id>', 'Session ID (optional)')
  .action(async (content, options) => {
    try {
      if (!options.wallet) {
        console.error('❌ Error: --wallet is required');
        process.exit(1);
      }

      const manager = getMemoryManager();
      const importance = parseFloat(options.importance);

      if (isNaN(importance) || importance < 0 || importance > 1) {
        console.error('❌ Error: --importance must be between 0.0 and 1.0');
        process.exit(1);
      }

      const memory = await manager.storeMemory(
        options.wallet,
        content,
        options.type,
        importance,
        options.session
      );

      console.log(`✅ Memory stored successfully!`);
      console.log(`   ID: ${memory.memory_id}`);
      console.log(`   Type: ${memory.memory_type}`);
      console.log(`   Importance: ${memory.importance_score}`);
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    }
  });

// Search memories command
program
  .command('search <query>')
  .description('Search memories using semantic similarity')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .option('--limit <n>', 'Number of results', '5')
  .option('--min-score <score>', 'Minimum similarity score (0.0-1.0)', '0.7')
  .action(async (query, options) => {
    try {
      if (!options.wallet) {
        console.error('❌ Error: --wallet is required');
        process.exit(1);
      }

      const manager = getMemoryManager();
      const limit = parseInt(options.limit);
      const minScore = parseFloat(options.minScore);

      const memories = await manager.retrieveMemories(options.wallet, query, {
        limit,
        min_score: minScore
      });

      if (!memories || memories.length === 0) {
        console.log(`\n🔍 No memories found matching "${query}"\n`);
        return;
      }

      console.log(`\n📚 Found ${memories.length} relevant memories:\n`);
      for (const memory of memories) {
        console.log(`  [${'━'.repeat(60)}]`);
        console.log(`  [${memory.memory_type.toUpperCase()}] ${memory.content}`);
        console.log(`  ├─ Importance: ${memory.importance_score.toFixed(2)}`);
        console.log(`  ├─ Similarity: ${(memory.similarity_score || 0).toFixed(2)}`);
        console.log(`  ├─ Timestamp: ${new Date(memory.timestamp).toLocaleString()}`);
        console.log(`  └─ ID: ${memory.memory_id}`);
        console.log();
      }
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    }
  });

// List memories command
program
  .command('list')
  .description('List recent memories')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .option('--limit <n>', 'Number of memories to show', '10')
  .option('--type <type>', 'Filter by memory type (fact, conversation, preference, pattern)')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('❌ Error: --wallet is required');
        process.exit(1);
      }

      const manager = getMemoryManager();
      const limit = parseInt(options.limit);

      let memories;
      if (options.type) {
        memories = await manager.retriever.getByType(options.wallet, options.type);
        memories = memories.slice(0, limit);
      } else {
        memories = await manager.retriever.getRecent(options.wallet, limit);
      }

      if (!memories || memories.length === 0) {
        console.log(`\n📭 No memories found\n`);
        return;
      }

      console.log(`\n📋 Recent memories (${memories.length}):\n`);
      for (const memory of memories) {
        console.log(`  [${'━'.repeat(60)}]`);
        console.log(`  [${memory.memory_type.toUpperCase()}] ${memory.content}`);
        console.log(`  ├─ Importance: ${memory.importance_score.toFixed(2)}`);
        console.log(`  ├─ Access count: ${memory.accessed_count}`);
        console.log(`  ├─ Timestamp: ${new Date(memory.timestamp).toLocaleString()}`);
        console.log(`  └─ ID: ${memory.memory_id}`);
        console.log();
      }
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    }
  });

// Delete memory command
program
  .command('delete <memory_id>')
  .description('Delete a specific memory')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .action(async (memoryId, options) => {
    try {
      if (!options.wallet) {
        console.error('❌ Error: --wallet is required');
        process.exit(1);
      }

      const manager = getMemoryManager();
      await manager.deleteMemory(options.wallet, memoryId);

      console.log(`✅ Memory ${memoryId} deleted successfully`);
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    }
  });

// Stats command
program
  .command('stats')
  .description('Show memory statistics')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('❌ Error: --wallet is required');
        process.exit(1);
      }

      const manager = getMemoryManager();
      const stats = await manager.getMemoryStats(options.wallet);

      console.log('\n📊 Memory Statistics:\n');
      console.log(`  Agent: ${options.wallet.substring(0, 10)}...`);
      console.log(`  Total Memories: ${stats.total_count}`);
      console.log(`  Tier: ${stats.tier.toUpperCase()}`);
      console.log(`  Quota: ${stats.memory_count} / ${stats.memory_limit === -1 ? '∞' : stats.memory_limit}`);

      if (stats.memory_limit > 0) {
        const usagePercent = (stats.memory_count / stats.memory_limit) * 100;
        console.log(`  Usage: ${usagePercent.toFixed(1)}%`);
      }

      console.log('\n  By Type:');
      for (const [type, count] of Object.entries(stats.by_type)) {
        console.log(`    ${type}: ${count}`);
      }

      if (stats.most_accessed && stats.most_accessed.length > 0) {
        console.log('\n  Most Accessed:');
        for (const memory of stats.most_accessed.slice(0, 3)) {
          console.log(`    [${memory.memory_type}] ${memory.content.substring(0, 50)}...`);
          console.log(`    └─ Accessed ${memory.accessed_count} times`);
        }
      }

      console.log();
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
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
        console.error('❌ Error: --wallet is required');
        process.exit(1);
      }

      const manager = getMemoryManager();
      const license = manager.checkLicense(options.wallet);

      console.log('\n📜 License Status:\n');
      console.log(`  Agent: ${options.wallet.substring(0, 10)}...`);
      console.log(`  Tier: ${license.tier.toUpperCase()}`);

      if (license.valid) {
        console.log(`  Status: ✅ ACTIVE`);
        console.log(`  Expires: ${new Date(license.expires).toLocaleDateString()}`);
        console.log(`  Days Remaining: ${license.days_remaining}`);
        console.log('\n  Features:');
        console.log('    ✓ Unlimited memory storage');
        console.log('    ✓ Permanent retention');
        console.log('    ✓ Advanced semantic search');
        console.log('    ✓ Memory relationship mapping');
      } else if (license.expired) {
        console.log(`  Status: ❌ EXPIRED`);
        console.log('\n  Your Pro license has expired.');
        console.log('  Run "openclaw memory subscribe" to renew.');
      } else {
        console.log(`  Status: 🆓 FREE TIER`);
        console.log('\n  Free Tier Limits:');
        console.log('    • Last 100 memories');
        console.log('    • 7-day retention');
        console.log('    • Basic semantic search');
        console.log('\n  Upgrade to Pro for:');
        console.log('    ✓ Unlimited memory storage');
        console.log('    ✓ Permanent retention');
        console.log('    ✓ Advanced semantic search');
        console.log('    ✓ Memory relationship mapping');
        console.log('\n  Price: 0.5 USDT/month');
        console.log('  Run "openclaw memory subscribe" to upgrade.');
      }

      console.log();
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    }
  });

// Subscribe command
program
  .command('subscribe')
  .description('Subscribe to Pro tier (unlimited memory)')
  .option('--wallet <wallet>', 'Agent wallet address (required)')
  .action(async (options) => {
    try {
      if (!options.wallet) {
        console.error('❌ Error: --wallet is required');
        process.exit(1);
      }

      const manager = getMemoryManager();
      const paymentRequest = await manager.createPaymentRequest(options.wallet);

      console.log('\n💎 Subscribe to Memory System Pro\n');
      console.log('════════════════════════════════════════════════════════════');
      console.log('  Price: 0.5 USDT/month');
      console.log('  Chain: Base');
      console.log('  Protocol: x402');
      console.log('════════════════════════════════════════════════════════════\n');

      console.log('Payment Request Details:\n');
      console.log(`  Request ID: ${paymentRequest.request_id}`);
      console.log(`  Recipient: ${paymentRequest.recipient}`);
      console.log(`  Amount: ${paymentRequest.amount} ${paymentRequest.token}`);
      console.log(`  Chain: ${paymentRequest.chain}`);
      console.log(`  Expires: ${new Date(paymentRequest.expires_at).toLocaleString()}\n`);

      console.log('Instructions:\n');
      console.log('  1. Send 0.5 USDT to the recipient address via x402 protocol');
      console.log('  2. After payment, verify with your transaction hash:\n');
      console.log(`     curl -X POST http://localhost:9091/api/x402/verify \\`);
      console.log(`       -H "Content-Type: application/json" \\`);
      console.log(`       -d '{`);
      console.log(`         "request_id": "${paymentRequest.request_id}",`);
      console.log(`         "tx_hash": "YOUR_TX_HASH",`);
      console.log(`         "agent_wallet": "${options.wallet}"`);
      console.log(`       }'\n`);

      console.log('  Or use the dashboard at: http://localhost:9091\n');
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse();
