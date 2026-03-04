/**
 * Token Bucket Rate Limiter
 * Protects against API rate limits
 */

class RateLimiter {
  constructor(options = {}) {
    this.maxTokens = options.maxTokens || 120;       // Max burst (Gemini paid: 4000 RPM)
    this.refillRate = options.refillRate || 200;     // Tokens per minute (~3.3/sec sustained)
    this.tokens = this.maxTokens;
    this.lastRefill = Date.now();
    this.queue = [];
    this.processing = false;
    this.totalRequests = 0;
    this.throttledRequests = 0;
    this.backoffUntil = 0;
    this.dailyRequests = 0;
    this.dailyLimit = options.dailyLimit || 0;       // 0 = no daily limit (paid tier)
    this.dayStart = this.getToday();
  }
  
  getToday() {
    return new Date().toISOString().split('T')[0];
  }
  
  checkDailyReset() {
    const today = this.getToday();
    if (today !== this.dayStart) {
      this.dailyRequests = 0;
      this.dayStart = today;
    }
  }

  refill() {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000 / 60; // minutes
    const newTokens = elapsed * this.refillRate;
    this.tokens = Math.min(this.maxTokens, this.tokens + newTokens);
    this.lastRefill = now;
  }

  async acquire() {
    this.checkDailyReset();
    this.totalRequests++;
    this.dailyRequests++;
    
    // Hard daily limit - refuse requests (0 = unlimited)
    if (this.dailyLimit > 0 && this.dailyRequests > this.dailyLimit) {
      console.error(`🛑 Daily limit reached (${this.dailyLimit} requests). Refusing.`);
      throw new Error('Daily request limit exceeded');
    }
    
    // Check if we're in backoff
    const now = Date.now();
    if (now < this.backoffUntil) {
      const waitTime = this.backoffUntil - now;
      this.throttledRequests++;
      await this.sleep(waitTime);
    }

    this.refill();

    if (this.tokens >= 1) {
      this.tokens -= 1;
      return true;
    }

    // No tokens available, wait for refill
    this.throttledRequests++;
    const waitTime = ((1 - this.tokens) / this.refillRate) * 60 * 1000;
    await this.sleep(Math.min(waitTime, 10000)); // Max 10s wait
    this.tokens = 0;
    return true;
  }

  // Call this on 429 response
  backoff(retryAfterMs = 10000) {
    this.backoffUntil = Date.now() + retryAfterMs;
    this.tokens = 0; // Drain tokens
    console.log(`⚠️ Rate limited - backing off for ${retryAfterMs}ms`);
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  getStats() {
    this.checkDailyReset();
    return {
      tokens: Math.floor(this.tokens),
      maxTokens: this.maxTokens,
      totalRequests: this.totalRequests,
      throttledRequests: this.throttledRequests,
      throttleRate: this.totalRequests > 0 
        ? (this.throttledRequests / this.totalRequests * 100).toFixed(1) + '%'
        : '0%',
      dailyRequests: this.dailyRequests,
      dailyLimit: this.dailyLimit,
      dailyRemaining: this.dailyLimit - this.dailyRequests,
      inBackoff: Date.now() < this.backoffUntil,
    };
  }
}

// Singleton instance
const globalLimiter = new RateLimiter();

module.exports = { RateLimiter, globalLimiter };
