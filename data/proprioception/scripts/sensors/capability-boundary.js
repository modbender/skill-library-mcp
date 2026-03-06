/**
 * CAPABILITY BOUNDARY SENSING (CBS)
 *
 * Real-time awareness of when the agent is approaching the edge of its
 * competence — the zone where helpfulness turns into hallucination.
 *
 * Detects: increasing hedging, decreasing specificity, rising contradictions,
 * and hallucination signature patterns.
 *
 * Score: 0.0 (deep in unknown territory) → 1.0 (solidly within capability)
 *
 * This sensor gets the highest weight (0.25) in the overall Proprioceptive
 * Index because hallucination is the most dangerous AI failure mode.
 */

const { countPatterns, splitSentences, wordCount, semanticTokens } = require("../text-utils");

// ---------------------------------------------------------------------------
// Boundary signal patterns
// ---------------------------------------------------------------------------

const HEDGING_MARKERS = [
  "\\bmight\\b", "\\bmaybe\\b", "\\bperhaps\\b", "\\bpossibly\\b",
  "\\bcould be\\b", "\\bi think\\b", "\\bi believe\\b",
  "\\bnot sure\\b", "\\bnot certain\\b", "\\bunclear\\b",
  "\\bhard to say\\b", "\\bdifficult to determine\\b",
  "\\bit depends\\b", "\\bvaries\\b",
  "\\bi'?m not (?:entirely |completely )?sure\\b",
  "\\bmy best guess\\b",
];

const VAGUENESS_MARKERS = [
  "\\bsomething like\\b", "\\bsome kind of\\b", "\\bmore or less\\b",
  "\\bkind of\\b", "\\bsort of\\b", "\\bin some ways\\b",
  "\\bto some extent\\b", "\\bvarious\\b", "\\bseveral\\b",
  "\\bnumerous\\b", "\\bsignificant\\b", "\\bconsiderable\\b",
  "\\betc\\.?\\b", "\\band so on\\b", "\\band so forth\\b",
  "\\bamong others\\b", "\\bthings like that\\b",
];

const HALLUCINATION_SIGNATURES = [
  // Overly specific fabricated details
  "\\bfounded in \\d{4}\\b",
  "\\baccording to a \\d{4} study\\b",
  // Contradictory structures within the same response
  "\\bbut (?:actually|in fact|really)\\b",
  "\\bwell,? actually\\b",
  // Confidence without source
  "\\bit is well known\\b",
  "\\beveryone knows\\b",
  "\\bas we all know\\b",
  // Suspiciously precise numbers
  "\\b\\d{2,}\\.\\d{2,}%\\b",
];

const DEFLECTION_MARKERS = [
  "\\bi (?:can'?t|cannot) (?:help|assist) with\\b",
  "\\bbeyond (?:my|the) scope\\b",
  "\\bi don'?t have (?:access|information)\\b",
  "\\byou (?:should|might want to) (?:consult|check|ask)\\b",
  "\\bi'?d recommend (?:checking|consulting|asking)\\b",
  "\\bi'?m (?:not |un)?able to\\b",
];

// ---------------------------------------------------------------------------
// Specificity score — how concrete vs vague the response is
// ---------------------------------------------------------------------------

function computeSpecificity(text) {
  const sentences = splitSentences(text);
  const totalSentences = Math.max(sentences.length, 1);

  // Count concrete indicators: numbers, proper nouns (capitalized words mid-sentence),
  // code blocks, URLs, specific technical terms
  const concretePatterns = [
    "\\b\\d+\\b",                          // numbers
    "```",                                  // code blocks
    "\\bhttps?://",                         // URLs
    "\\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\\b",  // camelCase (technical terms)
  ];

  const concreteCount = countPatterns(text, concretePatterns);
  const vaguenessCount = countPatterns(text, VAGUENESS_MARKERS);

  const concreteRatio = concreteCount / totalSentences;
  const vaguenessRatio = vaguenessCount / totalSentences;

  // Higher specificity = more concrete, less vague
  return Math.max(0, Math.min(1, 0.5 + concreteRatio * 0.25 - vaguenessRatio * 0.3));
}

// ---------------------------------------------------------------------------
// Contradiction detection across turns
// ---------------------------------------------------------------------------

function detectContradictions(currentResponse, priorSignals) {
  // Simple heuristic: check for negation of prior specific claims
  // In a full implementation, this would use semantic entailment
  const negationPatterns = [
    "\\bactually,? (?:it'?s|that'?s) not\\b",
    "\\bi (?:was|were) wrong\\b",
    "\\bcorrection\\b",
    "\\blet me (?:correct|fix|revise)\\b",
    "\\bcontrary to what i (?:said|mentioned)\\b",
    "\\bi misspoke\\b",
    "\\bthat'?s (?:incorrect|inaccurate|wrong)\\b",
  ];

  const selfContradictions = countPatterns(currentResponse, negationPatterns);

  return {
    selfContradictions,
    hasContradiction: selfContradictions > 0,
  };
}

// ---------------------------------------------------------------------------
// Main computation
// ---------------------------------------------------------------------------

/**
 * @param {string} currentResponse — The agent's current response text
 * @param {Array}  priorSignals    — Previous turn signals
 * @returns {{ score: number, boundaryDistance: string, details: object }}
 */
function computeCapabilityBoundary(currentResponse, priorSignals) {
  const words = wordCount(currentResponse);
  const sentences = splitSentences(currentResponse);
  const sentenceCount = Math.max(sentences.length, 1);

  if (words === 0) {
    return {
      score: 0.5,
      boundaryDistance: "unknown",
      details: {
        hedgingRatio: 0, specificityScore: 0.5, hallucinationSignals: 0,
        contradictions: 0, deflectionCount: 0,
      },
    };
  }

  // Measure boundary signals
  const hedgingCount = countPatterns(currentResponse, HEDGING_MARKERS);
  const hallucinationCount = countPatterns(currentResponse, HALLUCINATION_SIGNATURES);
  const deflectionCount = countPatterns(currentResponse, DEFLECTION_MARKERS);
  const contradictions = detectContradictions(currentResponse, priorSignals);
  const specificity = computeSpecificity(currentResponse);

  const hedgingRatio = hedgingCount / sentenceCount;

  // Compute boundary score
  let score = 0.85; // baseline — assume agent is within capability
  score -= hedgingRatio * 0.15;             // hedging pushes toward boundary
  score -= hallucinationCount * 0.10;       // hallucination signals are serious
  score -= contradictions.selfContradictions * 0.15; // contradictions are very serious
  score += (specificity - 0.5) * 0.20;     // specificity helps — vagueness hurts
  score -= deflectionCount * 0.05;          // deflections mildly indicate boundary

  // Trend: is hedging increasing over turns?
  const priorHedging = priorSignals
    .filter((s) => s.sensors?.capabilityBoundary?.details?.hedgingRatio !== undefined)
    .map((s) => s.sensors.capabilityBoundary.details.hedgingRatio);

  let hedgingTrend = "stable";
  if (priorHedging.length >= 2) {
    const recentAvg = priorHedging.slice(-3).reduce((a, b) => a + b, 0) / Math.min(priorHedging.length, 3);
    if (hedgingRatio > recentAvg + 0.1) {
      hedgingTrend = "increasing";
      score -= 0.10; // accelerating hedging is a strong boundary signal
    } else if (hedgingRatio < recentAvg - 0.1) {
      hedgingTrend = "decreasing";
    }
  }

  score = Math.max(0, Math.min(1, score));

  // Classify boundary distance
  let boundaryDistance;
  if (score >= 0.8) boundaryDistance = "safe";
  else if (score >= 0.6) boundaryDistance = "approaching";
  else if (score >= 0.4) boundaryDistance = "near_boundary";
  else boundaryDistance = "beyond_boundary";

  return {
    score: Math.round(score * 100) / 100,
    boundaryDistance,
    details: {
      hedgingRatio: Math.round(hedgingRatio * 100) / 100,
      hedgingTrend,
      specificityScore: Math.round(specificity * 100) / 100,
      hallucinationSignals: hallucinationCount,
      contradictions: contradictions.selfContradictions,
      hasContradiction: contradictions.hasContradiction,
      deflectionCount,
    },
  };
}

module.exports = { computeCapabilityBoundary };
