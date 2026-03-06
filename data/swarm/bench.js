#!/usr/bin/env node
// Full Swarm benchmark: Fetch + LLM Analysis

const { GoogleGenerativeAI } = require('@google/generative-ai');
const fs = require('fs');

// Load API key
const apiKey = process.env.GEMINI_API_KEY || 
  fs.readFileSync(process.env.HOME + '/.config/clawdbot/gemini-key.txt', 'utf8').trim();
const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

const urls = [
  { url: 'https://benefits.va.gov/transition', name: 'VA Transition' },
  { url: 'https://skillbridge.osd.mil/', name: 'SkillBridge' },
  { url: 'https://www.va.gov/education/about-gi-bill-benefits/', name: 'GI Bill' },
  { url: 'https://www.careeronestop.org/Veterans/', name: 'CareerOneStop' },
  { url: 'https://www.mynextmove.org/vets/', name: 'MyNextMove' },
  { url: 'https://www.sba.gov/business-guide/10-steps-start-your-business', name: 'SBA Business' },
  { url: 'https://www.hirevets.gov/', name: 'HIREVets' },
];

const PROMPT = `Analyze this webpage for a transitioning military member (E-7, nearing retirement).
Extract in 2-3 sentences:
1. What this resource offers
2. Key action items or deadlines
3. Relevance score (1-10) for someone planning retirement transition

Webpage content:
`;

async function fetchAndAnalyze(item) {
  const start = Date.now();
  try {
    // Fetch
    const res = await fetch(item.url, { 
      headers: { 'User-Agent': 'Mozilla/5.0' },
      signal: AbortSignal.timeout(10000)
    });
    const html = await res.text();
    const text = html.replace(/<[^>]*>/g, ' ').substring(0, 4000);
    
    // LLM Analyze
    const result = await model.generateContent(PROMPT + text);
    const analysis = result.response.text();
    
    return { 
      name: item.name,
      ms: Date.now() - start,
      analysis: analysis.substring(0, 300)
    };
  } catch (e) {
    return { name: item.name, error: e.message, ms: Date.now() - start };
  }
}

async function sequential() {
  console.log('\n📊 SEQUENTIAL (Fetch + Analyze one at a time)');
  console.log('─'.repeat(60));
  const start = Date.now();
  const results = [];
  for (const item of urls) {
    process.stdout.write(`  Analyzing ${item.name}...`);
    const result = await fetchAndAnalyze(item);
    results.push(result);
    console.log(` ${result.ms}ms`);
  }
  const total = Date.now() - start;
  console.log(`\n  TOTAL: ${(total/1000).toFixed(2)}s`);
  return { total, results };
}

async function parallel() {
  console.log('\n⚡ PARALLEL (All fetch + analyze at once)');
  console.log('─'.repeat(60));
  const start = Date.now();
  const results = await Promise.all(urls.map(fetchAndAnalyze));
  results.forEach(r => {
    console.log(`  ${r.ms}ms - ${r.name}`);
  });
  const total = Date.now() - start;
  console.log(`\n  TOTAL: ${(total/1000).toFixed(2)}s`);
  return { total, results };
}

async function main() {
  console.log('🐝 SWARM BENCHMARK: Sequential vs Parallel (Fetch + LLM)');
  console.log('═'.repeat(60));
  console.log(`Testing ${urls.length} URLs with Gemini Flash analysis\n`);
  
  const seq = await sequential();
  const par = await parallel();
  
  console.log('\n' + '═'.repeat(60));
  console.log('📈 RESULTS');
  console.log('─'.repeat(60));
  console.log(`  Sequential: ${(seq.total/1000).toFixed(2)}s`);
  console.log(`  Parallel:   ${(par.total/1000).toFixed(2)}s`);
  console.log(`  Speedup:    ${(seq.total/par.total).toFixed(1)}x faster`);
  console.log('═'.repeat(60));
  
  console.log('\n📋 SAMPLE ANALYSES (from parallel run):');
  console.log('─'.repeat(60));
  par.results.slice(0, 3).forEach(r => {
    if (r.analysis) {
      console.log(`\n${r.name}:`);
      console.log(r.analysis);
    }
  });
}

main().catch(console.error);
