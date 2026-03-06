#!/usr/bin/env node
/**
 * Answer Intent Map — AI Platform Query Tool
 * Part of: AEO (Answer Engine Optimization) Skill
 * Version: 1.0
 *
 * Queries AI platforms with purchase-intent questions and logs
 * competitive intelligence: which brands are recommended, in what
 * position, and what sources the AI cites.
 *
 * Usage:
 *   node answer-intent-map.js --category "magnesium supplements" --queries 20
 *   node answer-intent-map.js --config ../aeo-config.json
 *   node answer-intent-map.js --query "best magnesium for sleep" --platform perplexity
 *   node answer-intent-map.js --help
 *
 * Requires:
 *   PERPLEXITY_API_KEY env var (or pass via --api-key flag)
 *   OPENAI_API_KEY env var (optional, for ChatGPT queries)
 */

'use strict';

const https = require('https');
const fs = require('fs');
const path = require('path');

// ─── CONFIG ───────────────────────────────────────────────────────────────────

const DEFAULT_CONFIG = {
  brandName: null,
  category: null,
  priorityQueries: [],
  competitors: [],
  delayMs: 2000,        // Delay between API calls (ms) — respect rate limits
  outputDir: '.',
  platforms: ['perplexity'],  // Add 'openai' if OPENAI_API_KEY is available
};

// ─── QUERY TEMPLATES ──────────────────────────────────────────────────────────

/**
 * Generate a full set of 50 purchase-intent queries for a category.
 * Organized by the four AEO query types.
 */
function generateQueries(category, brandName, competitors = []) {
  const useCases = getCategoryUseCases(category);
  const queries = [];

  // 1. Category queries (highest volume, most competitive)
  for (const useCase of useCases.slice(0, 5)) {
    queries.push({
      type: 'category',
      query: `best ${category} for ${useCase}`,
    });
  }

  // Add generic category queries
  queries.push({ type: 'category', query: `best ${category} brand` });
  queries.push({ type: 'category', query: `best ${category} 2025` });
  queries.push({ type: 'category', query: `top rated ${category}` });
  queries.push({ type: 'category', query: `${category} recommendations` });
  queries.push({ type: 'category', query: `what is the best ${category}` });

  // 2. Comparison queries
  if (brandName) {
    queries.push({ type: 'comparison', query: `${brandName} review` });
    queries.push({ type: 'comparison', query: `is ${brandName} worth it` });
    for (const competitor of competitors.slice(0, 3)) {
      queries.push({
        type: 'comparison',
        query: `${brandName} vs ${competitor}`,
      });
    }
  }

  // Generic comparison queries
  if (useCases.length >= 2) {
    queries.push({
      type: 'comparison',
      query: `${useCases[0]} vs ${useCases[1]} ${category}`,
    });
  }

  // 3. Brand queries (if brand name provided)
  if (brandName) {
    queries.push({ type: 'brand', query: `${brandName} ingredients` });
    queries.push({ type: 'brand', query: `${brandName} side effects` });
    queries.push({ type: 'brand', query: `${brandName} dosage` });
    queries.push({ type: 'brand', query: `${brandName} customer reviews` });
  }

  // 4. Educational queries (top-funnel authority building)
  const educationalQueries = getCategoryEducationalQueries(category);
  for (const q of educationalQueries.slice(0, 5)) {
    queries.push({ type: 'educational', query: q });
  }

  return queries;
}

/**
 * Get common use cases for a category.
 * Extend this function as you add more product categories.
 */
function getCategoryUseCases(category) {
  const lower = category.toLowerCase();

  if (lower.includes('magnesium')) {
    return ['sleep', 'anxiety', 'muscle cramps', 'stress', 'energy', 'constipation', 'migraines'];
  }
  if (lower.includes('protein') || lower.includes('protein powder')) {
    return ['weight loss', 'muscle building', 'women', 'beginners', 'keto', 'seniors', 'athletes'];
  }
  if (lower.includes('collagen')) {
    return ['skin elasticity', 'joint pain', 'hair growth', 'gut health', 'anti-aging'];
  }
  if (lower.includes('pre-workout')) {
    return ['without caffeine', 'women', 'weight loss', 'pump', 'beginners'];
  }
  if (lower.includes('vitamin d')) {
    return ['adults', 'deficiency', 'immune support', 'bone health', 'mood'];
  }
  if (lower.includes('omega') || lower.includes('fish oil')) {
    return ['heart health', 'brain function', 'inflammation', 'children', 'pregnancy'];
  }
  if (lower.includes('probiotics') || lower.includes('probiotic')) {
    return ['women', 'ibs', 'bloating', 'weight loss', 'gut health', 'immune system'];
  }
  if (lower.includes('coffee')) {
    return ['espresso', 'cold brew at home', 'morning routine', 'sensitive stomach', 'dark roast'];
  }
  if (lower.includes('dog food') || lower.includes('pet food')) {
    return ['weight management', 'sensitive stomach', 'puppies', 'senior dogs', 'allergies'];
  }
  if (lower.includes('skincare') || lower.includes('moisturizer')) {
    return ['dry skin', 'oily skin', 'anti-aging', 'sensitive skin', 'acne-prone skin'];
  }

  // Generic fallback
  return ['beginners', 'professional use', 'budget buyers', 'premium quality', 'daily use'];
}

/**
 * Get educational queries for a category.
 */
function getCategoryEducationalQueries(category) {
  const lower = category.toLowerCase();

  if (lower.includes('magnesium')) {
    return [
      'does magnesium help with sleep',
      'magnesium deficiency symptoms',
      'how much magnesium per day',
      'magnesium glycinate vs citrate',
      'magnesium benefits for women',
    ];
  }
  if (lower.includes('protein')) {
    return [
      'how much protein per day to build muscle',
      'when to take protein powder',
      'whey vs plant protein',
      'does protein powder cause weight gain',
    ];
  }
  if (lower.includes('collagen')) {
    return [
      'does collagen actually work',
      'when to take collagen',
      'collagen types explained',
      'collagen vs biotin for hair',
    ];
  }

  // Generic educational queries
  return [
    `how does ${category} work`,
    `${category} benefits and side effects`,
    `how to choose ${category}`,
    `${category} dosage guide`,
  ];
}

// ─── API CLIENTS ──────────────────────────────────────────────────────────────

/**
 * Query Perplexity API with a single question.
 * Returns structured response with content and citations.
 */
async function queryPerplexity(question, apiKey) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: 'llama-3.1-sonar-small-128k-online',
      messages: [
        {
          role: 'user',
          content: question,
        },
      ],
      max_tokens: 500,
      return_citations: true,
    });

    const options = {
      hostname: 'api.perplexity.ai',
      path: '/chat/completions',
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) {
            reject(new Error(`Perplexity API error: ${parsed.error.message}`));
            return;
          }
          const content = parsed.choices?.[0]?.message?.content || '';
          const citations = parsed.citations || [];
          resolve({ content, citations, raw: parsed });
        } catch (e) {
          reject(new Error(`Failed to parse Perplexity response: ${e.message}`));
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

/**
 * Query OpenAI API with a single question.
 * Returns text response (no native citations — use web search model if available).
 */
async function queryOpenAI(question, apiKey) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: 'gpt-4o-search-preview',   // Use search-enabled model for current recommendations
      messages: [
        {
          role: 'system',
          content:
            'You are a helpful assistant. When asked about product recommendations, provide specific brand names, product specs, and your reasoning. Be direct and specific.',
        },
        {
          role: 'user',
          content: question,
        },
      ],
      max_tokens: 500,
    });

    const options = {
      hostname: 'api.openai.com',
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) {
            reject(new Error(`OpenAI API error: ${parsed.error.message}`));
            return;
          }
          const content = parsed.choices?.[0]?.message?.content || '';
          resolve({ content, citations: [], raw: parsed });
        } catch (e) {
          reject(new Error(`Failed to parse OpenAI response: ${e.message}`));
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ─── RESPONSE PARSER ──────────────────────────────────────────────────────────

/**
 * Extract brand mentions from an AI response.
 * Returns array of brand mentions in order of appearance.
 *
 * This is intentionally simple — it looks for capitalized sequences
 * and known competitor names. For production use, you should populate
 * the competitors array in your config for better detection.
 */
function extractBrandMentions(content, knownBrands = []) {
  const mentions = [];
  const seen = new Set();

  // Check for known brands first (most reliable)
  for (const brand of knownBrands) {
    const regex = new RegExp(brand.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    if (regex.test(content) && !seen.has(brand.toLowerCase())) {
      mentions.push(brand);
      seen.add(brand.toLowerCase());
    }
  }

  // Look for patterns like "Brand Name's Product" or "Brand Name is"
  // These are rough heuristics — manual review of the raw content is always recommended
  const brandPatterns = [
    /\b([A-Z][a-z]+ (?:[A-Z][a-z]+ )?(?:Labs?|Health|Nutrition|Supplements?|Brand|Co\.?))\b/g,
    /\bby ([A-Z][a-z]+(?: [A-Z][a-z]+)?)\b/g,
    /^\d+\.\s+\*?\*?([A-Z][a-zA-Z ]+?)\*?\*?(?:\s*[-–—]|\s*:)/gm,
  ];

  for (const pattern of brandPatterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const brandCandidate = (match[1] || match[0]).trim();
      if (brandCandidate.length > 2 && !seen.has(brandCandidate.toLowerCase())) {
        mentions.push(brandCandidate);
        seen.add(brandCandidate.toLowerCase());
      }
    }
  }

  return mentions.slice(0, 5); // Return top 5 mentions
}

// ─── REPORT GENERATOR ─────────────────────────────────────────────────────────

/**
 * Generate a Markdown summary report from query results.
 */
function generateMarkdownReport(results, config) {
  const date = new Date().toISOString().split('T')[0];
  const brandName = config.brandName || '[Your Brand]';
  const category = config.category || '[Category]';

  let md = `# Answer Intent Map — ${category}\n`;
  md += `**Brand:** ${brandName}  \n`;
  md += `**Date:** ${date}  \n`;
  md += `**Queries Run:** ${results.length}  \n\n`;
  md += `---\n\n`;

  // Summary table
  md += `## Summary: Brand Recommendation Positions\n\n`;
  md += `| Query | Platform | #1 Brand | #2 Brand | #3 Brand | Source Cited |\n`;
  md += `|-------|----------|----------|----------|----------|--------------|\n`;

  for (const result of results) {
    if (result.error) {
      md += `| ${result.query} | ${result.platform} | ERROR | - | - | - |\n`;
      continue;
    }

    const brands = result.brandMentions;
    const b1 = brands[0] || '-';
    const b2 = brands[1] || '-';
    const b3 = brands[2] || '-';
    const source = result.citations[0] ? new URL(result.citations[0]).hostname : '-';

    const isOurBrand = (b) =>
      b.toLowerCase().includes(brandName.toLowerCase());

    const formatBrand = (b) => (isOurBrand(b) ? `**${b}** ✓` : b);

    md += `| ${result.query} | ${result.platform} | ${formatBrand(b1)} | ${formatBrand(b2)} | ${formatBrand(b3)} | ${source} |\n`;
  }

  md += `\n---\n\n`;

  // Position analysis
  const ourPosition1 = results.filter(
    (r) => r.brandMentions[0]?.toLowerCase().includes(brandName.toLowerCase())
  ).length;
  const ourTopThree = results.filter((r) =>
    r.brandMentions
      .slice(0, 3)
      .some((b) => b.toLowerCase().includes(brandName.toLowerCase()))
  ).length;

  md += `## Position Analysis: ${brandName}\n\n`;
  md += `- Queries where ${brandName} is **#1 recommendation:** ${ourPosition1} / ${results.length}\n`;
  md += `- Queries where ${brandName} is in **top 3:** ${ourTopThree} / ${results.length}\n`;
  md += `- Queries where ${brandName} is **absent:** ${results.length - ourTopThree} / ${results.length}\n\n`;

  // Most-cited competitor
  const competitorCounts = {};
  for (const result of results) {
    for (const brand of result.brandMentions.slice(0, 3)) {
      if (!brand.toLowerCase().includes(brandName.toLowerCase())) {
        competitorCounts[brand] = (competitorCounts[brand] || 0) + 1;
      }
    }
  }

  const sortedCompetitors = Object.entries(competitorCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  md += `## Most Frequently Recommended Competitors\n\n`;
  for (const [comp, count] of sortedCompetitors) {
    md += `- **${comp}:** ${count} queries\n`;
  }

  md += `\n---\n\n`;

  // Citation sources
  const citationCounts = {};
  for (const result of results) {
    for (const url of result.citations || []) {
      try {
        const domain = new URL(url).hostname;
        citationCounts[domain] = (citationCounts[domain] || 0) + 1;
      } catch (_) {
        // ignore invalid URLs
      }
    }
  }

  const sortedCitations = Object.entries(citationCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  if (sortedCitations.length > 0) {
    md += `## Most-Cited Sources (Layer 6 Outreach Targets)\n\n`;
    md += `These sources are what AI models are citing when recommending brands in your category.\n`;
    md += `Getting listed on these sites is your highest-priority Layer 6 action.\n\n`;
    for (const [domain, count] of sortedCitations) {
      md += `- **${domain}** — cited in ${count} responses\n`;
    }
    md += `\n`;
  }

  // Priority gaps
  const priorityGaps = results
    .filter(
      (r) =>
        !r.error &&
        !r.brandMentions
          .slice(0, 3)
          .some((b) => b.toLowerCase().includes(brandName.toLowerCase()))
    )
    .slice(0, 10);

  if (priorityGaps.length > 0) {
    md += `## Priority Gaps: Queries to Target First\n\n`;
    md += `${brandName} is absent from these queries. These are your highest-value optimization targets.\n\n`;
    for (const gap of priorityGaps) {
      md += `- "${gap.query}" — ${gap.brandMentions[0] || 'unclear'} is #1\n`;
    }
    md += `\n`;
  }

  md += `---\n`;
  md += `\n*Generated by AEO Answer Intent Map script — ${date}*\n`;
  md += `*Manual review of raw responses recommended before drawing strategic conclusions.*\n`;

  return md;
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const args = process.argv.slice(2);

  // Parse flags
  const flags = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
      flags[key] = value;
    }
  }

  // Help
  if (flags.help || flags.h) {
    console.log(`
Answer Intent Map — AI Platform Query Tool

Usage:
  node answer-intent-map.js [options]

Options:
  --category <string>     Product category to research (required if no config)
  --brand <string>        Your brand name (optional)
  --queries <number>      Number of queries to run (default: 20)
  --platform <string>     Platform to query: perplexity, openai (default: perplexity)
  --query <string>        Run a single query (skips query generation)
  --config <path>         Path to aeo-config.json
  --api-key <string>      Perplexity API key (overrides PERPLEXITY_API_KEY env)
  --output <path>         Output directory (default: current directory)
  --delay <ms>            Delay between API calls in ms (default: 2000)
  --help                  Show this help

Examples:
  node answer-intent-map.js --category "magnesium supplements" --queries 20
  node answer-intent-map.js --category "protein powder" --brand "MyBrand" --queries 30
  node answer-intent-map.js --query "best magnesium for sleep" --platform perplexity
  node answer-intent-map.js --config ./aeo-config.json
`);
    process.exit(0);
  }

  // Load config
  let config = { ...DEFAULT_CONFIG };
  if (flags.config) {
    const configPath = path.resolve(flags.config);
    if (fs.existsSync(configPath)) {
      const loaded = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      config = { ...config, ...loaded };
    } else {
      console.error(`Config file not found: ${configPath}`);
      process.exit(1);
    }
  }

  // Override config with flags
  if (flags.category) config.category = flags.category;
  if (flags.brand) config.brandName = flags.brand;
  if (flags.output) config.outputDir = flags.output;
  if (flags.delay) config.delayMs = parseInt(flags.delay);

  // API keys
  const perplexityKey = flags['api-key'] || process.env.PERPLEXITY_API_KEY || config.perplexityApiKey;
  const openaiKey = process.env.OPENAI_API_KEY || config.openaiApiKey;

  const platform = flags.platform || 'perplexity';

  if (platform === 'perplexity' && !perplexityKey) {
    console.error('Error: PERPLEXITY_API_KEY not set. Pass --api-key or set the environment variable.');
    console.error('Get a free API key at: https://www.perplexity.ai/settings/api');
    process.exit(1);
  }

  if (platform === 'openai' && !openaiKey) {
    console.error('Error: OPENAI_API_KEY not set.');
    process.exit(1);
  }

  // Category required
  if (!config.category && !flags.query) {
    console.error('Error: --category is required (or pass --query for a single query)');
    process.exit(1);
  }

  // Generate queries
  let queries;
  if (flags.query) {
    queries = [{ type: 'single', query: flags.query }];
  } else {
    const maxQueries = parseInt(flags.queries) || 20;
    queries = generateQueries(
      config.category,
      config.brandName,
      config.competitors
    ).slice(0, maxQueries);
  }

  console.log(`\nAnswer Intent Map`);
  console.log(`Category: ${config.category || 'single query'}`);
  console.log(`Brand: ${config.brandName || 'not specified'}`);
  console.log(`Platform: ${platform}`);
  console.log(`Queries: ${queries.length}`);
  console.log(`Output: ${config.outputDir}\n`);
  console.log(`Starting queries...\n`);

  const results = [];

  for (let i = 0; i < queries.length; i++) {
    const { query, type } = queries[i];
    process.stdout.write(`[${i + 1}/${queries.length}] ${query} ... `);

    try {
      let response;
      if (platform === 'perplexity') {
        response = await queryPerplexity(query, perplexityKey);
      } else if (platform === 'openai') {
        response = await queryOpenAI(query, openaiKey);
      }

      const brandMentions = extractBrandMentions(
        response.content,
        [config.brandName, ...(config.competitors || [])].filter(Boolean)
      );

      results.push({
        query,
        type,
        platform,
        brandMentions,
        citations: response.citations || [],
        content: response.content,
        timestamp: new Date().toISOString(),
      });

      const top = brandMentions[0] || 'unclear';
      const ourBrand = config.brandName;
      const isUs = ourBrand && brandMentions.some((b) =>
        b.toLowerCase().includes(ourBrand.toLowerCase())
      );

      console.log(isUs ? `✓ (${top})` : `✗ (${top})`);
    } catch (err) {
      console.log(`ERROR: ${err.message}`);
      results.push({
        query,
        type,
        platform,
        brandMentions: [],
        citations: [],
        content: '',
        error: err.message,
        timestamp: new Date().toISOString(),
      });
    }

    // Delay between requests to respect rate limits
    if (i < queries.length - 1) {
      await sleep(config.delayMs);
    }
  }

  // Write outputs
  const date = new Date().toISOString().split('T')[0];
  const safeCat = (config.category || 'query').replace(/[^a-z0-9]/gi, '-').toLowerCase();
  const outputDir = path.resolve(config.outputDir);

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // JSON data file
  const jsonPath = path.join(outputDir, `answer-intent-map-${safeCat}-${date}.json`);
  fs.writeFileSync(jsonPath, JSON.stringify(results, null, 2));
  console.log(`\nJSON data saved: ${jsonPath}`);

  // Markdown report
  const mdPath = path.join(outputDir, `answer-intent-map-${safeCat}-${date}.md`);
  const report = generateMarkdownReport(results, config);
  fs.writeFileSync(mdPath, report);
  console.log(`Markdown report saved: ${mdPath}`);

  // Console summary
  const successful = results.filter((r) => !r.error).length;
  const ourWins = results.filter(
    (r) =>
      config.brandName &&
      r.brandMentions[0]?.toLowerCase().includes(config.brandName.toLowerCase())
  ).length;

  console.log(`\n─────────────────────────────`);
  console.log(`Queries completed: ${successful}/${queries.length}`);
  if (config.brandName) {
    console.log(`${config.brandName} as #1: ${ourWins}/${successful}`);
  }
  console.log(`─────────────────────────────\n`);
  console.log(`Review the Markdown report for the full competitive analysis.`);
  console.log(`Use the "Most-Cited Sources" section to prioritize Layer 6 outreach.\n`);
}

main().catch((err) => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
