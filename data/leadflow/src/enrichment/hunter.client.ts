/**
 * Hunter.io API client for email enrichment
 */

import { config, hasApiKey } from '../config/index.js';
import { createLogger } from '../utils/logger.js';
import type {
  HunterDomainSearchResponse,
  HunterEmailFinderResponse,
  HunterEmailVerifierResponse,
} from '../types/index.js';

const logger = createLogger('hunter-client');
const BASE_URL = 'https://api.hunter.io/v2';

function getApiKey(): string {
  const key = config.HUNTER_API_KEY;
  if (!key) throw new Error('HUNTER_API_KEY not configured');
  return key;
}

export function isHunterConfigured(): boolean {
  return hasApiKey('HUNTER_API_KEY');
}

/**
 * Search for emails associated with a domain
 */
export async function hunterDomainSearch(
  domain: string,
  options?: { limit?: number; type?: 'personal' | 'generic' }
): Promise<HunterDomainSearchResponse> {
  const params = new URLSearchParams({
    domain,
    api_key: getApiKey(),
    limit: String(options?.limit ?? 10),
  });
  if (options?.type) params.set('type', options.type);

  const url = `${BASE_URL}/domain-search?${params}`;
  logger.debug(`Hunter domain search: ${domain}`);

  const res = await fetch(url, { signal: AbortSignal.timeout(15000) });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Hunter API error ${res.status}: ${body}`);
  }

  return (await res.json()) as HunterDomainSearchResponse;
}

/**
 * Find an email for a specific person at a domain
 */
export async function hunterEmailFinder(
  domain: string,
  firstName: string,
  lastName: string
): Promise<HunterEmailFinderResponse> {
  const params = new URLSearchParams({
    domain,
    first_name: firstName,
    last_name: lastName,
    api_key: getApiKey(),
  });

  const url = `${BASE_URL}/email-finder?${params}`;
  logger.debug(`Hunter email finder: ${firstName} ${lastName} @ ${domain}`);

  const res = await fetch(url, { signal: AbortSignal.timeout(15000) });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Hunter API error ${res.status}: ${body}`);
  }

  return (await res.json()) as HunterEmailFinderResponse;
}

/**
 * Verify an email address
 */
export async function hunterVerifyEmail(email: string): Promise<HunterEmailVerifierResponse> {
  const params = new URLSearchParams({
    email,
    api_key: getApiKey(),
  });

  const url = `${BASE_URL}/email-verifier?${params}`;
  logger.debug(`Hunter verify email: ${email}`);

  const res = await fetch(url, { signal: AbortSignal.timeout(15000) });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Hunter API error ${res.status}: ${body}`);
  }

  return (await res.json()) as HunterEmailVerifierResponse;
}

/**
 * Find the best email for a company domain, preferring personal emails
 */
export async function hunterFindBestEmail(
  domain: string
): Promise<{ email: string; confidence: number; firstName?: string; lastName?: string; position?: string } | null> {
  try {
    const result = await hunterDomainSearch(domain, { limit: 5, type: 'personal' });

    if (!result.data.emails || result.data.emails.length === 0) {
      // Fall back to generic emails
      const genericResult = await hunterDomainSearch(domain, { limit: 5 });
      if (!genericResult.data.emails || genericResult.data.emails.length === 0) {
        return null;
      }
      const best = genericResult.data.emails[0]!;
      return {
        email: best.value,
        confidence: best.confidence,
        firstName: best.first_name ?? undefined,
        lastName: best.last_name ?? undefined,
        position: best.position ?? undefined,
      };
    }

    // Prefer verified personal emails
    const verified = result.data.emails.filter(e => e.verification?.status === 'valid');
    const best = verified.length > 0 ? verified[0]! : result.data.emails[0]!;

    return {
      email: best.value,
      confidence: best.confidence,
      firstName: best.first_name ?? undefined,
      lastName: best.last_name ?? undefined,
      position: best.position ?? undefined,
    };
  } catch (err) {
    logger.error(`Hunter find best email failed for ${domain}: ${err instanceof Error ? err.message : 'Unknown'}`);
    return null;
  }
}
