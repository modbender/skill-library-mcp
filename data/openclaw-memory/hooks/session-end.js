/**
 * OpenClaw Hook: session-end
 *
 * Performs cleanup and logging when a session ends.
 * Prunes expired memories and logs session summary.
 */

import { getMemoryManager } from '../src/index.js';

export default async function sessionEnd(context) {
  try {
    const { sessionId, agentWallet } = context;

    // Skip if no agent wallet (anonymous sessions)
    if (!agentWallet) {
      return;
    }

    const manager = getMemoryManager();

    // Prune expired memories
    const pruneResult = await manager.pruner.pruneExpired();
    if (pruneResult.pruned > 0) {
      console.log(`[Memory System] Pruned ${pruneResult.pruned} expired memories`);
    }

    // Get current quota status
    const quota = await manager.storage.getQuota(agentWallet);

    // Check license status
    const license = manager.x402.hasValidLicense(agentWallet);

    // Log session summary
    console.log(`\n========================================`);
    console.log(`[Memory System] Session ${sessionId} ended`);
    console.log(`========================================`);
    console.log(`  Agent: ${agentWallet.substring(0, 10)}...`);
    console.log(`  Memories: ${quota.memory_count} / ${quota.memory_limit === -1 ? '∞' : quota.memory_limit}`);
    console.log(`  Tier: ${quota.tier.toUpperCase()}`);

    if (license.valid) {
      console.log(`  License: Active (expires in ${license.days_remaining} days)`);
    } else if (license.expired) {
      console.log(`  License: EXPIRED - Upgrade to continue with unlimited memory`);
    } else {
      console.log(`  License: Free tier - Last 100 memories, 7-day retention`);
    }

    // Check if approaching quota limit (free tier)
    if (quota.tier === 'free' && quota.memory_limit > 0) {
      const usagePercent = (quota.memory_count / quota.memory_limit) * 100;
      if (usagePercent >= 90) {
        console.log(`\n  ⚠️  WARNING: ${usagePercent.toFixed(0)}% of memory quota used!`);
        console.log(`  Consider upgrading to Pro for unlimited memory storage.`);
        console.log(`  Run: openclaw memory subscribe`);
      } else if (usagePercent >= 75) {
        console.log(`\n  ℹ️  INFO: ${usagePercent.toFixed(0)}% of memory quota used.`);
      }
    }

    console.log(`========================================\n`);

    // Optional: Deduplicate memories (if configured)
    if (process.env.MEMORY_DEDUPLICATE === 'true') {
      await manager.pruner.deduplicateMemories(agentWallet);
    }
  } catch (error) {
    console.error('[Memory System] Error in session-end hook:', error.message);
  }
}
