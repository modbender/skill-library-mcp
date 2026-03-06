/**
 * Enrichment service - waterfall email enrichment
 *
 * Tries providers in order: website scrape -> Hunter.io -> Apollo -> Dropcontact
 * Stops on first verified email found.
 */

import { createLogger } from '../utils/logger.js';
import { extractDomain } from '../utils/formatters.js';
import { findLeads, updateLead, getLeadById } from '../storage/lead.repository.js';
import { scrapeWebsiteForEmails } from './email-scraper.js';
import { isHunterConfigured, hunterFindBestEmail } from './hunter.client.js';
import { isApolloConfigured, apolloFindBestEmail } from './apollo.client.js';
import { isDropcontactConfigured, dropcontactFindBestEmail } from './dropcontact.client.js';
import type { Lead, LeadStatus } from '../types/index.js';
import type { EnrichmentProvider } from '../types/enrichment.types.js';

const logger = createLogger('enrichment-service');

export interface EnrichmentStats {
  total: number;
  enriched: number;
  skipped: number;
  failed: number;
  alreadyHadEmail: number;
  noWebsite: number;
  byProvider: Record<string, number>;
}

export interface EnrichLeadResult {
  leadId: string;
  success: boolean;
  email?: string;
  previousEmail?: string;
  confidence?: number;
  provider?: EnrichmentProvider;
  contactName?: string;
  position?: string;
  error?: string;
}

interface WaterfallHit {
  email: string;
  confidence: number;
  provider: EnrichmentProvider;
  firstName?: string;
  lastName?: string;
  position?: string;
}

/**
 * Run waterfall enrichment for a single lead
 */
async function waterfallEnrich(lead: Lead): Promise<WaterfallHit | null> {
  const domain = extractDomain(lead.website);
  if (!domain) return null;

  let scraperFallback: WaterfallHit | null = null;

  // Step 1: Website scrape (free, always available)
  logger.debug(`Waterfall step 1: website scrape for ${domain}`);
  try {
    const scrapeResult = await scrapeWebsiteForEmails(lead.website!);
    if (scrapeResult.success && scrapeResult.emails.length > 0) {
      const best = scrapeResult.emails[0]!;
      if (!best.isGeneric && best.confidence >= 70) {
        logger.info(`Waterfall hit at step 1 (scraper) for ${lead.companyName}: ${best.email}`);
        return {
          email: best.email,
          confidence: best.confidence,
          provider: 'scraper',
        };
      }
      // Keep as fallback
      scraperFallback = {
        email: best.email,
        confidence: best.confidence,
        provider: 'scraper',
      };
    }
  } catch (err) {
    logger.debug(`Waterfall step 1 failed: ${err instanceof Error ? err.message : 'Unknown'}`);
  }

  // Step 2: Hunter.io (if configured)
  if (isHunterConfigured()) {
    logger.debug(`Waterfall step 2: Hunter.io for ${domain}`);
    try {
      const hunterResult = await hunterFindBestEmail(domain);
      if (hunterResult && hunterResult.confidence >= 70) {
        logger.info(`Waterfall hit at step 2 (Hunter) for ${lead.companyName}: ${hunterResult.email}`);
        return {
          email: hunterResult.email,
          confidence: hunterResult.confidence,
          provider: 'hunter',
          firstName: hunterResult.firstName,
          lastName: hunterResult.lastName,
          position: hunterResult.position,
        };
      }
    } catch (err) {
      logger.debug(`Waterfall step 2 failed: ${err instanceof Error ? err.message : 'Unknown'}`);
    }
    await sleep(300);
  }

  // Step 3: Apollo (if configured)
  if (isApolloConfigured()) {
    logger.debug(`Waterfall step 3: Apollo for ${domain}`);
    try {
      const apolloResult = await apolloFindBestEmail(domain, lead.companyName);
      if (apolloResult && apolloResult.confidence >= 60) {
        logger.info(`Waterfall hit at step 3 (Apollo) for ${lead.companyName}: ${apolloResult.email}`);
        return {
          email: apolloResult.email,
          confidence: apolloResult.confidence,
          provider: 'apollo',
          firstName: apolloResult.firstName,
          lastName: apolloResult.lastName,
          position: apolloResult.position,
        };
      }
    } catch (err) {
      logger.debug(`Waterfall step 3 failed: ${err instanceof Error ? err.message : 'Unknown'}`);
    }
    await sleep(300);
  }

  // Step 4: Dropcontact (if configured)
  if (isDropcontactConfigured()) {
    logger.debug(`Waterfall step 4: Dropcontact for ${domain}`);
    try {
      const dropResult = await dropcontactFindBestEmail(lead.companyName, lead.website);
      if (dropResult) {
        logger.info(`Waterfall hit at step 4 (Dropcontact) for ${lead.companyName}: ${dropResult.email}`);
        return {
          email: dropResult.email,
          confidence: dropResult.confidence,
          provider: 'dropcontact',
          firstName: dropResult.firstName,
          lastName: dropResult.lastName,
        };
      }
    } catch (err) {
      logger.debug(`Waterfall step 4 failed: ${err instanceof Error ? err.message : 'Unknown'}`);
    }
  }

  // Return scraper fallback (even generic email is better than nothing)
  return scraperFallback;
}

/**
 * Enrich a single lead using the waterfall
 */
export async function enrichLead(leadId: string): Promise<EnrichLeadResult> {
  const lead = getLeadById(leadId);

  if (!lead) {
    return { leadId, success: false, error: 'Lead not found' };
  }

  if (lead.email) {
    return { leadId, success: true, email: lead.email, previousEmail: lead.email };
  }

  if (!lead.website) {
    return { leadId, success: false, error: 'No website to scrape' };
  }

  try {
    const hit = await waterfallEnrich(lead);

    if (!hit) {
      return { leadId, success: false, error: 'No emails found across all providers' };
    }

    // Build contact name from enrichment data if we don't have one
    let contactName = lead.contactName;
    if (!contactName && hit.firstName) {
      contactName = [hit.firstName, hit.lastName].filter(Boolean).join(' ');
    }

    // Update the lead
    updateLead(leadId, {
      email: hit.email,
      contactName,
      status: 'Enriched' as LeadStatus,
      enrichedAt: new Date(),
      confidence: hit.confidence / 100,
      metadata: {
        ...lead.metadata,
        enrichmentProvider: hit.provider,
        enrichmentPosition: hit.position,
      },
    });

    logger.info(`Enriched ${lead.companyName} via ${hit.provider}: ${hit.email} (${hit.confidence}%)`);

    return {
      leadId,
      success: true,
      email: hit.email,
      confidence: hit.confidence,
      provider: hit.provider,
      contactName,
      position: hit.position,
    };
  } catch (err) {
    logger.error(`Failed to enrich ${leadId}: ${err instanceof Error ? err.message : 'Unknown'}`);
    return {
      leadId,
      success: false,
      error: err instanceof Error ? err.message : 'Unknown error',
    };
  }
}

/**
 * Enrich multiple leads by IDs
 */
export async function enrichLeads(
  leadIds: string[],
  onProgress?: (completed: number, total: number, result: EnrichLeadResult) => void
): Promise<{ results: EnrichLeadResult[]; stats: EnrichmentStats }> {
  const results: EnrichLeadResult[] = [];
  const stats: EnrichmentStats = {
    total: leadIds.length,
    enriched: 0,
    skipped: 0,
    failed: 0,
    alreadyHadEmail: 0,
    noWebsite: 0,
    byProvider: {},
  };

  for (let i = 0; i < leadIds.length; i++) {
    const result = await enrichLead(leadIds[i]!);
    results.push(result);

    if (result.success) {
      if (result.previousEmail) {
        stats.alreadyHadEmail++;
        stats.skipped++;
      } else {
        stats.enriched++;
        if (result.provider) {
          stats.byProvider[result.provider] = (stats.byProvider[result.provider] ?? 0) + 1;
        }
      }
    } else if (result.error === 'No website to scrape') {
      stats.noWebsite++;
      stats.skipped++;
    } else {
      stats.failed++;
    }

    if (onProgress) onProgress(i + 1, leadIds.length, result);
  }

  return { results, stats };
}

/**
 * Enrich all leads matching filters that don't have emails
 */
export async function enrichAllLeads(
  options: { trade?: string; source?: string; limit?: number } = {},
  onProgress?: (completed: number, total: number, result: EnrichLeadResult) => void
): Promise<{ results: EnrichLeadResult[]; stats: EnrichmentStats }> {
  const leads = findLeads({
    trade: options.trade as Lead['trade'],
    source: options.source as Lead['source'],
    hasEmail: false,
    limit: options.limit || 100,
  });

  const leadsWithWebsites = leads.filter((l: Lead) => l.website);

  logger.info(`Starting waterfall enrichment of ${leadsWithWebsites.length} leads`);
  logger.info(`Providers: scraper${isHunterConfigured() ? ' -> Hunter' : ''}${isApolloConfigured() ? ' -> Apollo' : ''}${isDropcontactConfigured() ? ' -> Dropcontact' : ''}`);

  const leadIds = leadsWithWebsites.map((l: Lead) => l.id);
  const result = await enrichLeads(leadIds, onProgress);

  result.stats.noWebsite = leads.length - leadsWithWebsites.length;
  result.stats.skipped += result.stats.noWebsite;
  result.stats.total = leads.length;

  logger.info(`Enrichment complete: ${result.stats.enriched} enriched, ${result.stats.failed} failed, ${result.stats.skipped} skipped`);
  if (Object.keys(result.stats.byProvider).length > 0) {
    logger.info(`By provider: ${JSON.stringify(result.stats.byProvider)}`);
  }

  return result;
}

/**
 * Get enrichment status summary
 */
export function getEnrichmentStatus(): {
  totalLeads: number;
  withEmail: number;
  withoutEmail: number;
  withWebsite: number;
  enrichable: number;
  providers: { name: string; configured: boolean }[];
} {
  const allLeads = findLeads({ limit: 10000 });

  const withEmail = allLeads.filter((l: Lead) => l.email).length;
  const withWebsite = allLeads.filter((l: Lead) => l.website).length;
  const enrichable = allLeads.filter((l: Lead) => l.website && !l.email).length;

  return {
    totalLeads: allLeads.length,
    withEmail,
    withoutEmail: allLeads.length - withEmail,
    withWebsite,
    enrichable,
    providers: [
      { name: 'Website Scraper', configured: true },
      { name: 'Hunter.io', configured: isHunterConfigured() },
      { name: 'Apollo.io', configured: isApolloConfigured() },
      { name: 'Dropcontact', configured: isDropcontactConfigured() },
    ],
  };
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
