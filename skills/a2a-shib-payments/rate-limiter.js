/**
 * Rate Limiting System
 * Protects agent from abuse and DoS
 */

class RateLimiter {
  constructor(config = {}) {
    this.config = {
      windowMs: config.windowMs || 60000, // 1 minute
      maxRequests: config.maxRequests || 10,
      maxPayments: config.maxPayments || 3,
      maxPaymentValue: config.maxPaymentValue || 500, // SHIB per window
      ...config
    };

    this.requests = new Map(); // agentId -> [timestamps]
    this.payments = new Map(); // agentId -> [{ timestamp, amount }]
  }

  /**
   * Check if request is allowed
   */
  checkRequest(agentId) {
    const now = Date.now();
    const windowStart = now - this.config.windowMs;

    // Clean old entries
    if (!this.requests.has(agentId)) {
      this.requests.set(agentId, []);
    }

    const agentRequests = this.requests.get(agentId);
    const recentRequests = agentRequests.filter(ts => ts > windowStart);
    
    if (recentRequests.length >= this.config.maxRequests) {
      const oldestRequest = recentRequests[0];
      const retryAfter = Math.ceil((oldestRequest + this.config.windowMs - now) / 1000);
      
      return {
        allowed: false,
        reason: 'Rate limit exceeded',
        retryAfter,
        limit: this.config.maxRequests,
        remaining: 0
      };
    }

    // Record request
    recentRequests.push(now);
    this.requests.set(agentId, recentRequests);

    return {
      allowed: true,
      limit: this.config.maxRequests,
      remaining: this.config.maxRequests - recentRequests.length
    };
  }

  /**
   * Check if payment is allowed (stricter limits)
   */
  checkPayment(agentId, amount) {
    const now = Date.now();
    const windowStart = now - this.config.windowMs;

    // Clean old entries
    if (!this.payments.has(agentId)) {
      this.payments.set(agentId, []);
    }

    const agentPayments = this.payments.get(agentId);
    const recentPayments = agentPayments.filter(p => p.timestamp > windowStart);

    // Check payment count
    if (recentPayments.length >= this.config.maxPayments) {
      const oldestPayment = recentPayments[0];
      const retryAfter = Math.ceil((oldestPayment.timestamp + this.config.windowMs - now) / 1000);
      
      return {
        allowed: false,
        reason: 'Payment rate limit exceeded',
        retryAfter,
        limit: this.config.maxPayments,
        remaining: 0
      };
    }

    // Check payment volume
    const totalValue = recentPayments.reduce((sum, p) => sum + p.amount, 0);
    if (totalValue + amount > this.config.maxPaymentValue) {
      return {
        allowed: false,
        reason: 'Payment volume limit exceeded',
        limit: this.config.maxPaymentValue,
        current: totalValue,
        requested: amount
      };
    }

    // Record payment
    recentPayments.push({ timestamp: now, amount });
    this.payments.set(agentId, recentPayments);

    return {
      allowed: true,
      limit: this.config.maxPayments,
      remaining: this.config.maxPayments - recentPayments.length,
      volumeRemaining: this.config.maxPaymentValue - (totalValue + amount)
    };
  }

  /**
   * Express middleware
   */
  middleware() {
    return (req, res, next) => {
      const agentId = req.agentAuth?.agentId || 'anonymous';
      
      const check = this.checkRequest(agentId);
      
      // Add rate limit headers
      res.setHeader('X-RateLimit-Limit', check.limit);
      res.setHeader('X-RateLimit-Remaining', check.remaining);
      
      if (!check.allowed) {
        res.setHeader('Retry-After', check.retryAfter);
        return res.status(429).json({
          jsonrpc: '2.0',
          error: {
            code: -32003,
            message: check.reason,
            data: {
              retryAfter: check.retryAfter,
              limit: check.limit
            }
          },
          id: req.body?.id || null
        });
      }

      next();
    };
  }

  /**
   * Get stats for agent
   */
  getStats(agentId) {
    const now = Date.now();
    const windowStart = now - this.config.windowMs;

    const requests = this.requests.get(agentId) || [];
    const payments = this.payments.get(agentId) || [];

    const recentRequests = requests.filter(ts => ts > windowStart);
    const recentPayments = payments.filter(p => p.timestamp > windowStart);
    const totalValue = recentPayments.reduce((sum, p) => sum + p.amount, 0);

    return {
      requests: {
        count: recentRequests.length,
        limit: this.config.maxRequests,
        remaining: this.config.maxRequests - recentRequests.length
      },
      payments: {
        count: recentPayments.length,
        limit: this.config.maxPayments,
        remaining: this.config.maxPayments - recentPayments.length,
        totalValue,
        volumeLimit: this.config.maxPaymentValue,
        volumeRemaining: this.config.maxPaymentValue - totalValue
      }
    };
  }
}

module.exports = { RateLimiter };
