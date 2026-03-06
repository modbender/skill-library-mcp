/**
 * Engagement Classifier
 *
 * Auto-classifies every request as hot/warm/cold based on signals.
 * Determines optimal model when user doesn't specify one.
 *
 * Signals:
 * - X-Priority header (explicit override)
 * - Message count (multi-turn = hotter)
 * - Request frequency (rapid = active conversation)
 * - System prompt complexity (long = complex task)
 * - Time of day (overnight = cold)
 * - Prompt length (short/simple = cold)
 */

export type EngagementLevel = 'hot' | 'warm' | 'cold';

export interface EngagementClassification {
  level: EngagementLevel;
  score: number;           // 0-100, higher = hotter
  signals: string[];       // Human-readable reasons
  autoModel: string;       // Recommended model if user didn't specify
  estimatedSavings: number; // % savings vs always using premium
}

// Model tiers — cheapest good option for each level
// All available through OpenRouter
const MODEL_TIERS = {
  hot: 'deepseek/deepseek-chat-v3-0324',        // Already excellent + cheap
  warm: 'deepseek/deepseek-chat-v3-0324',        // Same — it's that good
  cold: 'deepseek/deepseek-chat-v3-0324',         // Same for now; could use mistral-small later
};

// Premium model equivalent costs ($/1M tokens input) for savings calculation
const PREMIUM_COST_PER_M = 3.00;  // Claude Sonnet ~$3/M input tokens
const DEEPSEEK_COST_PER_M = 0.27; // DeepSeek V3 ~$0.27/M input tokens

// Track recent request timestamps per key for frequency analysis
const recentRequests = new Map<string, number[]>();
const MAX_HISTORY = 20;

export function classifyEngagement(params: {
  keyId?: string;
  messages: Array<{ role: string; content: string }>;
  priorityHeader?: string;
  userSpecifiedModel?: string;
}): EngagementClassification {
  const { keyId, messages, priorityHeader, userSpecifiedModel } = params;
  const signals: string[] = [];
  let score = 50; // Start neutral

  // --- Signal 1: Explicit priority header (strongest signal) ---
  if (priorityHeader) {
    const p = priorityHeader.toLowerCase();
    if (p === 'high' || p === 'hot') {
      score += 40;
      signals.push('explicit priority: high');
    } else if (p === 'low' || p === 'cold') {
      score -= 40;
      signals.push('explicit priority: low');
    } else if (p === 'medium' || p === 'warm') {
      signals.push('explicit priority: medium');
    }
  }

  // --- Signal 2: Message count (multi-turn = engaged conversation) ---
  const messageCount = messages.length;
  if (messageCount >= 6) {
    score += 15;
    signals.push(`multi-turn conversation (${messageCount} messages)`);
  } else if (messageCount >= 3) {
    score += 5;
    signals.push(`moderate conversation (${messageCount} messages)`);
  } else if (messageCount === 1) {
    score -= 10;
    signals.push('single message (likely background task)');
  }

  // --- Signal 3: Request frequency ---
  if (keyId) {
    const now = Date.now();
    let history = recentRequests.get(keyId) || [];
    history.push(now);
    if (history.length > MAX_HISTORY) history = history.slice(-MAX_HISTORY);
    recentRequests.set(keyId, history);

    if (history.length >= 2) {
      const lastGap = now - history[history.length - 2];
      if (lastGap < 10_000) {        // < 10 seconds
        score += 20;
        signals.push('rapid fire (<10s gap)');
      } else if (lastGap < 60_000) {  // < 1 minute
        score += 10;
        signals.push('active conversation (<1m gap)');
      } else if (lastGap > 300_000) { // > 5 minutes
        score -= 10;
        signals.push('infrequent (>5m gap)');
      }
    }
  }

  // --- Signal 4: System prompt complexity ---
  const systemMsg = messages.find(m => m.role === 'system');
  if (systemMsg) {
    const sysLen = systemMsg.content.length;
    if (sysLen > 2000) {
      score += 5;
      signals.push('complex system prompt');
    }
  }

  // --- Signal 5: User message complexity ---
  const lastUser = [...messages].reverse().find(m => m.role === 'user');
  if (lastUser) {
    const userLen = lastUser.content.length;
    if (userLen < 20) {
      score -= 10;
      signals.push('very short prompt');
    } else if (userLen > 500) {
      score += 5;
      signals.push('detailed prompt');
    }
  }

  // --- Signal 6: Time of day (UTC) ---
  const hour = new Date().getUTCHours();
  if (hour >= 2 && hour <= 6) {
    score -= 10;
    signals.push('off-peak hours (UTC 02-06)');
  }

  // Clamp score
  score = Math.max(0, Math.min(100, score));

  // Classify
  let level: EngagementLevel;
  if (score >= 65) {
    level = 'hot';
  } else if (score >= 35) {
    level = 'warm';
  } else {
    level = 'cold';
  }

  // Model selection: respect user choice, otherwise auto-select
  let autoModel: string;
  if (userSpecifiedModel && userSpecifiedModel !== 'auto') {
    autoModel = userSpecifiedModel;
  } else {
    autoModel = MODEL_TIERS[level];
  }

  // Estimate savings vs always using premium
  const savingsPercent = Math.round((1 - DEEPSEEK_COST_PER_M / PREMIUM_COST_PER_M) * 100);

  return {
    level,
    score,
    signals,
    autoModel,
    estimatedSavings: savingsPercent,
  };
}

/** Get engagement stats for a key. */
export function getEngagementProfile(keyId: string): {
  recentLevel: EngagementLevel;
  avgScore: number;
  requestsInLastHour: number;
} {
  const history = recentRequests.get(keyId) || [];
  const oneHourAgo = Date.now() - 3600_000;
  const recentCount = history.filter(t => t > oneHourAgo).length;

  // Estimate based on frequency
  let avgScore = 50;
  if (recentCount > 20) avgScore = 80;
  else if (recentCount > 5) avgScore = 60;
  else if (recentCount < 2) avgScore = 30;

  let recentLevel: EngagementLevel;
  if (avgScore >= 65) recentLevel = 'hot';
  else if (avgScore >= 35) recentLevel = 'warm';
  else recentLevel = 'cold';

  return { recentLevel, avgScore, requestsInLastHour: recentCount };
}
