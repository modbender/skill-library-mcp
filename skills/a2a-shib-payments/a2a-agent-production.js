#!/usr/bin/env node

/**
 * Production-Hardened A2A SHIB Payment Agent
 * Features:
 * - Authentication & Authorization
 * - Rate Limiting
 * - Audit Logging
 * - Payment Approvals
 * - Security monitoring
 */

const express = require('express');
const { AgentCard, AGENT_CARD_PATH } = require('@a2a-js/sdk');
const { AgentExecutor, DefaultRequestHandler, InMemoryTaskStore } = require('@a2a-js/sdk/server');
const { agentCardHandler, jsonRpcHandler, restHandler, UserBuilder } = require('@a2a-js/sdk/server/express');
const { ShibPaymentAgent, loadConfig } = require('./index.js');
const { AuthSystem } = require('./auth.js');
const { RateLimiter } = require('./rate-limiter.js');
const { AuditLogger } = require('./audit-logger.js');

const config = loadConfig();
const shibAgent = new ShibPaymentAgent(config);

// Initialize security systems
const authSystem = new AuthSystem();
const rateLimiter = new RateLimiter({
  windowMs: 60000, // 1 minute
  maxRequests: 10,
  maxPayments: 3,
  maxPaymentValue: 500 // SHIB
});
const auditLogger = new AuditLogger();

// Log startup
auditLogger.log('agent_start', {
  version: '1.0.0-production',
  wallet: config.walletAddress,
  timestamp: new Date().toISOString()
});

// Agent Card
const agentCard = {
  name: 'OpenClaw SHIB Payment Agent (Production)',
  description: 'Production-hardened AI agent for SHIB payments on Polygon',
  protocolVersion: '0.3.0',
  version: '1.0.0',
  url: 'http://localhost:8002/a2a/jsonrpc',
  
  skills: [
    {
      id: 'shib_payment',
      name: 'SHIB Payment',
      description: 'Send SHIB tokens on Polygon network with security controls',
      tags: ['payment', 'crypto', 'shib', 'polygon', 'production']
    },
    {
      id: 'shib_balance',
      name: 'SHIB Balance',
      description: 'Check SHIB balance on Polygon',
      tags: ['query', 'balance', 'shib']
    }
  ],
  
  capabilities: {
    pushNotifications: false,
    authentication: true,
    rateLimiting: true,
    auditLogging: true
  },
  
  defaultInputModes: ['text'],
  defaultOutputModes: ['text'],
  
  additionalInterfaces: [
    { url: 'http://localhost:8002/a2a/jsonrpc', transport: 'JSONRPC' },
    { url: 'http://localhost:8002/a2a/rest', transport: 'HTTP+JSON' }
  ],
  
  metadata: {
    wallet: config.walletAddress,
    network: 'eip155:137',
    token: 'SHIB',
    tokenContract: '0x6f8a06447ff6fcf75d803135a7de15ce88c1d4ec',
    gasToken: 'POL',
    avgGasCost: '$0.004',
    security: {
      authentication: 'API Key',
      rateLimiting: '3 payments/min, 500 SHIB/min',
      auditLogging: 'Immutable append-only'
    }
  }
};

// Production Executor with security checks
class ProductionShibPaymentExecutor {
  constructor() {
    this.currentAgentId = null; // Set by middleware
  }

  async execute(requestContext, eventBus) {
    const { userMessage, taskId, contextId } = requestContext;
    const text = userMessage.parts[0]?.text || '';
    
    // Extract agent ID (set by middleware before execution)
    const agentId = this.currentAgentId || 'unknown';
    
    console.log(`📨 [${agentId}] Received [${taskId}]: ${text}`);
    
    const createMessage = (text) => ({
      kind: 'message',
      messageId: require('crypto').randomUUID(),
      role: 'agent',
      parts: [{ kind: 'text', text }],
      contextId
    });
    
    // Parse command
    if (text.includes('send') || text.includes('pay')) {
      const match = text.match(/send (\d+(?:\.\d+)?) SHIB to (0x[a-fA-F0-9]{40})/i);
      if (!match) {
        eventBus.publish(createMessage('Usage: send <amount> SHIB to <0xaddress>'));
        eventBus.finished();
        return;
      }

      const amount = parseFloat(match[1]);
      const recipient = match[2];
      
      // Security checks
      const authCheck = authSystem.authorize(agentId, 'payment', amount);
      if (!authCheck.authorized) {
        auditLogger.logPaymentRequest(agentId, recipient, amount, false);
        eventBus.publish(createMessage(`❌ Payment denied: ${authCheck.reason}`));
        eventBus.finished();
        return;
      }

      const rateLimitCheck = rateLimiter.checkPayment(agentId, amount);
      if (!rateLimitCheck.allowed) {
        auditLogger.logRateLimitHit(agentId, rateLimitCheck.reason);
        eventBus.publish(createMessage(`❌ Rate limit: ${rateLimitCheck.reason}\nRetry after ${rateLimitCheck.retryAfter}s`));
        eventBus.finished();
        return;
      }

      // Log approved request
      auditLogger.logPaymentRequest(agentId, recipient, amount, true);

      try {
        const result = await shibAgent.sendPayment(recipient, amount);
        
        // Log successful payment
        auditLogger.logPaymentExecuted(agentId, recipient, amount, result.txHash, result.gasCostUSD);
        
        eventBus.publish(createMessage(
          `✅ Payment sent!\n\nAmount: ${amount} SHIB\nTo: ${recipient}\nTx: ${result.txHash}\nGas: ${result.gasCostUSD}\n\n${result.explorerUrl}\n\n🔒 Audit: Logged`
        ));
      } catch (error) {
        auditLogger.logPaymentFailed(agentId, recipient, amount, error.message);
        eventBus.publish(createMessage(`❌ Payment failed: ${error.message}`));
      }

    } else if (text.includes('balance')) {
      // Check auth
      const authCheck = authSystem.authorize(agentId, 'balance');
      if (!authCheck.authorized) {
        eventBus.publish(createMessage(`❌ Access denied: ${authCheck.reason}`));
        eventBus.finished();
        return;
      }

      try {
        const balance = await shibAgent.getBalance();
        auditLogger.logBalanceCheck(agentId, balance.address, balance.balance);
        
        eventBus.publish(createMessage(
          `💰 SHIB Balance\n\nAddress: ${balance.address}\nBalance: ${balance.balance} SHIB\nNetwork: Polygon`
        ));
      } catch (error) {
        eventBus.publish(createMessage(`❌ Balance check failed: ${error.message}`));
      }

    } else {
      eventBus.publish(createMessage(
        `🦪 SHIB Payment Agent (Production)\n\nCommands:\n- send <amount> SHIB to <address>\n- balance\n\n🔒 Security:\n- API key required (X-API-Key header)\n- Rate limit: 3 payments/min\n- Max payment: Check your agent config\n- All actions logged\n\nExample: send 100 SHIB to 0xDBD846593c1C89014a64bf0ED5802126912Ba99A`
      ));
    }
    
    eventBus.finished();
  }
  
  async cancelTask(taskId, eventBus) {
    console.log(`🛑 Task ${taskId} cancellation requested`);
    auditLogger.log('task_cancelled', { taskId });
  }
}

// Start Server
async function startServer() {
  const app = express();
  const port = 8002;
  
  // Custom auth middleware that integrates with A2A
  app.use((req, res, next) => {
    if (req.path === `/${AGENT_CARD_PATH}`) {
      // Agent card is public
      return next();
    }

    const apiKey = req.headers['x-api-key'] || req.headers['authorization']?.replace('Bearer ', '');
    const auth = authSystem.authenticate(apiKey);
    
    if (!auth.authenticated) {
      auditLogger.logAuth(req.ip, false, auth.error);
      return res.status(401).json({
        jsonrpc: '2.0',
        error: {
          code: -32001,
          message: 'Authentication required',
          data: { hint: 'Include X-API-Key header' }
        },
        id: req.body?.id || null
      });
    }

    auditLogger.logAuth(auth.agentId, true);
    req.agentAuth = auth;
    
    // Attach agentId to request context for executor
    if (req.body && req.body.params) {
      req.body.params.agentId = auth.agentId;
    }
    
    next();
  });

  // Rate limiting
  app.use((req, res, next) => {
    if (req.path === `/${AGENT_CARD_PATH}`) {
      return next();
    }

    const agentId = req.agentAuth?.agentId || 'anonymous';
    const check = rateLimiter.checkRequest(agentId);
    
    res.setHeader('X-RateLimit-Limit', check.limit);
    res.setHeader('X-RateLimit-Remaining', check.remaining);
    
    if (!check.allowed) {
      auditLogger.logRateLimitHit(agentId, check.reason);
      res.setHeader('Retry-After', check.retryAfter);
      return res.status(429).json({
        jsonrpc: '2.0',
        error: {
          code: -32003,
          message: check.reason,
          data: { retryAfter: check.retryAfter }
        },
        id: req.body?.id || null
      });
    }

    next();
  });

  // Set up agent executor
  const executor = new ProductionShibPaymentExecutor();
  const taskStore = new InMemoryTaskStore();
  
  // Custom request handler that passes agentId
  const requestHandler = new DefaultRequestHandler(agentCard, taskStore, executor);

  // Register routes  
  app.get(`/${AGENT_CARD_PATH}`, agentCardHandler({ agentCardProvider: requestHandler }));
  
  // JSON-RPC endpoint (must use app.post with express.json() first)
  const jsonRpcMiddleware = jsonRpcHandler({ requestHandler, userBuilder: UserBuilder.noAuthentication });
  app.post('/a2a/jsonrpc', express.json(), (req, res, next) => {
    // Inject agentId into executor before handling request
    if (req.agentAuth) {
      executor.currentAgentId = req.agentAuth.agentId;
    }
    jsonRpcMiddleware(req, res, next);
  });
  
  // REST endpoint
  app.use('/a2a/rest', express.json(), restHandler({ requestHandler, userBuilder: UserBuilder.noAuthentication }));

  // Admin endpoints
  app.get('/admin/audit/stats', (req, res) => {
    if (req.agentAuth?.agentId !== 'admin') {
      return res.status(403).json({ error: 'Admin only' });
    }
    res.json(auditLogger.getStats());
  });

  app.get('/admin/audit/verify', (req, res) => {
    if (req.agentAuth?.agentId !== 'admin') {
      return res.status(403).json({ error: 'Admin only' });
    }
    res.json(auditLogger.verify());
  });

  app.get('/admin/rate-limits/:agentId', (req, res) => {
    if (req.agentAuth?.agentId !== 'admin') {
      return res.status(403).json({ error: 'Admin only' });
    }
    res.json(rateLimiter.getStats(req.params.agentId));
  });

  // Start listening
  app.listen(port, () => {
    console.log('🦪 OpenClaw SHIB Payment Agent (PRODUCTION)');
    console.log('');
    console.log('✅ Agent is online and secured!');
    console.log('');
    console.log('Agent Info:');
    console.log(`  Name: ${agentCard.name}`);
    console.log(`  Version: ${agentCard.version}`);
    console.log(`  Wallet: ${config.walletAddress}`);
    console.log(`  Network: Polygon (eip155:137)`);
    console.log('');
    console.log('🔒 Security Features:');
    console.log('  ✓ API Key Authentication');
    console.log('  ✓ Rate Limiting (3 payments/min, 500 SHIB/min)');
    console.log('  ✓ Audit Logging (immutable, hash-chained)');
    console.log('  ✓ Payment Authorization');
    console.log('');
    console.log('Endpoints:');
    console.log(`  Agent Card: http://localhost:${port}${AGENT_CARD_PATH}`);
    console.log(`  JSON-RPC:   http://localhost:${port}/a2a/jsonrpc`);
    console.log(`  REST API:   http://localhost:${port}/a2a/rest`);
    console.log('');
    console.log('Admin Endpoints (requires admin API key):');
    console.log(`  Audit Stats:  http://localhost:${port}/admin/audit/stats`);
    console.log(`  Verify Logs:  http://localhost:${port}/admin/audit/verify`);
    console.log(`  Rate Limits:  http://localhost:${port}/admin/rate-limits/:agentId`);
    console.log('');
    
    // Print API keys for configured agents
    console.log('🔑 Configured Agents:');
    const authConfig = authSystem.config;
    Object.entries(authConfig.agents).forEach(([id, agent]) => {
      if (agent.enabled) {
        console.log(`  ${id}:`);
        console.log(`    API Key: ${agent.apiKey}`);
        console.log(`    Permissions: ${agent.permissions.join(', ')}`);
        console.log(`    Max Payment: ${agent.maxPaymentAmount} SHIB`);
      }
    });
    console.log('');
  });
  
  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log('');
    console.log('🛑 Shutting down agent...');
    auditLogger.log('agent_stop', { timestamp: new Date().toISOString() });
    process.exit(0);
  });
}

// CLI
const command = process.argv[2];

if (command === 'start' || !command) {
  startServer().catch(err => {
    console.error('Failed to start agent:', err);
    auditLogger.log('agent_start_failed', { error: err.message });
    process.exit(1);
  });
} else {
  console.log(`
Production SHIB Payment Agent - Usage:

  node a2a-agent-production.js start    - Start the production agent server

Security Features:
  • API Key Authentication - All requests require X-API-Key header
  • Rate Limiting - 10 requests/min, 3 payments/min, 500 SHIB/min
  • Audit Logging - All actions logged in immutable hash chain
  • Payment Authorization - Per-agent payment limits

Configuration:
  • Wallet: Set in ~/.env.local
  • Auth: ./auth-config.json (auto-generated on first run)
  • Logs: ./audit-logs/audit-YYYY-MM-DD.jsonl

Testing:
  curl http://localhost:8002/.well-known/agent-card.json

  curl -X POST http://localhost:8002/a2a/jsonrpc \\
    -H "X-API-Key: <your-key>" \\
    -H "Content-Type: application/json" \\
    -d '{"jsonrpc":"2.0","method":"message/send","params":{"message":{...}},"id":1}'
  `);
}
