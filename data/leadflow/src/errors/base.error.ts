/**
 * Custom error classes
 */

/**
 * Base error for all LeadFlow errors
 */
export class LeadFlowError extends Error {
  constructor(
    message: string,
    public code: string,
    public isRetryable: boolean = true,
    public metadata?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'LeadFlowError';
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      isRetryable: this.isRetryable,
      metadata: this.metadata,
    };
  }
}

/**
 * Error from a scraper
 */
export class ScraperError extends LeadFlowError {
  constructor(
    message: string,
    public source: string,
    isRetryable = true,
    metadata?: Record<string, unknown>
  ) {
    super(
      message,
      `SCRAPER_${source.toUpperCase().replace(/\s+/g, '_')}`,
      isRetryable,
      metadata
    );
    this.name = 'ScraperError';
  }
}

/**
 * Rate limit hit
 */
export class RateLimitError extends LeadFlowError {
  constructor(
    public retryAfterMs: number,
    source: string
  ) {
    super(
      `Rate limited by ${source}. Retry after ${retryAfterMs}ms`,
      'RATE_LIMITED',
      true,
      { retryAfterMs, source }
    );
    this.name = 'RateLimitError';
  }
}

/**
 * Anti-bot detection triggered
 */
export class BlockedError extends LeadFlowError {
  constructor(
    source: string,
    public blockType: 'captcha' | 'ip_block' | 'fingerprint' | 'unknown' = 'unknown'
  ) {
    super(
      `Blocked by ${source}: ${blockType}`,
      'BLOCKED',
      true, // May be retryable with different proxy
      { source, blockType }
    );
    this.name = 'BlockedError';
  }
}

/**
 * Error from enrichment API
 */
export class EnrichmentError extends LeadFlowError {
  constructor(
    message: string,
    public provider: string,
    isRetryable = true,
    metadata?: Record<string, unknown>
  ) {
    super(
      message,
      `ENRICHMENT_${provider.toUpperCase()}`,
      isRetryable,
      metadata
    );
    this.name = 'EnrichmentError';
  }
}

/**
 * Missing required configuration
 */
export class ConfigurationError extends LeadFlowError {
  constructor(message: string, public configKey?: string) {
    super(message, 'CONFIGURATION', false, { configKey });
    this.name = 'ConfigurationError';
  }
}

/**
 * Database error
 */
export class DatabaseError extends LeadFlowError {
  constructor(
    message: string,
    public operation: string,
    isRetryable = true,
    metadata?: Record<string, unknown>
  ) {
    super(message, `DATABASE_${operation.toUpperCase()}`, isRetryable, metadata);
    this.name = 'DatabaseError';
  }
}

/**
 * Validation error
 */
export class ValidationError extends LeadFlowError {
  constructor(message: string, public field?: string) {
    super(message, 'VALIDATION', false, { field });
    this.name = 'ValidationError';
  }
}
