/**
 * GOAL PROXIMITY RADAR (GPR)
 *
 * Continuously measures the distance between the conversation's current
 * trajectory and the user's actual objective.
 *
 * Score: 0.0 (completely off-target) → 1.0 (locked on)
 */

const {
  semanticTokens,
  cosineSimilarity,
  jaccardSimilarity,
} = require("../text-utils");

/**
 * @param {string} rootIntent     — The user's original goal / first message
 * @param {string} currentResponse — The agent's current response text
 * @param {Array}  priorSignals   — Previous turn signals for trend analysis
 * @returns {{ score: number, drift: string, details: object }}
 */
function computeGoalProximity(rootIntent, currentResponse, priorSignals) {
  const intentTokens = semanticTokens(rootIntent);
  const responseTokens = semanticTokens(currentResponse);

  // Two complementary similarity measures
  const cosine = cosineSimilarity(intentTokens, responseTokens);
  const jaccard = jaccardSimilarity(intentTokens, responseTokens);

  // Weighted blend — cosine captures term frequency alignment,
  // Jaccard captures vocabulary overlap
  const rawScore = cosine * 0.6 + jaccard * 0.4;

  // Trend analysis: is the score improving or declining over turns?
  const priorGPR = priorSignals
    .filter((s) => s.sensors?.goalProximityRadar)
    .map((s) => s.sensors.goalProximityRadar.score);

  let trend = "stable";
  if (priorGPR.length >= 2) {
    const recent = priorGPR.slice(-3);
    const avg = recent.reduce((a, b) => a + b, 0) / recent.length;
    if (rawScore < avg - 0.1) trend = "drifting";
    else if (rawScore > avg + 0.1) trend = "converging";
  }

  // Detect goal mutation — if the user's language has shifted significantly
  // between turns, the goal itself may have evolved
  let goalMutation = false;
  if (priorGPR.length >= 1) {
    const lastScore = priorGPR[priorGPR.length - 1];
    // A sudden large drop followed by recovery suggests the goal changed
    if (Math.abs(rawScore - lastScore) > 0.3) {
      goalMutation = true;
    }
  }

  // Clamp to [0, 1]
  const score = Math.max(0, Math.min(1, rawScore));

  return {
    score: Math.round(score * 100) / 100,
    drift: trend,
    details: {
      cosineSimilarity: Math.round(cosine * 100) / 100,
      jaccardSimilarity: Math.round(jaccard * 100) / 100,
      goalMutation,
      intentTerms: intentTokens.length,
      responseTerms: responseTokens.length,
      priorReadings: priorGPR.length,
    },
  };
}

module.exports = { computeGoalProximity };
