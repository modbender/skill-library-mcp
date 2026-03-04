/**
 * OpenClaw Smart Router - REST API Dashboard
 *
 * Provides HTTP endpoints for routing operations and x402 payment integration.
 * Port: 9093 (to avoid conflicts with other OpenClaw services)
 */

import express from 'express';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getSmartRouter } from './index.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

const app = express();
const port = process.argv.includes('--port') ?
  parseInt(process.argv[process.argv.indexOf('--port') + 1]) : 9093;

// Middleware
app.use(express.json({ limit: '10mb' }));

// Serve static files (if web interface exists)
app.use(express.static(join(__dirname, '../web')));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'openclaw-smart-router',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// Routing Operations
// ============================================================================

/**
 * GET /api/stats
 * Get routing statistics for an agent
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 * - timeframe: Timeframe (e.g., "30 days", default: "30 days")
 */
app.get('/api/stats', async (req, res) => {
  try {
    const { agent_wallet, timeframe } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const router = getSmartRouter();
    const stats = await router.getStats(agent_wallet, timeframe || '30 days');

    res.json({
      success: true,
      agent_wallet,
      ...stats
    });
  } catch (error) {
    console.error('[Dashboard] Error fetching stats:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/patterns
 * Get learned routing patterns
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 * - limit: Number of results (default: 20)
 */
app.get('/api/patterns', async (req, res) => {
  try {
    const { agent_wallet, limit } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const router = getSmartRouter();
    let patterns = router.getPatterns(agent_wallet);

    // Apply limit
    const maxResults = limit ? parseInt(limit) : 20;
    patterns = patterns.slice(0, maxResults);

    res.json({
      success: true,
      agent_wallet,
      count: patterns.length,
      patterns: patterns.map(p => ({
        pattern_id: p.pattern_id,
        pattern_type: p.pattern_type,
        optimal_model: p.optimal_model,
        optimal_provider: p.optimal_provider,
        confidence_score: p.confidence_score,
        usage_count: p.usage_count || 0,
        success_rate: p.success_rate || 0,
        avg_cost: p.avg_cost,
        created_at: p.created_at,
        updated_at: p.updated_at
      }))
    });
  } catch (error) {
    console.error('[Dashboard] Error fetching patterns:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/savings
 * Get cost savings analysis
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 * - timeframe: Timeframe (e.g., "30 days", default: "30 days")
 */
app.get('/api/savings', async (req, res) => {
  try {
    const { agent_wallet, timeframe } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const router = getSmartRouter();
    const stats = await router.getStats(agent_wallet, timeframe || '30 days');

    res.json({
      success: true,
      agent_wallet,
      timeframe: stats.timeframe,
      savings: stats.savings,
      routing: {
        total_decisions: stats.routing.total_decisions,
        avg_quality: stats.routing.avg_quality
      }
    });
  } catch (error) {
    console.error('[Dashboard] Error fetching savings:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * POST /api/test
 * Test model selection for a query
 *
 * Body:
 * {
 *   "agent_wallet": "0x...",
 *   "query": "..."
 * }
 */
app.post('/api/test', async (req, res) => {
  try {
    const { agent_wallet, query } = req.body;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'query is required and must be a string' });
    }

    const router = getSmartRouter();
    const result = await router.testSelection(query, agent_wallet);

    res.json({
      success: true,
      query: result.query,
      task_analysis: result.task_analysis,
      model_selection: result.model_selection
    });
  } catch (error) {
    console.error('[Dashboard] Error testing selection:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/insights
 * Get learning insights for an agent
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 */
app.get('/api/insights', async (req, res) => {
  try {
    const { agent_wallet } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const router = getSmartRouter();
    const insights = await router.getInsights(agent_wallet);

    res.json({
      success: true,
      agent_wallet,
      ...insights
    });
  } catch (error) {
    console.error('[Dashboard] Error fetching insights:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

// ============================================================================
// x402 Payment Endpoints
// ============================================================================

/**
 * POST /api/x402/subscribe
 * Create a payment request for Pro tier subscription
 *
 * Body:
 * {
 *   "agent_wallet": "0x..."
 * }
 */
app.post('/api/x402/subscribe', async (req, res) => {
  try {
    const { agent_wallet } = req.body;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const router = getSmartRouter();
    const paymentRequest = await router.createPaymentRequest(agent_wallet);

    res.json({
      success: true,
      payment_request: paymentRequest,
      instructions: 'Send 0.5 USDT via x402 protocol, then call /api/x402/verify with tx_hash',
      pricing: {
        amount: '0.5 USDT/month',
        features: [
          'Unlimited routing decisions',
          'Advanced ML-enhanced routing',
          'Custom model preferences',
          'Priority support'
        ]
      }
    });
  } catch (error) {
    console.error('[Dashboard] Error creating payment request:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * POST /api/x402/verify
 * Verify payment and activate Pro tier
 *
 * Body:
 * {
 *   "request_id": "...",
 *   "tx_hash": "0x...",
 *   "agent_wallet": "0x..."
 * }
 */
app.post('/api/x402/verify', async (req, res) => {
  try {
    const { request_id, tx_hash, agent_wallet } = req.body;

    if (!request_id || !tx_hash || !agent_wallet) {
      return res.status(400).json({
        error: 'request_id, tx_hash, and agent_wallet are required'
      });
    }

    const router = getSmartRouter();
    const result = await router.verifyPayment(request_id, tx_hash, agent_wallet);

    res.json({
      success: true,
      ...result,
      message: 'Payment verified! Pro tier activated - unlimited routing decisions.'
    });
  } catch (error) {
    console.error('[Dashboard] Error verifying payment:', error);
    res.status(400).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/x402/license/:wallet
 * Check license status for an agent wallet
 */
app.get('/api/x402/license/:wallet', (req, res) => {
  try {
    const agentWallet = req.params.wallet;

    if (!agentWallet) {
      return res.status(400).json({ error: 'wallet address is required' });
    }

    const router = getSmartRouter();
    const license = router.checkLicense(agentWallet);

    res.json({
      agent_wallet: agentWallet,
      ...license,
      pricing: {
        pro_monthly: '0.5 USDT/month',
        features: [
          'Unlimited routing decisions',
          'Advanced ML-enhanced routing',
          'Custom model preferences',
          'Priority support'
        ]
      }
    });
  } catch (error) {
    console.error('[Dashboard] Error checking license:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/x402/quota/:wallet
 * Check quota status for an agent wallet
 */
app.get('/api/x402/quota/:wallet', (req, res) => {
  try {
    const agentWallet = req.params.wallet;

    if (!agentWallet) {
      return res.status(400).json({ error: 'wallet address is required' });
    }

    const router = getSmartRouter();
    const quota = router.getQuotaStatus(agentWallet);

    res.json({
      agent_wallet: agentWallet,
      ...quota
    });
  } catch (error) {
    console.error('[Dashboard] Error checking quota:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

// ============================================================================
// Error Handling
// ============================================================================

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    path: req.path,
    method: req.method
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('[Dashboard] Unhandled error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message,
    details: process.env.NODE_ENV === 'development' ? err.stack : undefined
  });
});

// ============================================================================
// Server Start
// ============================================================================

app.listen(port, () => {
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  OpenClaw Smart Router - REST API Dashboard`);
  console.log(`${'='.repeat(70)}`);
  console.log(`  Status: Running`);
  console.log(`  URL: http://localhost:${port}`);
  console.log(`  Version: 1.0.0`);
  console.log(`${'='.repeat(70)}\n`);
  console.log(`  API Endpoints:`);
  console.log(`    GET    /api/stats                 Get routing statistics`);
  console.log(`    GET    /api/patterns              Get learned patterns`);
  console.log(`    GET    /api/savings               Get cost savings analysis`);
  console.log(`    POST   /api/test                  Test model selection`);
  console.log(`    GET    /api/insights              Get learning insights`);
  console.log(`    POST   /api/x402/subscribe        Create payment request`);
  console.log(`    POST   /api/x402/verify           Verify payment`);
  console.log(`    GET    /api/x402/license/:wallet  Check license status`);
  console.log(`    GET    /api/x402/quota/:wallet    Check quota status`);
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  Press Ctrl+C to stop\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\nShutting down Smart Router dashboard...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\nShutting down Smart Router dashboard...');
  process.exit(0);
});
