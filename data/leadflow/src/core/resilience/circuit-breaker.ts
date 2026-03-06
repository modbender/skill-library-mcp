/**
 * Circuit breaker wrapper using Opossum
 */

import CircuitBreaker from 'opossum';
import { createLogger } from '../../utils/logger.js';

const logger = createLogger('circuit-breaker');

export interface CircuitBreakerConfig {
  /** Name for logging */
  name: string;
  /** Time in ms before timeout error */
  timeout: number;
  /** Error percentage that opens the circuit */
  errorThresholdPercentage: number;
  /** Time in ms before trying again after circuit opens */
  resetTimeout: number;
  /** Minimum requests before circuit can open */
  volumeThreshold?: number;
  /** Fallback function */
  fallback?: (...args: unknown[]) => unknown;
}

/**
 * Circuit breaker state
 */
export type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

/**
 * Wrap a function with circuit breaker protection
 */
export function createCircuitBreaker<T extends (...args: unknown[]) => Promise<unknown>>(
  fn: T,
  config: CircuitBreakerConfig
): CircuitBreaker<Parameters<T>, Awaited<ReturnType<T>>> {
  const breaker = new CircuitBreaker(fn, {
    timeout: config.timeout,
    errorThresholdPercentage: config.errorThresholdPercentage,
    resetTimeout: config.resetTimeout,
    volumeThreshold: config.volumeThreshold ?? 5,
    name: config.name,
  });

  // Set up fallback if provided
  if (config.fallback) {
    breaker.fallback(config.fallback as () => Awaited<ReturnType<T>>);
  }

  // Event logging
  breaker.on('open', () => {
    logger.warn(`[${config.name}] Circuit OPENED - too many failures`);
  });

  breaker.on('halfOpen', () => {
    logger.info(`[${config.name}] Circuit HALF-OPEN - testing recovery`);
  });

  breaker.on('close', () => {
    logger.info(`[${config.name}] Circuit CLOSED - back to normal`);
  });

  breaker.on('reject', () => {
    logger.debug(`[${config.name}] Request rejected - circuit is open`);
  });

  breaker.on('timeout', () => {
    logger.warn(`[${config.name}] Request timed out after ${config.timeout}ms`);
  });

  breaker.on('fallback', () => {
    logger.debug(`[${config.name}] Fallback executed`);
  });

  return breaker as CircuitBreaker<Parameters<T>, Awaited<ReturnType<T>>>;
}

/**
 * Get circuit breaker stats
 */
export function getCircuitStats(breaker: CircuitBreaker) {
  const stats = breaker.stats;
  return {
    state: breaker.opened ? 'OPEN' : breaker.halfOpen ? 'HALF_OPEN' : 'CLOSED',
    successes: stats.successes,
    failures: stats.failures,
    fallbacks: stats.fallbacks,
    rejects: stats.rejects,
    timeouts: stats.timeouts,
    latencyMean: stats.latencyMean,
    latencyP50: stats.percentiles['50'],
    latencyP95: stats.percentiles['95'],
    latencyP99: stats.percentiles['99'],
  };
}

/**
 * Default circuit breaker config for APIs
 */
export const defaultApiCircuitConfig: Omit<CircuitBreakerConfig, 'name'> = {
  timeout: 30000,
  errorThresholdPercentage: 50,
  resetTimeout: 60000,
  volumeThreshold: 5,
};

/**
 * Default circuit breaker config for scraping
 */
export const defaultScrapingCircuitConfig: Omit<CircuitBreakerConfig, 'name'> = {
  timeout: 60000,
  errorThresholdPercentage: 30,
  resetTimeout: 120000,
  volumeThreshold: 3,
};
