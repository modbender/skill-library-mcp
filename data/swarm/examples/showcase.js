#!/usr/bin/env node
/**
 * Swarm Showcase
 * Demonstrates parallel research across multiple subjects
 */

const { research, parallel } = require('../lib');

async function showcase() {
  console.log('\n' + '═'.repeat(60));
  console.log('🐝 SWARM SHOWCASE: AI Startup Research');
  console.log('═'.repeat(60));
  console.log('\nTask: Research 6 AI startups - funding, products, differentiators\n');
  
  const startups = [
    'Anthropic',
    'Mistral AI', 
    'Cohere',
    'Perplexity AI',
    'Runway ML',
    'Stability AI'
  ];
  
  console.log(`Subjects: ${startups.join(', ')}\n`);
  console.log('Starting parallel research...\n');
  
  const startTime = Date.now();
  
  const result = await research(
    startups,
    'AI startup 2024 funding products technology',
    { verbose: true }
  );
  
  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  const seqEstimate = startups.length * 6; // ~6s per subject sequential
  const speedup = (seqEstimate / parseFloat(totalTime)).toFixed(1);
  
  console.log('\n' + '═'.repeat(60));
  console.log('📊 RESULTS');
  console.log('═'.repeat(60));
  
  for (const analysis of result.analyses) {
    console.log(`\n### ${analysis.subject}`);
    console.log('─'.repeat(40));
    // Truncate to first 500 chars for display
    const text = analysis.analysis?.substring(0, 500) || 'No data';
    console.log(text + (text.length >= 500 ? '...' : ''));
  }
  
  console.log('\n' + '═'.repeat(60));
  console.log('⏱️  PERFORMANCE');
  console.log('═'.repeat(60));
  console.log(`Total time:      ${totalTime}s`);
  console.log(`Est. sequential: ${seqEstimate}s`);
  console.log(`Speedup:         ${speedup}x faster`);
  console.log(`Subjects:        ${startups.length}`);
  console.log(`Success rate:    ${result.analyses.length}/${startups.length}`);
  console.log('═'.repeat(60) + '\n');
}

showcase().catch(console.error);
