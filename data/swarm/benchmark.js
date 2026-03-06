#!/usr/bin/env node
/**
 * Swarm Benchmark Suite
 * Tests speed, quality, and efficiency across different task types
 */

const { parallel } = require('./lib');
const { SwarmCoordinator } = require('./lib/swarm-coordinator');
const { globalLimiter } = require('./lib/rate-limiter');

const BENCHMARKS = {
  // Test 1: Simple parallel prompts
  parallel_simple: {
    name: 'Parallel Simple (3 prompts)',
    fn: async () => {
      return await parallel([
        'What is the capital of France?',
        'What is 15 * 17?',
        'Name three programming languages.',
      ], { quiet: true });
    },
    validate: (r) => r.stats.successful === 3,
  },

  // Test 2: Parallel with more prompts
  parallel_medium: {
    name: 'Parallel Medium (6 prompts)',
    fn: async () => {
      return await parallel([
        'Explain recursion in one sentence.',
        'What is the speed of light?',
        'Name the largest planet.',
        'Who wrote 1984?',
        'What is HTTP?',
        'Define machine learning.',
      ], { quiet: true });
    },
    validate: (r) => r.stats.successful >= 5,
  },

  // Test 3: Complex analysis prompts
  parallel_complex: {
    name: 'Parallel Complex (3 analysis prompts)',
    fn: async () => {
      return await parallel([
        'Compare REST and GraphQL APIs. List 3 pros and cons of each.',
        'Explain the CAP theorem and give a real-world example.',
        'What are the key differences between SQL and NoSQL databases?',
      ], { quiet: true });
    },
    validate: (r) => r.stats.successful === 3,
  },

  // Test 4: Fact extraction
  fact_extraction: {
    name: 'Fact Extraction',
    fn: async () => {
      const text = `
        Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei.
        The company raised $450 million in 2023 and is headquartered in San Francisco.
        Their flagship product is Claude, an AI assistant.
        Dario previously worked at OpenAI as VP of Research.
      `;
      return await parallel([
        `Extract all facts from this text as a JSON array of {fact, entity, category}:\n${text}`
      ], { quiet: true });
    },
    validate: (r) => r.stats.successful === 1 && r.results[0]?.includes('Anthropic'),
  },

  // Test 5: Summarization
  summarization: {
    name: 'Multi-doc Summarization',
    fn: async () => {
      const docs = [
        'AI safety research focuses on ensuring AI systems behave as intended and remain under human control.',
        'Large language models are trained on vast amounts of text data using transformer architectures.',
        'Prompt engineering involves crafting inputs to get optimal outputs from AI models.',
      ];
      return await parallel(
        docs.map(d => `Summarize in 10 words or less: ${d}`),
        { quiet: true }
      );
    },
    validate: (r) => r.stats.successful === 3,
  },

  // Test 6: Autonomous research (Supabase)
  autonomous_research: {
    name: 'Autonomous Research (2 subjects, 2 rounds)',
    fn: async () => {
      const swarm = new SwarmCoordinator({ maxRounds: 2, useSupabase: true });
      try {
        return await swarm.research('AI trends 2025', {
          subjects: ['OpenAI', 'Anthropic'],
        });
      } finally {
        swarm.shutdown();
      }
    },
    validate: (r) => r.stats.totalFindings >= 2 && r.synthesis?.length > 100,
  },
};

async function runBenchmark(name, benchmark) {
  const startRequests = globalLimiter.totalRequests;
  const startTime = Date.now();
  
  let result, error;
  try {
    result = await benchmark.fn();
  } catch (e) {
    error = e.message;
  }
  
  const duration = Date.now() - startTime;
  const requests = globalLimiter.totalRequests - startRequests;
  const passed = !error && benchmark.validate(result);
  
  return {
    name: benchmark.name,
    duration,
    requests,
    passed,
    error,
    result,
  };
}

async function main() {
  const args = process.argv.slice(2);
  const specificTest = args[0];
  
  console.log('🏋️ SWARM BENCHMARK SUITE');
  console.log('========================\n');
  
  const results = [];
  const testsToRun = specificTest 
    ? { [specificTest]: BENCHMARKS[specificTest] }
    : BENCHMARKS;
  
  if (specificTest && !BENCHMARKS[specificTest]) {
    console.log('Available tests:', Object.keys(BENCHMARKS).join(', '));
    process.exit(1);
  }
  
  for (const [key, benchmark] of Object.entries(testsToRun)) {
    process.stdout.write(`⏱️ ${benchmark.name}... `);
    
    const result = await runBenchmark(key, benchmark);
    results.push(result);
    
    if (result.passed) {
      console.log(`✅ ${result.duration}ms (${result.requests} API calls)`);
    } else {
      console.log(`❌ FAILED - ${result.error || 'validation failed'}`);
    }
    
    // Small delay between tests
    await new Promise(r => setTimeout(r, 500));
  }
  
  // Summary
  console.log('\n📊 BENCHMARK RESULTS');
  console.log('====================');
  console.log('');
  console.log('| Test | Duration | API Calls | Status |');
  console.log('|------|----------|-----------|--------|');
  
  let totalDuration = 0;
  let totalRequests = 0;
  let passedCount = 0;
  
  for (const r of results) {
    const status = r.passed ? '✅ Pass' : '❌ Fail';
    console.log(`| ${r.name.padEnd(40)} | ${(r.duration + 'ms').padStart(8)} | ${String(r.requests).padStart(9)} | ${status} |`);
    totalDuration += r.duration;
    totalRequests += r.requests;
    if (r.passed) passedCount++;
  }
  
  console.log('');
  console.log(`📈 Summary:`);
  console.log(`   Total time: ${totalDuration}ms`);
  console.log(`   Total API calls: ${totalRequests}`);
  console.log(`   Tests passed: ${passedCount}/${results.length}`);
  console.log(`   Avg time/test: ${Math.round(totalDuration / results.length)}ms`);
  console.log(`   Avg calls/test: ${(totalRequests / results.length).toFixed(1)}`);
  
  // Rate limiter status
  const limiterStats = globalLimiter.getStats();
  console.log(`\n🚦 Rate Limiter:`);
  console.log(`   Daily requests: ${limiterStats.dailyRequests}/${limiterStats.dailyLimit}`);
  console.log(`   Remaining: ${limiterStats.dailyRemaining}`);
  console.log(`   Throttled: ${limiterStats.throttledRequests} (${limiterStats.throttleRate})`);
  
  return results;
}

main().catch(console.error);
