/**
 * OpenClaw Memory System - REST API Dashboard
 *
 * Provides HTTP endpoints for memory operations and x402 payment integration.
 * Port: 9091 (to avoid conflict with Cost Governor on 9090)
 */

import express from 'express';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { getMemoryManager } from './index.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

const app = express();
const port = process.argv.includes('--port') ?
  parseInt(process.argv[process.argv.indexOf('--port') + 1]) : 9091;

// Middleware
app.use(express.json());

// Serve static files (if web interface exists)
app.use(express.static(join(__dirname, '../web')));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'openclaw-memory',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// Memory Operations
// ============================================================================

/**
 * POST /api/memories
 * Store a new memory
 *
 * Body:
 * {
 *   "agent_wallet": "0x...",
 *   "content": "User prefers TypeScript",
 *   "type": "preference",
 *   "importance": 0.8,
 *   "session_id": "optional-session-id"
 * }
 */
app.post('/api/memories', async (req, res) => {
  try {
    const { agent_wallet, content, type, importance, session_id } = req.body;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    if (!content || typeof content !== 'string') {
      return res.status(400).json({ error: 'content is required and must be a string' });
    }

    const manager = getMemoryManager();
    const memory = await manager.storeMemory(
      agent_wallet,
      content,
      type || 'fact',
      importance || 0.5,
      session_id
    );

    res.json({
      success: true,
      memory: {
        memory_id: memory.memory_id,
        content: memory.content,
        type: memory.memory_type,
        importance: memory.importance_score,
        timestamp: memory.timestamp
      }
    });
  } catch (error) {
    console.error('[Dashboard] Error storing memory:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/memories/search
 * Semantic search for memories
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 * - query: Search query (required)
 * - limit: Number of results (default: 5)
 * - min_score: Minimum similarity score (default: 0.7)
 */
app.get('/api/memories/search', async (req, res) => {
  try {
    const { agent_wallet, query, limit, min_score } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    if (!query) {
      return res.status(400).json({ error: 'query is required' });
    }

    const manager = getMemoryManager();
    const memories = await manager.retrieveMemories(agent_wallet, query, {
      limit: limit ? parseInt(limit) : 5,
      min_score: min_score ? parseFloat(min_score) : 0.7
    });

    res.json({
      query,
      count: memories.length,
      memories: memories.map(m => ({
        memory_id: m.memory_id,
        content: m.content,
        type: m.memory_type,
        importance: m.importance_score,
        similarity_score: m.similarity_score,
        timestamp: m.timestamp,
        accessed_count: m.accessed_count
      }))
    });
  } catch (error) {
    console.error('[Dashboard] Error searching memories:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/memories/recent
 * List recent memories
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 * - limit: Number of results (default: 10)
 * - type: Filter by memory type (optional)
 */
app.get('/api/memories/recent', async (req, res) => {
  try {
    const { agent_wallet, limit, type } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const manager = getMemoryManager();
    let memories;

    if (type) {
      memories = await manager.retriever.getByType(agent_wallet, type);
      memories = memories.slice(0, limit ? parseInt(limit) : 10);
    } else {
      memories = await manager.retriever.getRecent(
        agent_wallet,
        limit ? parseInt(limit) : 10
      );
    }

    res.json({
      count: memories.length,
      memories: memories.map(m => ({
        memory_id: m.memory_id,
        content: m.content,
        type: m.memory_type,
        importance: m.importance_score,
        timestamp: m.timestamp,
        accessed_count: m.accessed_count,
        session_id: m.session_id
      }))
    });
  } catch (error) {
    console.error('[Dashboard] Error fetching recent memories:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * DELETE /api/memories/:id
 * Delete a specific memory
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 */
app.delete('/api/memories/:id', async (req, res) => {
  try {
    const { agent_wallet } = req.query;
    const memoryId = req.params.id;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    if (!memoryId) {
      return res.status(400).json({ error: 'memory_id is required' });
    }

    const manager = getMemoryManager();
    await manager.deleteMemory(agent_wallet, memoryId);

    res.json({
      success: true,
      message: `Memory ${memoryId} deleted successfully`
    });
  } catch (error) {
    console.error('[Dashboard] Error deleting memory:', error);
    res.status(500).json({
      error: error.message,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});

/**
 * GET /api/memories/stats
 * Get memory statistics for an agent
 *
 * Query params:
 * - agent_wallet: Agent wallet address (required)
 */
app.get('/api/memories/stats', async (req, res) => {
  try {
    const { agent_wallet } = req.query;

    if (!agent_wallet) {
      return res.status(400).json({ error: 'agent_wallet is required' });
    }

    const manager = getMemoryManager();
    const stats = await manager.getMemoryStats(agent_wallet);

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

    const manager = getMemoryManager();
    const paymentRequest = await manager.createPaymentRequest(agent_wallet);

    res.json({
      success: true,
      payment_request: paymentRequest,
      instructions: 'Send 0.5 USDT via x402 protocol, then call /api/x402/verify with tx_hash',
      pricing: {
        amount: '0.5 USDT/month',
        features: [
          'Unlimited memory storage',
          'Permanent retention',
          'Advanced semantic search',
          'Memory relationship mapping'
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

    const manager = getMemoryManager();
    const result = await manager.verifyPayment(request_id, tx_hash, agent_wallet);

    res.json({
      success: true,
      ...result,
      message: 'Payment verified! Pro tier activated - unlimited memory storage.'
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

    const manager = getMemoryManager();
    const license = manager.checkLicense(agentWallet);

    res.json({
      agent_wallet: agentWallet,
      ...license,
      pricing: {
        pro_monthly: '0.5 USDT/month',
        features: [
          'Unlimited memory storage',
          'Permanent retention',
          'Advanced semantic search',
          'Memory relationship mapping'
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
  console.log(`  OpenClaw Memory System - REST API Dashboard`);
  console.log(`${'='.repeat(70)}`);
  console.log(`  Status: Running`);
  console.log(`  URL: http://localhost:${port}`);
  console.log(`  Version: 1.0.0`);
  console.log(`${'='.repeat(70)}\n`);
  console.log(`  API Endpoints:`);
  console.log(`    POST   /api/memories              Store new memory`);
  console.log(`    GET    /api/memories/search       Semantic search`);
  console.log(`    GET    /api/memories/recent       List recent memories`);
  console.log(`    DELETE /api/memories/:id          Delete memory`);
  console.log(`    GET    /api/memories/stats        Get statistics`);
  console.log(`    POST   /api/x402/subscribe        Create payment request`);
  console.log(`    POST   /api/x402/verify           Verify payment`);
  console.log(`    GET    /api/x402/license/:wallet  Check license status`);
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  Press Ctrl+C to stop\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down Memory System dashboard...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\n🛑 Shutting down Memory System dashboard...');
  process.exit(0);
});
