/**
 * Self-Reflection Loop for Swarm Chains
 * 
 * After a chain produces output, optionally run a critic pass:
 * 1. Critic scores the output on multiple dimensions (1-10)
 * 2. If average score < threshold, generate critique with specific fixes
 * 3. Re-run the final synthesis stage with critique as additional context
 * 4. Return improved output (or original if already good enough)
 * 
 * Design: minimal overhead. One extra LLM call for scoring, one more if refinement needed.
 * Worst case: 2 extra calls. Best case: 1 call (score is good, skip refinement).
 */

const { securePrompt } = require('./security');

const SCORE_DIMENSIONS = [
  'accuracy',      // Are claims factual and well-supported?
  'completeness',  // Does it cover all aspects of the task?
  'coherence',     // Is it well-structured and logically organized?
  'actionability', // Can the reader act on this output?
  'conciseness',   // Is it appropriately concise without losing substance?
];

const CRITIC_PROMPT = securePrompt(`You are a rigorous output quality critic. You evaluate text against specific dimensions and provide honest scores.

You MUST respond in EXACTLY this JSON format, nothing else:
{
  "scores": {
    "accuracy": <1-10>,
    "completeness": <1-10>,
    "coherence": <1-10>,
    "actionability": <1-10>,
    "conciseness": <1-10>
  },
  "avgScore": <number>,
  "weakest": "<dimension name>",
  "critique": "<2-3 sentences on what's weak and how to fix it>",
  "verdict": "pass" | "refine"
}

Scoring guide:
- 8-10: Good to excellent. No refinement needed.
- 5-7: Acceptable but has clear weaknesses.
- 1-4: Poor. Needs significant improvement.

Set verdict to "refine" if avgScore < 7 OR any single dimension < 5.
Be harsh but fair. Don't inflate scores.`);

const REFINE_PROMPT = securePrompt(`You are refining output based on specific critique. 
Improve the weak areas identified by the critic while preserving what's already strong.
Do NOT start with "Here's the refined version" or similar meta-commentary — just output the improved content directly.`);

/**
 * Default reflection config
 */
const DEFAULTS = {
  enabled: false,
  threshold: 7.0,        // Avg score below this triggers refinement
  maxRefinements: 1,      // Max refinement cycles (1 = one critic + one refine)
  dimensions: SCORE_DIMENSIONS,
};

/**
 * Run the critic on chain output
 * @param {Function} executeFn - async (instruction, input, systemPrompt) => string
 * @param {string} output - The chain's final output
 * @param {string} task - Original task description (for context)
 * @returns {{ scores, avgScore, weakest, critique, verdict, raw }}
 */
async function criticize(executeFn, output, task) {
  const instruction = `Score this output that was generated for the task: "${task}"

Evaluate each dimension 1-10. Respond with ONLY the JSON object.`;

  const raw = await executeFn(instruction, output, CRITIC_PROMPT);
  
  // Parse JSON from response (handle markdown code blocks, extra text)
  let parsed;
  try {
    let jsonStr = raw.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    // Try to extract JSON object if surrounded by text
    const jsonMatch = jsonStr.match(/\{[\s\S]*\}/);
    if (jsonMatch) jsonStr = jsonMatch[0];
    parsed = JSON.parse(jsonStr);
  } catch (e) {
    // If critic can't produce valid JSON, assume output is fine
    return {
      scores: Object.fromEntries(SCORE_DIMENSIONS.map(d => [d, 7])),
      avgScore: 7,
      weakest: null,
      critique: 'Critic response was not valid JSON — skipping refinement.',
      verdict: 'pass',
      raw,
      parseError: true,
    };
  }
  
  // Validate and normalize
  const scores = {};
  for (const dim of SCORE_DIMENSIONS) {
    scores[dim] = Math.max(1, Math.min(10, Number(parsed.scores?.[dim]) || 5));
  }
  const avgScore = Object.values(scores).reduce((a, b) => a + b, 0) / SCORE_DIMENSIONS.length;
  const weakest = Object.entries(scores).sort((a, b) => a[1] - b[1])[0][0];
  
  return {
    scores,
    avgScore: Math.round(avgScore * 10) / 10,
    weakest,
    critique: parsed.critique || '',
    verdict: parsed.verdict || (avgScore < 7 ? 'refine' : 'pass'),
    raw,
  };
}

/**
 * Refine output based on critique
 * @param {Function} executeFn - async (instruction, input, systemPrompt) => string
 * @param {string} output - Current output
 * @param {object} critique - Critique result from criticize()
 * @param {string} task - Original task
 * @returns {string} Refined output
 */
async function refine(executeFn, output, critique, task) {
  const instruction = `Original task: "${task}"

Critic feedback (avg score: ${critique.avgScore}/10, weakest: ${critique.weakest}):
${critique.critique}

Dimension scores: ${JSON.stringify(critique.scores)}

Improve the output below. Focus especially on "${critique.weakest}" (scored ${critique.scores[critique.weakest]}/10).`;

  return await executeFn(instruction, output, REFINE_PROMPT);
}

/**
 * Full reflection loop: criticize → maybe refine → return result
 * @param {Function} executeFn - async (instruction, input, systemPrompt) => string
 * @param {string} output - Chain output to reflect on
 * @param {string} task - Original task description
 * @param {object} opts - { threshold, maxRefinements }
 * @returns {{ output, reflection: { originalScore, finalScore, refined, cycles, critiques } }}
 */
async function reflect(executeFn, output, task, opts = {}) {
  const threshold = opts.threshold ?? DEFAULTS.threshold;
  const maxCycles = opts.maxRefinements ?? DEFAULTS.maxRefinements;
  
  const critiques = [];
  let currentOutput = output;
  let refined = false;
  
  for (let cycle = 0; cycle <= maxCycles; cycle++) {
    const critique = await criticize(executeFn, currentOutput, task);
    critiques.push(critique);
    
    if (critique.verdict === 'pass' || critique.avgScore >= threshold || cycle === maxCycles) {
      break;
    }
    
    // Refine
    currentOutput = await refine(executeFn, currentOutput, critique, task);
    refined = true;
  }
  
  return {
    output: currentOutput,
    reflection: {
      originalScore: critiques[0]?.avgScore,
      finalScore: critiques[critiques.length - 1]?.avgScore,
      refined,
      cycles: critiques.length - (refined ? 0 : 0),
      critiques,
    },
  };
}

module.exports = {
  reflect,
  criticize,
  refine,
  DEFAULTS,
  SCORE_DIMENSIONS,
};
