/**
 * Circuit breaker for external API calls.
 * States: CLOSED (normal), OPEN (failing, serve stale), HALF_OPEN (testing recovery).
 */
export class CircuitBreaker {
  /**
   * @param {Object} [opts]
   * @param {number} [opts.threshold=5] - Consecutive failures before opening
   * @param {number} [opts.cooldownMs=300000] - Cooldown in ms (default 5min)
   * @param {number} [opts.maxBackoffMs=60000] - Max backoff for retries
   */
  constructor(opts = {}) {
    this.threshold = opts.threshold ?? 5;
    this.cooldownMs = opts.cooldownMs ?? 300_000;
    this.maxBackoffMs = opts.maxBackoffMs ?? 60_000;
    this.state = 'CLOSED';
    this.failures = 0;
    this.lastFailure = 0;
    this.lastResult = undefined;
  }

  /**
   * Execute a function through the circuit breaker.
   * @template T
   * @param {() => Promise<T>} fn - The function to call
   * @returns {Promise<T>}
   * @throws {Error} If circuit is open and no stale data available
   */
  async call(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailure > this.cooldownMs) {
        this.state = 'HALF_OPEN';
      } else {
        if (this.lastResult !== undefined) return this.lastResult;
        throw new Error('Circuit breaker is OPEN and no stale data available');
      }
    }

    try {
      const result = await fn();
      this.lastResult = result;
      this.failures = 0;
      this.state = 'CLOSED';
      return result;
    } catch (err) {
      this.failures++;
      this.lastFailure = Date.now();
      if (this.failures >= this.threshold) {
        this.state = 'OPEN';
      }
      if (this.lastResult !== undefined) return this.lastResult;
      throw err;
    }
  }

  /**
   * Calculate backoff with jitter for retry delay.
   * @param {number} attempt - Attempt number (0-based)
   * @returns {number} Delay in ms
   */
  backoffMs(attempt) {
    const base = Math.min(1000 * Math.pow(2, attempt), this.maxBackoffMs);
    return base + Math.random() * base * 0.1;
  }
}
