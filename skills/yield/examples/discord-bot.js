/**
 * YIELD × Discord Bot Integration Example
 *
 * Minimal example showing how to add YIELD intelligence
 * to a Discord.js bot. Works with any Discord bot framework.
 *
 * This example uses discord.js v14+ syntax.
 */

import { YieldEngine } from '../src/index.js';

// ─── Setup ───────────────────────────────────────────────────────────────────

const yield_engine = new YieldEngine();

/**
 * Discord message handler with YIELD intelligence.
 *
 * Add this to your existing bot's message event handler.
 * YIELD runs locally — no extra API calls, no latency.
 *
 * @example
 * // In your Discord bot:
 * client.on('messageCreate', (message) => {
 *   if (message.author.bot) return;
 *   const yieldData = processWithYield(message);
 *   // Use yieldData.directive to shape your bot's response
 * });
 */
function processWithYield(message) {
  // Use channel + user as conversation ID for per-user tracking
  const conversationId = `${message.channelId}-${message.author.id}`;

  const analysis = yield_engine.processMessage(
    message.content,
    conversationId
  );

  return analysis;
}

// ─── Example: Community Engagement Bot ───────────────────────────────────────

/**
 * A community bot that uses YIELD to:
 * 1. Detect when a new member is warming up (ACCUMULATE → COMPOUND)
 * 2. Know when to suggest premium features (LEVERAGE → HARVEST)
 * 3. Catch frustration before it leads to server leave (HEDGE)
 * 4. Gracefully disengage from hostile users (EXIT_GRACEFULLY)
 */

function handleCommunityMessage(message) {
  const analysis = processWithYield(message);

  // Strategy-based response routing
  switch (analysis.strategy) {
    case 'ACCUMULATE':
      // New or uncertain member — be warm, ask questions
      return {
        action: 'welcome',
        tone: 'warm_curious',
        suggestion: 'Ask about their interests or what brought them here',
      };

    case 'COMPOUND':
      // Member is engaging — stack micro-commitments
      return {
        action: 'engage',
        tone: 'enthusiastic',
        suggestion: 'Invite them to participate in a poll or share their opinion',
      };

    case 'LEVERAGE':
      // Trusted member — introduce advanced features
      return {
        action: 'recommend',
        tone: 'confident',
        suggestion: 'Mention premium channels or exclusive content',
      };

    case 'HARVEST':
      // Peak engagement — this is when to convert
      return {
        action: 'convert',
        tone: 'direct',
        suggestion: 'Present the upgrade/subscription offer NOW',
      };

    case 'HEDGE':
      // Member is frustrated — de-escalate
      return {
        action: 'support',
        tone: 'empathetic',
        suggestion: 'Acknowledge frustration, offer direct help or human support',
      };

    case 'EXIT_GRACEFULLY':
      // Lost cause for now — preserve the relationship
      return {
        action: 'disengage',
        tone: 'respectful',
        suggestion: 'Offer a helpful resource and let them know you are here when needed',
      };

    default:
      return {
        action: 'observe',
        tone: 'neutral',
        suggestion: 'Continue normal conversation',
      };
  }
}

// ─── Example: Tracking Server-Wide Yield ─────────────────────────────────────

/**
 * Get aggregate yield stats across all conversations in your server.
 * Useful for server analytics and engagement dashboards.
 */
function getServerYieldReport() {
  const stats = yield_engine.getStats();
  return `
**Server Yield Report**
Active Conversations: ${stats.totalConversations}
Total Messages Tracked: ${stats.totalMessages}
Avg Yield Score: ${(stats.avgYield * 100).toFixed(1)}%
Open Conversion Windows: ${stats.conversionsOpen}
Active Yield Inversions: ${stats.inversionsActive}
`;
}

export { processWithYield, handleCommunityMessage, getServerYieldReport };
