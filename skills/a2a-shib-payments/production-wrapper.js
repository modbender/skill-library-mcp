#!/usr/bin/env node

/**
 * Production Security Wrapper for A2A Agent
 * Adds auth, rate limiting, and audit logging to existing agent
 */

const express = require('express');
const { AuthSystem } = require('./auth.js');
const { RateLimiter } = require('./rate-limiter.js');
const { AuditLogger } = require('./audit-logger.js');
const { createProxyMiddleware } = require('http-proxy-middleware');

const UPSTREAM_AGENT = 'http://localhost:8001'; // Point to basic agent
const PRODUCTION_PORT = 8002;

// Initialize security systems
const authSystem = new AuthSystem();
const rateLimiter = new RateLimiter({
  windowMs: 60000,
  maxRequests: 10,
  maxPayments: 3,
  maxPaymentValue: 500
});
const auditLogger = new AuditLogger();

const app = express();

// Parse JSON for inspection
app.use(express.json());

// Log all incoming requests
app.use((req, res, next) => {
  console.log(`📨 ${req.method} ${req.path} from ${req.ip}`);
  next();
});

// Public endpoints (no auth required)
const publicPaths = ['/.well-known/agent-card.json'];

// Authentication middleware
app.use((req, res, next) => {
  if (publicPaths.includes(req.path)) {
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
        message: 'Authentication required - use X-API-Key header'
      },
      id: req.body?.id || null
    });
  }

  auditLogger.logAuth(auth.agentId, true);
  req.agentAuth = auth;
  next();
});

// Rate limiting middleware
app.use((req, res, next) => {
  if (publicPaths.includes(req.path)) {
    return next();
  }

  const agentId = req.agentAuth?.agentId || 'unknown';
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

// Audit logging middleware (log request details)
app.use((req, res, next) => {
  if (req.method === 'POST' && req.body) {
    const agentId = req.agentAuth?.agentId || 'unknown';
    const message = req.body.params?.message?.parts?.[0]?.text;
    
    if (message) {
      // Log the request type
      if (message.includes('balance')) {
        auditLogger.log('balance_request', { agentId, message });
      } else if (message.includes('send')) {
        const match = message.match(/send (\d+(?:\.\d+)?) SHIB to (0x[a-fA-F0-9]{40})/i);
        if (match) {
          const amount = parseFloat(match[1]);
          const recipient = match[2];
          
          // Check authorization
          const authCheck = authSystem.authorize(agentId, 'payment', amount);
          if (!authCheck.authorized) {
            auditLogger.logPaymentRequest(agentId, recipient, amount, false);
            return res.json({
              jsonrpc: '2.0',
              error: {
                code: -32004,
                message: `Payment denied: ${authCheck.reason}`
              },
              id: req.body?.id || null
            });
          }

          // Check payment rate limit
          const paymentCheck = rateLimiter.checkPayment(agentId, amount);
          if (!paymentCheck.allowed) {
            auditLogger.logRateLimitHit(agentId, paymentCheck.reason);
            return res.status(429).json({
              jsonrpc: '2.0',
              error: {
                code: -32003,
                message: `Payment rate limit: ${paymentCheck.reason}`
              },
              id: req.body?.id || null
            });
          }

          auditLogger.logPaymentRequest(agentId, recipient, amount, true);
        }
      }
    }
  }
  
  next();
});

// Intercept responses to log outcomes
app.use((req, res, next) => {
  const originalJson = res.json.bind(res);
  
  res.json = function(body) {
    // Log payment outcomes
    if (body.result?.parts?.[0]?.text) {
      const text = body.result.parts[0].text;
      const txMatch = text.match(/Tx: (0x[a-fA-F0-9]{64})/);
      const gasMatch = text.match(/Gas: \$([\d.]+)/);
      
      if (txMatch && gasMatch) {
        const agentId = req.agentAuth?.agentId || 'unknown';
        auditLogger.log('payment_completed', {
          agentId,
          txHash: txMatch[1],
          gasCost: gasMatch[1]
        });
      }
    }
    
    return originalJson(body);
  };
  
  next();
});

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

// Proxy all other requests to upstream agent
app.use('/', (req, res, next) => {
  const proxy = createProxyMiddleware({
    target: UPSTREAM_AGENT,
    changeOrigin: true,
    onProxyReq: (proxyReq, req, res) => {
      // Forward the authenticated agentId in a header
      if (req.agentAuth) {
        proxyReq.setHeader('X-Agent-ID', req.agentAuth.agentId);
      }
      
      // Re-write body for POST requests
      if (req.body && req.method === 'POST') {
        const bodyData = JSON.stringify(req.body);
        proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
        proxyReq.write(bodyData);
      }
    }
  });
  
  proxy(req, res, next);
});

// Start server
app.listen(PRODUCTION_PORT, () => {
  console.log('🦪 OpenClaw SHIB Payment Agent - Production Wrapper');
  console.log('');
  console.log('✅ Production security layer active!');
  console.log('');
  console.log(`Upstream Agent: ${UPSTREAM_AGENT}`);
  console.log(`Production Port: ${PRODUCTION_PORT}`);
  console.log('');
  console.log('🔒 Security Features:');
  console.log('  ✓ API Key Authentication');
  console.log('  ✓ Rate Limiting (3 payments/min, 500 SHIB/min)');
  console.log('  ✓ Audit Logging (immutable, hash-chained)');
  console.log('  ✓ Payment Authorization');
  console.log('');
  console.log('🔑 API Keys:');
  Object.entries(authSystem.config.agents).forEach(([id, agent]) => {
    if (agent.enabled) {
      console.log(`  ${id}: ${agent.apiKey.substring(0, 20)}...`);
      console.log(`    Permissions: ${agent.permissions.join(', ')}`);
      console.log(`    Max Payment: ${agent.maxPaymentAmount} SHIB`);
    }
  });
  console.log('');
  
  auditLogger.log('wrapper_start', {
    upstream: UPSTREAM_AGENT,
    port: PRODUCTION_PORT,
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down production wrapper...');
  auditLogger.log('wrapper_stop', { timestamp: new Date().toISOString() });
  process.exit(0);
});
