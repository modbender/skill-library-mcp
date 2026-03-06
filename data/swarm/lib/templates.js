/**
 * Chain Templates — Pre-built pipelines for common analysis patterns
 * 
 * Usage:
 *   POST /chain/template { template: "swot", data: "..." }
 *   
 *   const { getTemplate, TEMPLATES } = require('./templates');
 *   const chain = getTemplate('swot', { data: '...' });
 */

const TEMPLATES = {
  swot: {
    name: 'SWOT Analysis',
    description: 'Strengths, Weaknesses, Opportunities, Threats',
    stages: [
      { name: 'Extract', mode: 'single', perspective: 'extractor',
        prompt: 'Extract all relevant facts, metrics, and signals from the data.' },
      { name: 'SWOT Perspectives', mode: 'fan-out',
        perspectives: ['analyst', 'challenger', 'strategist'],
        prompt: 'Analyze from your perspective. Identify Strengths, Weaknesses, Opportunities, and Threats. Be specific with evidence.' },
      { name: 'Synthesize', mode: 'reduce', perspective: 'synthesizer',
        prompt: 'Combine into a single SWOT matrix. Format: ## Strengths, ## Weaknesses, ## Opportunities, ## Threats. Include 3-5 items per category ranked by impact.' },
    ],
  },

  competitor: {
    name: 'Competitor Analysis',
    description: 'Multi-competitor comparison with strategic recommendations',
    stages: [
      { name: 'Extract', mode: 'single', perspective: 'extractor',
        prompt: 'Extract all competitor data: pricing, features, market position, strengths, weaknesses.' },
      { name: 'Analyze', mode: 'fan-out',
        perspectives: ['analyst', 'strategist', 'critic'],
        prompt: 'Compare the competitors. Who wins on what? Where are the gaps? What would you build differently?' },
      { name: 'Synthesize', mode: 'reduce', perspective: 'synthesizer',
        prompt: 'Create a competitor comparison matrix, then recommend the top 3 strategic moves. Be specific and opinionated.' },
    ],
  },

  'market-entry': {
    name: 'Market Entry Analysis',
    description: 'Assess viability of entering a new market',
    stages: [
      { name: 'Extract', mode: 'single', perspective: 'extractor',
        prompt: 'Extract market data: size, growth, players, barriers, trends, customer segments.' },
      { name: 'Multi-Angle', mode: 'fan-out',
        perspectives: ['analyst', 'challenger', 'strategist'],
        prompt: 'Evaluate market entry viability. Consider: TAM/SAM/SOM, competition intensity, barriers to entry, timing, required investment.' },
      { name: 'Challenge', mode: 'single', perspective: 'challenger',
        prompt: 'What could go wrong? List the top 5 reasons this market entry could fail. Be specific.',
        inputTransform: 'merge' },
      { name: 'Decision', mode: 'reduce', perspective: 'synthesizer',
        prompt: 'Go/No-Go recommendation with confidence level (1-10). Include: recommended entry strategy, timeline, required resources, key risks and mitigations.' },
    ],
  },

  'content-pipeline': {
    name: 'Content Generation Pipeline',
    description: 'Research → Draft → Refine → Polish',
    stages: [
      { name: 'Research', mode: 'single', perspective: 'researcher',
        prompt: 'Research the topic. Extract key facts, angles, and interesting hooks. Include data points.',
        webSearch: true },
      { name: 'Draft', mode: 'single', perspective: 'analyst',
        prompt: 'Write a compelling first draft based on the research. Be engaging, use a clear structure, include data.',
        inputTransform: 'merge' },
      { name: 'Critique', mode: 'fan-out',
        perspectives: ['critic', 'optimizer'],
        prompt: 'Review the draft. Critic: what\'s weak, inaccurate, or boring? Optimizer: what would make this 10x better?' },
      { name: 'Polish', mode: 'reduce', perspective: 'optimizer',
        prompt: 'Produce the final version incorporating the feedback. Make it tight, engaging, and authoritative.' },
    ],
  },

  'due-diligence': {
    name: 'Due Diligence',
    description: 'Comprehensive evaluation for investment or partnership decisions',
    stages: [
      { name: 'Extract', mode: 'single', perspective: 'extractor',
        prompt: 'Extract all factual claims, metrics, financials, team info, and competitive positioning.' },
      { name: 'Verify', mode: 'fan-out',
        perspectives: ['analyst', 'challenger', 'researcher'],
        prompt: 'Evaluate the claims. Analyst: do the numbers add up? Challenger: what\'s being hidden or overstated? Researcher: how does this compare to industry benchmarks?' },
      { name: 'Risk Assessment', mode: 'single', perspective: 'challenger',
        prompt: 'Compile a risk register. Rate each risk (High/Medium/Low) for likelihood and impact. What are the deal-breakers?',
        inputTransform: 'merge' },
      { name: 'Verdict', mode: 'reduce', perspective: 'synthesizer',
        prompt: 'Investment/partnership recommendation: Proceed / Proceed with conditions / Pass. Include: top 3 strengths, top 3 risks, key conditions, and confidence score (1-10).' },
    ],
  },

  brainstorm: {
    name: 'Brainstorm',
    description: 'Divergent idea generation followed by convergent selection',
    stages: [
      { name: 'Generate', mode: 'fan-out',
        perspectives: ['strategist', 'researcher', 'optimizer', 'challenger'],
        prompt: 'Generate 5 creative ideas or solutions. Think outside the box. No filtering — quantity over quality.' },
      { name: 'Evaluate', mode: 'single', perspective: 'critic',
        prompt: 'Review all ideas. Score each 1-10 on: feasibility, impact, novelty. Remove duplicates. Rank by total score.',
        inputTransform: 'merge' },
      { name: 'Refine', mode: 'reduce', perspective: 'strategist',
        prompt: 'Take the top 3 ideas. For each: flesh out the concept, identify first steps, estimate effort, and name the biggest risk.' },
    ],
  },

  summarize: {
    name: 'Multi-Perspective Summary',
    description: 'Summarize with validation — no single perspective bias',
    stages: [
      { name: 'Perspectives', mode: 'fan-out',
        perspectives: ['analyst', 'challenger'],
        prompt: 'Summarize the key points. What matters most? What\'s being overlooked?' },
      { name: 'Merge', mode: 'reduce', perspective: 'synthesizer',
        prompt: 'Create a single definitive summary that captures both perspectives. Be concise — aim for 200 words or less.' },
    ],
  },
};

/**
 * Get a template chain definition, injecting user data
 */
function getTemplate(name, opts = {}) {
  const template = TEMPLATES[name];
  if (!template) {
    const available = Object.entries(TEMPLATES)
      .map(([k, v]) => `  ${k}: ${v.description}`)
      .join('\n');
    throw new Error(`Unknown template "${name}". Available:\n${available}`);
  }
  
  return {
    name: template.name,
    input: opts.data || opts.input || '',
    _meta: {
      template: name,
      description: template.description,
    },
    stages: template.stages.map(stage => {
      // Inject task context into prompts if provided
      const taskCtx = opts.task ? ` Context: ${opts.task}` : '';
      return {
        ...stage,
        prompt: stage.prompt + taskCtx,
      };
    }),
  };
}

/**
 * List available templates with descriptions
 */
function listTemplates() {
  return Object.entries(TEMPLATES).map(([key, t]) => ({
    key,
    name: t.name,
    description: t.description,
    stages: t.stages.length,
    modes: t.stages.map(s => s.mode),
  }));
}

module.exports = { TEMPLATES, getTemplate, listTemplates };
