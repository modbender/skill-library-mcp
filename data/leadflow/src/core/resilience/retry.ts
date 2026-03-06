/**
 * Retry logic with exponential backoff
 */

import { createLogger } from '../../utils/logger.js';
import { sleep, addJitter } from '../../utils/sleep.js';
import { RateLimitError } from '../../errors/index.js';

const logger = createLogger('retry');

export interface RetryConfig {
  /** Maximum number of retries */
  maxRetries: number;
  /** Base delay in milliseconds */
  baseDelayMs: number;
  /** Maximum delay in milliseconds */
  maxDelayMs: number;
  /** Jitter percentage (0-1) */
  jitterPercent?: number;
  /** Error messages that should trigger a retry */
  retryableErrors?: string[];
  /** HTTP status codes that should trigger a retry */
  retryableStatusCodes?: number[];
  /** Callback on retry */
  onRetry?: (error: Error, attempt: number, delayMs: number) => void;
}

const DEFAULT_RETRYABLE_ERRORS = [
  'ECONNRESET',
  'ECONNREFUSED',
  'ETIMEDOUT',
  'ENOTFOUND',
  'socket hang up',
  'network error',
  'timeout',
];

const DEFAULT_RETRYABLE_STATUS_CODES = [
  408, // Request Timeout
  429, // Too Many Requests
  500, // Internal Server Error
  502, // Bad Gateway
  503, // Service Unavailable
  504, // Gateway Timeout
];

/**
 * Check if an error is retryable
 */
function isRetryable(error: Error, config: RetryConfig): boolean {
  const retryableErrors = config.retryableErrors ?? DEFAULT_RETRYABLE_ERRORS;
  const retryableStatusCodes = config.retryableStatusCodes ?? DEFAULT_RETRYABLE_STATUS_CODES;

  // Check error message
  const errorMessage = error.message.toLowerCase();
  for (const retryableError of retryableErrors) {
    if (errorMessage.includes(retryableError.toLowerCase())) {
      return true;
    }
  }

  // Check if it's a rate limit error
  if (error instanceof RateLimitError) {
    return true;
  }

  // Check HTTP status code (axios errors)
  if ('response' in error && typeof error.response === 'object' && error.response !== null) {
    const response = error.response as { status?: number };
    if (response.status && retryableStatusCodes.includes(response.status)) {
      return true;
    }
  }

  // Check if error has isRetryable flag
  if ('isRetryable' in error && typeof error.isRetryable === 'boolean') {
    return error.isRetryable;
  }

  return false;
}

/**
 * Calculate delay for a retry attempt
 */
function calculateDelay(attempt: number, config: RetryConfig): number {
  // Exponential backoff: baseDelay * 2^attempt
  const exponentialDelay = config.baseDelayMs * Math.pow(2, attempt - 1);

  // Cap at maxDelay
  const cappedDelay = Math.min(exponentialDelay, config.maxDelayMs);

  // Add jitter
  const jitterPercent = config.jitterPercent ?? 0.2;
  return addJitter(cappedDelay, jitterPercent);
}

/**
 * Execute a function with retry logic
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  config: RetryConfig
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= config.maxRetries + 1; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry if we've exhausted attempts
      if (attempt > config.maxRetries) {
        logger.warn(`All ${config.maxRetries} retries exhausted`);
        throw lastError;
      }

      // Don't retry non-retryable errors
      if (!isRetryable(lastError, config)) {
        logger.debug(`Error is not retryable: ${lastError.message}`);
        throw lastError;
      }

      // Calculate delay (special handling for rate limits)
      let delayMs: number;
      if (lastError instanceof RateLimitError) {
        delayMs = lastError.retryAfterMs;
      } else {
        delayMs = calculateDelay(attempt, config);
      }

      // Notify callback
      config.onRetry?.(lastError, attempt, delayMs);

      logger.debug(
        `Retry ${attempt}/${config.maxRetries} after ${delayMs}ms: ${lastError.message}`
      );

      await sleep(delayMs);
    }
  }

  // This shouldn't be reached, but TypeScript needs it
  throw lastError ?? new Error('Retry failed');
}

/**
 * Create a retry wrapper with preset config
 */
export function createRetryWrapper(config: RetryConfig) {
  return <T>(fn: () => Promise<T>): Promise<T> => withRetry(fn, config);
}

/**
 * Default retry config for API calls
 */
export const defaultApiRetryConfig: RetryConfig = {
  maxRetries: 3,
  baseDelayMs: 1000,
  maxDelayMs: 30000,
  jitterPercent: 0.2,
};

/**
 * Default retry config for scraping
 */
export const defaultScrapingRetryConfig: RetryConfig = {
  maxRetries: 5,
  baseDelayMs: 2000,
  maxDelayMs: 60000,
  jitterPercent: 0.3,
};
