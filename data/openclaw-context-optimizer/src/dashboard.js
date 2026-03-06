/**
 * OpenClaw Context Optimizer - REST API Dashboard
 *
 * Provides HTTP endpoints for compression operations and x402 payment integration.
 * Port: 9092 (to avoid conflict with Memory System on 9091 and Cost Governor on 9090)
 */

import express from 'express';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getContextOptimizer } from './index.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

const app = express();
const port = process.argv.includes('--port') ?
  parseInt(process.argv[process.argv.indexOf('--port') + 1]) : 9092;

// Middleware
app.use(express.json({ limit: '10mb' })); // Allow larger payloads for context

// Serve static files (if web interface exists)
app.use(express.static(join(__dirname, '../web')));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'openclaw-context-optimizer',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// Compression Operations
// ============================================================================

/**
 * POST /api/compress
 * Compress context text
 *
 * Body:
 * {
 *   "agent_wallet": "0x...",
 *   "text": "Context to compress...",
 *   "strategy": "hybrid" (optional: deduplication, pruning, summarization, template, hybrid)
 * }
 */
app.post('/api/compress', async (req, res) => {
  try {
    const { agent_wallet, text, strategy } = req.body;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    if (!text || typeof text !== 'string') {
      return res.status(400).json({ error: 'text is required and must be a string' });
    }

    const optimizer = getContextOptimizer();
    const result = await optimizer.compress(text, agent_wallet, strategy || 'hybrid');

    res.json({
      success: true,
      result: {
        original: result.original,
        compressed: result.compressed,
        strategy: result.strategy,
        metrics: {
          original_tokens: result.metrics.originalTokens,
          compressed_tokens: result.metrics.compressedTokens,
          tokens_saved: result.metrics.tokensRemoved,
          compression_ratio: result.metrics.compressionRatio,
          percentage_reduction: result.metrics.percentageReduction,
          quality_score: result.metrics.qualityScore,
          compression_time: result.metrics.compressionTime,
          cost_saved_usd: (result.metrics.tokensRemoved / 1000) * 0.002
        }
      }
    });
  } catch (error) {
    console.error('[Dashboard] Error compressing context:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/stats
 * Get compression statistics for an agent
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 */
app.get('/api/stats', async (req, res) => {
  try {
    const { agent_wallet } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const optimizer = getContextOptimizer();
    const stats = await optimizer.getStats(agent_wallet);

    res.json({
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
 * Get learned compression patterns
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 * - type: Pattern type filter (optional)
 * - limit: Number of results (default: 20)
 */
app.get('/api/patterns', async (req, res) => {
  try {
    const { agent_wallet, type, limit } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const optimizer = getContextOptimizer();
    let patterns = await optimizer.getPatterns(agent_wallet, type || null);

    // Apply limit
    const maxResults = limit ? parseInt(limit) : 20;
    patterns = patterns.slice(0, maxResults);

    res.json({
      agent_wallet,
      pattern_type: type || 'all',
      count: patterns.length,
      patterns: patterns.map(p => ({
        pattern_id: p.pattern_id,
        pattern_type: p.pattern_type,
        pattern_text: p.pattern_text,
        frequency: p.frequency,
        token_impact: p.token_impact,
        importance_score: p.importance_score,
        last_seen: p.last_seen
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
 * POST /api/feedback
 * Submit feedback on compression quality
 *
 * Body:
 * {
 *   "agent_wallet": "0x...",
 *   "session_id": "...",
 *   "feedback_type": "success" | "failure",
 *   "score": 0.0-1.0,
 *   "notes": "Optional feedback notes"
 * }
 */
app.post('/api/feedback', async (req, res) => {
  try {
    const { agent_wallet, session_id, feedback_type, score, notes } = req.body;

    if (!agent_wallet || !session_id) {
      return res.status(400).json({ error: 'agent_wallet and session_id are required' });
    }

    if (score !== undefined && (score < 0 || score > 1)) {
      return res.status(400).json({ error: 'score must be between 0.0 and 1.0' });
    }

    const optimizer = getContextOptimizer();
    optimizer.storage.recordFeedback(
      session_id,
      feedback_type || 'success',
      score || 0.8,
      notes || null
    );

    res.json({
      success: true,
      message: 'Feedback recorded successfully'
    });
  } catch (error) {
    console.error('[Dashboard] Error recording feedback:', error);
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

    const optimizer = getContextOptimizer();
    const paymentRequest = await optimizer.createPaymentRequest(agent_wallet);

    res.json({
      success: true,
      payment_request: paymentRequest,
      instructions: 'Send 0.5 USDT via x402 protocol, then call /api/x402/verify with tx_hash',
      pricing: {
        amount: '0.5 USDT/month',
        features: [
          'Unlimited daily compressions',
          'Advanced compression strategies',
          'Full pattern learning',
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

    const optimizer = getContextOptimizer();
    const result = await optimizer.verifyPayment(request_id, tx_hash, agent_wallet);

    res.json({
      success: true,
      ...result,
      message: 'Payment verified! Pro tier activated - unlimited compressions.'
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

    const optimizer = getContextOptimizer();
    const license = optimizer.checkLicense(agentWallet);

    res.json({
      agent_wallet: agentWallet,
      ...license,
      pricing: {
        pro_monthly: '0.5 USDT/month',
        features: [
          'Unlimited daily compressions',
          'Advanced compression strategies',
          'Full pattern learning',
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
  console.log(`  OpenClaw Context Optimizer - REST API Dashboard`);
  console.log(`${'='.repeat(70)}`);
  console.log(`  Status: Running`);
  console.log(`  URL: http://localhost:${port}`);
  console.log(`  Version: 1.0.0`);
  console.log(`${'='.repeat(70)}\n`);
  console.log(`  API Endpoints:`);
  console.log(`    POST   /api/compress              Compress context`);
  console.log(`    GET    /api/stats                 Get statistics`);
  console.log(`    GET    /api/patterns              Get learned patterns`);
  console.log(`    POST   /api/feedback              Submit feedback`);
  console.log(`    POST   /api/x402/subscribe        Create payment request`);
  console.log(`    POST   /api/x402/verify           Verify payment`);
  console.log(`    GET    /api/x402/license/:wallet  Check license status`);
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  Press Ctrl+C to stop\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\nShutting down Context Optimizer dashboard...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\nShutting down Context Optimizer dashboard...');
  process.exit(0);
});
