/**
 * Content Router (Enhanced Keyword Version)
 *
 * Classifies content into memory types using pattern matching.
 * No LLM required - fast, deterministic, zero dependencies.
 *
 * Accuracy target: 90%+
 */

export interface RoutingResult {
  types: {
    episodic: number;   // 0.0 - 1.0 confidence
    semantic: number;
    procedural: number;
  };
  reasoning: string;
  confidence: number;   // Overall confidence in classification
  matchedPatterns: string[];  // For debugging
}

// ============================================
// PATTERN DEFINITIONS
// ============================================

// Past-tense verbs indicating events (episodic)
const PAST_TENSE_VERBS = [
  'met', 'discussed', 'talked', 'called', 'happened', 'occurred',
  'built', 'created', 'made', 'completed', 'finished', 'started',
  'learned', 'discovered', 'found', 'saw', 'heard', 'read',
  'decided', 'agreed', 'disagreed', 'resolved', 'fixed',
  'deployed', 'shipped', 'released', 'launched', 'implemented',
  'received', 'sent', 'wrote', 'said', 'asked', 'answered',
  'went', 'came', 'left', 'arrived', 'visited', 'attended',
  'caused', 'triggered', 'resulted', 'led', 'broke', 'failed'
];

// Time indicators for episodic
const TIME_INDICATORS = [
  'yesterday', 'today', 'last week', 'last month', 'recently',
  'this morning', 'this afternoon', 'this evening', 'tonight',
  'on monday', 'on tuesday', 'on wednesday', 'on thursday', 'on friday',
  'ago', 'earlier', 'previously', 'before'
];

// Common typos for time indicators (fuzzy matching)
const TIME_TYPOS: { [key: string]: string } = {
  'yestrday': 'yesterday',
  'yesturday': 'yesterday',
  'yestday': 'yesterday',
  'yday': 'yesterday',
  'todays': 'today',
  'tday': 'today',
  'nigth': 'night',
  'nite': 'night',
  'ystrday': 'yesterday',
};

// Meeting/event indicators (episodic)
const EVENT_INDICATORS = [
  'meeting', 'call', 'conversation', 'discussion', 'session',
  'interview', 'presentation', 'demo', 'workshop', 'standup',
  'we had', 'we discussed', 'we talked', 'we met'
];

// Procedure/action verbs (procedural)
const PROCEDURE_VERBS = [
  'run', 'execute', 'install', 'configure', 'setup', 'create',
  'delete', 'remove', 'update', 'upgrade', 'deploy', 'build',
  'test', 'verify', 'check', 'validate', 'restart', 'reload',
  'clone', 'commit', 'push', 'pull', 'merge', 'branch'
];

// Step indicators (procedural)
const STEP_INDICATORS = [
  'first,', 'second,', 'third,', 'then,', 'next,', 'finally,',
  'step 1', 'step 2', 'step 3', '1)', '2)', '3)', '1.', '2.', '3.',
  'before you', 'after you', 'you need to', 'you should',
  'make sure to', 'ensure that', 'remember to'
];

// Conditional patterns (procedural) - "when X, do Y"
const CONDITIONAL_PATTERNS = [
  /when\s+.+,\s*(check|verify|run|execute|use|ensure|make|do)/i,
  /if\s+.+,\s*(check|verify|run|execute|use|ensure|make|do)/i,
  /when\s+.+\s+(fails|breaks|errors)/i,
  /if\s+.+\s+(fails|breaks|errors)/i
];

// Protocol/process keywords (procedural)
const PROCESS_KEYWORDS = [
  'protocol', 'workflow', 'process', 'procedure', 'steps',
  'how to', 'guide', 'instructions', 'tutorial', 'method',
  'pipeline', 'checklist', 'routine'
];

// Semantic indicators - preferences
const PREFERENCE_INDICATORS = [
  'prefer', 'prefers', 'like', 'likes', 'dislike', 'dislikes',
  'love', 'hate', 'want', 'needs', 'favorite', 'best'
];

// Semantic indicators - facts
const FACT_INDICATORS = [
  'is', 'are', 'was', 'were', 'have', 'has', 'had',
  'means', 'refers to', 'defined as', 'stands for',
  'default', 'typically', 'usually', 'always', 'never'
];

// Ownership/belonging (often semantic)
const OWNERSHIP_PATTERNS = [
  /'s\s+\w+$/i,           // "Phillip's timezone"
  /\w+\s+target/i,        // "revenue target"
  /\w+\s+default/i,       // "gateway default"
  /runs on/i,             // "runs on port"
  /uses\s+\w+\s+for/i     // "uses SQLite for storage"
];

// ============================================
// SCORING FUNCTIONS
// ============================================

function scoreEpisodic(content: string): { score: number; patterns: string[] } {
  const patterns: string[] = [];
  let score = 0;
  const lower = content.toLowerCase();

  // Past-tense verbs (strong indicator)
  // Exclude gerunds (ing form) which are often procedural
  for (const verb of PAST_TENSE_VERBS) {
    // Match past tense but not gerund (e.g., "started" is past, "starting" is gerund)
    const regex = new RegExp(`\\b${verb}\\b`, 'i');
    const gerundRegex = new RegExp(`\\b${verb.replace(/ed$/, 'ing')}\\b`, 'i');
    if (regex.test(content) && !gerundRegex.test(content)) {
      score += 0.3;
      patterns.push(`past-tense:${verb}`);
    }
  }

  // Time indicators (strong)
  for (const time of TIME_INDICATORS) {
    if (lower.includes(time)) {
      score += 0.25;
      patterns.push(`time:${time}`);
    }
  }

  // Time typo fuzzy matching
  for (const [typo, correct] of Object.entries(TIME_TYPOS)) {
    if (lower.includes(typo)) {
      score += 0.2;  // Slightly lower for typos
      patterns.push(`time-typo:${typo}->${correct}`);
    }
  }

  // Event indicators (strong)
  for (const event of EVENT_INDICATORS) {
    if (lower.includes(event)) {
      score += 0.3;
      patterns.push(`event:${event}`);
    }
  }

  // "We" + past action pattern
  if (/we\s+(met|discussed|talked|had|decided|agreed|built|created)/i.test(content)) {
    score += 0.4;
    patterns.push('we+past-action');
  }

  // "X caused Y" pattern - events causing outcomes
  if (/\b(caused|led to|resulted in|triggered)\b/i.test(content)) {
    score += 0.35;
    patterns.push('causation-event');
  }

  // Outage/incident/breakage words (event outcomes)
  if (/\b(outage|incident|failure|error|crash|crashed|broke|broken|issue|problem|garbage)\b/i.test(content)) {
    score += 0.3;
    patterns.push('incident');
  }

  // Strong event verbs (crashed, broke, failed - definitive past events)
  if (/\b(crashed|broke|failed|borked|died|exploded)\b/i.test(content)) {
    score += 0.35;
    patterns.push('strong-event-verb');
  }

  return { score: Math.min(score, 1), patterns };
}

function scoreProcedural(content: string): { score: number; patterns: string[] } {
  const patterns: string[] = [];
  let score = 0;
  const lower = content.toLowerCase();

  // Step indicators (very strong)
  for (const step of STEP_INDICATORS) {
    if (lower.includes(step)) {
      score += 0.35;
      patterns.push(`step:${step}`);
    }
  }

  // Conditional patterns (strong)
  for (const pattern of CONDITIONAL_PATTERNS) {
    if (pattern.test(content)) {
      score += 0.4;
      patterns.push(`conditional:${pattern.source.slice(0, 20)}`);
    }
  }

  // Process keywords (strong)
  for (const keyword of PROCESS_KEYWORDS) {
    if (lower.includes(keyword)) {
      score += 0.3;
      patterns.push(`process:${keyword}`);
    }
  }

  // Procedure verbs with context
  for (const verb of PROCEDURE_VERBS) {
    const regex = new RegExp(`\\b(run|execute|check|verify)\\s+\\w+`, 'i');
    if (regex.test(content)) {
      score += 0.25;
      patterns.push(`action:${verb}`);
    }
  }

  // Numbered list detection
  if (/\d+[.)]\s+\w+/.test(content)) {
    score += 0.35;
    patterns.push('numbered-list');
  }

  // "then... then" chain pattern (implied steps)
  const thenCount = (lower.match(/\bthen\b/g) || []).length;
  if (thenCount >= 2) {
    score += 0.3;
    patterns.push('then-chain');
  }

  // "involves" + actions pattern
  if (/involves\s+(reading|checking|running|executing|using)/i.test(content)) {
    score += 0.4;
    patterns.push('involves+action');
  }

  // "To [verb], run/do/execute" pattern (instructional)
  if (/^to\s+\w+.*,\s*(run|do|execute|use|call|type|enter)/i.test(content)) {
    score += 0.5;
    patterns.push('instructional');
  }

  // Command pattern: "run:", "execute:", "use:" (common in docs)
  if (/(run|execute|use|call|type):\s*\w+/i.test(content)) {
    score += 0.35;
    patterns.push('command-pattern');
  }

  // "Before/After [gerund]" pattern (procedural instructions)
  if (/\b(before|after)\s+\w+ing\b/i.test(content)) {
    score += 0.45;
    patterns.push('before-after-instruction');
  }

  // "Make sure to/that" pattern (procedural)
  if (/\bmake sure\s+(to|that)\b/i.test(content)) {
    score += 0.35;
    patterns.push('make-sure');
  }
  if (/^(run|execute|check|verify|install|configure|setup|create|delete|update|restart|reload|clone|commit|push|pull)\s/i.test(content)) {
    score += 0.4;
    patterns.push('imperative');
  }

  return { score: Math.min(score, 1), patterns };
}

function scoreSemantic(content: string): { score: number; patterns: string[] } {
  const patterns: string[] = [];
  let score = 0;
  const lower = content.toLowerCase();

  // Preference indicators (very strong for semantic)
  for (const pref of PREFERENCE_INDICATORS) {
    if (lower.includes(pref)) {
      score += 0.4;
      patterns.push(`preference:${pref}`);
    }
  }

  // Ownership patterns (strong)
  for (const pattern of OWNERSHIP_PATTERNS) {
    if (pattern.test(content)) {
      score += 0.3;
      patterns.push(`ownership:${pattern.source.slice(0, 15)}`);
    }
  }

  // Fact indicators (moderate - common words)
  // Only count if no other strong signals
  if (/\b(is|are|was)\s+\w+/i.test(content)) {
    score += 0.15;
    patterns.push('fact-verb');
  }

  // Technical facts
  if (/\d+\s*(port|mb|gb|ms|seconds?|minutes?|hours?)/i.test(content)) {
    score += 0.25;
    patterns.push('technical-measurement');
  }

  // "X's Y" possession pattern (e.g., "Phillip's timezone")
  if (/\b[A-Z][a-z]+'s\s+\w+/i.test(content)) {
    score += 0.3;
    patterns.push('possession');
  }

  return { score: Math.min(score, 1), patterns };
}

// ============================================
// MAIN ROUTER
// ============================================

export async function routeWithLLM(
  content: string,
  context?: string
): Promise<RoutingResult> {
  // This is the keyword-only version
  // LLM fallback will be added in Phase 1.1b
  return routeWithKeywords(content, context);
}

export async function routeContent(
  content: string,
  context?: string
): Promise<{ episodic: boolean; semantic: boolean; procedural: boolean }> {
  const result = await routeWithKeywords(content, context);
  const threshold = 0.4;

  return {
    episodic: result.types.episodic > threshold,
    semantic: result.types.semantic > threshold,
    procedural: result.types.procedural > threshold,
  };
}

// Keyword-based router (main implementation)
export function routeWithKeywords(
  content: string,
  context?: string
): RoutingResult {
  const patterns: string[] = [];

  // Score each type
  const epResult = scoreEpisodic(content);
  const procResult = scoreProcedural(content);
  const semResult = scoreSemantic(content);

  patterns.push(...epResult.patterns, ...procResult.patterns, ...semResult.patterns);

  let episodic = epResult.score;
  let procedural = procResult.score;
  let semantic = semResult.score;

  // Penalize conflicts

  // "I think we should automate" - suggestion, not procedure
  if (/i think we should/i.test(content) || /we should/i.test(content)) {
    procedural *= 0.3;  // Reduce procedural score
    semantic += 0.3;     // Boost semantic (it's an opinion/suggestion)
    patterns.push('suggestion-penalty');
  }

  // Past-tense verbs strongly indicate episodic
  if (epResult.score > 0.3) {
    semantic *= 0.7;  // Reduce semantic if clearly episodic
    patterns.push('episodic-dominant');
  }

  // If nothing significant detected, default to semantic
  const maxScore = Math.max(episodic, procedural, semantic);
  if (maxScore < 0.2) {
    semantic = 0.5;
    patterns.push('default-semantic');
  }

  // Normalize to sum to ~1
  const total = episodic + procedural + semantic;
  if (total > 0) {
    episodic /= total;
    procedural /= total;
    semantic /= total;
  }

  // Determine confidence
  const sorted = [episodic, procedural, semantic].sort((a, b) => b - a);
  const confidence = sorted[0] - sorted[1] > 0.3 ? 0.9 : 0.6;

  // Build reasoning
  const topType = episodic > procedural && episodic > semantic ? 'episodic'
    : procedural > semantic ? 'procedural'
    : 'semantic';

  const reasoning = `Classified as ${topType} based on: ${patterns.slice(0, 3).join(', ')}`;

  return {
    types: { episodic, semantic, procedural },
    reasoning,
    confidence,
    matchedPatterns: patterns,
  };
}