#!/usr/bin/env node
/**
 * Deep Swarm Benchmark
 * Profiles bottlenecks and tests optimization opportunities
 */

const { parallel } = require('./lib');
const { SwarmCoordinator } = require('./lib/swarm-coordinator');
const { globalLimiter } = require('./lib/rate-limiter');
const { SupabaseBlackboard } = require('./lib/blackboard-supabase');
const { Blackboard } = require('./lib/blackboard');

async function timeIt(name, fn) {
  const start = Date.now();
  const result = await fn();
  const duration = Date.now() - start;
  return { name, duration, result };
}

async function runDeepBenchmark() {
  console.log('🔬 DEEP SWARM BENCHMARK');
  console.log('=======================\n');

  const results = [];

  // ========================================
  // 1. CONCURRENCY SCALING TEST
  // ========================================
  console.log('📊 Test 1: Concurrency Scaling');
  console.log('   How does speed scale with parallel prompts?\n');

  const concurrencyTests = [1, 2, 4, 6, 8, 10];
  const simplePrompt = 'What is 2+2? Answer with just the number.';

  for (const count of concurrencyTests) {
    const prompts = Array(count).fill(simplePrompt);
    const { duration } = await timeIt(`${count} parallel`, async () => {
      return await parallel(prompts, { quiet: true });
    });
    const perPrompt = Math.round(duration / count);
    console.log(`   ${count} prompts: ${duration}ms total, ${perPrompt}ms/prompt`);
    results.push({ test: 'concurrency', count, duration, perPrompt });
  }

  // ========================================
  // 2. PROMPT SIZE TEST
  // ========================================
  console.log('\n📊 Test 2: Prompt Size Impact');
  console.log('   How does prompt length affect latency?\n');

  const sizes = [
    { name: 'tiny', prompt: 'Say hi.' },
    { name: 'small', prompt: 'Explain what a variable is in programming in one sentence.' },
    { name: 'medium', prompt: 'Write a paragraph explaining how neural networks learn. Include details about backpropagation and gradient descent.' },
    { name: 'large', prompt: `Analyze this code and explain what it does, then suggest improvements:\n\n${'function fibonacci(n) { if (n <= 1) return n; return fibonacci(n-1) + fibonacci(n-2); }'.repeat(10)}` },
  ];

  for (const { name, prompt } of sizes) {
    const { duration } = await timeIt(name, async () => {
      return await parallel([prompt], { quiet: true });
    });
    console.log(`   ${name.padEnd(8)} (${prompt.length} chars): ${duration}ms`);
    results.push({ test: 'prompt_size', name, chars: prompt.length, duration });
  }

  // ========================================
  // 3. BLACKBOARD COMPARISON
  // ========================================
  console.log('\n📊 Test 3: Blackboard Backend Comparison');
  console.log('   File-based vs Supabase\n');

  // File-based blackboard
  const fileBoard = new Blackboard('bench-file-' + Date.now());
  const fileStart = Date.now();
  for (let i = 0; i < 20; i++) {
    fileBoard.postFinding(`worker-${i}`, `Finding ${i}: Lorem ipsum dolor sit amet`);
  }
  const fileCtx = fileBoard.getContext();
  const fileWrite = Date.now() - fileStart;
  console.log(`   File blackboard: ${fileWrite}ms for 20 writes + read`);

  // Supabase blackboard
  const supaBoard = new SupabaseBlackboard('bench-supa-' + Date.now());
  const supaStart = Date.now();
  for (let i = 0; i < 20; i++) {
    await supaBoard.postFinding(`worker-${i}`, `Finding ${i}: Lorem ipsum dolor sit amet`);
  }
  const supaCtx = await supaBoard.getContext();
  const supaWrite = Date.now() - supaStart;
  console.log(`   Supabase blackboard: ${supaWrite}ms for 20 writes + read`);
  console.log(`   Supabase overhead: ${supaWrite - fileWrite}ms (+${Math.round((supaWrite/fileWrite - 1) * 100)}%)`);

  results.push({ test: 'blackboard', file: fileWrite, supabase: supaWrite });

  // Cleanup Supabase test data (requires SUPABASE_URL and SUPABASE_SERVICE_KEY env vars)
  if (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_KEY) {
    const { createClient } = require('@supabase/supabase-js');
    const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
    await supabase.from('swarm_blackboard').delete().like('task_id', 'bench-%');
  }

  // ========================================
  // 4. AUTONOMOUS RESEARCH SCALING
  // ========================================
  console.log('\n📊 Test 4: Autonomous Research Scaling');
  console.log('   How does research time scale with subjects?\n');

  for (const subjectCount of [2, 4]) {
    const subjects = ['OpenAI', 'Anthropic', 'Google', 'Meta', 'Microsoft'].slice(0, subjectCount);
    const swarm = new SwarmCoordinator({ maxRounds: 1, useSupabase: true });
    
    const { duration } = await timeIt(`${subjectCount} subjects`, async () => {
      return await swarm.research('AI products', { subjects });
    });
    swarm.shutdown();
    
    console.log(`   ${subjectCount} subjects: ${duration}ms`);
    results.push({ test: 'research_scaling', subjects: subjectCount, duration });
  }

  // ========================================
  // 5. API LATENCY BASELINE
  // ========================================
  console.log('\n📊 Test 5: Raw API Latency');
  console.log('   Measuring Gemini API response time\n');

  const latencies = [];
  for (let i = 0; i < 5; i++) {
    const { duration } = await timeIt(`call-${i}`, async () => {
      return await parallel(['Say OK'], { quiet: true });
    });
    latencies.push(duration);
    process.stdout.write(`   Call ${i+1}: ${duration}ms\n`);
  }
  
  const avgLatency = Math.round(latencies.reduce((a,b) => a+b, 0) / latencies.length);
  const minLatency = Math.min(...latencies);
  const maxLatency = Math.max(...latencies);
  console.log(`   Avg: ${avgLatency}ms, Min: ${minLatency}ms, Max: ${maxLatency}ms`);
  
  results.push({ test: 'api_latency', avg: avgLatency, min: minLatency, max: maxLatency });

  // ========================================
  // SUMMARY
  // ========================================
  console.log('\n📈 BENCHMARK SUMMARY');
  console.log('====================\n');

  // Calculate insights
  const concurrency = results.filter(r => r.test === 'concurrency');
  const linearTime = concurrency[0].duration * 10; // What 10 prompts would take sequentially
  const parallelTime = concurrency.find(r => r.count === 10)?.duration || 0;
  const speedup = linearTime / parallelTime;

  console.log('🚀 Parallelization:');
  console.log(`   Sequential (est): ${linearTime}ms for 10 prompts`);
  console.log(`   Parallel:         ${parallelTime}ms for 10 prompts`);
  console.log(`   Speedup:          ${speedup.toFixed(1)}x\n`);

  const bb = results.find(r => r.test === 'blackboard');
  console.log('💾 Blackboard:');
  console.log(`   File:     ${bb.file}ms`);
  console.log(`   Supabase: ${bb.supabase}ms`);
  console.log(`   Winner:   ${bb.file < bb.supabase ? 'File (faster local I/O)' : 'Supabase (realtime benefits)'}\n`);

  const latency = results.find(r => r.test === 'api_latency');
  console.log('⚡ Gemini API:');
  console.log(`   Avg latency: ${latency.avg}ms`);
  console.log(`   This is the floor - can\'t go faster than the API\n`);

  console.log('🎯 BOTTLENECK ANALYSIS:');
  if (latency.avg > 500) {
    console.log('   → API latency is high (>500ms). Network or Gemini load.');
  }
  if (bb.supabase > bb.file * 3) {
    console.log('   → Supabase adds significant overhead. Consider file-based for speed.');
  }
  if (speedup < 5) {
    console.log('   → Parallelization not reaching full potential. Check rate limits.');
  }
  console.log('');

  console.log('🔧 OPTIMIZATION OPPORTUNITIES:');
  console.log('   1. Batch small prompts into single calls');
  console.log('   2. Use file blackboard for speed, Supabase for persistence');
  console.log('   3. Increase max_concurrent_api if not hitting limits');
  console.log('   4. Pre-warm workers with daemon mode');

  // Rate limiter final stats
  const limiter = globalLimiter.getStats();
  console.log(`\n🚦 Rate Limiter: ${limiter.totalRequests} requests, ${limiter.throttledRequests} throttled`);
}

runDeepBenchmark().catch(console.error);
