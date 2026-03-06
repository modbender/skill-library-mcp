/**
 * YIELD × Telegram Bot Integration Example
 *
 * Shows how to wire YIELD into a grammY-based Telegram bot.
 * Works with any Telegram bot framework.
 *
 * Zero cost. No additional API calls. Pure local intelligence.
 */

import { YieldEngine } from '../src/index.js';

// ─── Setup ───────────────────────────────────────────────────────────────────

const yield_engine = new YieldEngine();

/**
 * grammY middleware that injects YIELD analysis into the context.
 *
 * @example
 * // In your grammY bot:
 * import { Bot } from 'grammy';
 * const bot = new Bot('YOUR_TOKEN');
 * bot.use(yieldMiddleware);
 *
 * bot.on('message:text', (ctx) => {
 *   const { strategy, directive, conversionWindow } = ctx.yield;
 *   // Use these to shape your response
 * });
 */
function yieldMiddleware(ctx, next) {
  if (ctx.message?.text) {
    const conversationId = `tg-${ctx.chat.id}-${ctx.from.id}`;
    ctx.yield = yield_engine.processMessage(ctx.message.text, conversationId);
  }
  return next();
}

// ─── Example: E-Commerce Bot ─────────────────────────────────────────────────

/**
 * Telegram e-commerce bot that uses YIELD to:
 * 1. Know when to show product recommendations (trust > 0.4)
 * 2. Time discount offers to peak urgency moments (HARVEST)
 * 3. Detect cart abandonment intent before it happens (inversion)
 * 4. Recover conversations heading toward exit (HEDGE)
 */

function handleEcommerceMessage(ctx) {
  const y = ctx.yield;
  if (!y) return;

  // Conversion window is OPEN — present the offer!
  if (y.conversionWindow) {
    return {
      action: 'show_checkout',
      message: 'Ready to grab it? Here is your cart with free shipping included.',
      urgency: y.portfolio.urgency > 0.5 ? 'add_countdown' : 'none',
    };
  }

  // Yield inversion — user about to abandon
  if (y.inversion) {
    return {
      action: 'save_conversation',
      message: 'No pressure at all! By the way, I can save your cart and send you a reminder whenever you want.',
      offer: y.turnsUntilAbandon <= 2 ? 'surprise_discount' : 'helpful_content',
    };
  }

  // Strategy-based responses
  const responses = {
    ACCUMULATE: {
      action: 'discover',
      message: 'What are you looking for today? I can help you find exactly the right fit.',
    },
    COMPOUND: {
      action: 'narrow_down',
      message: 'Based on what you like so far, I think these three would be perfect. Which style catches your eye?',
    },
    LEVERAGE: {
      action: 'recommend',
      message: 'I have seen hundreds of customers with similar preferences, and this one is consistently the favorite. Here is why...',
    },
    HEDGE: {
      action: 'address_concern',
      message: 'Totally valid concern. Here is what I can do — full refund within 30 days, no questions asked.',
    },
    REBALANCE: {
      action: 'engage',
      message: 'Quick question — is this for yourself or a gift? That will help me nail the recommendation.',
    },
    EXIT_GRACEFULLY: {
      action: 'bookmark',
      message: 'I will save these for you. Just say "my picks" anytime and they will be right here.',
    },
  };

  return responses[y.strategy] || responses.ACCUMULATE;
}

// ─── Example: Export Conversation for CRM ────────────────────────────────────

/**
 * Export a Telegram user's YIELD data for CRM integration.
 * Useful for handing off high-yield conversations to human sales.
 */
function exportForCRM(chatId, userId) {
  const conversationId = `tg-${chatId}-${userId}`;
  const data = yield_engine.exportConversation(conversationId);

  if (!data) return null;

  return {
    source: 'telegram',
    conversationId,
    yieldScore: data.portfolio.assets
      ? new (yield_engine.constructor)()
          .processMessage('', conversationId).totalYield
      : 0,
    portfolio: data.portfolio,
    messageCount: data.portfolio.messageCount,
    exportedAt: new Date().toISOString(),
  };
}

export { yieldMiddleware, handleEcommerceMessage, exportForCRM };
