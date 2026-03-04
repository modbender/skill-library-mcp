/**
 * Scraper interfaces and types
 */

import type { LeadSource, RawLead, Trade } from './lead.types.js';

/**
 * Configuration for a single scraper
 */
export interface ScraperConfig {
  name: LeadSource;
  enabled: boolean;
  rateLimit: {
    maxRequests: number;
    windowMs: number;
  };
  retryConfig: {
    maxRetries: number;
    baseDelayMs: number;
    maxDelayMs: number;
  };
  circuitBreaker: {
    timeout: number;
    errorThresholdPercentage: number;
    resetTimeout: number;
  };
  proxyRequired: boolean;
  browserRequired: boolean;
}

/**
 * Query parameters for scraping
 */
export interface ScrapeQuery {
  trades: Trade[];
  location: LocationQuery;
  keywords?: string[];
  maxResults?: number;
}

export interface LocationQuery {
  city?: string;
  state?: string;
  county?: string;
  zipCode?: string;
  radius?: number; // miles
  coordinates?: {
    lat: number;
    lng: number;
  };
}

/**
 * Result from a scrape operation
 */
export interface ScrapeResult {
  leads: RawLead[];
  nextPageToken?: string;
  hasMore: boolean;
  totalFound?: number;
}

/**
 * Status of a scrape job
 */
export type ScrapeJobStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

/**
 * A scrape job in the queue
 */
export interface ScrapeJob {
  id: string;
  source: LeadSource;
  query: ScrapeQuery;
  status: ScrapeJobStatus;
  attempts: number;
  error?: string;
  progress?: {
    found: number;
    processed: number;
  };
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
}

/**
 * Base scraper interface - all scrapers must implement this
 */
export interface IScraper {
  readonly name: LeadSource;
  readonly config: ScraperConfig;

  /**
   * Scrape leads from this source
   * Returns an async generator for memory efficiency
   */
  scrape(query: ScrapeQuery): AsyncGenerator<RawLead, void, unknown>;

  /**
   * Test if the scraper can connect to the source
   */
  testConnection(): Promise<boolean>;

  /**
   * Check if the scraper is enabled
   */
  isEnabled(): boolean;

  /**
   * Check if proxies are required but not available
   */
  needsProxy(): boolean;

  /**
   * Clean up resources (browser instances, etc.)
   */
  cleanup(): Promise<void>;
}

/**
 * Options for creating a scraper instance
 */
export interface ScraperOptions {
  httpClient?: unknown; // Will be typed when we create the HTTP client
  proxyRotator?: unknown;
  rateLimiter?: unknown;
  logger?: unknown;
}
