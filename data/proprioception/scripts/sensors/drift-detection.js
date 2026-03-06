/**
 * DRIFT DETECTION (DD)
 *
 * Detects the three conversation anti-patterns that waste the most time:
 *   1. Circular — repeating the same content across turns
 *   2. Tangential — drifting to unrelated topics
 *   3. Degenerative — declining response utility over time
 *
 * Score: 0.0 (severe drift) → 1.0 (perfectly on-track)
 */

const {
  semanticTokens,
  cosineSimilarity,
  jaccardSimilarity,
  lexicalDiversity,
  wordCount,
} = require("../text-utils");

// ---------------------------------------------------------------------------
// Conversation arc phases
// ---------------------------------------------------------------------------

const ARC_PHASES = ["opening", "exploration", "convergence", "resolution"];

function estimateArcPhase(turnNumber, totalSimilarityTrend) {
  // Heuristic: early turns = opening/exploration, later turns should converge
  if (turnNumber <= 2) return "opening";
  if (turnNumber <= 5) return "exploration";
  // If similarity is increasing in later turns, we're converging
  if (totalSimilarityTrend > 0) return "convergence";
  return "resolution";
}

// ---------------------------------------------------------------------------
// Main computation
// ---------------------------------------------------------------------------

/**
 * @param {string} currentResponse — The agent's current response text
 * @param {Array}  priorSignals    — Previous turn signals
 * @param {number} turnNumber      — Current turn index
 * @returns {{ score: number, patterns: object, arcPhase: string, details: object }}
 */
function computeDriftDetection(currentResponse, priorSignals, turnNumber) {
  const currentTokens = semanticTokens(currentResponse);

  // Collect prior response tokens from signal history
  const priorResponses = priorSignals
    .filter((s) => s._responseTokens)
    .map((s) => s._responseTokens);

  // Default state for first turn
  if (priorResponses.length === 0) {
    return {
      score: 1.0,
      patterns: { circular: false, tangential: false, degenerative: false },
      arcPhase: "opening",
      details: {
        circularScore: 0,
        tangentialScore: 0,
        degenerativeScore: 0,
        consecutiveSimilarity: 0,
        lexicalDiversity: Math.round(lexicalDiversity(currentResponse) * 100) / 100,
      },
    };
  }

  // -----------------------------------------------------------------------
  // 1. Circular detection: high similarity between consecutive turns
  // -----------------------------------------------------------------------
  const lastResponse = priorResponses[priorResponses.length - 1];
  const consecutiveSimilarity = cosineSimilarity(currentTokens, lastResponse);

  // Check for circular pattern (3+ turns with >0.8 similarity)
  let circularCount = 0;
  if (priorResponses.length >= 2) {
    for (let i = priorResponses.length - 1; i >= Math.max(0, priorResponses.length - 3); i--) {
      const sim = cosineSimilarity(currentTokens, priorResponses[i]);
      if (sim > 0.8) circularCount++;
    }
  }
  const isCircular = circularCount >= 2;
  const circularScore = isCircular ? 0.8 : consecutiveSimilarity > 0.8 ? 0.4 : 0;

  // -----------------------------------------------------------------------
  // 2. Tangential detection: sudden topic jump without user initiation
  // -----------------------------------------------------------------------
  // If current response is very DIFFERENT from last response, it might be tangential
  const topicDistance = 1 - consecutiveSimilarity;

  // Compare against running average of topic distances
  let avgTopicDistance = 0;
  if (priorResponses.length >= 2) {
    let totalDist = 0;
    for (let i = 1; i < priorResponses.length; i++) {
      totalDist += 1 - cosineSimilarity(priorResponses[i], priorResponses[i - 1]);
    }
    avgTopicDistance = totalDist / (priorResponses.length - 1);
  }

  // Tangential = current topic distance is 2x+ the average
  const isTangential = avgTopicDistance > 0 && topicDistance > avgTopicDistance * 2;
  const tangentialScore = isTangential ? 0.6 : 0;

  // -----------------------------------------------------------------------
  // 3. Degenerative detection: declining utility over time
  // -----------------------------------------------------------------------
  // Use lexical diversity as a proxy for response utility —
  // declining diversity suggests the agent is running out of useful things to say
  const currentDiversity = lexicalDiversity(currentResponse);
  const currentWordCount = wordCount(currentResponse);

  const priorDiversities = priorSignals
    .filter((s) => s.sensors?.driftDetection?.details?.lexicalDiversity)
    .map((s) => s.sensors.driftDetection.details.lexicalDiversity);

  let isDegenerative = false;
  if (priorDiversities.length >= 2) {
    const recentDiversities = priorDiversities.slice(-3);
    const trend = recentDiversities.reduce((acc, d, i) => {
      if (i === 0) return 0;
      return acc + (d - recentDiversities[i - 1]);
    }, 0);

    // If diversity has been declining AND word count is dropping
    isDegenerative = trend < -0.05 && currentDiversity < recentDiversities[0];
  }
  const degenerativeScore = isDegenerative ? 0.5 : 0;

  // -----------------------------------------------------------------------
  // Composite drift score
  // -----------------------------------------------------------------------
  const driftPenalty = Math.max(circularScore, tangentialScore, degenerativeScore);
  const score = Math.max(0, Math.min(1, 1 - driftPenalty));

  // Estimate conversation arc phase
  const similarityTrend = priorResponses.length >= 2
    ? consecutiveSimilarity - cosineSimilarity(
        priorResponses[priorResponses.length - 1],
        priorResponses[Math.max(0, priorResponses.length - 2)]
      )
    : 0;
  const arcPhase = estimateArcPhase(turnNumber, similarityTrend);

  return {
    score: Math.round(score * 100) / 100,
    patterns: {
      circular: isCircular,
      tangential: isTangential,
      degenerative: isDegenerative,
    },
    arcPhase,
    details: {
      circularScore: Math.round(circularScore * 100) / 100,
      tangentialScore: Math.round(tangentialScore * 100) / 100,
      degenerativeScore: Math.round(degenerativeScore * 100) / 100,
      consecutiveSimilarity: Math.round(consecutiveSimilarity * 100) / 100,
      lexicalDiversity: Math.round(currentDiversity * 100) / 100,
      circularTurns: circularCount,
      turnNumber,
    },
  };
}

module.exports = { computeDriftDetection };
