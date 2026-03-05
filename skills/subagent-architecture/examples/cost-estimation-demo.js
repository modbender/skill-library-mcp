/**
 * Cost Estimation and Tracking Demo
 * 
 * Demonstrates how to use cost estimator for pre-spawn budgeting and accuracy tracking
 * Use case: Estimate subagent costs before spawning, log actuals, improve accuracy over time
 */

const {
  estimateSubagentCost,
  logSubagentCost,
  recalibrateEstimator,
  estimateWithHistory,
  getCostTier,
  getPatternHistory,
  MODEL_COSTS,
  COMPLEXITY_TOKENS
} = require('../lib/cost-estimator');

/**
 * Example 1: Basic cost estimation
 */
function basicEstimationExample() {
  console.log('=== Basic Cost Estimation Example ===\n');
  
  // Simple task
  const simple = estimateSubagentCost({
    task_complexity: 'simple',
    expected_duration_min: 5,
    model: 'haiku',
    research_required: false
  });
  
  console.log('Simple fact-checking task (haiku, 5min):');
  console.log(`  Expected: $${simple.expected.toFixed(3)}`);
  console.log(`  Range: $${simple.min.toFixed(3)} - $${simple.max.toFixed(3)}`);
  console.log(`  Confidence: ${(simple.confidence * 100).toFixed(0)}%`);
  console.log(`  Tier: ${getCostTier(simple.expected)}\n`);
  
  // Medium task
  const medium = estimateSubagentCost({
    task_complexity: 'medium',
    expected_duration_min: 15,
    model: 'sonnet',
    research_required: true
  });
  
  console.log('Research task (sonnet, 15min, web searches):');
  console.log(`  Expected: $${medium.expected.toFixed(3)}`);
  console.log(`  Range: $${medium.min.toFixed(3)} - $${medium.max.toFixed(3)}`);
  console.log(`  Confidence: ${(medium.confidence * 100).toFixed(0)}%`);
  console.log(`  Tier: ${getCostTier(medium.expected)}\n`);
  
  // High complexity task
  const high = estimateSubagentCost({
    task_complexity: 'high',
    expected_duration_min: 30,
    model: 'opus',
    research_required: false
  });
  
  console.log('Complex implementation (opus, 30min):');
  console.log(`  Expected: $${high.expected.toFixed(3)}`);
  console.log(`  Range: $${high.min.toFixed(3)} - $${high.max.toFixed(3)}`);
  console.log(`  Confidence: ${(high.confidence * 100).toFixed(0)}%`);
  console.log(`  Tier: ${getCostTier(high.expected)}\n`);
}

/**
 * Example 2: Pre-spawn cost gating
 */
function costGatingExample() {
  console.log('=== Cost Gating Example ===\n');
  
  const tasks = [
    { label: 'quick-lookup', complexity: 'simple', duration: 3, model: 'haiku' },
    { label: 'code-review', complexity: 'medium', duration: 12, model: 'sonnet' },
    { label: 'feature-implementation', complexity: 'high', duration: 45, model: 'opus', research: true }
  ];
  
  console.log('Evaluating tasks against budget gates:\n');
  
  tasks.forEach(task => {
    const estimate = estimateSubagentCost({
      task_complexity: task.complexity,
      expected_duration_min: task.duration,
      model: task.model,
      research_required: task.research || false
    });
    
    console.log(`Task: ${task.label}`);
    console.log(`  Estimate: $${estimate.expected.toFixed(3)} (max: $${estimate.max.toFixed(3)})`);
    
    // Apply gates
    if (estimate.expected < 0.10) {
      console.log(`  ✓ Auto-approved (micro tier)`);
    } else if (estimate.expected < 0.50) {
      console.log(`  ⚠️  Logged to cost tracking`);
    } else if (estimate.expected < 2.00) {
      console.log(`  ⚠️  Requires review (medium tier)`);
    } else {
      console.log(`  ✗ Requires human approval (large tier)`);
    }
    console.log('');
  });
}

/**
 * Example 3: Model selection optimization
 */
function modelSelectionExample() {
  console.log('=== Model Selection Optimization Example ===\n');
  
  const task = {
    complexity: 'medium',
    duration: 15,
    research: true
  };
  
  console.log('Same task, different models:\n');
  
  const models = ['haiku', 'sonnet', 'opus'];
  models.forEach(model => {
    const estimate = estimateSubagentCost({
      task_complexity: task.complexity,
      expected_duration_min: task.duration,
      model: model,
      research_required: task.research
    });
    
    const savings = model !== 'opus' 
      ? estimateSubagentCost({ ...task, model: 'opus', task_complexity: task.complexity, expected_duration_min: task.duration, research_required: task.research }).expected - estimate.expected
      : 0;
    
    console.log(`${model.toUpperCase()}:`);
    console.log(`  Cost: $${estimate.expected.toFixed(3)}`);
    if (savings > 0) {
      console.log(`  Savings vs opus: $${savings.toFixed(3)} (${((savings / estimate.expected) * 100).toFixed(0)}%)`);
    }
    console.log('');
  });
  
  console.log('Recommendation: Use haiku for simple tasks, sonnet for analysis, opus only for complex reasoning\n');
}

/**
 * Example 4: Cost logging and tracking
 */
function costLoggingExample() {
  console.log('=== Cost Logging Example ===\n');
  
  // Simulate a spawn with estimation
  const estimate = estimateSubagentCost({
    task_complexity: 'medium',
    expected_duration_min: 12,
    model: 'sonnet',
    research_required: true,
    pattern: 'researcher'
  });
  
  console.log('Pre-spawn estimate:');
  console.log(`  Expected: $${estimate.expected.toFixed(3)}`);
  console.log('');
  
  // Simulate execution
  console.log('Spawning subagent...');
  console.log('(simulation: actual cost varies from estimate)\n');
  
  const actual_cost = estimate.expected * (0.8 + Math.random() * 0.4);  // ±20% variance
  
  console.log('Post-execution logging:');
  console.log(`  Actual: $${actual_cost.toFixed(3)}`);
  console.log(`  Error: ${(((actual_cost - estimate.expected) / estimate.expected) * 100).toFixed(1)}%`);
  console.log('');
  
  // Log the result
  const record = logSubagentCost(
    'researcher-market-analysis',
    { 
      expected: estimate.expected, 
      min: estimate.min, 
      max: estimate.max,
      complexity: 'medium',
      model: 'sonnet'
    },
    actual_cost,
    {
      duration_min: 11,
      tokens_used: 38500,
      research_required: true
    }
  );
  
  console.log('✓ Logged to memory/subagent-costs.jsonl');
  console.log('  Pattern:', record.pattern);
  console.log('  Error:', (record.error * 100).toFixed(1) + '%');
  console.log('');
}

/**
 * Example 5: Accuracy improvement via recalibration
 */
function recalibrationExample() {
  console.log('=== Recalibration Example ===\n');
  
  // Simulate historical data by logging multiple spawns
  console.log('Simulating 10 historical spawns...\n');
  
  const patterns = ['researcher', 'coder', 'reviewer'];
  const complexities = ['simple', 'medium', 'high'];
  const models = ['haiku', 'sonnet'];
  
  for (let i = 0; i < 10; i++) {
    const pattern = patterns[Math.floor(Math.random() * patterns.length)];
    const complexity = complexities[Math.floor(Math.random() * complexities.length)];
    const model = models[Math.floor(Math.random() * models.length)];
    
    const estimate = estimateSubagentCost({
      task_complexity: complexity,
      expected_duration_min: 10 + Math.random() * 20,
      model: model,
      research_required: Math.random() > 0.5
    });
    
    // Simulate actual with bias (researcher tasks tend to cost more)
    const bias = pattern === 'researcher' ? 1.15 : 1.0;
    const actual = estimate.expected * bias * (0.8 + Math.random() * 0.4);
    
    logSubagentCost(
      `${pattern}-task-${i}`,
      { expected: estimate.expected, complexity, model },
      actual,
      { pattern, complexity, model }
    );
  }
  
  console.log('✓ 10 spawns logged\n');
  
  // Recalibrate
  console.log('Running recalibration...\n');
  const summary = recalibrateEstimator({ window_days: 30, min_samples: 2 });
  
  console.log('Recalibration results:');
  console.log(`  Groups updated: ${summary.groups_updated}`);
  console.log(`  Total records: ${summary.total_records}`);
  console.log('');
  
  if (summary.adjustments && Object.keys(summary.adjustments).length > 0) {
    console.log('Pattern adjustments:');
    Object.entries(summary.adjustments).forEach(([key, adj]) => {
      const direction = adj.mean_error > 0 ? 'over' : 'under';
      console.log(`  ${key}:`);
      console.log(`    ${direction}estimated by ${Math.abs(adj.mean_error * 100).toFixed(1)}%`);
      console.log(`    confidence: ${(adj.confidence * 100).toFixed(0)}%`);
      console.log(`    samples: ${adj.sample_size}`);
    });
  }
  console.log('');
  
  // Show improved estimate
  console.log('Future estimates will use these adjustments automatically\n');
}

/**
 * Example 6: Pattern history analysis
 */
function patternHistoryExample() {
  console.log('=== Pattern History Analysis Example ===\n');
  
  const patterns = ['researcher', 'coder', 'reviewer'];
  
  console.log('Historical performance by pattern:\n');
  
  patterns.forEach(pattern => {
    const history = getPatternHistory(pattern, { window_days: 90 });
    
    if (history.total_spawns > 0) {
      console.log(`${pattern.toUpperCase()}:`);
      console.log(`  Total spawns: ${history.total_spawns}`);
      console.log(`  Avg cost: $${history.avg_cost.toFixed(3)}`);
      console.log(`  Cost accuracy: ${(history.cost_accuracy * 100).toFixed(1)}% error`);
      
      if (Math.abs(history.cost_accuracy) > 0.2) {
        console.log(`  ⚠️  High estimation error - consider recalibration`);
      }
    } else {
      console.log(`${pattern.toUpperCase()}: No historical data`);
    }
    console.log('');
  });
}

/**
 * Example 7: Real-world workflow
 */
function realWorldWorkflowExample() {
  console.log('=== Real-World Workflow Example ===\n');
  
  console.log('Scenario: Planning a research task\n');
  
  // Step 1: Estimate
  console.log('Step 1: Pre-spawn estimation');
  const estimate = estimateSubagentCost({
    task_complexity: 'medium',
    expected_duration_min: 18,
    model: 'sonnet',
    research_required: true,
    pattern: 'researcher'
  });
  
  console.log(`  Estimated cost: $${estimate.expected.toFixed(3)}`);
  console.log(`  Tier: ${getCostTier(estimate.expected)}`);
  console.log('');
  
  // Step 2: Check budget gate
  console.log('Step 2: Budget gate check');
  if (estimate.max > 0.50) {
    console.log('  ⚠️  Exceeds auto-approval threshold');
    console.log('  → Logging to cost tracking (required for >$0.50)');
  } else {
    console.log('  ✓ Within auto-approval limit');
  }
  console.log('');
  
  // Step 3: Check pattern history
  console.log('Step 3: Pattern history check');
  const history = getPatternHistory('researcher');
  if (history.total_spawns > 0 && Math.abs(history.cost_accuracy) > 0.3) {
    console.log(`  ⚠️  Warning: researcher pattern has ${Math.abs(history.cost_accuracy * 100).toFixed(0)}% avg error`);
    console.log(`  → Adjusting estimate by ${(history.cost_accuracy * 100).toFixed(0)}%`);
    const adjusted = estimate.expected * (1 + history.cost_accuracy);
    console.log(`  → New estimate: $${adjusted.toFixed(3)}`);
  } else {
    console.log('  ✓ Pattern has acceptable accuracy');
  }
  console.log('');
  
  // Step 4: Spawn decision
  console.log('Step 4: Spawn decision');
  console.log('  ✓ Approved for spawn');
  console.log('  → Spawning researcher subagent...');
  console.log('');
  
  // Step 5: Post-execution logging
  console.log('Step 5: Post-execution logging');
  const actual = 0.62;
  console.log(`  Actual cost: $${actual.toFixed(3)}`);
  console.log(`  vs estimate: $${estimate.expected.toFixed(3)}`);
  console.log(`  Error: ${(((actual - estimate.expected) / estimate.expected) * 100).toFixed(1)}%`);
  
  logSubagentCost('researcher-workflow-demo', estimate, actual, {
    duration_min: 16,
    pattern: 'researcher',
    model: 'sonnet',
    complexity: 'medium'
  });
  
  console.log('  ✓ Logged for future calibration');
  console.log('');
}

/**
 * Example 8: Cost tiers and gates
 */
function costTiersExample() {
  console.log('=== Cost Tiers & Gates Example ===\n');
  
  const costs = [0.05, 0.25, 1.20, 3.50];
  
  console.log('Cost tier classification:\n');
  
  costs.forEach(cost => {
    const tier = getCostTier(cost);
    const gate = cost < 0.10 ? 'Auto-approve' :
                 cost < 0.50 ? 'Log required' :
                 cost < 2.00 ? 'Review recommended' :
                 'Human approval required';
    
    console.log(`$${cost.toFixed(2)}`);
    console.log(`  Tier: ${tier}`);
    console.log(`  Gate: ${gate}`);
    console.log('');
  });
  
  console.log('Cost tier definitions:');
  console.log('  • Micro (<$0.10): Simple lookups, fact-checking');
  console.log('  • Small ($0.10-0.50): Research, code review');
  console.log('  • Medium ($0.50-2.00): Feature implementation');
  console.log('  • Large (>$2.00): Complex refactors, multi-phase\n');
}

/**
 * Display current model costs
 */
function displayModelCosts() {
  console.log('=== Current Model Costs (per 1M tokens) ===\n');
  
  Object.entries(MODEL_COSTS).forEach(([model, costs]) => {
    console.log(`${model.toUpperCase()}:`);
    console.log(`  Input:  $${costs.input.toFixed(2)}`);
    console.log(`  Output: $${costs.output.toFixed(2)}`);
    console.log('');
  });
  
  console.log('Complexity token estimates:');
  Object.entries(COMPLEXITY_TOKENS).forEach(([complexity, tokens]) => {
    console.log(`  ${complexity}: ${tokens.toLocaleString()} tokens`);
  });
  console.log('');
}

// Run examples
function main() {
  console.log('╔════════════════════════════════════════════════╗');
  console.log('║   Cost Estimation & Tracking Demo             ║');
  console.log('╚════════════════════════════════════════════════╝\n');
  
  displayModelCosts();
  basicEstimationExample();
  costGatingExample();
  modelSelectionExample();
  costLoggingExample();
  recalibrationExample();
  patternHistoryExample();
  costTiersExample();
  realWorldWorkflowExample();
  
  console.log('═══════════════════════════════════════════════════');
  console.log('All examples completed!');
  console.log('\nKey takeaways:');
  console.log('1. Always estimate before spawning');
  console.log('2. Log actuals for continuous improvement');
  console.log('3. Recalibrate monthly for better accuracy');
  console.log('4. Use cheapest model that works (haiku > sonnet > opus)');
  console.log('5. Enforce cost gates (>$0.50 requires logging, >$2 requires approval)');
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  basicEstimationExample,
  costGatingExample,
  modelSelectionExample,
  costLoggingExample,
  recalibrationExample,
  patternHistoryExample,
  realWorldWorkflowExample
};
