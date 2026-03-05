/**
 * SESSION QUALITY PULSE (SQP)
 *
 * Tracks the cumulative health of the entire session — detecting whether the
 * overall interaction is improving, stable, or degrading.
 *
 * Scores each response on four axes:
 *   - Relevance: how directly it addresses the need
 *   - Precision: how specific and actionable
 *   - Novelty: how much new value vs repetition
 *   - Efficiency: token economy (saying more with less)
 *
 * Score: 0.0 (session is failing) → 1.0 (session is thriving)
 */

const {
  semanticTokens,
  cosineSimilarity,
  jaccardSimilarity,
  lexicalDiversity,
  wordCount,
  splitSentences,
  countPatterns,
} = require("../text-utils");

// ---------------------------------------------------------------------------
// Actionability markers — indicators of concrete, useful content
// ---------------------------------------------------------------------------

const ACTIONABLE_PATTERNS = [
  "\\bstep \\d+\\b",
  "\\bfirst\\b.*\\bthen\\b",
  "\\byou (?:can|should|need to|must)\\b",
  "\\brun\\b.*\\bcommand\\b",
  "\\binstall\\b",
  "\\bcreate\\b",
  "\\bexecute\\b",
  "\\bopen\\b",
  "\\bnavigate to\\b",
  "\\bclick\\b",
  "\\benter\\b",
  "\\btype\\b",
  "```",                  // code blocks = actionable
  "\\bhttps?://\\S+\\b",  // links = actionable
];

const FILLER_PATTERNS = [
  "\\bof course\\b",
  "\\bsure thing\\b",
  "\\bhappy to help\\b",
  "\\bgreat question\\b",
  "\\bthat'?s a good (?:question|point)\\b",
  "\\blet me (?:think|see|check)\\b",
  "\\bwell,?\\b",
  "\\bso,?\\b",
  "\\bbasically\\b",
  "\\bessentially\\b",
  "\\bfundamentally\\b",
];

// ---------------------------------------------------------------------------
// Axis computations
// ---------------------------------------------------------------------------

function computeRelevance(currentTokens, priorSignals) {
  // Relevance is measured by overlap with the accumulating conversation context
  // A relevant response connects to what came before
  if (priorSignals.length === 0) return 0.8; // first turn — assume relevant

  const priorTokenSets = priorSignals
    .filter((s) => s._responseTokens)
    .map((s) => s._responseTokens);

  if (priorTokenSets.length === 0) return 0.8;

  // Combine all prior tokens to form a "conversation context"
  const contextTokens = priorTokenSets.flat();
  const similarity = jaccardSimilarity(currentTokens, contextTokens);

  // Some similarity = relevant. Too much similarity = redundant (not relevant in a different way)
  // Sweet spot is 0.2–0.6 Jaccard with context
  if (similarity >= 0.2 && similarity <= 0.6) return 0.9;
  if (similarity > 0.6) return Math.max(0.4, 0.9 - (similarity - 0.6) * 2);
  return Math.max(0.3, similarity * 4);
}

function computePrecision(responseText) {
  const sentences = splitSentences(responseText);
  const sentenceCount = Math.max(sentences.length, 1);

  const actionableCount = countPatterns(responseText, ACTIONABLE_PATTERNS);
  const fillerCount = countPatterns(responseText, FILLER_PATTERNS);

  const actionableRatio = actionableCount / sentenceCount;
  const fillerRatio = fillerCount / sentenceCount;

  // Precision = actionable content minus filler
  return Math.max(0, Math.min(1, 0.6 + actionableRatio * 0.3 - fillerRatio * 0.2));
}

function computeNovelty(currentTokens, priorSignals) {
  if (priorSignals.length === 0) return 1.0; // first response is all novel

  const priorTokenSets = priorSignals
    .filter((s) => s._responseTokens)
    .map((s) => s._responseTokens);

  if (priorTokenSets.length === 0) return 1.0;

  // Novelty = proportion of current tokens NOT seen in prior responses
  const allPriorTokens = new Set(priorTokenSets.flat());
  const currentSet = new Set(currentTokens);
  const novelTokens = [...currentSet].filter((t) => !allPriorTokens.has(t));

  if (currentSet.size === 0) return 0;
  return novelTokens.length / currentSet.size;
}

function computeEfficiency(responseText) {
  const words = wordCount(responseText);
  const diversity = lexicalDiversity(responseText);
  const sentences = splitSentences(responseText).length;

  // Efficiency rewards: high diversity (not repetitive), reasonable length
  // Penalizes: very long responses, low diversity (lots of filler/repetition)
  const wordsPerSentence = words / Math.max(sentences, 1);

  let score = 0.7;
  score += (diversity - 0.5) * 0.3;  // higher diversity = more efficient

  // Optimal words per sentence: 10-25. Too short = shallow. Too long = bloated.
  if (wordsPerSentence >= 10 && wordsPerSentence <= 25) score += 0.1;
  else if (wordsPerSentence > 40) score -= 0.15;
  else if (wordsPerSentence < 5) score -= 0.10;

  return Math.max(0, Math.min(1, score));
}

// ---------------------------------------------------------------------------
// Trend analysis
// ---------------------------------------------------------------------------

function computeTrend(currentScore, priorSignals) {
  const priorScores = priorSignals
    .filter((s) => s.sensors?.sessionQualityPulse?.score !== undefined)
    .map((s) => s.sensors.sessionQualityPulse.score);

  if (priorScores.length < 2) return "insufficient_data";

  const recent = priorScores.slice(-3);
  const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;

  // Volatility: standard deviation of recent scores
  const variance = recent.reduce((acc, s) => acc + Math.pow(s - recentAvg, 2), 0) / recent.length;
  const volatility = Math.sqrt(variance);

  if (volatility > 0.15) return "volatile";
  if (currentScore > recentAvg + 0.05) return "improving";
  if (currentScore < recentAvg - 0.05) return "declining";
  return "stable";
}

// ---------------------------------------------------------------------------
// Main computation
// ---------------------------------------------------------------------------

/**
 * @param {string} currentResponse — The agent's current response text
 * @param {Array}  priorSignals    — Previous turn signals
 * @param {number} turnNumber      — Current turn index
 * @returns {{ score: number, trend: string, axes: object, details: object }}
 */
function computeSessionQuality(currentResponse, priorSignals, turnNumber) {
  const currentTokens = semanticTokens(currentResponse);

  const relevance = computeRelevance(currentTokens, priorSignals);
  const precision = computePrecision(currentResponse);
  const novelty = computeNovelty(currentTokens, priorSignals);
  const efficiency = computeEfficiency(currentResponse);

  // Weighted composite — relevance and precision matter most
  const score =
    relevance * 0.30 +
    precision * 0.30 +
    novelty * 0.20 +
    efficiency * 0.20;

  const trend = computeTrend(score, priorSignals);

  return {
    score: Math.round(score * 100) / 100,
    trend,
    axes: {
      relevance: Math.round(relevance * 100) / 100,
      precision: Math.round(precision * 100) / 100,
      novelty: Math.round(novelty * 100) / 100,
      efficiency: Math.round(efficiency * 100) / 100,
    },
    details: {
      turnNumber,
      totalPriorTurns: priorSignals.length,
      wordCount: wordCount(currentResponse),
      sentenceCount: splitSentences(currentResponse).length,
    },
  };
}

module.exports = { computeSessionQuality };
