/**
 * Rate Limiter - Phase 3.3
 *
 * Per-host rate limiting with configurable delay and robots.txt crawl-delay.
 * Ensures politeness by spacing requests to the same host.
 */

class RateLimiter {
  constructor(config, robotsManager) {
    this.config = config;
    this.robotsManager = robotsManager;
    this.buckets = new Map(); // hostname -> { lastRequest: timestamp }
  }

  /**
   * Wait until it's acceptable to make a request to the given host
   * @param {string} hostname - Hostname (no scheme, no path)
   */
  async waitForSlot(hostname) {
    const now = Date.now();
    const bucket = this.buckets.get(hostname) || { lastRequest: 0 };
    const delay = await this.getDelay(hostname);
    const timeSinceLast = now - bucket.lastRequest;

    if (timeSinceLast < delay) {
      const waitTime = delay - timeSinceLast;
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }

    bucket.lastRequest = Date.now();
    this.buckets.set(hostname, bucket);
  }

  /**
   * Compute effective delay for a host (ms)
   * Uses Math.max(config delay, robots crawl-delay) to be lenient (more conservative)
   * @param {string} hostname
   * @returns {Promise<number>} Delay in milliseconds
   */
  async getDelay(hostname) {
    const baseDelay = this.config.crawl.delay;
    // robotsManager.getCrawlDelay may be async if it needs to fetch
    const robotsDelay = await this.robotsManager.getCrawlDelay(hostname);
    if (robotsDelay) {
      // robots.txt delay is in seconds, convert to ms
      return Math.max(baseDelay, robotsDelay * 1000);
    }
    return baseDelay;
  }
}

module.exports = RateLimiter;
