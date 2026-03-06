/**
 * Taste Spectrum Dimensions
 *
 * 4 continuous spectrums (0-100) that capture HOW users operate:
 *   learning:  try-first (0) <-> study-first (100)
 *   decision:  gut (0) <-> deliberate (100)
 *   novelty:   early-adopter (0) <-> wait-and-see (100)
 *   risk:      bold (0) <-> cautious (100)
 */

export interface TasteSpectrums {
  learning: number;  // 0 = try-first, 100 = study-first
  decision: number;  // 0 = gut, 100 = deliberate
  novelty: number;   // 0 = early-adopter, 100 = wait-and-see
  risk: number;      // 0 = bold, 100 = cautious
}

export interface DetectedStrengths {
  strengths: string[];
  confidence: number; // 0-100
}

// ─── Keyword sets for spectrum detection ─────────────────────────────────

export const LEARNING_TRY_FIRST_KEYWORDS = [
  'try', 'build', 'ship', 'prototype', 'hack', 'just do it',
  'hands-on', 'learn by doing', 'trial', 'tinker', 'iterate',
  'mvp', 'quick start', 'jump in', 'figure it out',
];

export const LEARNING_STUDY_FIRST_KEYWORDS = [
  'research', 'study', 'understand', 'read', 'analyze',
  'theory', 'documentation', 'whitepaper', 'deep dive', 'literature',
  'systematic', 'methodology', 'framework', 'fundamentals', 'principles',
];

export const DECISION_GUT_KEYWORDS = [
  'gut', 'instinct', 'feel', 'vibe', 'hunch',
  'intuition', 'snap decision', 'trust my gut', 'just knew', 'sense',
];

export const DECISION_DELIBERATE_KEYWORDS = [
  'analyze', 'compare', 'pros and cons', 'evaluate', 'weigh',
  'spreadsheet', 'criteria', 'due diligence', 'data-driven', 'benchmark',
];

export const NOVELTY_EARLY_KEYWORDS = [
  'first', 'early', 'beta', 'alpha', 'bleeding edge',
  'day one', 'before anyone', 'pre-launch', 'pioneer', 'cutting edge',
];

export const NOVELTY_WAIT_KEYWORDS = [
  'wait', 'proven', 'stable', 'mature', 'established',
  'track record', 'safe', 'battle-tested', 'mainstream', 'after others',
];

export const RISK_BOLD_KEYWORDS = [
  'yolo', 'all in', 'bet big', 'bold', 'aggressive',
  'risk', 'moon', 'gamble', 'fearless', 'ambitious',
];

export const RISK_CAUTIOUS_KEYWORDS = [
  'careful', 'conservative', 'hedge', 'safe', 'diversify',
  'cautious', 'slow', 'measured', 'steady', 'prudent',
];

// ─── Episodic memory patterns ────────────────────────────────────────────
// Match narrative sentences that reveal HOW users operate.
// Each pattern carries weighted signals for one or more spectrums.
// Weight range: -1.0 (low end) to +1.0 (high end) per spectrum.

export interface EpisodePattern {
  pattern: RegExp;
  label: string; // Human-readable episode type
  signals: {
    learning?: number;
    decision?: number;
    novelty?: number;
    risk?: number;
  };
}

export const EPISODE_PATTERNS: EpisodePattern[] = [
  // ── Decision / Pivot episodes ──────────────────────────────────────────
  // "I switched from React to Vue" → tried something, pivoted = try-first learner + gut decision
  { pattern: /i (?:switched|moved|migrated|transitioned) from \w+/i, label: 'pivot', signals: { learning: -0.8, decision: -0.5 } },
  // "I tried X but ended up..." → experimentation = try-first + gut
  { pattern: /i tried .{3,40} but/i, label: 'pivot', signals: { learning: -0.7, decision: -0.3 } },
  // "I gave up on X and built Y instead" → pivot + builder = gut + bold
  { pattern: /i (?:gave up on|abandoned|dropped) .{3,30} (?:and|to|for)/i, label: 'pivot', signals: { learning: -0.6, decision: -0.4, risk: -0.3 } },
  // "I decided to..." → deliberate decision
  { pattern: /i decided to (?:focus|build|ship|launch|commit)/i, label: 'decision', signals: { decision: 0.7 } },
  // "I chose X over Y" → deliberate evaluation
  { pattern: /i chose .{3,30} over/i, label: 'decision', signals: { decision: 0.8, learning: 0.3 } },
  // "after comparing X and Y" → study-first + deliberate approach
  { pattern: /after (?:comparing|evaluating|researching|reading about)/i, label: 'decision', signals: { learning: 0.8, decision: 0.8 } },

  // ── Learning experience episodes ───────────────────────────────────────
  // "I read the docs before..." → study-first
  { pattern: /i (?:read|studied|researched) .{3,40} before/i, label: 'study', signals: { learning: 0.9 } },
  // "I just started building without..." → try-first
  { pattern: /i just (?:started|jumped in|dove in|began)/i, label: 'hands-on', signals: { learning: -0.8 } },
  // "I figured it out by..." → learning through doing
  { pattern: /i figured (?:it |things )?out (?:by|through|while)/i, label: 'hands-on', signals: { learning: -0.7 } },
  // "I spent time understanding..." → study-first
  { pattern: /i spent (?:time|weeks|days|hours) (?:understanding|learning|studying|reading)/i, label: 'study', signals: { learning: 0.9 } },

  // ── Novelty response episodes ──────────────────────────────────────────
  // "I was one of the first to try..." → early adopter
  { pattern: /i was (?:one of )?(?:the )?first (?:to|who)/i, label: 'early-adopter', signals: { novelty: -0.9, risk: -0.3 } },
  // "I got in early on..." → early adopter
  { pattern: /i (?:got in|jumped on|signed up) early/i, label: 'early-adopter', signals: { novelty: -0.8 } },
  // "I waited until it was proven..." → wait-and-see
  { pattern: /i waited (?:until|for|till)/i, label: 'wait-and-see', signals: { novelty: 0.8, risk: 0.3 } },
  // "I prefer to wait and see..." → wait-and-see
  { pattern: /i prefer (?:to )?(?:wait|see|observe)/i, label: 'wait-and-see', signals: { novelty: 0.9 } },
  // "I tried the beta/alpha..." → early adopter
  { pattern: /i (?:tried|tested|used) (?:the )?(?:beta|alpha|preview|early access)/i, label: 'early-adopter', signals: { novelty: -0.8, risk: -0.2 } },

  // ── Risk tolerance episodes ────────────────────────────────────────────
  // "I bet everything on..." → bold risk-taker
  { pattern: /i (?:bet|went all in|risked|gambled) (?:everything|it all|big)/i, label: 'bold', signals: { risk: -0.9 } },
  // "I shipped/launched/delivered X" → goal completion + bold
  { pattern: /i (?:shipped|launched|delivered|completed|finished|released) .{3,30}/i, label: 'shipped', signals: { risk: -0.4 } },
  // "I played it safe..." → cautious
  { pattern: /i (?:played it safe|hedged|diversified|took the safe)/i, label: 'cautious', signals: { risk: 0.9 } },
  // "I was careful to..." → cautious approach
  { pattern: /i was (?:careful|cautious|conservative|measured)/i, label: 'cautious', signals: { risk: 0.7 } },
  // "I took a leap..." → bold
  { pattern: /i (?:took a leap|went for it|took the plunge|dived in)/i, label: 'bold', signals: { risk: -0.8, decision: -0.4 } },

  // ── Exploration / discovery episodes ───────────────────────────────────
  // "I was exploring/experimenting..." → early-adopter + bold
  { pattern: /i was (?:exploring|experimenting|playing|tinkering)\b/i, label: 'exploring', signals: { novelty: -0.5, risk: -0.3 } },
  // "I stumbled upon/discovered" → serendipity = early-adopter
  { pattern: /i (?:stumbled upon|discovered|found out|came across)/i, label: 'discovery', signals: { novelty: -0.5 } },
  // "I set a goal to..." → deliberate + cautious planning
  { pattern: /i set (?:a |my )?(?:goal|target|deadline|milestone)/i, label: 'goal-setting', signals: { decision: 0.7, risk: 0.3 } },
  // "I hit my target/goal" → deliberate + risk tolerance through achievement
  { pattern: /i (?:hit|reached|achieved|met) (?:my |the )?(?:target|goal|milestone|deadline)/i, label: 'achieved', signals: { decision: 0.5 } },
];

// ─── Strength detection patterns ─────────────────────────────────────────

export const STRENGTH_PATTERNS: Array<{ pattern: RegExp; label: string }> = [
  { pattern: /i (?:built|created|made|developed|wrote)\s+(?:a |an |the )?(\w[\w\s]{2,20})/i, label: 'Builder' },
  { pattern: /i (?:taught|mentored|coached|trained|helped others)/i, label: 'Teacher' },
  { pattern: /i (?:designed|prototyped|wireframed|styled)/i, label: 'Designer' },
  { pattern: /i (?:analyzed|researched|studied|investigated)/i, label: 'Analyst' },
  { pattern: /i (?:organized|managed|coordinated|led|facilitated)/i, label: 'Organizer' },
  { pattern: /i (?:wrote|published|blogged|documented|authored)/i, label: 'Writer' },
  { pattern: /i (?:automated|optimized|streamlined|improved)/i, label: 'Optimizer' },
  { pattern: /i (?:founded|started|launched|bootstrapped|co-founded)/i, label: 'Founder' },
  { pattern: /(?:open[- ]?source|contributor|maintainer|pull request)/i, label: 'Open Source Contributor' },
  { pattern: /(?:community|moderator|ambassador|advocate)/i, label: 'Community Builder' },
];
