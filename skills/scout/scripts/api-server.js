#!/usr/bin/env node
/**
 * Scout Trust API Server
 * 
 * Tiered trust intelligence API with x402 payment support.
 * 
 * Endpoints:
 *   GET /score/:agent     - Free tier: basic score + trust level + recommendation
 *   GET /report/:agent    - Paid tier: full dimensional report with flags and analysis
 *   GET /compare?agents=  - Paid tier: multi-agent comparison
 *   GET /health           - Health check
 * 
 * x402 Payment:
 *   All paid endpoints return 402 Payment Required with pricing headers.
 *   Price is currently 0 USDC (free launch period).
 *   When pricing is enabled, agents pay via USDC on Base Sepolia.
 * 
 * Usage:
 *   MOLTBOOK_API_KEY=... node api-server.js [--port 3000]
 */

const http = require('http');
const { MoltbookClient } = require('./lib/moltbook');
const { TrustScorer } = require('./lib/scoring');

const PORT = parseInt(process.argv.find((a, i) => process.argv[i-1] === '--port') || '3000');
const API_KEY = process.env.MOLTBOOK_API_KEY;

if (!API_KEY) {
  console.error('Error: MOLTBOOK_API_KEY required');
  process.exit(1);
}

const client = new MoltbookClient(API_KEY);
const scorer = new TrustScorer();

// x402 pricing config
const PRICING = {
  score: { amount: '0', currency: 'USDC', network: 'base-sepolia' },
  report: { amount: '0', currency: 'USDC', network: 'base-sepolia' },
  compare: { amount: '0', currency: 'USDC', network: 'base-sepolia' },
};

// Future pricing (uncomment when ready)
// const PRICING = {
//   score:   { amount: '0',    currency: 'USDC', network: 'base-sepolia' },
//   report:  { amount: '0.05', currency: 'USDC', network: 'base-sepolia' },
//   compare: { amount: '0.10', currency: 'USDC', network: 'base-sepolia' },
// };

const SCOUT_WALLET = '0xc300c065F0a5E5160A9066D4a7BD8b03298dbB25';

function json(res, status, data) {
  res.writeHead(status, { 
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'X-Scout-Version': '2.0',
    'X-Scout-Pricing-Tier': 'launch',
  });
  res.end(JSON.stringify(data, null, 2));
}

function addPaymentHeaders(res, tier) {
  const price = PRICING[tier];
  res.setHeader('X-Payment-Required', price.amount === '0' ? 'false' : 'true');
  res.setHeader('X-Payment-Amount', price.amount);
  res.setHeader('X-Payment-Currency', price.currency);
  res.setHeader('X-Payment-Network', price.network);
  res.setHeader('X-Payment-Recipient', SCOUT_WALLET);
  res.setHeader('X-Payment-Tier', tier);
}

async function scoreAgent(agentName) {
  const profile = await client.getProfile(agentName);
  if (!profile || !profile.agent?.name) {
    throw new Error(`Agent "${agentName}" not found`);
  }
  return scorer.score(profile);
}

// Route handlers
async function handleScore(res, agentName) {
  addPaymentHeaders(res, 'score');
  
  try {
    const result = await scoreAgent(agentName);
    
    // Free tier: summary only
    json(res, 200, {
      agent: result.agentName,
      score: result.score,
      level: result.recommendation.level,
      recommendation: {
        maxTransaction: result.recommendation.maxTransaction,
        escrowTerms: result.recommendation.escrowTerms,
      },
      flagCount: result.flags.length,
      confidence: result.confidence,
      tier: 'free',
      upgrade: 'Use /report/:agent for full dimensional analysis, flags, and originality breakdown',
      pricing: PRICING.report,
    });
  } catch (e) {
    json(res, e.message.includes('not found') ? 404 : 500, { error: e.message });
  }
}

async function handleReport(res, agentName) {
  addPaymentHeaders(res, 'report');
  
  // x402 payment check (when pricing > 0)
  // For now, all requests pass through (price = 0)
  
  try {
    const result = await scoreAgent(agentName);
    
    // Paid tier: everything
    json(res, 200, {
      agent: result.agentName,
      score: result.score,
      level: result.recommendation.level,
      dimensions: result.dimensions,
      flags: result.flags,
      confidence: result.confidence,
      decay: result.decay,
      recommendation: result.recommendation,
      originality: result.originality || null,
      engagement: result.engagementDetail || null,
      activity: result.activity || null,
      tier: 'paid',
      pricing: PRICING.report,
    });
  } catch (e) {
    json(res, e.message.includes('not found') ? 404 : 500, { error: e.message });
  }
}

async function handleCompare(res, agentNames) {
  addPaymentHeaders(res, 'compare');
  
  if (!agentNames || agentNames.length < 2) {
    return json(res, 400, { error: 'Provide at least 2 agent names: /compare?agents=Agent1,Agent2' });
  }
  
  try {
    const results = await Promise.all(agentNames.map(name => scoreAgent(name.trim())));
    
    const comparison = results.map(r => ({
      agent: r.agentName,
      score: r.score,
      level: r.recommendation.level,
      dimensions: {
        volumeValue: r.dimensions.volumeValue.score,
        originality: r.dimensions.originality.score,
        engagement: r.dimensions.engagement.score,
        credibility: r.dimensions.credibility.score,
        capability: r.dimensions.capability.score,
        spam: r.dimensions.spam.score,
      },
      flags: r.flags,
      maxTransaction: r.recommendation.maxTransaction,
    }));
    
    // Sort by score descending
    comparison.sort((a, b) => b.score - a.score);
    
    json(res, 200, {
      comparison,
      winner: comparison[0].agent,
      tier: 'paid',
      pricing: PRICING.compare,
    });
  } catch (e) {
    json(res, 500, { error: e.message });
  }
}

function handleHealth(res) {
  json(res, 200, {
    status: 'ok',
    version: '2.0',
    endpoints: {
      '/score/:agent': { tier: 'free', price: PRICING.score.amount + ' USDC', description: 'Basic score + trust level + recommendation' },
      '/report/:agent': { tier: 'paid', price: PRICING.report.amount + ' USDC', description: 'Full dimensional report with flags and analysis' },
      '/compare?agents=A,B': { tier: 'paid', price: PRICING.compare.amount + ' USDC', description: 'Side-by-side multi-agent comparison' },
    },
    payment: {
      currency: 'USDC',
      network: 'Base Sepolia',
      recipient: SCOUT_WALLET,
      currentPricing: 'Free launch period (all tiers at 0 USDC)',
    },
  });
}

// Server
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const path = url.pathname;
  
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Payment-Hash',
    });
    return res.end();
  }
  
  // Route matching
  const scoreMatch = path.match(/^\/score\/(.+)$/);
  const reportMatch = path.match(/^\/report\/(.+)$/);
  
  if (path === '/' || path === '/health') {
    return handleHealth(res);
  } else if (scoreMatch) {
    return handleScore(res, decodeURIComponent(scoreMatch[1]));
  } else if (reportMatch) {
    return handleReport(res, decodeURIComponent(reportMatch[1]));
  } else if (path === '/compare') {
    const agents = url.searchParams.get('agents')?.split(',') || [];
    return handleCompare(res, agents);
  } else {
    return json(res, 404, { error: 'Not found', endpoints: ['/', '/score/:agent', '/report/:agent', '/compare?agents=A,B'] });
  }
});

server.listen(PORT, () => {
  console.log(`\n🔍 Scout Trust API v2.0`);
  console.log(`   http://localhost:${PORT}\n`);
  console.log(`Endpoints:`);
  console.log(`  GET /score/:agent       Free  - Basic score + recommendation`);
  console.log(`  GET /report/:agent      Paid  - Full report (${PRICING.report.amount} USDC)`);
  console.log(`  GET /compare?agents=A,B Paid  - Multi-agent comparison (${PRICING.compare.amount} USDC)`);
  console.log(`  GET /health             Free  - API status\n`);
  console.log(`Payment: USDC on Base Sepolia → ${SCOUT_WALLET}`);
  console.log(`Current pricing: Free launch period\n`);
});
