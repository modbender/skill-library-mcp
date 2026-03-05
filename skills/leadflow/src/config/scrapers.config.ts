/**
 * Per-scraper configuration
 */

import { LeadSource } from '../types/index.js';
import type { ScraperConfig } from '../types/index.js';

/**
 * Default scraper configurations
 */
export const scraperConfigs: Record<LeadSource, ScraperConfig> = {
  [LeadSource.GOOGLE_MAPS]: {
    name: LeadSource.GOOGLE_MAPS,
    enabled: true,
    rateLimit: {
      maxRequests: 100, // Google Places API allows 100 QPS
      windowMs: 1000,
    },
    retryConfig: {
      maxRetries: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
    },
    circuitBreaker: {
      timeout: 30000,
      errorThresholdPercentage: 50,
      resetTimeout: 60000,
    },
    proxyRequired: false, // API doesn't need proxy
    browserRequired: false,
  },

  [LeadSource.YELP]: {
    name: LeadSource.YELP,
    enabled: true,
    rateLimit: {
      maxRequests: 5, // Conservative to stay under 5000/day
      windowMs: 1000,
    },
    retryConfig: {
      maxRetries: 3,
      baseDelayMs: 1000,
      maxDelayMs: 30000,
    },
    circuitBreaker: {
      timeout: 30000,
      errorThresholdPercentage: 50,
      resetTimeout: 60000,
    },
    proxyRequired: false, // API doesn't need proxy
    browserRequired: false,
  },

  [LeadSource.LINKEDIN]: {
    name: LeadSource.LINKEDIN,
    enabled: false, // Requires Proxycurl API key
    rateLimit: {
      maxRequests: 5, // Proxycurl limits
      windowMs: 1000,
    },
    retryConfig: {
      maxRetries: 3,
      baseDelayMs: 2000,
      maxDelayMs: 60000,
    },
    circuitBreaker: {
      timeout: 45000,
      errorThresholdPercentage: 30,
      resetTimeout: 120000,
    },
    proxyRequired: false, // Proxycurl handles this
    browserRequired: false,
  },

  [LeadSource.HOMEADVISOR]: {
    name: LeadSource.HOMEADVISOR,
    enabled: false, // No scraper implementation yet
    rateLimit: {
      maxRequests: 10, // Aggressive anti-bot
      windowMs: 60000,
    },
    retryConfig: {
      maxRetries: 5,
      baseDelayMs: 5000,
      maxDelayMs: 120000,
    },
    circuitBreaker: {
      timeout: 60000,
      errorThresholdPercentage: 30,
      resetTimeout: 300000,
    },
    proxyRequired: true,
    browserRequired: true,
  },

  [LeadSource.ANGI]: {
    name: LeadSource.ANGI,
    enabled: false, // No scraper implementation yet
    rateLimit: {
      maxRequests: 10, // Aggressive anti-bot
      windowMs: 60000,
    },
    retryConfig: {
      maxRetries: 5,
      baseDelayMs: 5000,
      maxDelayMs: 120000,
    },
    circuitBreaker: {
      timeout: 60000,
      errorThresholdPercentage: 30,
      resetTimeout: 300000,
    },
    proxyRequired: true,
    browserRequired: true,
  },

  [LeadSource.THUMBTACK]: {
    name: LeadSource.THUMBTACK,
    enabled: false, // No scraper implementation yet
    rateLimit: {
      maxRequests: 10,
      windowMs: 60000,
    },
    retryConfig: {
      maxRetries: 5,
      baseDelayMs: 5000,
      maxDelayMs: 120000,
    },
    circuitBreaker: {
      timeout: 60000,
      errorThresholdPercentage: 30,
      resetTimeout: 300000,
    },
    proxyRequired: true,
    browserRequired: true,
  },

  [LeadSource.BBB]: {
    name: LeadSource.BBB,
    enabled: false, // No scraper implementation yet
    rateLimit: {
      maxRequests: 30, // Less aggressive anti-bot
      windowMs: 60000,
    },
    retryConfig: {
      maxRetries: 3,
      baseDelayMs: 2000,
      maxDelayMs: 30000,
    },
    circuitBreaker: {
      timeout: 30000,
      errorThresholdPercentage: 50,
      resetTimeout: 60000,
    },
    proxyRequired: false, // Usually works without proxy
    browserRequired: true,
  },

  [LeadSource.MANUAL]: {
    name: LeadSource.MANUAL,
    enabled: false, // Not a real scraper
    rateLimit: {
      maxRequests: 0,
      windowMs: 0,
    },
    retryConfig: {
      maxRetries: 0,
      baseDelayMs: 0,
      maxDelayMs: 0,
    },
    circuitBreaker: {
      timeout: 0,
      errorThresholdPercentage: 0,
      resetTimeout: 0,
    },
    proxyRequired: false,
    browserRequired: false,
  },
};

/**
 * Get config for a specific scraper
 */
export function getScraperConfig(source: LeadSource): ScraperConfig {
  return scraperConfigs[source];
}

/**
 * Get all enabled scrapers
 */
export function getEnabledScrapers(): LeadSource[] {
  return Object.values(LeadSource).filter(
    (source) => scraperConfigs[source].enabled
  );
}
