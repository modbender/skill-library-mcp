/**
 * YIELD Strategy Engine
 *
 * Selects the optimal conversational investment strategy based on
 * the current portfolio state. Each strategy comes with a plain-English
 * directive that can be injected into any bot's system prompt.
 *
 * Strategies modeled after portfolio management:
 *   ACCUMULATE     — Build trust. Don't sell. Listen more.
 *   COMPOUND       — Stack micro-commitments. Ask small yeses.
 *   LEVERAGE       — Make bold recommendations with proof.
 *   HARVEST        — Present the offer. This is the window.
 *   HEDGE          — Acknowledge, validate, rebuild trust.
 *   REBALANCE      — Diversify. Build neglected assets.
 *   EXIT_GRACEFULLY — Preserve relationship. Offer value. Leave.
 */

// ─── Strategy Definitions ────────────────────────────────────────────────────

const STRATEGIES = {
  ACCUMULATE: {
    name: 'ACCUMULATE',
    description: 'Build foundational trust. The conversation is young — invest in understanding.',
    directive: 'Focus on LISTENING and UNDERSTANDING. Ask clarifying questions. Reflect back what the user said. Do NOT pitch, recommend, or push any action. Your only job right now is to make them feel genuinely heard. Short, warm responses. Match their energy.',
    priority: 1,
    conditions: (assets, meta) =>
      assets.trust < 0.3 && meta.messageCount < 8,
  },

  COMPOUND: {
    name: 'COMPOUND',
    description: 'Trust is building. Stack micro-commitments to compound it.',
    directive: 'The user trusts you enough to engage. Now stack small agreements. Ask questions where the natural answer is "yes." Summarize shared understanding ("So you need X because of Y, right?"). Each micro-yes compounds into bigger commitment. Keep it conversational, not interrogative.',
    priority: 2,
    conditions: (assets) =>
      assets.trust > 0.35 && assets.trust < 0.65 &&
      assets.commitment < 0.5,
  },

  LEVERAGE: {
    name: 'LEVERAGE',
    description: 'Strong trust + authority. Time to make bold moves with evidence.',
    directive: 'You have earned credibility. Now USE it. Make specific, confident recommendations backed by evidence. Use phrases like "Based on what you told me..." and "In my experience..." Be direct — hedging now would waste the authority you built. Include proof points, numbers, or examples.',
    priority: 3,
    conditions: (assets) =>
      assets.trust > 0.55 && assets.authority > 0.45 &&
      assets.commitment > 0.3,
  },

  HARVEST: {
    name: 'HARVEST',
    description: 'Portfolio is aligned. This is the optimal conversion window.',
    directive: 'THIS IS THE MOMENT. Trust is high, commitment is stacked, and the user is ready. Present your offer/CTA/recommendation clearly and confidently. Be specific about next steps. Make it EASY to say yes — reduce friction to zero. One clear action, not multiple choices. If there is a price, state it without apologizing.',
    priority: 5, // Highest priority when conditions met
    conditions: (assets, meta) =>
      meta.conversionWindow && meta.conversionWindow.open,
  },

  HEDGE: {
    name: 'HEDGE',
    description: 'Trust is dipping. Objections detected. Protect the relationship.',
    directive: 'STOP SELLING. The user has concerns — honor them. Acknowledge the objection explicitly ("I hear you, that is a valid concern"). Do NOT immediately counter-argue. Ask what would need to be true for them to feel comfortable. Rebuild trust by showing you prioritize their needs over your goal. Empathy first, logic second.',
    priority: 4,
    conditions: (assets, meta) =>
      meta.inversion && meta.inversion.inverted && meta.inversion.severity < 0.7,
  },

  REBALANCE: {
    name: 'REBALANCE',
    description: 'Portfolio is lopsided. One asset dominates while others starve.',
    directive: 'The conversation is unbalanced. Check which dimension is weak and invest there: If trust is low → listen more, validate. If curiosity is low → ask a thought-provoking question or share a surprising fact. If authority is low → provide evidence or a specific example. If urgency is low → create gentle time-awareness. If commitment is low → ask for a small opinion or preference.',
    priority: 2,
    conditions: (assets) => {
      const values = Object.values(assets);
      const max = Math.max(...values);
      const min = Math.min(...values);
      return max > 0.7 && min < 0.2;
    },
  },

  EXIT_GRACEFULLY: {
    name: 'EXIT_GRACEFULLY',
    description: 'Conversation is failing. Preserve the relationship for future value.',
    directive: 'This conversation is not converting and forcing it will damage the relationship. Gracefully summarize what you discussed, provide genuine value (a resource, insight, or takeaway), and leave the door open. Say something like "Whenever you are ready, I am here." Do NOT make one last pitch. The relationship has future compounding value — protect it.',
    priority: 5,
    conditions: (assets, meta) =>
      (meta.inversion && meta.inversion.inverted && meta.inversion.severity >= 0.7) ||
      (assets.trust < 0.12 && meta.messageCount > 5),
  },
};

// ─── Strategy Selection ──────────────────────────────────────────────────────

/**
 * Select the optimal strategy based on current portfolio state.
 *
 * @param {Object} portfolioState - Output from portfolio.getState()
 * @returns {{ strategy: string, directive: string, description: string, confidence: number }}
 */
export function selectStrategy(portfolioState) {
  const { assets, messageCount, inversion, conversionWindow } = portfolioState;

  const meta = { messageCount, inversion, conversionWindow };

  // Evaluate all strategies and find matching ones
  const candidates = [];

  for (const [name, strategy] of Object.entries(STRATEGIES)) {
    try {
      if (strategy.conditions(assets, meta)) {
        candidates.push({
          name,
          ...strategy,
        });
      }
    } catch {
      // Condition evaluation failed — skip this strategy
      continue;
    }
  }

  // No matches — default to ACCUMULATE (safest)
  if (candidates.length === 0) {
    const fallback = STRATEGIES.ACCUMULATE;
    return {
      strategy: fallback.name,
      directive: fallback.directive,
      description: fallback.description,
      confidence: 0.5,
      fallback: true,
    };
  }

  // Sort by priority (highest first) and return the winner
  candidates.sort((a, b) => b.priority - a.priority);
  const winner = candidates[0];

  return {
    strategy: winner.name,
    directive: winner.directive,
    description: winner.description,
    confidence: Math.min(0.6 + (candidates.length * 0.1), 0.95),
    alternates: candidates.slice(1).map(c => c.name),
  };
}

/**
 * Generate a contextual directive with specific instructions
 * based on the current portfolio imbalance.
 *
 * @param {Object} portfolioState
 * @returns {string} Enhanced directive with asset-specific guidance
 */
export function generateContextualDirective(portfolioState) {
  const { strategy, directive } = selectStrategy(portfolioState);
  const { assets } = portfolioState;

  // Find the weakest and strongest assets
  const sorted = Object.entries(assets).sort((a, b) => a[1] - b[1]);
  const weakest = sorted[0];
  const strongest = sorted[sorted.length - 1];

  const context = [];
  context.push(`[YIELD: ${strategy}]`);
  context.push(directive);

  if (strategy === 'REBALANCE') {
    context.push(`\nWeakest asset: ${weakest[0]} (${(weakest[1] * 100).toFixed(0)}%). Invest here.`);
    context.push(`Strongest asset: ${strongest[0]} (${(strongest[1] * 100).toFixed(0)}%). Leverage this.`);
  }

  if (strategy === 'HEDGE') {
    const inv = portfolioState.inversion;
    if (inv && inv.turnsUntilAbandon) {
      context.push(`\nWARNING: Estimated ${inv.turnsUntilAbandon} messages until user disengages.`);
    }
  }

  return context.join('\n');
}

/**
 * Get all available strategy names.
 */
export function getStrategyNames() {
  return Object.keys(STRATEGIES);
}

export { STRATEGIES };
