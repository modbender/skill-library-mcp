/**
 * Chain Builder — Dynamic Pipeline Construction
 * 
 * Analyzes a task description and automatically constructs
 * the optimal chain definition. The orchestrator (LLM) describes
 * WHAT it wants, the builder figures out HOW to structure the pipeline.
 * 
 * Usage:
 *   // From daemon endpoint
 *   POST /chain/auto { task: "...", data: "...", depth: "standard" }
 * 
 *   // From code  
 *   const chain = buildAutoChain({ task, data, depth });
 *   const result = await dispatcher.orchestrate(buildChainPhases(chain));
 */

const { PERSPECTIVES } = require('./chain');

/**
 * Task analysis patterns — detect what kind of processing is needed
 */
const TASK_PATTERNS = [
  {
    name: 'comparative',
    match: /compare|vs\.?|versus|difference|better|worse|rank|which.*best/i,
    stages: ['extract', 'fan-out-compare', 'synthesize'],
    description: 'Comparing multiple options or entities',
  },
  {
    name: 'research-deep',
    match: /research|investigate|deep.?dive|thorough|comprehensive|everything about/i,
    stages: ['extract', 'enrich', 'fan-out-perspectives', 'synthesize'],
    description: 'Deep research requiring multiple passes',
  },
  {
    name: 'adversarial',
    match: /challenge|devil.?s?.?advocate|poke holes|risk|what could go wrong|critique|stress.?test/i,
    stages: ['extract', 'fan-out-perspectives', 'challenge', 'synthesize'],
    description: 'Analysis with adversarial review',
  },
  {
    name: 'filter-refine',
    match: /filter|refine|narrow|top \d+|best \d+|most important|prioritize|relevant/i,
    stages: ['extract', 'filter', 'fan-out-perspectives', 'synthesize'],
    description: 'Extract then progressively filter and refine',
  },
  {
    name: 'multi-perspective',
    match: /perspective|viewpoint|angle|different.*view|stakeholder|opinion/i,
    stages: ['extract', 'fan-out-perspectives', 'synthesize'],
    description: 'Same data analyzed from multiple viewpoints',
  },
  {
    name: 'opportunity',
    match: /opportunit|business|market|monetiz|revenue|profit|build|product/i,
    stages: ['extract', 'enrich', 'fan-out-strategy', 'synthesize'],
    description: 'Business opportunity analysis',
  },
  {
    name: 'summarize',
    match: /summarize|summary|tldr|brief|condense|digest|overview/i,
    stages: ['extract', 'synthesize'],
    description: 'Condensed summary',
  },
];

/**
 * Depth presets — control how many stages and how thorough
 */
const DEPTH_PRESETS = {
  quick: {
    maxStages: 2,
    fanOutCount: 2,
    description: 'Fast — 2 stages max, minimal perspectives',
  },
  standard: {
    maxStages: 4,
    fanOutCount: 3,
    description: 'Balanced — up to 4 stages, 3 perspectives on fan-out',
  },
  deep: {
    maxStages: 6,
    fanOutCount: 4,
    description: 'Thorough — up to 6 stages, 4 perspectives, extra refinement passes',
  },
  exhaustive: {
    maxStages: 8,
    fanOutCount: 5,
    description: 'Maximum depth — all stages, all perspectives, multiple refinement loops',
  },
};

/**
 * Stage templates — building blocks for chains
 */
const STAGE_TEMPLATES = {
  extract: (task, data) => ({
    name: 'Extract',
    mode: 'single',
    perspective: 'extractor',
    prompt: `Extract key data points and signals. One per line. Include numbers/metrics. Focus: ${task}`,
  }),

  filter: (task) => ({
    name: 'Filter & Score',
    mode: 'single',
    perspective: 'filter',
    prompt: `Remove noise and duplicates. Score items 1-10 for relevance to: ${task}. Output only 6+ as: [score] item`,
    inputTransform: 'merge',
  }),

  analyze: (task) => ({
    name: 'Analyze',
    mode: 'single',
    perspective: 'analyst',
    prompt: `Identify patterns, trends, and implications. What's surprising? What's missing? Be concise. Focus: ${task}`,
    inputTransform: 'merge',
  }),

  enrich: (task) => ({
    name: 'Enrich',
    mode: 'single',
    perspective: 'enricher',
    webSearch: true,
    prompt: `Add market context and competitor data. No fluff — only facts that change the analysis. Focus: ${task}`,
    inputTransform: 'merge',
  }),

  challenge: (task) => ({
    name: 'Challenge',
    mode: 'single',
    perspective: 'challenger',
    prompt: `Devil's advocate: blind spots, unsupported assumptions, ignored risks. Be specific. Context: ${task}`,
    inputTransform: 'merge',
  }),

  optimize: (task) => ({
    name: 'Optimize',
    mode: 'single',
    perspective: 'optimizer',
    prompt: `Sharpen conclusions, fix inconsistencies, make actionable. Context: ${task}`,
    inputTransform: 'merge',
  }),

  synthesize: (task) => ({
    name: 'Synthesize',
    mode: 'reduce',
    perspective: 'synthesizer',
    prompt: `Synthesize into one coherent output. Resolve contradictions. Key insights + actionable takeaways. Be concise. Context: ${task}`,
    inputTransform: 'merge',
  }),

  'fan-out-compare': (task) => ({
    name: 'Compare from Multiple Angles',
    mode: 'fan-out',
    perspectives: ['analyst', 'strategist', 'critic'],
    prompt: `Compare the items in this data. Evaluate strengths, weaknesses, and tradeoffs. Be specific. Context: ${task}`,
    inputTransform: 'merge',
  }),

  'fan-out-perspectives': (task) => ({
    name: 'Multi-Perspective Analysis',
    mode: 'fan-out',
    perspectives: ['analyst', 'challenger', 'strategist'],
    prompt: `Analyze this data from your unique perspective. What do you see that others might miss? Context: ${task}`,
    inputTransform: 'merge',
  }),

  'fan-out-strategy': (task) => ({
    name: 'Strategic Analysis',
    mode: 'fan-out',
    perspectives: ['analyst', 'strategist', 'challenger'],
    prompt: `Evaluate the business opportunities in this data. What should be built? Who pays? What's the moat? Context: ${task}`,
    inputTransform: 'merge',
  }),
};

/**
 * Detect task type from natural language description
 */
function detectTaskType(task) {
  for (const pattern of TASK_PATTERNS) {
    if (pattern.match.test(task)) {
      return pattern;
    }
  }
  // Default: general analysis — use fan-out for parallel perspectives
  return {
    name: 'general',
    stages: ['extract', 'fan-out-perspectives', 'synthesize'],
    description: 'General analysis',
  };
}

/**
 * Select perspectives for fan-out based on task context
 */
function selectPerspectives(task, count = 3) {
  const perspectiveScores = {};
  
  const keywords = {
    analyst: /data|pattern|trend|number|metric|stat/i,
    strategist: /business|market|revenue|growth|compete|position/i,
    challenger: /risk|wrong|fail|problem|issue|concern|challenge/i,
    optimizer: /improve|better|refine|optimize|efficient/i,
    researcher: /research|learn|discover|explore|investigate/i,
    critic: /quality|evaluate|assess|judge|rate|review/i,
    enricher: /context|detail|depth|background|history/i,
    synthesizer: /combine|merge|overall|summary|conclusion/i,
  };
  
  for (const [persp, regex] of Object.entries(keywords)) {
    perspectiveScores[persp] = regex.test(task) ? 2 : 1;
  }
  
  // Always include analyst and one contrarian voice
  perspectiveScores['analyst'] += 1;
  perspectiveScores['challenger'] += 0.5;
  
  return Object.entries(perspectiveScores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, count)
    .map(([name]) => name);
}

/**
 * Build a chain definition automatically from a task description
 * 
 * @param {object} opts
 * @param {string} opts.task - What to accomplish (natural language)
 * @param {string} [opts.data] - Input data to process
 * @param {string} [opts.depth='standard'] - Depth preset
 * @param {string[]} [opts.perspectives] - Override perspective selection
 * @param {string[]} [opts.stages] - Override stage selection
 * @returns {object} Chain definition ready for /chain endpoint
 */
function buildAutoChain(opts) {
  const { task, data, depth = 'standard', perspectives, stages: overrideStages } = opts;
  
  const depthConfig = DEPTH_PRESETS[depth] || DEPTH_PRESETS.standard;
  const taskType = detectTaskType(task);
  
  // Determine stages
  let stageNames = overrideStages || taskType.stages;
  
  // Trim to depth limit
  if (stageNames.length > depthConfig.maxStages) {
    // Always keep first (extract) and last (synthesize)
    const first = stageNames[0];
    const last = stageNames[stageNames.length - 1];
    const middle = stageNames.slice(1, -1).slice(0, depthConfig.maxStages - 2);
    stageNames = [first, ...middle, last];
  }
  
  // If deep/exhaustive, add extra refinement stages
  if (depth === 'deep' && !stageNames.includes('challenge')) {
    // Insert challenge before synthesize
    const synthIdx = stageNames.indexOf('synthesize');
    if (synthIdx > 0) stageNames.splice(synthIdx, 0, 'challenge');
  }
  if (depth === 'exhaustive') {
    if (!stageNames.includes('challenge')) {
      const synthIdx = stageNames.indexOf('synthesize');
      if (synthIdx > 0) stageNames.splice(synthIdx, 0, 'challenge');
    }
    if (!stageNames.includes('optimize')) {
      stageNames.push('optimize');
    }
  }
  
  // Build stage definitions
  const stages = stageNames.map(name => {
    const template = STAGE_TEMPLATES[name];
    if (!template) throw new Error(`Unknown stage template: ${name}`);
    
    const stage = template(task, data);
    
    // Override fan-out perspectives if specified
    if (stage.mode === 'fan-out') {
      const selectedPerspectives = perspectives || selectPerspectives(task, depthConfig.fanOutCount);
      stage.perspectives = selectedPerspectives;
    }
    
    return stage;
  });
  
  return {
    name: `Auto: ${taskType.description}`,
    input: data || undefined,
    _meta: {
      taskType: taskType.name,
      depth,
      detectedPattern: taskType.description,
      stageCount: stages.length,
      estimatedTasks: stages.reduce((sum, s) => {
        if (s.mode === 'fan-out') return sum + (s.perspectives?.length || 3);
        if (s.mode === 'parallel') return sum + 5; // estimate
        return sum + 1;
      }, 0),
    },
    stages,
  };
}

/**
 * Preview what a chain would look like without executing it
 */
function previewChain(opts) {
  const chain = buildAutoChain(opts);
  return {
    name: chain.name,
    meta: chain._meta,
    stages: chain.stages.map(s => ({
      name: s.name,
      mode: s.mode,
      perspective: s.perspective || s.perspectives?.join(', ') || 'default',
      webSearch: s.webSearch || false,
    })),
  };
}

module.exports = {
  buildAutoChain,
  previewChain,
  detectTaskType,
  selectPerspectives,
  TASK_PATTERNS,
  DEPTH_PRESETS,
  STAGE_TEMPLATES,
};
