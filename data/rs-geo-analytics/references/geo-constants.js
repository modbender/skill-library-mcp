'use strict';
/**
 * geo-constants.js
 * GEO Analysis constants derived from @architect's research (ROA-40).
 * Used by analyzeEngineStrength, analyzeContentGaps,
 * and computeReputationScore in rankscale-skill.js.
 */

// Engine visibility weights (sum ≈ 1.0)
// Source: Engine Intelligence Matrix from research doc
const ENGINE_WEIGHTS = {
  chatgpt:      0.27,  // Largest user base, most impactful
  perplexity:   0.18,  // Citation-heavy, great for authority
  gemini:       0.17,  // Google ecosystem
  claude:       0.12,  // Tech-savvy, quality responses
  deepseek:     0.05,  // Strong in Asia/technical audiences
  ai_overview:  0.05,  // Embedded in Google Search, high-intent
  grok:         0.04,  // X/Twitter integration
  mistral:      0.03,  // EU-focused, niche
  ai_mode:      0.03,  // Newer Google integration
  bing_copilot: 0.02,  // Microsoft/Bing AI — significant enterprise reach
  meta_ai:      0.02,  // Meta ecosystem (Facebook, Instagram, WhatsApp)
  you_com:      0.02,  // Privacy-focused, research audience
};

// Default weight for unknown engines
const ENGINE_WEIGHT_DEFAULT = 0.02;

// GEO Pattern detection thresholds
const GEO_PATTERNS = {
  // Pattern 1: Content Gap
  // Flag terms visible on <40% of engines
  CONTENT_GAP_PRESENT_RATIO: 0.4,
  // Engine drops >20pts vs avg = engine-specific weakness flag
  CONTENT_GAP_ENGINE_DROP_PTS: 20,

  // Pattern 2: Authority Gap
  // citations.total / report.mentions < 0.3
  AUTHORITY_GAP_RATIO: 0.3,

  // Pattern 3: Negative Sentiment
  // negativeKeywords.length > positiveKeywords.length * 0.5
  SENTIMENT_RISK_RATIO: 0.5,

  // Pattern 4: Engine-Specific Weakness
  // engine avgScore < overall_avg * 0.4
  ENGINE_WEAKNESS_RATIO: 0.4,

  // Pattern 5: Topic/Query Imbalance
  // generic_avg < branded_avg * 0.3
  TOPIC_IMBALANCE_RATIO: 0.3,

  // Pattern 6: Mention-to-Visibility Drop
  MENTION_MIN: 10,
  VISIBILITY_DROP_MAX: 30,

  // Pattern 7: Trending Decline
  TREND_DECLINE_PCT: -15,
};

// Reputation score algorithm weights (must sum to 1.0)
// Source: §4 Reputation Summary Algorithm from research doc
const REPUTATION_SCORE_WEIGHTS = {
  BASE_RATIO: 0.60,        // Weight for (pos - 2*neg) / total ratio
  ENGINE_SCORE: 0.20,      // Weight for engine-weighted sentiment
  SEVERITY_PENALTY: 0.20,  // Penalty for high-frequency negative kw

  // Trend thresholds (score delta points)
  TREND_IMPROVING_DELTA: 5,
  TREND_DECLINING_DELTA: -5,

  // Top risk keyword count
  TOP_RISK_KEYWORDS: 5,

  // Score normalisation formula: (raw + 1) * 50, clamp 0-100
  NORM_OFFSET: 1,
  NORM_SCALE: 50,
};

// Human-readable display names for engine IDs
// Source: engine-reference.md (all 20+ engine IDs from RankScale API)
const ENGINE_DISPLAY_NAMES = {
  // GUI Engines
  'chatgpt_gui':                      'ChatGPT',
  'perplexity_gui':                   'Perplexity',
  'google_ai_overview':               'Google AI Overview',
  'google_ai_mode_gui':               'Google AI Mode',
  'xai_grok_gui':                     'Grok',
  'bing_copilot_gui':                 'Bing Copilot',

  // Perplexity API Engines
  'perplexity_sonar':                 'Perplexity Sonar',
  'perplexity_sonar_pro':             'Perplexity Sonar Pro',
  'perplexity_sonar_reasoning':       'Perplexity Sonar R',
  'perplexity_sonar_reasoning_pro':   'Perplexity Sonar R Pro',

  // OpenAI
  'openai_gpt-4o':                    'GPT-4o',
  'openai_gpt-5':                     'GPT-5',

  // Google Gemini
  'google_gemini_15':                 'Gemini 1.5',
  'google_gemini_20':                 'Gemini 2.0',
  'google_gemini_25':                 'Gemini 2.5',

  // Anthropic Claude
  'anthropic_claude_3_5_sonnet':      'Claude 3.5 Sonnet',
  'anthropic_claude_3_5_haiku':       'Claude 3.5 Haiku',
  'anthropic_claude_4_5_haiku':       'Claude Haiku',

  // DeepSeek
  'deepseek_chat':                    'DeepSeek V3',

  // Mistral
  'mistral_large':                    'Mistral Large',
};

/**
 * Get a human-readable display name for an engine ID.
 * Falls back to cleaning underscores/hyphens if no mapping found.
 * @param {string} engineId
 * @returns {string}
 */
function getEngineDisplayName(engineId) {
  if (!engineId) return 'Unknown';
  const id = String(engineId);
  return ENGINE_DISPLAY_NAMES[id]
    || ENGINE_DISPLAY_NAMES[id.toLowerCase()]
    || id.replace(/_/g, ' ').replace(/-/g, '-').replace(/\b\w/g, (c) => c.toUpperCase());
}

module.exports = {
  ENGINE_WEIGHTS,
  ENGINE_WEIGHT_DEFAULT,
  GEO_PATTERNS,
  REPUTATION_SCORE_WEIGHTS,
  ENGINE_DISPLAY_NAMES,
  getEngineDisplayName,
};
