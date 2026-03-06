/**
 * Swarm Benchmark — Quality & Cost Comparison
 * 
 * Runs the SAME task through three execution modes:
 *   1. Single (one worker, one pass)
 *   2. Parallel (multiple workers, one pass, merged)
 *   3. Chain (multi-stage refinement pipeline)
 * 
 * Then uses LLM-as-Judge to score each output on standardized dimensions.
 * Based on G-Eval / FLASK methodologies adapted for practical use.
 * 
 * Usage:
 *   POST /benchmark { task, data, depth }
 *   swarm benchmark --task "..." --data "..." --depth standard
 */

const { GeminiClient } = require('./gemini-client');
const { securePrompt } = require('./security');

/**
 * Scoring dimensions — based on FLASK evaluation framework
 * Each dimension scored 1-5 with specific rubric criteria
 */
const SCORING_DIMENSIONS = {
  accuracy: {
    name: 'Factual Accuracy',
    description: 'Are claims supported by the input data? No hallucinations or fabrications.',
    rubric: {
      1: 'Multiple factual errors or hallucinations',
      2: 'Some inaccuracies or unsupported claims',
      3: 'Mostly accurate with minor issues',
      4: 'Accurate with well-supported claims',
      5: 'Flawless accuracy, every claim traceable to input',
    },
  },
  depth: {
    name: 'Analytical Depth',
    description: 'Does the analysis go beyond surface observations? Are insights non-obvious?',
    rubric: {
      1: 'Surface-level, states the obvious',
      2: 'Some analysis but mostly restating input',
      3: 'Decent analysis with some original insights',
      4: 'Deep analysis revealing non-obvious patterns',
      5: 'Exceptional depth, reveals hidden connections and implications',
    },
  },
  completeness: {
    name: 'Completeness',
    description: 'Are all aspects of the task addressed? Any significant gaps?',
    rubric: {
      1: 'Major gaps, most of the task unaddressed',
      2: 'Partial coverage, significant aspects missing',
      3: 'Adequate coverage of main points',
      4: 'Thorough coverage with minor gaps',
      5: 'Exhaustive, addresses every aspect including edge cases',
    },
  },
  coherence: {
    name: 'Coherence & Structure',
    description: 'Is the output well-organized? Does it flow logically? Is it internally consistent?',
    rubric: {
      1: 'Disorganized, contradictory, hard to follow',
      2: 'Loosely organized with some contradictions',
      3: 'Adequate structure, mostly consistent',
      4: 'Well-organized, logical flow, consistent',
      5: 'Exemplary structure, perfect logical flow, fully consistent',
    },
  },
  actionability: {
    name: 'Actionability',
    description: 'Can someone act on this output? Are recommendations specific and practical?',
    rubric: {
      1: 'Vague, no clear next steps',
      2: 'Some suggestions but too generic',
      3: 'Reasonable recommendations, somewhat actionable',
      4: 'Specific, practical recommendations with clear next steps',
      5: 'Immediately actionable with prioritized steps and contingencies',
    },
  },
  nuance: {
    name: 'Nuance & Critical Thinking',
    description: 'Does it acknowledge tradeoffs, risks, and limitations? Does it avoid oversimplification?',
    rubric: {
      1: 'Black-and-white thinking, no tradeoffs acknowledged',
      2: 'Minimal acknowledgment of complexity',
      3: 'Some tradeoffs noted but not deeply explored',
      4: 'Good balance of perspectives with thoughtful tradeoffs',
      5: 'Exceptional nuance, acknowledges uncertainty and presents balanced multi-faceted analysis',
    },
  },
};

/**
 * Build the judge prompt for scoring an output
 */
function buildJudgePrompt(task, data, output, mode) {
  const dimensionText = Object.entries(SCORING_DIMENSIONS)
    .map(([key, dim]) => {
      const rubricText = Object.entries(dim.rubric)
        .map(([score, desc]) => `    ${score}: ${desc}`)
        .join('\n');
      return `  ${key} (${dim.name}): ${dim.description}\n${rubricText}`;
    })
    .join('\n\n');

  return `You are an expert evaluator scoring the quality of an AI-generated analysis.

TASK: ${task}

INPUT DATA:
${data}

OUTPUT TO EVALUATE (generated via "${mode}" execution mode):
---
${output}
---

Score this output on each dimension using the rubric below. Be strict and consistent.
For each dimension, provide the score (1-5) and a brief justification (one sentence).

SCORING DIMENSIONS:
${dimensionText}

Respond in EXACTLY this JSON format (no markdown, no code blocks, just raw JSON):
{
  "scores": {
    "accuracy": { "score": N, "reason": "..." },
    "depth": { "score": N, "reason": "..." },
    "completeness": { "score": N, "reason": "..." },
    "coherence": { "score": N, "reason": "..." },
    "actionability": { "score": N, "reason": "..." },
    "nuance": { "score": N, "reason": "..." }
  },
  "overall": N,
  "summary": "One sentence overall assessment"
}

The "overall" score should be the weighted average: accuracy(2x) + depth(1.5x) + completeness(1x) + coherence(1x) + actionability(1.5x) + nuance(1x). Divide by 8 and round to 1 decimal.`;
}

/**
 * Parse judge response into structured scores
 */
function parseJudgeResponse(response) {
  try {
    // Try direct JSON parse
    let cleaned = response.trim();
    // Strip markdown code blocks if present
    cleaned = cleaned.replace(/^```json?\n?/, '').replace(/\n?```$/, '');
    return JSON.parse(cleaned);
  } catch (e) {
    // Try to extract JSON from response
    const jsonMatch = response.match(/\{[\s\S]*"scores"[\s\S]*\}/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[0]);
      } catch {}
    }
    return { error: 'Failed to parse judge response', raw: response.substring(0, 500) };
  }
}

/**
 * Run a single-mode execution
 */
async function runSingle(client, task, data) {
  const start = Date.now();
  const result = await client.complete(
    `${task}\n\nData:\n${data}\n\nProvide a thorough analysis.`,
    {}
  );
  const duration = Date.now() - start;
  const stats = client.getStats();
  return {
    mode: 'single',
    output: result,
    durationMs: duration,
    tokens: { ...stats.tokens },
    cost: { ...stats.cost },
  };
}

/**
 * Run the full benchmark: single vs parallel vs chain
 * Returns comparative results with quality scores
 */
async function runBenchmark(opts, dispatcher, chainAutoFn) {
  const { task, data, depth = 'standard' } = opts;
  const results = {};
  
  // --- Mode 1: SINGLE (one worker, one pass) ---
  const singleClient = new GeminiClient();
  const singleStart = Date.now();
  const singleResult = await singleClient.complete(
    `${task}\n\nData:\n${data}\n\nProvide a thorough, well-structured analysis.`,
    {}
  );
  const singleStats = singleClient.getStats();
  results.single = {
    mode: 'single',
    output: singleResult,
    durationMs: Date.now() - singleStart,
    tokens: { input: singleStats.tokens.input, output: singleStats.tokens.output },
    cost: parseFloat(singleStats.cost.totalCost || 0),
    taskCount: 1,
  };

  // --- Mode 2: PARALLEL (3 workers, different angles, merged) ---
  const parallelTasks = [
    { nodeType: 'analyze', instruction: `Analyze this data focusing on opportunities and strengths: ${task}`, input: data, label: 'Opportunities' },
    { nodeType: 'analyze', instruction: `Analyze this data focusing on risks and weaknesses: ${task}`, input: data, label: 'Risks' },
    { nodeType: 'analyze', instruction: `Analyze this data focusing on actionable recommendations: ${task}`, input: data, label: 'Actions' },
  ];
  
  const parallelStart = Date.now();
  const parallelResult = await dispatcher.executeParallel(parallelTasks);
  const parallelOutput = parallelResult.results
    .filter(r => r.success)
    .map(r => r.result?.response || '')
    .join('\n\n---\n\n');
  
  // Get cost from workers
  let parallelCost = 0;
  for (const node of dispatcher.nodes.values()) {
    const s = node.getStats();
    parallelCost += parseFloat(s.cost?.totalCost || 0);
  }
  
  results.parallel = {
    mode: 'parallel',
    output: parallelOutput,
    durationMs: Date.now() - parallelStart,
    tokens: { input: 0, output: 0 }, // aggregated in cost
    cost: parallelCost,
    taskCount: 3,
  };

  // --- Mode 3: CHAIN (auto-built pipeline) ---
  const chainDef = chainAutoFn({ task, data, depth });
  const { buildChainPhases } = require('./chain');
  const phases = buildChainPhases(chainDef);
  
  // Reset node stats for clean measurement
  const preChainCost = parallelCost;
  
  const chainStart = Date.now();
  const chainResult = await dispatcher.orchestrate(phases, { description: 'benchmark-chain' });
  
  // Get chain-specific cost (delta from parallel)
  let totalCostNow = 0;
  for (const node of dispatcher.nodes.values()) {
    const s = node.getStats();
    totalCostNow += parseFloat(s.cost?.totalCost || 0);
  }
  const chainCost = totalCostNow - preChainCost;
  
  const lastPhase = chainResult.phases[chainResult.phases.length - 1];
  const chainOutput = lastPhase?.results
    .filter(r => r.success)
    .map(r => r.result?.response || '')
    .join('\n\n') || '';
  
  const chainTaskCount = chainResult.phases.reduce((sum, p) => sum + (p.results?.length || 0), 0);
  
  results.chain = {
    mode: `chain (${depth})`,
    output: chainOutput,
    durationMs: Date.now() - chainStart,
    cost: chainCost,
    taskCount: chainTaskCount,
    stages: chainResult.phases.map(p => ({
      name: p.phase,
      durationMs: p.totalDurationMs,
      tasks: p.results?.length || 0,
    })),
  };

  // --- JUDGE: Score each output ---
  const judgeClient = new GeminiClient();
  const scores = {};
  
  for (const [mode, result] of Object.entries(results)) {
    const judgePrompt = buildJudgePrompt(task, data, result.output, mode);
    const judgeResponse = await judgeClient.complete(judgePrompt, {});
    scores[mode] = parseJudgeResponse(judgeResponse);
  }

  // Add judge cost
  const judgeStats = judgeClient.getStats();
  const judgeCost = parseFloat(judgeStats.cost?.totalCost || 0);

  return {
    task,
    depth,
    results: Object.entries(results).map(([mode, r]) => ({
      mode: r.mode,
      durationMs: r.durationMs,
      taskCount: r.taskCount,
      cost: r.cost,
      outputLength: r.output.length,
      scores: scores[mode],
      stages: r.stages,
    })),
    judgeCost,
    totalBenchmarkCost: Object.values(results).reduce((sum, r) => sum + (r.cost || 0), 0) + judgeCost,
    comparison: buildComparison(results, scores),
  };
}

/**
 * Build human-readable comparison table
 */
function buildComparison(results, scores) {
  const modes = Object.keys(results);
  const dimensions = Object.keys(SCORING_DIMENSIONS);
  
  const table = {
    headers: ['Metric', ...modes.map(m => results[m].mode)],
    rows: [],
  };
  
  // Score rows
  for (const dim of dimensions) {
    const row = [SCORING_DIMENSIONS[dim].name];
    for (const mode of modes) {
      const s = scores[mode]?.scores?.[dim];
      row.push(s ? `${s.score}/5` : 'N/A');
    }
    table.rows.push(row);
  }
  
  // Overall
  table.rows.push(['OVERALL', ...modes.map(m => {
    const o = scores[m]?.overall;
    return o ? `${o}/5` : 'N/A';
  })]);
  
  // Performance rows
  table.rows.push(['Duration', ...modes.map(m => `${results[m].durationMs}ms`)]);
  table.rows.push(['Tasks', ...modes.map(m => `${results[m].taskCount}`)]);
  table.rows.push(['Cost', ...modes.map(m => `$${(results[m].cost || 0).toFixed(4)}`)]);
  table.rows.push(['Output length', ...modes.map(m => `${results[m].output.length} chars`)]);
  
  // Value ratio: quality per dollar
  table.rows.push(['Quality/$', ...modes.map(m => {
    const quality = scores[m]?.overall || 0;
    const cost = results[m].cost || 0.0001;
    return `${(quality / cost).toFixed(0)}/dollar`;
  })]);
  
  return table;
}

/**
 * Format comparison as text table
 */
function formatComparisonTable(comparison) {
  if (!comparison?.rows) return 'No comparison data';
  
  // Calculate column widths
  const allRows = [comparison.headers, ...comparison.rows];
  const widths = comparison.headers.map((_, i) => 
    Math.max(...allRows.map(r => String(r[i] || '').length))
  );
  
  const sep = widths.map(w => '─'.repeat(w + 2)).join('┼');
  const formatRow = (row) => row.map((cell, i) => 
    ` ${String(cell || '').padEnd(widths[i])} `
  ).join('│');
  
  let output = '';
  output += formatRow(comparison.headers) + '\n';
  output += sep + '\n';
  for (const row of comparison.rows) {
    output += formatRow(row) + '\n';
  }
  
  return output;
}

module.exports = {
  runBenchmark,
  buildJudgePrompt,
  parseJudgeResponse,
  buildComparison,
  formatComparisonTable,
  SCORING_DIMENSIONS,
};
