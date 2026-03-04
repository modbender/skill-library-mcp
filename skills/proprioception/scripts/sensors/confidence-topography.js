/**
 * CONFIDENCE TOPOGRAPHY (CT)
 *
 * Maps which parts of a response are solid ground versus thin ice.
 * Detects hedging language, speculative markers, and uncertainty signals.
 *
 * Score: 0.0 (everything uncertain) → 1.0 (everything confident)
 */

const { splitSentences, countPatterns, wordCount } = require("../text-utils");

// ---------------------------------------------------------------------------
// Linguistic markers by confidence zone
// ---------------------------------------------------------------------------

const HEDGING_PATTERNS = [
  "\\bmight\\b", "\\bmaybe\\b", "\\bperhaps\\b", "\\bpossibly\\b",
  "\\bcould be\\b", "\\bprobably\\b", "\\bi think\\b", "\\bi believe\\b",
  "\\bit seems\\b", "\\bappears to\\b", "\\bseems like\\b",
  "\\bnot sure\\b", "\\bnot certain\\b", "\\bunclear\\b",
  "\\blikely\\b", "\\bunlikely\\b", "\\btend to\\b", "\\bgenerally\\b",
  "\\btypically\\b", "\\busually\\b", "\\bsometimes\\b",
  "\\bmy understanding\\b", "\\bas far as i know\\b",
  "\\bi'm not (?:entirely |completely )?sure\\b",
  "\\bdon'?t quote me\\b", "\\btake this with\\b",
  "\\bit'?s possible\\b", "\\bthere'?s a chance\\b",
];

const SPECULATIVE_PATTERNS = [
  "\\bhypothetically\\b", "\\bin theory\\b", "\\btheoretically\\b",
  "\\bspeculat", "\\bassume\\b", "\\bassuming\\b",
  "\\bif i had to guess\\b", "\\bmy guess\\b", "\\broughly\\b",
  "\\bapproximate", "\\bestimate",
];

const HIGH_CONFIDENCE_PATTERNS = [
  "\\bdefinitely\\b", "\\bcertainly\\b", "\\babsolutely\\b",
  "\\bwithout doubt\\b", "\\bguaranteed\\b", "\\bproven\\b",
  "\\bestablished\\b", "\\bverified\\b", "\\bconfirmed\\b",
  "\\bfact\\b", "\\bevidence shows\\b", "\\bresearch shows\\b",
  "\\baccording to\\b", "\\bdocumented\\b",
];

const DISCLAIMER_PATTERNS = [
  "\\bdisclaimer\\b", "\\bnote that\\b", "\\bkeep in mind\\b",
  "\\bimportant to note\\b", "\\bbe aware\\b", "\\bcaveat\\b",
  "\\bhowever\\b", "\\bthat said\\b", "\\bon the other hand\\b",
  "\\balthough\\b",
];

// ---------------------------------------------------------------------------
// Confidence zone classification
// ---------------------------------------------------------------------------

function classifyConfidenceZone(score) {
  if (score >= 0.9) return "bedrock";
  if (score >= 0.7) return "firm_ground";
  if (score >= 0.5) return "soft_ground";
  if (score >= 0.3) return "thin_ice";
  return "open_water";
}

// ---------------------------------------------------------------------------
// Main computation
// ---------------------------------------------------------------------------

/**
 * @param {string} currentResponse — The agent's current response text
 * @returns {{ score: number, zones: object, details: object }}
 */
function computeConfidenceTopography(currentResponse) {
  const sentences = splitSentences(currentResponse);
  const totalWords = wordCount(currentResponse);

  if (totalWords === 0) {
    return {
      score: 0.5,
      zones: { bedrock: 0, firm_ground: 0, soft_ground: 0, thin_ice: 0, open_water: 0 },
      details: { hedgingRatio: 0, speculativeRatio: 0, highConfidenceRatio: 0 },
    };
  }

  // Count pattern hits
  const hedgingCount = countPatterns(currentResponse, HEDGING_PATTERNS);
  const speculativeCount = countPatterns(currentResponse, SPECULATIVE_PATTERNS);
  const highConfCount = countPatterns(currentResponse, HIGH_CONFIDENCE_PATTERNS);
  const disclaimerCount = countPatterns(currentResponse, DISCLAIMER_PATTERNS);

  // Ratios relative to sentence count (patterns per sentence)
  const sentenceCount = Math.max(sentences.length, 1);
  const hedgingRatio = hedgingCount / sentenceCount;
  const speculativeRatio = speculativeCount / sentenceCount;
  const highConfRatio = highConfCount / sentenceCount;
  const disclaimerRatio = disclaimerCount / sentenceCount;

  // Composite confidence score
  // High confidence markers push UP, hedging/speculative push DOWN
  let score = 0.75; // baseline — most well-formed responses are reasonably confident
  score += highConfRatio * 0.15;       // boost for confident language
  score -= hedgingRatio * 0.20;        // penalty for hedging
  score -= speculativeRatio * 0.25;    // heavier penalty for speculation
  score -= disclaimerRatio * 0.05;     // mild penalty for disclaimers (they're actually good practice)

  score = Math.max(0, Math.min(1, score));

  // Per-sentence zone classification
  const zones = { bedrock: 0, firm_ground: 0, soft_ground: 0, thin_ice: 0, open_water: 0 };

  for (const sentence of sentences) {
    const sHedge = countPatterns(sentence, HEDGING_PATTERNS);
    const sSpec = countPatterns(sentence, SPECULATIVE_PATTERNS);
    const sHigh = countPatterns(sentence, HIGH_CONFIDENCE_PATTERNS);

    let sScore = 0.75;
    sScore += sHigh * 0.15;
    sScore -= sHedge * 0.20;
    sScore -= sSpec * 0.25;
    sScore = Math.max(0, Math.min(1, sScore));

    const zone = classifyConfidenceZone(sScore);
    zones[zone]++;
  }

  // Normalize zone counts to percentages
  const zonePercentages = {};
  for (const [zone, count] of Object.entries(zones)) {
    zonePercentages[zone] = Math.round((count / sentenceCount) * 100);
  }

  return {
    score: Math.round(score * 100) / 100,
    zones: zonePercentages,
    details: {
      hedgingRatio: Math.round(hedgingRatio * 100) / 100,
      speculativeRatio: Math.round(speculativeRatio * 100) / 100,
      highConfidenceRatio: Math.round(highConfRatio * 100) / 100,
      disclaimerRatio: Math.round(disclaimerRatio * 100) / 100,
      totalSentences: sentenceCount,
      markersFound: hedgingCount + speculativeCount + highConfCount + disclaimerCount,
    },
  };
}

module.exports = { computeConfidenceTopography };
