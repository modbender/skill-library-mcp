/**
 * Token bucket rate limiter
 */

import { createLogger } from '../../utils/logger.js';
import { sleep } from '../../utils/sleep.js';

const logger = createLogger('rate-limiter');

export interface RateLimiterConfig {
  /** Maximum tokens in the bucket */
  maxTokens: number;
  /** Tokens added per second */
  refillRate: number;
  /** Name for logging */
  name?: string;
}

/**
 * Token bucket rate limiter
 *
 * Allows bursting up to maxTokens, then rate limits to refillRate per second
 */
export class TokenBucketRateLimiter {
  private tokens: number;
  private lastRefill: number;
  private readonly name: string;

  constructor(private config: RateLimiterConfig) {
    this.tokens = config.maxTokens;
    this.lastRefill = Date.now();
    this.name = config.name ?? 'default';
  }

  /**
   * Acquire tokens, waiting if necessary
   */
  async acquire(count: number = 1): Promise<void> {
    this.refill();

    while (this.tokens < count) {
      const waitTime = ((count - this.tokens) / this.config.refillRate) * 1000;
      const actualWait = Math.min(waitTime, 1000); // Check every second max
      logger.debug(
        `[${this.name}] Waiting ${actualWait.toFixed(0)}ms for tokens (have ${this.tokens.toFixed(2)}, need ${count})`
      );
      await sleep(actualWait);
      this.refill();
    }

    this.tokens -= count;
    logger.debug(`[${this.name}] Acquired ${count} tokens (${this.tokens.toFixed(2)} remaining)`);
  }

  /**
   * Try to acquire tokens without waiting
   * Returns true if successful, false if not enough tokens
   */
  tryAcquire(count: number = 1): boolean {
    this.refill();

    if (this.tokens >= count) {
      this.tokens -= count;
      return true;
    }

    return false;
  }

  /**
   * Get current token count
   */
  getTokens(): number {
    this.refill();
    return this.tokens;
  }

  /**
   * Get time until tokens will be available
   */
  getWaitTime(count: number = 1): number {
    this.refill();

    if (this.tokens >= count) {
      return 0;
    }

    return ((count - this.tokens) / this.config.refillRate) * 1000;
  }

  /**
   * Refill tokens based on elapsed time
   */
  private refill(): void {
    const now = Date.now();
    const elapsed = now - this.lastRefill;
    const tokensToAdd = (elapsed / 1000) * this.config.refillRate;

    this.tokens = Math.min(this.config.maxTokens, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }
}

/**
 * Create a rate limiter for a specific source
 */
export function createRateLimiter(
  name: string,
  maxRequests: number,
  windowMs: number
): TokenBucketRateLimiter {
  // Convert window-based rate to tokens per second
  const refillRate = maxRequests / (windowMs / 1000);

  return new TokenBucketRateLimiter({
    maxTokens: maxRequests,
    refillRate,
    name,
  });
}

/**
 * Rate limiter registry - one per source
 */
const limiters = new Map<string, TokenBucketRateLimiter>();

/**
 * Get or create a rate limiter for a source
 */
export function getRateLimiter(
  name: string,
  maxRequests: number,
  windowMs: number
): TokenBucketRateLimiter {
  let limiter = limiters.get(name);

  if (!limiter) {
    limiter = createRateLimiter(name, maxRequests, windowMs);
    limiters.set(name, limiter);
  }

  return limiter;
}
