---
id: rate-limit-pro
version: 1.0.0
name: Rate Limit Pro
description: Advanced rate limiting with tiered controls and quota management
author: NeoClaw Team
category: utility
tags:
  - rate-limiting
  - quota
  - throttling
dependencies: []
---

# Rate Limit Pro

Advanced rate limiting with multiple tiers and quota management.

## Implementation

```javascript
class RateLimiter {
  constructor(options = {}) {
    this.tiers = options.tiers || {
      free: { requests: 10, window: 60000 }, // 10 req/min
      basic: { requests: 100, window: 60000 },
      pro: { requests: 1000, window: 60000 }
    };
    this.requests = new Map();
  }

  checkLimit(userId, tier = 'free') {
    const tierConfig = this.tiers[tier];
    if (!tierConfig) {
      return { allowed: false, reason: 'invalid_tier' };
    }

    const now = Date.now();
    const userRequests = this.requests.get(userId) || [];

    // Remove old requests outside window
    const validRequests = userRequests.filter(
      timestamp => now - timestamp < tierConfig.window
    );

    // Check if under limit
    if (validRequests.length >= tierConfig.requests) {
      const oldestRequest = validRequests[0];
      const resetIn = tierConfig.window - (now - oldestRequest);

      return {
        allowed: false,
        reason: 'rate_limit_exceeded',
        limit: tierConfig.requests,
        remaining: 0,
        resetIn: Math.ceil(resetIn / 1000)
      };
    }

    // Add current request
    validRequests.push(now);
    this.requests.set(userId, validRequests);

    return {
      allowed: true,
      limit: tierConfig.requests,
      remaining: tierConfig.requests - validRequests.length,
      resetIn: Math.ceil(tierConfig.window / 1000)
    };
  }

  resetUser(userId) {
    this.requests.delete(userId);
  }

  getStats(userId) {
    const userRequests = this.requests.get(userId) || [];
    return {
      totalRequests: userRequests.length,
      oldestRequest: userRequests[0] || null,
      newestRequest: userRequests[userRequests.length - 1] || null
    };
  }
}

// Export for OpenClaw
module.exports = { RateLimiter };
```

## Usage

```javascript
const limiter = new skills.rateLimitPro.RateLimiter({
  tiers: {
    free: { requests: 10, window: 60000 },
    pro: { requests: 1000, window: 60000 }
  }
});

const result = limiter.checkLimit('user123', 'free');
if (result.allowed) {
  // Process request
} else {
  console.log(`Rate limit exceeded. Reset in ${result.resetIn}s`);
}
```

## Configuration

```json
{
  "tiers": {
    "free": { "requests": 10, "window": 60000 },
    "basic": { "requests": 100, "window": 60000 },
    "pro": { "requests": 1000, "window": 60000 }
  }
}
```
