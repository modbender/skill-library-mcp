/**
 * Lead deduplication with fuzzy matching
 */

import Fuse from 'fuse.js';
import {
  normalizeCompanyName,
  normalizePhone,
  normalizeAddress,
} from '../../utils/formatters.js';
import { createLogger } from '../../utils/logger.js';
import type { Lead, RawLead } from '../../types/index.js';

const logger = createLogger('deduplication');

/**
 * Result of a duplicate check
 */
export interface DuplicateResult {
  match: Lead;
  confidence: number;
  reason: 'exact_phone' | 'exact_website' | 'exact_source_id' | 'fuzzy_name' | 'fuzzy_match';
}

/**
 * Deduplication matcher using Fuse.js for fuzzy matching
 */
export class LeadMatcher {
  private fuse: Fuse<Lead>;
  private phoneIndex = new Map<string, Lead>();
  private websiteIndex = new Map<string, Lead>();
  private sourceIdIndex = new Map<string, Lead>();

  constructor(existingLeads: Lead[]) {
    // Build exact match indexes
    for (const lead of existingLeads) {
      if (lead.normalizedPhone) {
        this.phoneIndex.set(lead.normalizedPhone, lead);
      }
      if (lead.website) {
        const domain = this.extractDomain(lead.website);
        if (domain) {
          this.websiteIndex.set(domain, lead);
        }
      }
      if (lead.sourceId && lead.source) {
        this.sourceIdIndex.set(`${lead.source}:${lead.sourceId}`, lead);
      }
    }

    // Build fuzzy search index
    this.fuse = new Fuse(existingLeads, {
      keys: [
        { name: 'normalizedName', weight: 0.5 },
        { name: 'companyName', weight: 0.3 },
        { name: 'address', weight: 0.2 },
      ],
      threshold: 0.3, // Lower = stricter matching
      includeScore: true,
      ignoreLocation: true,
      minMatchCharLength: 3,
    });

    logger.debug(`Initialized matcher with ${existingLeads.length} existing leads`);
  }

  /**
   * Find duplicate of a new lead
   */
  findDuplicate(lead: Lead | RawLead): DuplicateResult | null {
    // 1. Check exact source ID match first
    if (lead.sourceId && lead.source) {
      const key = `${lead.source}:${lead.sourceId}`;
      const match = this.sourceIdIndex.get(key);
      if (match) {
        return { match, confidence: 1.0, reason: 'exact_source_id' };
      }
    }

    // 2. Check exact phone match
    const normalizedPhoneValue =
      'normalizedPhone' in lead ? lead.normalizedPhone : normalizePhone(lead.phone);
    if (normalizedPhoneValue) {
      const match = this.phoneIndex.get(normalizedPhoneValue);
      if (match) {
        return { match, confidence: 0.95, reason: 'exact_phone' };
      }
    }

    // 3. Check exact website match
    if (lead.website) {
      const domain = this.extractDomain(lead.website);
      if (domain) {
        const match = this.websiteIndex.get(domain);
        if (match) {
          return { match, confidence: 0.9, reason: 'exact_website' };
        }
      }
    }

    // 4. Fuzzy name match
    const normalizedName =
      'normalizedName' in lead
        ? lead.normalizedName
        : normalizeCompanyName(lead.companyName);

    const results = this.fuse.search(normalizedName, { limit: 5 });

    for (const result of results) {
      const confidence = 1 - (result.score ?? 0);

      // High confidence fuzzy match
      if (confidence >= 0.7) {
        // Additional verification: check if address is similar
        const normalizedAddressValue =
          'normalizedAddress' in lead
            ? lead.normalizedAddress
            : normalizeAddress(lead.address);

        if (normalizedAddressValue && result.item.normalizedAddress) {
          // If addresses are similar, increase confidence
          const addressSimilarity = this.calculateSimilarity(
            normalizedAddressValue,
            result.item.normalizedAddress
          );
          if (addressSimilarity > 0.6) {
            return {
              match: result.item,
              confidence: Math.min(0.95, confidence + 0.1),
              reason: 'fuzzy_match',
            };
          }
        }

        return { match: result.item, confidence, reason: 'fuzzy_name' };
      }
    }

    return null;
  }

  /**
   * Add a lead to the indexes
   */
  addLead(lead: Lead): void {
    if (lead.normalizedPhone) {
      this.phoneIndex.set(lead.normalizedPhone, lead);
    }
    if (lead.website) {
      const domain = this.extractDomain(lead.website);
      if (domain) {
        this.websiteIndex.set(domain, lead);
      }
    }
    if (lead.sourceId && lead.source) {
      this.sourceIdIndex.set(`${lead.source}:${lead.sourceId}`, lead);
    }

    // Note: Fuse.js doesn't support efficient incremental updates,
    // so we'd need to rebuild the index for large batches
  }

  /**
   * Calculate string similarity (Dice coefficient)
   */
  private calculateSimilarity(s1: string, s2: string): number {
    if (s1 === s2) return 1;
    if (s1.length < 2 || s2.length < 2) return 0;

    const bigrams1 = this.getBigrams(s1);
    const bigrams2 = this.getBigrams(s2);

    let intersection = 0;
    for (const bigram of bigrams1) {
      if (bigrams2.has(bigram)) {
        intersection++;
        bigrams2.delete(bigram); // Count each bigram only once
      }
    }

    return (2 * intersection) / (s1.length - 1 + s2.length - 1);
  }

  /**
   * Get bigrams (character pairs) from a string
   */
  private getBigrams(s: string): Set<string> {
    const bigrams = new Set<string>();
    for (let i = 0; i < s.length - 1; i++) {
      bigrams.add(s.slice(i, i + 2));
    }
    return bigrams;
  }

  /**
   * Extract domain from URL
   */
  private extractDomain(url: string): string | null {
    try {
      let fullUrl = url;
      if (!fullUrl.startsWith('http://') && !fullUrl.startsWith('https://')) {
        fullUrl = `https://${fullUrl}`;
      }
      const parsed = new URL(fullUrl);
      return parsed.hostname.replace(/^www\./, '').toLowerCase();
    } catch {
      return null;
    }
  }
}

/**
 * Merge two leads, preferring non-empty values
 */
export function mergeLeads(canonical: Lead, duplicate: Lead): Lead {
  return {
    ...canonical,
    // Prefer non-empty values
    email: canonical.email || duplicate.email,
    contactName: canonical.contactName || duplicate.contactName,
    phone: canonical.phone || duplicate.phone,
    website: canonical.website || duplicate.website,
    address: canonical.address || duplicate.address,
    city: canonical.city || duplicate.city,
    state: canonical.state || duplicate.state,
    zipCode: canonical.zipCode || duplicate.zipCode,
    // Prefer higher rating/review count
    rating:
      canonical.rating !== undefined && duplicate.rating !== undefined
        ? Math.max(canonical.rating, duplicate.rating)
        : canonical.rating ?? duplicate.rating,
    reviewCount:
      canonical.reviewCount !== undefined && duplicate.reviewCount !== undefined
        ? canonical.reviewCount + duplicate.reviewCount
        : canonical.reviewCount ?? duplicate.reviewCount,
    // Merge notes
    notes: canonical.notes
      ? `${canonical.notes}; Also found on ${duplicate.source}`
      : `Also found on ${duplicate.source}`,
    // Track merged sources
    metadata: {
      ...canonical.metadata,
      mergedFrom: [
        ...(canonical.metadata.mergedFrom ?? []),
        duplicate.id,
      ],
      sources: [
        ...((canonical.metadata.sources as string[]) ?? [canonical.source]),
        duplicate.source,
      ],
    },
  };
}
