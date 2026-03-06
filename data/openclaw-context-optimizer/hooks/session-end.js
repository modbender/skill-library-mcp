/**
 * OpenClaw Hook: session-end
 *
 * Reports compression statistics when a session ends.
 * Shows tokens saved and compression effectiveness.
 */

import { getContextOptimizer } from '../src/index.js';

export default async function sessionEnd(context) {
  try {
    const { sessionId, agentWallet } = context;

    // Skip if no agent wallet (anonymous sessions)
    if (!agentWallet) {
      return;
    }

    const optimizer = getContextOptimizer();

    // Get session statistics
    const stats = await optimizer.stats.getStats(agentWallet);

    // Check license status
    const license = optimizer.x402.hasValidLicense(agentWallet);

    // Log session summary
    console.log(`\n========================================`);
    console.log(`[Context Optimizer] Session ${sessionId} ended`);
    console.log(`========================================`);
    console.log(`  Agent: ${agentWallet.substring(0, 10)}...`);
    console.log(`  Total Compressions: ${stats.total_compressions}`);
    console.log(`  Total Tokens Saved: ${stats.total_tokens_saved.toLocaleString()}`);
    console.log(`  Average Compression: ${(stats.avg_compression_ratio * 100).toFixed(1)}%`);
    console.log(`  Tier: ${stats.tier.toUpperCase()}`);

    if (license.valid) {
      console.log(`  License: Active (expires in ${license.days_remaining} days)`);
    } else if (license.expired) {
      console.log(`  License: EXPIRED - Upgrade to continue with advanced compression`);
    } else {
      console.log(`  License: Free tier - Basic compression (40% reduction)`);
    }

    // Show compression effectiveness
    if (stats.quality_maintained_rate !== undefined) {
      console.log(`  Quality Rate: ${(stats.quality_maintained_rate * 100).toFixed(1)}%`);
    }

    // Cost savings estimate (assuming $0.002 per 1K tokens)
    const costSaved = (stats.total_tokens_saved / 1000) * 0.002;
    if (costSaved > 0) {
      console.log(`  Estimated Cost Saved: $${costSaved.toFixed(4)}`);
    }

    // Check if approaching quota limit (free tier)
    if (stats.tier === 'free' && stats.compression_limit > 0) {
      const usagePercent = (stats.total_compressions / stats.compression_limit) * 100;
      if (usagePercent >= 90) {
        console.log(`\n  Warning: ${usagePercent.toFixed(0)}% of compression quota used!`);
        console.log(`  Consider upgrading to Pro for unlimited compressions.`);
        console.log(`  Run: openclaw context-optimizer subscribe`);
      } else if (usagePercent >= 75) {
        console.log(`\n  Info: ${usagePercent.toFixed(0)}% of compression quota used.`);
      }
    }

    console.log(`========================================\n`);

    // Show top learned patterns
    if (stats.learned_patterns && stats.learned_patterns.length > 0) {
      console.log(`  Top Learned Patterns:`);
      for (const pattern of stats.learned_patterns.slice(0, 3)) {
        console.log(`    - ${pattern.pattern_type}: ${pattern.effectiveness.toFixed(1)}% effective`);
      }
      console.log();
    }
  } catch (error) {
    console.error('[Context Optimizer] Error in session-end hook:', error.message);
  }
}
