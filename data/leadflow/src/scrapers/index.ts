/**
 * Re-export scrapers
 */

export * from './base.scraper.js';
export * from './yelp.scraper.js';
export * from './google-maps.scraper.js';

import { YelpScraper } from './yelp.scraper.js';
import { GoogleMapsScraper } from './google-maps.scraper.js';
import type { IScraper, LeadSource } from '../types/index.js';

/**
 * Registry of all available scrapers
 */
const scraperRegistry = new Map<LeadSource, () => IScraper>();

// Register scrapers
scraperRegistry.set('Yelp' as LeadSource, () => new YelpScraper());
scraperRegistry.set('Google Maps' as LeadSource, () => new GoogleMapsScraper());

/**
 * Get a scraper instance by source
 */
export function getScraper(source: LeadSource): IScraper | null {
  const factory = scraperRegistry.get(source);
  return factory ? factory() : null;
}

/**
 * Get all available scraper sources
 */
export function getAvailableScrapers(): LeadSource[] {
  return Array.from(scraperRegistry.keys());
}

/**
 * Check if a scraper is available for a source
 */
export function hasScraperFor(source: LeadSource): boolean {
  return scraperRegistry.has(source);
}
