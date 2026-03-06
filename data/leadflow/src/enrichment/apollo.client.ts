/**
 * Apollo.io API client for email enrichment
 */

import { config, hasApiKey } from '../config/index.js';
import { createLogger } from '../utils/logger.js';
import type { ApolloPersonSearchResponse } from '../types/index.js';

const logger = createLogger('apollo-client');
const BASE_URL = 'https://api.apollo.io/api/v1';

function getApiKey(): string {
  const key = config.APOLLO_API_KEY;
  if (!key) throw new Error('APOLLO_API_KEY not configured');
  return key;
}

export function isApolloConfigured(): boolean {
  return hasApiKey('APOLLO_API_KEY');
}

/**
 * Search for people at a company domain
 */
export async function apolloPeopleSearch(
  domain: string,
  options?: { companyName?: string; limit?: number }
): Promise<ApolloPersonSearchResponse> {
  const body: Record<string, unknown> = {
    api_key: getApiKey(),
    q_organization_domains: domain,
    page: 1,
    per_page: options?.limit ?? 5,
  };

  if (options?.companyName) {
    body.q_organization_name = options.companyName;
  }

  logger.debug(`Apollo people search: ${domain}`);

  const res = await fetch(`${BASE_URL}/mixed_people/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Apollo API error ${res.status}: ${text}`);
  }

  return (await res.json()) as ApolloPersonSearchResponse;
}

/**
 * Find the best email for a company domain via Apollo
 */
export async function apolloFindBestEmail(
  domain: string,
  companyName?: string
): Promise<{ email: string; confidence: number; firstName?: string; lastName?: string; position?: string } | null> {
  try {
    const result = await apolloPeopleSearch(domain, { companyName, limit: 5 });

    if (!result.people || result.people.length === 0) {
      return null;
    }

    // Prefer verified emails from decision makers
    const withEmail = result.people.filter(p => p.email && p.email_status === 'verified');
    const person = withEmail.length > 0 ? withEmail[0]! : result.people.find(p => p.email);

    if (!person?.email) return null;

    return {
      email: person.email,
      confidence: person.email_status === 'verified' ? 90 : 60,
      firstName: person.first_name,
      lastName: person.last_name,
      position: person.title ?? undefined,
    };
  } catch (err) {
    logger.error(`Apollo find best email failed for ${domain}: ${err instanceof Error ? err.message : 'Unknown'}`);
    return null;
  }
}
