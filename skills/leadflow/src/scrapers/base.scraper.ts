/**
 * Base scraper abstract class
 */

import CircuitBreaker from 'opossum';
import pino from 'pino';
import { createLogger } from '../utils/logger.js';
import { HttpClient, createApiClient, createScrapingClient } from '../core/http/client.js';
import {
  TokenBucketRateLimiter,
  createRateLimiter,
} from '../core/http/rate-limiter.js';
import { ProxyRotator, getProxyRotator } from '../core/http/proxy-rotator.js';
import { createCircuitBreaker } from '../core/resilience/circuit-breaker.js';
import { withRetry } from '../core/resilience/retry.js';
import { getScraperConfig } from '../config/scrapers.config.js';
import type {
  IScraper,
  ScraperConfig,
  ScrapeQuery,
  RawLead,
  LeadSource,
} from '../types/index.js';

/**
 * Base class for all scrapers
 */
export abstract class BaseScraper implements IScraper {
  abstract readonly name: LeadSource;

  protected _logger?: pino.Logger;
  protected _httpClient?: HttpClient;
  protected _rateLimiter?: TokenBucketRateLimiter;
  protected _proxyRotator?: ProxyRotator;
  protected _circuitBreaker?: CircuitBreaker<unknown[], unknown>;
  protected _config?: ScraperConfig;
  private _initialized = false;

  /**
   * Lazy initialization - called on first use
   */
  protected initialize(): void {
    if (this._initialized) return;

    // Get config from registry
    this._config = getScraperConfig(this.name);

    // Create logger
    this._logger = createLogger(`scraper:${this.name}`);

    // Create rate limiter
    this._rateLimiter = createRateLimiter(
      this.name,
      this._config.rateLimit.maxRequests,
      this._config.rateLimit.windowMs
    );

    // Get proxy rotator
    this._proxyRotator = getProxyRotator();

    // Create HTTP client based on scraper requirements
    if (this._config.browserRequired) {
      // Browser-based scrapers use scraping client with proxies
      this._httpClient = createScrapingClient(this._rateLimiter, this._proxyRotator);
    } else {
      // API-based scrapers use simpler client
      this._httpClient = createApiClient('', this._rateLimiter);
    }

    this._initialized = true;
    this._logger.debug(`Initialized ${this.name} scraper`);
  }

  /**
   * Get logger (initializes if needed)
   */
  protected get logger(): pino.Logger {
    this.initialize();
    return this._logger!;
  }

  /**
   * Get HTTP client (initializes if needed)
   */
  protected get httpClient(): HttpClient {
    this.initialize();
    return this._httpClient!;
  }

  /**
   * Get rate limiter (initializes if needed)
   */
  protected get rateLimiter(): TokenBucketRateLimiter {
    this.initialize();
    return this._rateLimiter!;
  }

  /**
   * Get proxy rotator (initializes if needed)
   */
  protected get proxyRotator(): ProxyRotator {
    this.initialize();
    return this._proxyRotator!;
  }

  /**
   * Get the scraper configuration
   */
  get config(): ScraperConfig {
    this.initialize();
    return this._config!;
  }

  /**
   * Override config (for testing)
   */
  setConfig(config: Partial<ScraperConfig>): void {
    this.initialize();
    this._config = { ...this._config!, ...config };
  }

  /**
   * Scrape leads from this source
   * Subclasses must implement this
   */
  abstract scrape(query: ScrapeQuery): AsyncGenerator<RawLead, void, unknown>;

  /**
   * Test connection to the source
   */
  abstract testConnection(): Promise<boolean>;

  /**
   * Clean up resources
   */
  async cleanup(): Promise<void> {
    if (this._initialized) {
      this.logger.debug(`Cleaning up ${this.name} scraper`);
    }
    // Subclasses can override for browser cleanup, etc.
  }

  /**
   * Execute a function with retry logic
   */
  protected async withRetry<T>(fn: () => Promise<T>): Promise<T> {
    this.initialize();
    return withRetry(fn, {
      maxRetries: this._config!.retryConfig.maxRetries,
      baseDelayMs: this._config!.retryConfig.baseDelayMs,
      maxDelayMs: this._config!.retryConfig.maxDelayMs,
      onRetry: (error, attempt, delayMs) => {
        this.logger.warn(
          `Retry ${attempt}/${this._config!.retryConfig.maxRetries} after ${delayMs}ms: ${error.message}`
        );
      },
    });
  }

  /**
   * Create a circuit breaker for a function
   */
  protected createCircuitBreaker<T extends (...args: unknown[]) => Promise<unknown>>(
    fn: T,
    cbName: string
  ): CircuitBreaker<Parameters<T>, Awaited<ReturnType<T>>> {
    this.initialize();
    return createCircuitBreaker(fn, {
      name: `${this.name}:${cbName}`,
      timeout: this._config!.circuitBreaker.timeout,
      errorThresholdPercentage: this._config!.circuitBreaker.errorThresholdPercentage,
      resetTimeout: this._config!.circuitBreaker.resetTimeout,
    });
  }

  /**
   * Check if the scraper is enabled
   */
  isEnabled(): boolean {
    this.initialize();
    return this._config!.enabled;
  }

  /**
   * Check if proxies are required but not available
   */
  needsProxy(): boolean {
    this.initialize();
    return this._config!.proxyRequired && !this._proxyRotator!.hasProxies();
  }
}
