/**
 * Smart Prompt Router
 * 
 * Analyzes prompt complexity and routes to the optimal model tier.
 * Simple prompts → Flash (cheap, fast). Complex prompts → Pro (better quality).
 * 
 * Complexity signals:
 * - Input length (tokens proxy)
 * - Task type (chain stages are inherently more complex)
 * - Instruction complexity (multi-step, analytical depth)
 * - Perspective (challenger/critic need more reasoning)
 */

const TIERS = {
  flash: {
    name: 'flash',
    model: 'gemini-2.0-flash',
    description: 'Fast and cheap — simple extraction, factual questions, formatting',
    costPer1M: { input: 0.075, output: 0.30 },
  },
  pro: {
    name: 'pro',
    model: 'gemini-2.5-flash',  // Better quality, still cheap
    description: 'Higher quality — complex analysis, multi-step reasoning, synthesis',
    costPer1M: { input: 0.15, output: 0.60 },
  },
};

/**
 * Complexity signals with weights
 */
const COMPLEXITY_SIGNALS = [
  // Input size — more context = harder to process well
  { name: 'input_length', weight: 1.5, fn: (ctx) => {
    const len = (ctx.input || '').length;
    if (len < 500) return 0;
    if (len < 2000) return 1;
    if (len < 5000) return 2;
    return 3;
  }},
  
  // Instruction complexity — multi-step or analytical
  { name: 'instruction_complexity', weight: 2, fn: (ctx) => {
    const inst = (ctx.instruction || '').toLowerCase();
    let score = 0;
    
    // Multi-step indicators
    if (/\b(then|after|next|finally|first.*then)\b/.test(inst)) score += 1;
    if (/\b(compare|contrast|evaluate|assess|weigh)\b/.test(inst)) score += 1;
    if (/\b(synthesize|reconcile|resolve|integrate)\b/.test(inst)) score += 2;
    if (/\b(strategy|strategic|recommend|advise)\b/.test(inst)) score += 1;
    if (/\b(why|how|implications|consequences)\b/.test(inst)) score += 1;
    if (/\b(critique|challenge|devil|blind.?spot|assumption)\b/.test(inst)) score += 2;
    
    return Math.min(score, 4);
  }},
  
  // Perspective complexity — some roles need more reasoning
  { name: 'perspective', weight: 1.5, fn: (ctx) => {
    const highComplexity = ['challenger', 'critic', 'strategist', 'synthesizer'];
    const medComplexity = ['analyst', 'optimizer', 'researcher'];
    
    if (highComplexity.includes(ctx.perspective)) return 3;
    if (medComplexity.includes(ctx.perspective)) return 1;
    return 0;
  }},
  
  // Chain stage position — later stages have more context and need more reasoning
  { name: 'stage_position', weight: 1, fn: (ctx) => {
    if (!ctx.stageIndex) return 0;
    if (ctx.stageIndex === 0) return 0;  // Extract = simple
    if (ctx.isLastStage) return 2;        // Synthesize = complex
    return 1;
  }},
  
  // Output expectations — if we need structured/precise output
  { name: 'output_precision', weight: 1, fn: (ctx) => {
    const inst = (ctx.instruction || '').toLowerCase();
    if (/\b(json|format|matrix|table|score.*1.*10|rank|rate)\b/.test(inst)) return 2;
    if (/\b(specific|precise|exact|detailed)\b/.test(inst)) return 1;
    return 0;
  }},
];

/**
 * Route a task to the optimal model tier
 * 
 * @param {object} ctx - Task context
 * @param {string} ctx.instruction - The task instruction
 * @param {string} ctx.input - The input data
 * @param {string} ctx.perspective - The perspective/role name
 * @param {number} ctx.stageIndex - Stage position in chain (0-based)
 * @param {boolean} ctx.isLastStage - Whether this is the final chain stage
 * @param {object} options
 * @param {number} options.threshold - Score threshold for Pro tier (default: 8)
 * @param {boolean} options.forceFlash - Always use Flash
 * @param {boolean} options.forcePro - Always use Pro
 * @returns {object} { tier, model, score, signals }
 */
function routePrompt(ctx, options = {}) {
  if (options.forceFlash) return { tier: 'flash', model: TIERS.flash.model, score: 0, forced: true };
  if (options.forcePro) return { tier: 'pro', model: TIERS.pro.model, score: 99, forced: true };
  
  const threshold = options.threshold ?? 8;
  const signals = {};
  let totalScore = 0;
  
  for (const signal of COMPLEXITY_SIGNALS) {
    const raw = signal.fn(ctx);
    const weighted = raw * signal.weight;
    signals[signal.name] = { raw, weighted };
    totalScore += weighted;
  }
  
  const tier = totalScore >= threshold ? 'pro' : 'flash';
  
  return {
    tier,
    model: TIERS[tier].model,
    score: Math.round(totalScore * 10) / 10,
    threshold,
    signals,
  };
}

/**
 * Analyze a batch of tasks and return routing decisions
 */
function routeBatch(tasks, options = {}) {
  const decisions = tasks.map((task, i) => {
    const ctx = {
      instruction: task.instruction || task.prompt || '',
      input: task.input || '',
      perspective: task._perspective || '',
      stageIndex: task._stageIndex,
      isLastStage: task._isLastStage,
    };
    return { taskIndex: i, ...routePrompt(ctx, options) };
  });
  
  const flashCount = decisions.filter(d => d.tier === 'flash').length;
  const proCount = decisions.filter(d => d.tier === 'pro').length;
  
  return {
    decisions,
    summary: {
      total: tasks.length,
      flash: flashCount,
      pro: proCount,
      avgScore: decisions.reduce((s, d) => s + d.score, 0) / decisions.length,
    },
  };
}

module.exports = { routePrompt, routeBatch, TIERS, COMPLEXITY_SIGNALS };
