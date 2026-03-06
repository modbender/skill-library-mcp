/**
 * Chain — Refinement Pipeline for Swarm
 * 
 * Optional execution mode that runs data through multiple stages,
 * each with different perspectives/filters. The orchestrator (LLM)
 * decides when to use chains vs simple parallel vs single calls.
 * 
 * Execution modes per stage:
 *   - "parallel": N workers process N inputs simultaneously  
 *   - "single":   One worker processes merged input
 *   - "fan-out":  One input → N workers with different perspectives
 *   - "reduce":   N inputs → one synthesized output
 * 
 * Example chain:
 *   { stages: [
 *     { name: "Extract", mode: "parallel", perspective: "data extractor", prompts: [...] },
 *     { name: "Filter",  mode: "single",   perspective: "relevance filter", transform: mergeAll },
 *     { name: "Enrich",  mode: "parallel",  perspective: "market analyst", webSearch: true },
 *     { name: "Challenge", mode: "fan-out", perspectives: ["optimist", "pessimist", "pragmatist"] },
 *     { name: "Synthesize", mode: "reduce", perspective: "strategic advisor" },
 *   ]}
 */

const { securePrompt } = require('./security');

/**
 * Built-in perspectives — reusable system prompts for common chain roles
 */
const PERSPECTIVES = {
  'extractor': 'You extract raw data, facts, and signals from text. No interpretation — just clean extraction. Be exhaustive.',
  'filter': 'You filter for relevance and quality. Remove noise, duplicates, and low-signal items. Score remaining items by importance. Be ruthless.',
  'enricher': 'You add context, market data, and connections to raw facts. Cross-reference with your knowledge. Add depth without adding noise.',
  'analyst': 'You analyze patterns, trends, and implications. Find what others miss. Be specific with numbers and evidence.',
  'synthesizer': 'You combine multiple analyses into a coherent narrative. Resolve contradictions. Highlight consensus and disagreements. Be concise.',
  'challenger': 'You are a devil\'s advocate. Poke holes in every argument. Find blind spots, risks, and assumptions. Be constructive but skeptical.',
  'optimizer': 'You refine and improve output quality. Fix inconsistencies, sharpen language, add missing context. Make it actionable.',
  'strategist': 'You think in terms of business strategy, competitive advantage, and ROI. Prioritize by impact. Be opinionated.',
  'researcher': 'You research thoroughly using available data. Cite sources. Focus on accuracy and completeness.',
  'critic': 'You evaluate quality and rigor. Rate confidence levels. Flag unsupported claims. Suggest what needs more evidence.',
};

/**
 * Build the system prompt for a stage, incorporating perspective
 */
function buildStagePrompt(stage) {
  let perspective = '';
  
  if (stage.perspective && PERSPECTIVES[stage.perspective]) {
    perspective = PERSPECTIVES[stage.perspective];
  } else if (stage.perspective) {
    // Custom perspective string
    perspective = stage.perspective;
  } else if (stage.systemPrompt) {
    perspective = stage.systemPrompt;
  } else {
    perspective = 'Process the input thoroughly and produce high-quality output.';
  }
  
  return securePrompt(perspective);
}

/**
 * Apply a transform function between stages.
 * Transforms reshape data from one stage's output to the next stage's input.
 */
const TRANSFORMS = {
  // Merge all parallel results into one string
  merge: (results) => results.filter(Boolean).join('\n\n---\n\n'),
  
  // Merge and deduplicate (line-level)
  mergeUnique: (results) => {
    const lines = results.filter(Boolean).flatMap(r => r.split('\n').map(l => l.trim()).filter(Boolean));
    return [...new Set(lines)].join('\n');
  },
  
  // Take only the best result (longest, as proxy for most thorough)
  best: (results) => results.filter(Boolean).sort((a, b) => b.length - a.length)[0] || '',
  
  // Split result into array of items (by double newline or --- separator)
  split: (results) => {
    const merged = results.filter(Boolean).join('\n\n');
    return merged.split(/\n\n---\n\n|\n\n\n/).filter(Boolean);
  },
  
  // Pass through as-is (array of results)
  passthrough: (results) => results,
  
  // JSON parse each result
  jsonParse: (results) => results.map(r => {
    try { return JSON.parse(r); } catch { return r; }
  }),
};

/**
 * Resolve a transform — can be a string name, function, or null (default: merge)
 */
function resolveTransform(transform) {
  if (!transform) return TRANSFORMS.merge;
  if (typeof transform === 'function') return transform;
  if (typeof transform === 'string' && TRANSFORMS[transform]) return TRANSFORMS[transform];
  throw new Error(`Unknown transform: ${transform}`);
}

/**
 * Build orchestration phases from a chain definition.
 * Returns phases compatible with dispatcher.orchestrate().
 */
function buildChainPhases(chainDef) {
  const stages = chainDef.stages;
  if (!stages || !stages.length) throw new Error('Chain requires at least one stage');
  
  const phases = [];
  
  for (let i = 0; i < stages.length; i++) {
    const stage = stages[i];
    const mode = stage.mode || 'single';
    const systemPrompt = buildStagePrompt(stage);
    const webSearch = stage.webSearch || false;
    
    phases.push({
      name: stage.name || `Stage ${i + 1}`,
      required: stage.required !== false,
      tasks: (prevPhases) => {
        // Get input for this stage
        let input;
        if (i === 0) {
          // First stage — use chain input or stage prompts directly
          input = chainDef.input || null;
        } else {
          // Transform previous stage's output
          const prevResults = prevPhases[i - 1].results
            .filter(r => r.success)
            .map(r => r.result?.response || (typeof r.result === 'string' ? r.result : JSON.stringify(r.result)));
          
          const transform = resolveTransform(stage.inputTransform || stages[i - 1]?.outputTransform);
          input = transform(prevResults);
          
          // Truncate to prevent context snowball
          const maxChars = stage.maxInputChars || 4000;
          if (typeof input === 'string' && input.length > maxChars) {
            input = input.substring(0, maxChars) + '\n\n[... truncated for brevity]';
          }
        }
        
        // Build tasks based on mode
        switch (mode) {
          case 'parallel': {
            // N inputs → N workers (same perspective)
            const prompts = typeof stage.prompts === 'function' 
              ? stage.prompts(input, prevPhases) 
              : (stage.prompts || []);
            
            return prompts.map((prompt, idx) => ({
              nodeType: 'analyze',
              instruction: typeof prompt === 'string' ? prompt : prompt.instruction,
              input: typeof prompt === 'object' ? prompt.input : (Array.isArray(input) ? input[idx] : input),
              context: stage.context,
              webSearch,
              label: `${stage.name} [${idx + 1}/${prompts.length}]`,
              // Override system prompt with perspective
              _systemPrompt: systemPrompt,
            }));
          }
          
          case 'single': {
            // Merged input → 1 worker
            const prompt = typeof stage.prompt === 'function'
              ? stage.prompt(input, prevPhases)
              : (stage.prompt || stage.instruction || 'Process the following input.');
            
            return [{
              nodeType: 'analyze',
              instruction: prompt,
              input: typeof input === 'string' ? input : JSON.stringify(input),
              context: stage.context,
              webSearch,
              label: stage.name,
              _systemPrompt: systemPrompt,
            }];
          }
          
          case 'fan-out': {
            // 1 input → N workers with DIFFERENT perspectives
            const perspectives = stage.perspectives || [stage.perspective || 'analyst'];
            const prompt = typeof stage.prompt === 'function'
              ? stage.prompt(input, prevPhases)
              : (stage.prompt || 'Analyze the following from your unique perspective.');
            
            return perspectives.map((persp, idx) => ({
              nodeType: 'analyze',
              instruction: prompt,
              input: typeof input === 'string' ? input : JSON.stringify(input),
              context: `Your perspective: ${PERSPECTIVES[persp] || persp}`,
              webSearch,
              label: `${stage.name} [${persp}]`,
              _systemPrompt: securePrompt(PERSPECTIVES[persp] || persp),
            }));
          }
          
          case 'reduce': {
            // N inputs → 1 synthesized output
            const prompt = typeof stage.prompt === 'function'
              ? stage.prompt(input, prevPhases)
              : (stage.prompt || 'Synthesize the following analyses into a single coherent output.');
            
            const mergedInput = Array.isArray(input) ? input.join('\n\n---\n\n') : input;
            
            return [{
              nodeType: 'analyze',
              instruction: prompt,
              input: mergedInput,
              context: stage.context,
              webSearch,
              label: stage.name,
              _systemPrompt: systemPrompt,
            }];
          }
          
          default:
            throw new Error(`Unknown chain mode: ${mode}`);
        }
      },
    });
  }
  
  return phases;
}

/**
 * Validate a chain definition before execution
 */
function validateChain(chainDef) {
  const errors = [];
  
  if (!chainDef.stages || !Array.isArray(chainDef.stages)) {
    errors.push('Chain must have a "stages" array');
    return { valid: false, errors };
  }
  
  for (let i = 0; i < chainDef.stages.length; i++) {
    const stage = chainDef.stages[i];
    const validModes = ['parallel', 'single', 'fan-out', 'reduce'];
    
    if (stage.mode && !validModes.includes(stage.mode)) {
      errors.push(`Stage ${i} has invalid mode "${stage.mode}". Valid: ${validModes.join(', ')}`);
    }
    
    if (stage.mode === 'parallel' && !stage.prompts) {
      errors.push(`Stage ${i} (parallel) requires "prompts" array or function`);
    }
    
    if (stage.mode === 'fan-out' && !stage.perspectives && !stage.perspective) {
      errors.push(`Stage ${i} (fan-out) requires "perspectives" array or "perspective"`);
    }
    
    if (stage.inputTransform && typeof stage.inputTransform === 'string' && !TRANSFORMS[stage.inputTransform]) {
      errors.push(`Stage ${i} has unknown inputTransform "${stage.inputTransform}". Valid: ${Object.keys(TRANSFORMS).join(', ')}`);
    }
  }
  
  return { valid: errors.length === 0, errors };
}

module.exports = {
  buildChainPhases,
  validateChain,
  buildStagePrompt,
  resolveTransform,
  PERSPECTIVES,
  TRANSFORMS,
};
