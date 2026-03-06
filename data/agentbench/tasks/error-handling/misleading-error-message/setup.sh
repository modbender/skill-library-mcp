#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"

cd "$WORKSPACE"
git init -q
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

# ── lib/session-cache.js ─────────────────────────────────────────────────────
mkdir -p lib

cat > lib/session-cache.js << 'SESSION_CACHE_EOF'
/**
 * Simple in-memory session cache with TTL.
 * Sessions expire after 30 minutes of inactivity.
 */
class SessionCache {
  constructor(ttlMs = 30 * 60 * 1000) {
    this.cache = new Map();
    this.ttlMs = ttlMs;
  }

  set(sessionId, userData) {
    this.cache.set(sessionId, {
      data: userData,
      expires: Date.now() + this.ttlMs
    });
  }

  get(sessionId) {
    const entry = this.cache.get(sessionId);
    if (!entry) return undefined;
    if (Date.now() > entry.expires) {
      this.cache.delete(sessionId);
      return undefined;  // Expired — returns undefined
    }
    return entry.data;
  }

  clear(sessionId) {
    this.cache.delete(sessionId);
  }
}

module.exports = SessionCache;
SESSION_CACHE_EOF

# ── middleware/auth.js ───────────────────────────────────────────────────────
mkdir -p middleware

cat > middleware/auth.js << 'AUTH_EOF'
/**
 * Authentication middleware.
 * Looks up session from cookie, attaches user to request.
 */
const SessionCache = require('../lib/session-cache');

const sessionCache = new SessionCache();

// Seed some test sessions (for demonstration)
sessionCache.set('session-active-123', { id: 1, name: 'Alice', role: 'admin' });
sessionCache.set('session-active-456', { id: 2, name: 'Bob', role: 'user' });
// Note: these sessions will expire after 30 minutes

function authMiddleware(req, res, next) {
  const sessionId = req.cookies?.sessionId;

  if (!sessionId) {
    return res.status(401).json({ error: 'No session cookie' });
  }

  const user = sessionCache.get(sessionId);

  // BUG: When session has expired, sessionCache.get() returns undefined.
  // We should reject the request, but instead we silently continue
  // without setting req.user, causing downstream crashes.
  if (user) {
    req.user = user;
  }
  // Missing: else { return res.status(401).json({ error: 'Session expired' }); }

  next();
}

module.exports = { authMiddleware, sessionCache };
AUTH_EOF

# ── routes/orders.js ─────────────────────────────────────────────────────────
mkdir -p routes

cat > routes/orders.js << 'ORDERS_EOF'
/**
 * Order routes.
 */

const orders = [
  { id: 1, product: 'Widget', quantity: 5, userId: 1 },
  { id: 2, product: 'Gadget', quantity: 3, userId: 2 },
  { id: 3, product: 'Doohickey', quantity: 1, userId: 1 },
];

function listOrders(req, res) {
  // Filter orders by the authenticated user
  const userOrders = orders.filter(o => o.userId === req.user.id);  // Line ~47 — crashes when req.user is undefined
  res.json(userOrders);
}

function getOrder(req, res) {
  const orderId = parseInt(req.params.id);
  const order = orders.find(o => o.id === orderId && o.userId === req.user.id);
  if (!order) {
    return res.status(404).json({ error: 'Order not found' });
  }
  res.json(order);
}

module.exports = { listOrders, getOrder };
ORDERS_EOF

# ── routes/users.js ──────────────────────────────────────────────────────────
cat > routes/users.js << 'USERS_EOF'
/**
 * User routes.
 */

const users = [
  { id: 1, name: 'Alice', email: 'alice@example.com', role: 'admin' },
  { id: 2, name: 'Bob', email: 'bob@example.com', role: 'user' },
];

function getProfile(req, res) {
  const user = users.find(u => u.id === req.user.id);
  res.json(user);
}

module.exports = { getProfile };
USERS_EOF

# ── app.js ───────────────────────────────────────────────────────────────────
cat > app.js << 'APP_EOF'
/**
 * Main application setup.
 * Note: This is a simplified Express-like structure for demonstration.
 * Not meant to be run directly — see BUG_REPORT.md for the error.
 */

// In production this would be:
// const express = require('express');
// const { authMiddleware } = require('./middleware/auth');
// const { listOrders, getOrder } = require('./routes/orders');
// const { getProfile } = require('./routes/users');
//
// const app = express();
// app.use(authMiddleware);
// app.get('/orders', listOrders);
// app.get('/orders/:id', getOrder);
// app.get('/profile', getProfile);
// app.listen(3000);

console.log('App module loaded. See routes/ and middleware/ for implementation.');
APP_EOF

# ── BUG_REPORT.md ────────────────────────────────────────────────────────────
cat > BUG_REPORT.md << 'BUG_EOF'
# Bug Report: Intermittent 500 Error on /orders

**Reported by:** Customer Support Team
**Date:** 2025-03-15
**Severity:** High
**Frequency:** Intermittent — happens ~20% of the time

## Description
Users report getting 500 Internal Server Error when accessing the orders page.
The error does not happen consistently — it works fine most of the time but
randomly fails for some users.

## Error Details
```
TypeError: Cannot read property 'id' of undefined
    at listOrders (routes/orders.js:14)
    at authMiddleware (middleware/auth.js:25)
    at Layer.handle
```

## Steps to Reproduce
1. Log in to the application
2. Navigate to /orders
3. Sometimes works, sometimes returns 500

## Notes
- The error seems to happen more frequently for users who haven't been
  active for a while (30+ minutes of inactivity).
- Reloading the page or logging out and back in usually fixes it.
- No recent code changes to orders.js.
BUG_EOF

# ── Initial commit ───────────────────────────────────────────────────────────
git add -A
git commit -q -m "initial: add Node.js app with intermittent 500 error"
