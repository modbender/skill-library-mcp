/**
 * Tests for Procedure Evolution Module
 */

import { 
  analyzeFailure, 
  calculateReliability, 
  shouldAutoEvolve,
  evolveProcedure 
} from './evolution.js';
import { Procedure, ProcedureStep } from '../storage/index.js';

// Test data
const testProcedure: Procedure = {
  id: 'proc_test123',
  title: 'Deploy to Production',
  description: 'Deploy code to production environment',
  steps: [
    { id: 'step_1', order: 1, description: 'Run tests' },
    { id: 'step_2', order: 2, description: 'Build Docker image' },
    { id: 'step_3', order: 3, description: 'Push to registry' },
    { id: 'step_4', order: 4, description: 'Deploy to cluster' }
  ],
  version: 1,
  success_count: 3,
  failure_count: 2,
  is_reliable: false,
  evolution_log: [
    { version: 1, trigger: 'success_pattern', change: 'Initial success', timestamp: '2026-02-20T10:00:00Z' },
    { version: 1, trigger: 'failure', change: 'Failed at step 3: registry timeout', timestamp: '2026-02-21T14:00:00Z' },
    { version: 1, trigger: 'success_pattern', change: 'Success after retry', timestamp: '2026-02-22T09:00:00Z' },
    { version: 1, trigger: 'failure', change: 'Failed at step 4: cluster unreachable', timestamp: '2026-02-23T16:00:00Z' }
  ],
  created_at: '2026-02-20T08:00:00Z',
  updated_at: '2026-02-23T16:00:00Z'
};

interface TestResult {
  name: string;
  passed: boolean;
  message: string;
}

async function runTests(): Promise<void> {
  const results: TestResult[] = [];

  console.log('🧪 Procedure Evolution Tests\n');
  console.log('='.repeat(80));

  // Test 1: calculateReliability
  console.log('\n📋 Test 1: Reliability Calculation\n');
  const metrics = calculateReliability(testProcedure);
  
  const test1a = metrics.successRate === 3 / 5;
  results.push({
    name: 'Success rate calculation',
    passed: test1a,
    message: test1a ? `✅ Success rate: ${(metrics.successRate * 100).toFixed(0)}%` : `❌ Expected 60%, got ${metrics.successRate}`
  });

  const test1b = metrics.recentTrend === 'declining';
  results.push({
    name: 'Trend detection',
    passed: test1b,
    message: test1b ? `✅ Trend: ${metrics.recentTrend}` : `❌ Expected declining, got ${metrics.recentTrend}`
  });

  const test1c = metrics.reliability > 0 && metrics.reliability <= 1;
  results.push({
    name: 'Reliability score range',
    passed: test1c,
    message: test1c ? `✅ Reliability: ${metrics.reliability.toFixed(2)}` : `❌ Reliability out of range: ${metrics.reliability}`
  });

  const test1d = metrics.lastFailures.length === 2;
  results.push({
    name: 'Last failures extracted',
    passed: test1d,
    message: test1d ? `✅ Found ${metrics.lastFailures.length} failures` : `❌ Expected 2 failures, got ${metrics.lastFailures.length}`
  });

  // Test 2: shouldAutoEvolve
  console.log('\n📋 Test 2: Auto-Evolution Decision\n');
  const shouldEvolve = shouldAutoEvolve(testProcedure);
  
  const test2 = shouldEvolve === true;
  results.push({
    name: 'Auto-evolve decision',
    passed: test2,
    message: test2 
      ? `✅ Correctly identified procedure for auto-evolution` 
      : `❌ Should have recommended evolution (declining, 2 failures)`
  });

  // Test 3: analyzeFailure (LLM call - may fallback)
  console.log('\n📋 Test 3: Failure Analysis (LLM)\n');
  const analysis = await analyzeFailure(testProcedure, 4, 'cluster unreachable');
  
  const test3a = analysis.failedStep === 4;
  results.push({
    name: 'Failed step identified',
    passed: test3a,
    message: test3a ? `✅ Step ${analysis.failedStep}` : `❌ Expected step 4, got ${analysis.failedStep}`
  });

  const test3b = analysis.failureReason.length > 0;
  results.push({
    name: 'Failure reason provided',
    passed: test3b,
    message: test3b ? `✅ Reason: ${analysis.failureReason.slice(0, 50)}...` : `❌ No failure reason`
  });

  const test3c = analysis.newSteps.length > 0;
  results.push({
    name: 'New steps suggested',
    passed: test3c,
    message: test3c ? `✅ ${analysis.newSteps.length} new steps` : `❌ No new steps`
  });

  const test3d = analysis.confidence >= 0 && analysis.confidence <= 1;
  results.push({
    name: 'Confidence score valid',
    passed: test3d,
    message: test3d ? `✅ Confidence: ${(analysis.confidence * 100).toFixed(0)}%` : `❌ Invalid confidence: ${analysis.confidence}`
  });

  // Test 4: evolveProcedure
  console.log('\n📋 Test 4: Full Evolution\n');
  const evolution = await evolveProcedure(testProcedure, 4, 'cluster unreachable');
  
  const test4a = evolution.newSteps.length > 0;
  results.push({
    name: 'New steps generated',
    passed: test4a,
    message: test4a ? `✅ ${evolution.newSteps.length} steps in new version` : `❌ No steps generated`
  });

  const test4b = evolution.evolutionEvent.version === 2;
  results.push({
    name: 'Version incremented',
    passed: test4b,
    message: test4b ? `✅ Version ${evolution.evolutionEvent.version}` : `❌ Expected version 2, got ${evolution.evolutionEvent.version}`
  });

  const test4c = evolution.evolutionEvent.trigger === 'failure';
  results.push({
    name: 'Evolution trigger recorded',
    passed: test4c,
    message: test4c ? `✅ Trigger: ${evolution.evolutionEvent.trigger}` : `❌ Wrong trigger: ${evolution.evolutionEvent.trigger}`
  });

  // Test 5: Reliable procedure (should NOT auto-evolve)
  console.log('\n📋 Test 5: Stable Procedure Decision\n');
  const reliableProcedure: Procedure = {
    ...testProcedure,
    success_count: 10,
    failure_count: 1,
    is_reliable: true,
    evolution_log: [
      { version: 1, trigger: 'success_pattern', change: 'Success 1', timestamp: '2026-02-20T10:00:00Z' },
      { version: 1, trigger: 'success_pattern', change: 'Success 2', timestamp: '2026-02-21T10:00:00Z' },
      { version: 1, trigger: 'success_pattern', change: 'Success 3', timestamp: '2026-02-22T10:00:00Z' }
    ]
  };
  
  const reliableMetrics = calculateReliability(reliableProcedure);
  const shouldNotEvolve = shouldAutoEvolve(reliableProcedure);
  
  const test5a = reliableMetrics.recentTrend === 'improving';
  results.push({
    name: 'Reliable trend detection',
    passed: test5a,
    message: test5a ? `✅ Trend: improving` : `❌ Expected improving, got ${reliableMetrics.recentTrend}`
  });

  const test5b = shouldNotEvolve === false;
  results.push({
    name: 'Should NOT auto-evolve',
    passed: test5b,
    message: test5b ? `✅ Correctly skipped evolution` : `❌ Should not recommend evolution for stable procedure`
  });

  // Print results
  console.log('\n' + '='.repeat(80));
  console.log('\n📊 Test Results:\n');
  
  for (const result of results) {
    console.log(`${result.passed ? '✅' : '❌'} ${result.name}: ${result.message}`);
  }

  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  
  console.log(`\n${'='.repeat(80)}`);
  console.log(`\n📊 Results: ${passed}/${total} passed (${Math.round(passed / total * 100)}%)`);
  
  if (passed < total) {
    process.exit(1);
  }
}

runTests().catch(console.error);