/**
 * Scrape orchestrator - coordinates scraping from multiple sources
 */

import { createLogger } from '../utils/logger.js';
import { getScraper, getAvailableScrapers, hasScraperFor } from '../scrapers/index.js';
import { createLead, findLeads, updateLead, persistChanges } from '../storage/index.js';
import { LeadMatcher, mergeLeads } from '../core/deduplication/matcher.js';
import type {
  ScrapeQuery,
  RawLead,
  Lead,
  LeadSource,
  Trade,
  LeadStatus,
} from '../types/index.js';

const logger = createLogger('scrape-orchestrator');

export interface ScrapeOptions {
  /** Sources to scrape from */
  sources: LeadSource[];
  /** Trades to search for */
  trades: Trade[];
  /** Location to search */
  location: {
    city?: string;
    county?: string;
    state?: string;
    zipCode?: string;
    radius?: number; // miles
  };
  /** Maximum results per source */
  maxResultsPerSource?: number;
  /** Whether to skip deduplication */
  skipDeduplication?: boolean;
  /** Callback for progress updates */
  onProgress?: (progress: ScrapeProgress) => void;
}

export interface ScrapeProgress {
  source: LeadSource;
  trade?: Trade;
  found: number;
  saved: number;
  duplicates: number;
  status: 'starting' | 'scraping' | 'complete' | 'error';
  error?: string;
}

export interface ScrapeResult {
  totalFound: number;
  totalSaved: number;
  totalDuplicates: number;
  bySource: Record<string, { found: number; saved: number; duplicates: number }>;
  errors: { source: string; error: string }[];
}

/**
 * Orchestrate scraping from multiple sources
 */
export async function runScrape(options: ScrapeOptions): Promise<ScrapeResult> {
  const result: ScrapeResult = {
    totalFound: 0,
    totalSaved: 0,
    totalDuplicates: 0,
    bySource: {},
    errors: [],
  };

  // Load existing leads for deduplication
  const existingLeads = options.skipDeduplication ? [] : findLeads();
  const matcher = new LeadMatcher(existingLeads);

  logger.info(`Starting scrape with ${existingLeads.length} existing leads for deduplication`);

  // Filter to available scrapers
  const availableSources = options.sources.filter((source) => {
    if (!hasScraperFor(source)) {
      logger.warn(`No scraper available for ${source}`);
      return false;
    }
    return true;
  });

  if (availableSources.length === 0) {
    logger.error('No valid scrapers available');
    return result;
  }

  logger.info(`Scraping from: ${availableSources.join(', ')}`);
  logger.info(`Trades: ${options.trades.join(', ')}`);

  // Scrape each source
  for (const source of availableSources) {
    const sourceStats = { found: 0, saved: 0, duplicates: 0 };
    result.bySource[source] = sourceStats;

    try {
      const scraper = getScraper(source);
      if (!scraper) {
        throw new Error(`Could not create scraper for ${source}`);
      }

      // Check if scraper is enabled
      if (!scraper.isEnabled()) {
        logger.info(`Skipping disabled scraper: ${source}`);
        continue;
      }

      // Check if proxy is required but not available
      if (scraper.needsProxy()) {
        logger.warn(`Skipping ${source} - requires proxy but none configured`);
        result.errors.push({
          source,
          error: 'Proxy required but not configured',
        });
        continue;
      }

      // Notify progress
      options.onProgress?.({
        source,
        found: 0,
        saved: 0,
        duplicates: 0,
        status: 'starting',
      });

      // Build query
      const query: ScrapeQuery = {
        trades: options.trades,
        location: options.location,
        maxResults: options.maxResultsPerSource,
      };

      // Test connection first
      const connected = await scraper.testConnection();
      if (!connected) {
        throw new Error(`Could not connect to ${source}`);
      }

      // Scrape leads
      logger.info(`Starting scrape from ${source}`);

      for await (const rawLead of scraper.scrape(query)) {
        sourceStats.found++;
        result.totalFound++;

        // Notify progress
        options.onProgress?.({
          source,
          trade: rawLead.trade,
          found: sourceStats.found,
          saved: sourceStats.saved,
          duplicates: sourceStats.duplicates,
          status: 'scraping',
        });

        // Check for duplicates
        if (!options.skipDeduplication) {
          const duplicate = matcher.findDuplicate(rawLead);
          if (duplicate) {
            sourceStats.duplicates++;
            result.totalDuplicates++;
            logger.debug(
              `Duplicate found: "${rawLead.companyName}" matches "${duplicate.match.companyName}" (${duplicate.reason}, ${(duplicate.confidence * 100).toFixed(0)}%)`
            );

            // Merge data into existing lead
            const merged = mergeLeads(duplicate.match, rawLead as unknown as Lead);
            updateLead(duplicate.match.id, merged);
            continue;
          }
        }

        // Save new lead
        const lead = await createLead(rawLead);
        sourceStats.saved++;
        result.totalSaved++;

        // Add to matcher for future duplicate checks
        matcher.addLead(lead);

        logger.debug(`Saved: ${lead.companyName} (${lead.trade}) from ${lead.source}`);
      }

      // Cleanup scraper
      await scraper.cleanup();

      // Notify complete
      options.onProgress?.({
        source,
        found: sourceStats.found,
        saved: sourceStats.saved,
        duplicates: sourceStats.duplicates,
        status: 'complete',
      });

      logger.info(
        `Completed ${source}: ${sourceStats.found} found, ${sourceStats.saved} saved, ${sourceStats.duplicates} duplicates`
      );
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(`Error scraping ${source}: ${errorMessage}`);
      result.errors.push({ source, error: errorMessage });

      options.onProgress?.({
        source,
        found: sourceStats.found,
        saved: sourceStats.saved,
        duplicates: sourceStats.duplicates,
        status: 'error',
        error: errorMessage,
      });
    }
  }

  // Persist all changes
  await persistChanges();

  logger.info(
    `Scrape complete: ${result.totalFound} found, ${result.totalSaved} saved, ${result.totalDuplicates} duplicates`
  );

  return result;
}

/**
 * Get available sources that can be scraped
 */
export function getScrapableSources(): LeadSource[] {
  return getAvailableScrapers();
}
