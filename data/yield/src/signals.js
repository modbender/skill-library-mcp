/**
 * YIELD Signal Detection System
 *
 * Detects psychological signals in user messages using zero-cost
 * pattern matching. No NLP APIs. No ML models. Pure lexical intelligence.
 *
 * Each signal maps to one or more asset classes it affects.
 */

// ─── Signal Pattern Definitions ──────────────────────────────────────────────

const SIGNAL_PATTERNS = {
  // ── Agreement Signals → +trust, +commitment ──
  AGREEMENT: {
    patterns: [
      /\b(yes|yeah|yep|yup|sure|absolutely|definitely|exactly|right|correct|agreed|true|indeed|totally|of course|makes sense|good point|fair enough)\b/i,
      /\b(i agree|that works|sounds good|sounds great|perfect|love it|let'?s do it|i'?m in|count me in|deal)\b/i,
      /\b(you'?re right|that'?s right|bingo|nailed it|spot on|100%|💯)\b/i,
    ],
    assets: { trust: 0.06, commitment: 0.10 },
    type: 'positive',
  },

  // ── Disagreement Signals → -trust, -commitment ──
  DISAGREEMENT: {
    patterns: [
      /\b(no|nah|nope|disagree|wrong|incorrect|not really|i don'?t think so)\b/i,
      /\b(that'?s not|you'?re wrong|actually no|hard pass|no way|not interested)\b/i,
      /\b(i disagree|don'?t agree|can'?t agree|won'?t work|bad idea)\b/i,
    ],
    assets: { trust: -0.08, commitment: -0.12 },
    type: 'negative',
  },

  // ── Question Signals → +curiosity, +engagement ──
  QUESTION: {
    patterns: [
      /\?$/,
      /\b(how|what|why|when|where|which|who|can you|could you|would you|tell me|explain|clarify)\b/i,
      /\b(what if|how about|what about|is it possible|can i|wondering)\b/i,
    ],
    assets: { curiosity: 0.10, trust: 0.02 },
    type: 'positive',
  },

  // ── Objection Signals → -trust, +urgency (they care enough to push back) ──
  OBJECTION: {
    patterns: [
      /\b(but|however|although|too expensive|too much|can'?t afford|not worth)\b/i,
      /\b(i'?m worried|concerned|skeptical|not sure about|hesitant|risky)\b/i,
      /\b(what about|what if .+ goes wrong|downside|catch|hidden)\b/i,
      /\b(competitor|alternative|other option|cheaper|better deal)\b/i,
    ],
    assets: { trust: -0.05, urgency: 0.08, curiosity: 0.03 },
    type: 'mixed',
  },

  // ── Personal Disclosure Signals → +trust, +commitment ──
  PERSONAL: {
    patterns: [
      /\b(i feel|i think|i believe|i need|i want|i wish|i hope|my experience)\b/i,
      /\b(personally|for me|in my case|my situation|my team|my company|my budget)\b/i,
      /\b(i'?ve been|i used to|i tried|i struggled|i failed|i learned)\b/i,
    ],
    assets: { trust: 0.08, commitment: 0.06 },
    type: 'positive',
  },

  // ── Hesitation Signals → -momentum, +friction ──
  HESITATION: {
    patterns: [
      /\b(maybe|perhaps|possibly|i guess|i suppose|not sure|idk|hmm+|umm+)\b/i,
      /\b(let me think|need to think|sleep on it|get back to you|later|sometime)\b/i,
      /\b(i don'?t know|might|kinda|sort of|it depends|we'?ll see)\b/i,
      /^\.{2,}$/,  // just "..." or ".."
    ],
    assets: { commitment: -0.06, urgency: -0.04, curiosity: -0.03 },
    type: 'negative',
  },

  // ── Enthusiasm Signals → +momentum, +curiosity, +commitment ──
  ENTHUSIASM: {
    patterns: [
      /\b(amazing|awesome|incredible|fantastic|brilliant|excellent|wow|omg|love)\b/i,
      /\b(this is great|so cool|mind blown|game changer|exactly what i need)\b/i,
      /!{2,}/,  // multiple exclamation marks
      /\b(can'?t wait|excited|pumped|stoked|thrilled|let'?s go)\b/i,
    ],
    assets: { commitment: 0.10, curiosity: 0.08, trust: 0.04 },
    type: 'positive',
  },

  // ── Time Pressure Signals → +urgency (decaying asset) ──
  TIME_PRESSURE: {
    patterns: [
      /\b(asap|urgent|quickly|hurry|deadline|by (monday|tuesday|wednesday|thursday|friday|tomorrow|tonight|end of))\b/i,
      /\b(running out of time|time sensitive|need it now|right away|immediately)\b/i,
      /\b(before|by the time|countdown|last chance|closing|expir)\b/i,
    ],
    assets: { urgency: 0.15, commitment: 0.05 },
    type: 'positive',
  },

  // ── Social Proof Seeking → +curiosity, -authority (they need validation) ──
  SOCIAL_PROOF: {
    patterns: [
      /\b(who else|anyone else|other (companies|people|teams|users)|reviews|testimonials)\b/i,
      /\b(case study|success story|example|proof|evidence|results|numbers)\b/i,
      /\b(do others|have you seen|popular|trending|recommended by)\b/i,
    ],
    assets: { curiosity: 0.08, authority: -0.06 },
    type: 'mixed',
  },

  // ── Buying / Action Signals → +commitment, +urgency ──
  BUYING: {
    patterns: [
      /\b(how (much|do i|to (buy|get|start|sign up|subscribe|order|pay)))\b/i,
      /\b(pricing|price|cost|fee|plan|package|discount|coupon|trial|demo)\b/i,
      /\b(where (do i|can i|to) (buy|get|sign|register|download|install))\b/i,
      /\b(ready to|want to (start|buy|try|get)|take my money|shut up and)\b/i,
    ],
    assets: { commitment: 0.15, urgency: 0.12, trust: 0.04 },
    type: 'positive',
  },

  // ── Frustration Signals → -trust, -commitment, +urgency ──
  FRUSTRATION: {
    patterns: [
      /\b(frustrat|annoy|irritat|disappoint|waste of time|useless|terrible|awful)\b/i,
      /\b(this (sucks|is broken|doesn'?t work|is wrong)|give up|done with this)\b/i,
      /\b(still (not|doesn'?t|won'?t|can'?t)|again\?|seriously\??|come on)\b/i,
    ],
    assets: { trust: -0.12, commitment: -0.10, urgency: 0.06 },
    type: 'negative',
  },

  // ── Gratitude Signals → +trust, +authority ──
  GRATITUDE: {
    patterns: [
      /\b(thank|thanks|thx|ty|appreciate|grateful|helpful|you saved me)\b/i,
      /\b(great (help|job|work)|well done|nice one|bravo|kudos)\b/i,
    ],
    assets: { trust: 0.10, authority: 0.08, commitment: 0.04 },
    type: 'positive',
  },

  // ── Comparison Signals → +curiosity, -commitment (still shopping) ──
  COMPARISON: {
    patterns: [
      /\b(vs\.?|versus|compared to|difference between|better than|worse than)\b/i,
      /\b(alternative|competitor|other tool|other service|switch from)\b/i,
      /\b(pros and cons|tradeoff|trade-off|which is better|should i use)\b/i,
    ],
    assets: { curiosity: 0.10, commitment: -0.08, authority: -0.04 },
    type: 'mixed',
  },
};

// ─── Message Meta-Signals (structural, not lexical) ──────────────────────────

/**
 * Detects structural signals from message metadata:
 * - Message length compression (getting shorter = losing interest)
 * - Response contains only emoji or very short responses
 * - ALL CAPS (intensity)
 */
function detectMetaSignals(message, history) {
  const signals = [];

  // Short response detection (< 10 chars that aren't agreement)
  if (message.length < 10 && !SIGNAL_PATTERNS.AGREEMENT.patterns.some(p => p.test(message))) {
    signals.push({
      type: 'LENGTH_COMPRESSION',
      assets: { commitment: -0.04, curiosity: -0.03 },
      confidence: 0.6,
    });
  }

  // ALL CAPS detection (intensity signal)
  if (message.length > 5 && message === message.toUpperCase() && /[A-Z]/.test(message)) {
    signals.push({
      type: 'INTENSITY',
      assets: { urgency: 0.08, commitment: 0.04 },
      confidence: 0.7,
    });
  }

  // Message length trend (comparing to recent history)
  if (history && history.length >= 3) {
    const recentLengths = history.slice(-3).map(m => m.length);
    const avgRecent = recentLengths.reduce((a, b) => a + b, 0) / recentLengths.length;
    const currentRatio = message.length / Math.max(avgRecent, 1);

    if (currentRatio < 0.4) {
      // Message significantly shorter than recent average
      signals.push({
        type: 'ENGAGEMENT_DECAY',
        assets: { commitment: -0.06, curiosity: -0.05, trust: -0.03 },
        confidence: 0.65,
      });
    } else if (currentRatio > 2.0) {
      // Message significantly longer than recent average
      signals.push({
        type: 'ENGAGEMENT_SURGE',
        assets: { commitment: 0.06, curiosity: 0.05, trust: 0.03 },
        confidence: 0.65,
      });
    }
  }

  return signals;
}

// ─── Main Detection Function ─────────────────────────────────────────────────

/**
 * Detects all signals in a user message.
 *
 * @param {string} message - The user's message text
 * @param {string[]} [history=[]] - Recent message history for meta-signal detection
 * @returns {Array<{type: string, assets: Object, confidence: number}>}
 */
export function detectSignals(message, history = []) {
  if (!message || typeof message !== 'string') {
    return [];
  }

  const trimmed = message.trim();
  if (trimmed.length === 0) return [];

  const detected = [];

  // Pattern-based signal detection
  for (const [signalType, config] of Object.entries(SIGNAL_PATTERNS)) {
    for (const pattern of config.patterns) {
      if (pattern.test(trimmed)) {
        detected.push({
          type: signalType,
          assets: { ...config.assets },
          confidence: 0.8,
          category: config.type,
        });
        break; // One match per signal type is enough
      }
    }
  }

  // Meta-signal detection
  const metaSignals = detectMetaSignals(trimmed, history);
  detected.push(...metaSignals);

  return detected;
}

/**
 * Returns all available signal type names.
 * Useful for debugging and configuration.
 */
export function getSignalTypes() {
  return Object.keys(SIGNAL_PATTERNS);
}

export { SIGNAL_PATTERNS };
