#!/usr/bin/env node
/**
 * TAP URL Analyzer - Parallel analysis for military transition resources
 * Uses Swarm pattern to fetch and analyze URLs in parallel
 */

const { GoogleGenerativeAI } = require('@google/generative-ai');
const fs = require('fs');
const path = require('path');

// Config
const BATCH_SIZE = 15;  // Parallel requests per batch
const TIMEOUT_MS = 15000;
const OUTPUT_FILE = process.env.HOME + '/clawd/data/tap-analysis-results.json';

// User context for relevance scoring — customize for your situation
const USER_CONTEXT = process.env.TAP_USER_CONTEXT || `
TRANSITIONING SERVICE MEMBER PROFILE:
- Rank: E-7 (Senior NCO)
- Timeline: ~12 months from retirement
- Years of Service: 20 years
- Career Interests: Software development, IT management
- Key Priorities: VA benefits, healthcare transition, retirement pay, 
  SkillBridge, entrepreneurship support
`;

const ANALYSIS_PROMPT = `Analyze this resource for a transitioning military member.

${USER_CONTEXT}

For this webpage, provide a JSON response with:
{
  "relevant": true/false (is this useful for this specific person?),
  "score": 1-10 (relevance score, 10 = critical),
  "category": "one of: benefits|employment|education|healthcare|finance|entrepreneurship|family|housing|mental_health|other",
  "summary": "2-3 sentence summary of what this offers",
  "action_items": ["specific actions this person should take"],
  "timeline": "when should they engage with this (now, 6mo out, 90 days out, post-retirement)",
  "needs_context": ["any questions needed to better assess relevance"]
}

Respond ONLY with valid JSON, no markdown.

WEBPAGE CONTENT:
`;

// Load API key
const apiKey = process.env.GEMINI_API_KEY || 
  fs.readFileSync(process.env.HOME + '/.config/clawdbot/gemini-key.txt', 'utf8').trim();
const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

async function fetchAndAnalyze(url) {
  const start = Date.now();
  try {
    // Fetch with timeout
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);
    
    const res = await fetch(url, { 
      headers: { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
      },
      signal: controller.signal,
      redirect: 'follow'
    });
    clearTimeout(timeout);
    
    if (!res.ok) {
      return { url, error: `HTTP ${res.status}`, ms: Date.now() - start };
    }
    
    const html = await res.text();
    // Extract text content (remove HTML tags, scripts, styles)
    const text = html
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]*>/g, ' ')
      .replace(/\s+/g, ' ')
      .substring(0, 6000);
    
    if (text.length < 100) {
      return { url, error: 'No content extracted', ms: Date.now() - start };
    }
    
    // LLM Analysis
    const result = await model.generateContent(ANALYSIS_PROMPT + text);
    const responseText = result.response.text();
    
    // Parse JSON response
    let analysis;
    try {
      // Try to extract JSON from response
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      analysis = jsonMatch ? JSON.parse(jsonMatch[0]) : { error: 'No JSON in response' };
    } catch (e) {
      analysis = { error: 'JSON parse failed', raw: responseText.substring(0, 200) };
    }
    
    return { 
      url,
      ms: Date.now() - start,
      ...analysis
    };
  } catch (e) {
    return { 
      url, 
      error: e.name === 'AbortError' ? 'Timeout' : e.message, 
      ms: Date.now() - start 
    };
  }
}

async function processBatch(urls, batchNum, totalBatches) {
  console.log(`\n📦 Batch ${batchNum}/${totalBatches} (${urls.length} URLs)`);
  const start = Date.now();
  
  const results = await Promise.all(urls.map(fetchAndAnalyze));
  
  const successful = results.filter(r => !r.error).length;
  const elapsed = ((Date.now() - start) / 1000).toFixed(1);
  console.log(`   ✓ ${successful}/${urls.length} analyzed in ${elapsed}s`);
  
  return results;
}

async function main() {
  console.log('🐝 TAP URL ANALYZER - Swarm Mode');
  console.log('═'.repeat(60));
  
  // Load URLs
  const urlsFile = '/tmp/tap_urls_clean.txt';
  const allUrls = fs.readFileSync(urlsFile, 'utf8')
    .split('\n')
    .filter(u => u.trim())
    .filter(u => !u.includes('...'))  // Skip truncated
    .filter(u => u.length > 15 && u.length < 150);  // Reasonable length
  
  console.log(`\n📊 Found ${allUrls.length} URLs to analyze`);
  console.log(`👤 Analyzing for: transitioning service member`);
  console.log(`⚡ Batch size: ${BATCH_SIZE} parallel requests`);
  
  const totalStart = Date.now();
  const allResults = [];
  
  // Process in batches
  const batches = [];
  for (let i = 0; i < allUrls.length; i += BATCH_SIZE) {
    batches.push(allUrls.slice(i, i + BATCH_SIZE));
  }
  
  for (let i = 0; i < batches.length; i++) {
    const results = await processBatch(batches[i], i + 1, batches.length);
    allResults.push(...results);
    
    // Small delay between batches to avoid rate limiting
    if (i < batches.length - 1) {
      await new Promise(r => setTimeout(r, 1000));
    }
  }
  
  const totalTime = ((Date.now() - totalStart) / 1000).toFixed(1);
  
  // Compile results
  const successful = allResults.filter(r => !r.error && r.relevant !== undefined);
  const relevant = successful.filter(r => r.relevant && r.score >= 5);
  const errors = allResults.filter(r => r.error);
  
  console.log('\n' + '═'.repeat(60));
  console.log('📈 ANALYSIS COMPLETE');
  console.log('─'.repeat(60));
  console.log(`   Total time: ${totalTime}s`);
  console.log(`   URLs processed: ${allResults.length}`);
  console.log(`   Successfully analyzed: ${successful.length}`);
  console.log(`   Relevant (score ≥5): ${relevant.length}`);
  console.log(`   Errors/timeouts: ${errors.length}`);
  
  // Save full results
  const output = {
    generatedAt: new Date().toISOString(),
    userContext: USER_CONTEXT,
    stats: {
      totalUrls: allResults.length,
      successful: successful.length,
      relevant: relevant.length,
      errors: errors.length,
      totalTimeSeconds: parseFloat(totalTime)
    },
    relevantResources: relevant.sort((a, b) => b.score - a.score),
    allResults: allResults,
    needsContext: successful.filter(r => r.needs_context && r.needs_context.length > 0)
  };
  
  fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
  console.log(`\n💾 Results saved to: ${OUTPUT_FILE}`);
  
  // Print top resources
  console.log('\n🏆 TOP 15 MOST RELEVANT RESOURCES:');
  console.log('─'.repeat(60));
  relevant.slice(0, 15).forEach((r, i) => {
    console.log(`\n${i + 1}. [${r.score}/10] ${r.category?.toUpperCase() || 'N/A'}`);
    console.log(`   ${r.url}`);
    console.log(`   ${r.summary || 'No summary'}`);
    if (r.timeline) console.log(`   ⏰ Timeline: ${r.timeline}`);
  });
  
  // Print questions needing context
  const allQuestions = [];
  successful.forEach(r => {
    if (r.needs_context && r.needs_context.length) {
      r.needs_context.forEach(q => {
        if (!allQuestions.includes(q)) allQuestions.push(q);
      });
    }
  });
  
  if (allQuestions.length > 0) {
    console.log('\n\n❓ QUESTIONS TO REFINE ANALYSIS:');
    console.log('─'.repeat(60));
    allQuestions.slice(0, 15).forEach((q, i) => {
      console.log(`${i + 1}. ${q}`);
    });
  }
}

main().catch(console.error);
