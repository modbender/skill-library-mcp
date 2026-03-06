/**
 * Majority Voting / Best-of-N
 * Same prompt → N parallel executions → pick the best/consensus answer
 * 
 * Strategies:
 * - "judge": LLM picks the best from all candidates (most reliable)
 * - "longest": Pick longest response (heuristic, zero extra cost)
 * - "similarity": Pick the most common/similar answer (consensus)
 * 
 * v1.3.7
 */

const DEFAULT_N = 3;
const MAX_N = 7;

/**
 * Run majority voting: same prompt N times in parallel, pick best
 * 
 * @param {Function} executeFn - async (instruction, input, systemPrompt) => string
 * @param {string} instruction - The prompt
 * @param {string} input - Optional input data
 * @param {object} opts
 * @param {number} opts.n - Number of candidates (default 3, max 7)
 * @param {string} opts.strategy - "judge" | "longest" | "similarity" (default "judge")
 * @param {string} opts.systemPrompt - Optional system prompt
 * @returns {{ output, candidates, strategy, winner, scores, cost }}
 */
async function vote(executeFn, instruction, input, opts = {}) {
  const n = Math.min(opts.n || DEFAULT_N, MAX_N);
  const strategy = opts.strategy || 'judge';

  // Phase 1: Generate N candidates in parallel
  const promises = [];
  for (let i = 0; i < n; i++) {
    promises.push(executeFn(instruction, input, opts.systemPrompt));
  }
  
  const results = await Promise.allSettled(promises);
  const candidates = results
    .filter(r => r.status === 'fulfilled' && r.value && r.value.trim().length > 0)
    .map((r, i) => ({ index: i, text: r.value.trim() }));

  if (candidates.length === 0) {
    return { output: '', candidates: [], strategy, winner: -1, error: 'All candidates failed' };
  }

  if (candidates.length === 1) {
    return { output: candidates[0].text, candidates, strategy, winner: 0, note: 'Only 1 valid candidate' };
  }

  // Phase 2: Pick winner based on strategy
  let winner;
  let scores = null;

  switch (strategy) {
    case 'longest':
      winner = pickLongest(candidates);
      break;

    case 'similarity':
      const sim = pickBySimilarity(candidates);
      winner = sim.winner;
      scores = sim.scores;
      break;

    case 'judge':
    default:
      const judgeResult = await judgePickBest(executeFn, instruction, candidates);
      winner = judgeResult.winner;
      scores = judgeResult.scores;
      break;
  }

  return {
    output: candidates[winner]?.text || candidates[0].text,
    candidates: candidates.map(c => ({ index: c.index, length: c.text.length, preview: c.text.substring(0, 200) })),
    strategy,
    winner,
    scores,
    n,
    validCandidates: candidates.length,
  };
}

/**
 * Simple heuristic: longest response is often most thorough
 */
function pickLongest(candidates) {
  let best = 0;
  let bestLen = 0;
  for (let i = 0; i < candidates.length; i++) {
    if (candidates[i].text.length > bestLen) {
      bestLen = candidates[i].text.length;
      best = i;
    }
  }
  return best;
}

/**
 * Similarity-based consensus: pick the candidate most similar to all others
 * Uses Jaccard similarity on word sets
 */
function pickBySimilarity(candidates) {
  const wordSets = candidates.map(c => new Set(c.text.toLowerCase().split(/\s+/)));
  
  const scores = candidates.map((_, i) => {
    let totalSim = 0;
    for (let j = 0; j < candidates.length; j++) {
      if (i === j) continue;
      totalSim += jaccard(wordSets[i], wordSets[j]);
    }
    return totalSim / (candidates.length - 1);
  });

  let best = 0;
  for (let i = 1; i < scores.length; i++) {
    if (scores[i] > scores[best]) best = i;
  }

  return { winner: best, scores: scores.map((s, i) => ({ candidate: i, similarity: parseFloat(s.toFixed(3)) })) };
}

/**
 * Jaccard similarity between two sets
 */
function jaccard(a, b) {
  const intersection = new Set([...a].filter(x => b.has(x)));
  const union = new Set([...a, ...b]);
  return union.size === 0 ? 0 : intersection.size / union.size;
}

/**
 * LLM judge picks the best candidate
 */
async function judgePickBest(executeFn, originalTask, candidates) {
  const candidateList = candidates.map((c, i) => 
    `--- CANDIDATE ${i + 1} ---\n${c.text.substring(0, 2000)}\n`
  ).join('\n');

  const judgePrompt = `You are a quality judge. Given the original task and ${candidates.length} candidate responses, pick the BEST one.

Score each on: accuracy, completeness, clarity, actionability (1-10 each).
Then pick the winner.

Original task: ${originalTask}

${candidateList}

Respond in JSON:
{
  "scores": [{"candidate": 1, "accuracy": N, "completeness": N, "clarity": N, "actionability": N, "total": N}, ...],
  "winner": <candidate number 1-indexed>,
  "reasoning": "why this one wins"
}`;

  const judgeSystemPrompt = 'You are a precise quality evaluator. Always respond with valid JSON only, no markdown.';

  try {
    const raw = await executeFn(judgePrompt, '', judgeSystemPrompt);
    // Aggressive JSON extraction (same pattern as reflect.js)
    const jsonMatch = raw.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      return { winner: pickLongest(candidates), scores: null, judgeError: 'No JSON in judge response' };
    }
    
    const parsed = JSON.parse(jsonMatch[0]);
    // Convert 1-indexed winner to 0-indexed
    const winnerIdx = (parsed.winner || 1) - 1;
    const clampedWinner = Math.max(0, Math.min(winnerIdx, candidates.length - 1));
    
    return {
      winner: clampedWinner,
      scores: parsed.scores || null,
      reasoning: parsed.reasoning || null,
    };
  } catch (e) {
    // Fallback to longest on judge failure
    return { winner: pickLongest(candidates), scores: null, judgeError: e.message };
  }
}

module.exports = { vote, pickLongest, pickBySimilarity, MAX_N, DEFAULT_N };
