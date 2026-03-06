/**
 * Dropcontact API client for email enrichment
 */

import { config, hasApiKey } from '../config/index.js';
import { createLogger } from '../utils/logger.js';
import type { DropcontactEnrichResponse } from '../types/index.js';

const logger = createLogger('dropcontact-client');
const BASE_URL = 'https://api.dropcontact.com';

function getApiKey(): string {
  const key = config.DROPCONTACT_API_KEY;
  if (!key) throw new Error('DROPCONTACT_API_KEY not configured');
  return key;
}

export function isDropcontactConfigured(): boolean {
  return hasApiKey('DROPCONTACT_API_KEY');
}

/**
 * Enrich a company/person to find email
 */
export async function dropcontactEnrich(
  data: { companyName?: string; website?: string; firstName?: string; lastName?: string }
): Promise<DropcontactEnrichResponse> {
  const payload: Record<string, string>[] = [{}];

  if (data.companyName) payload[0]!.company = data.companyName;
  if (data.website) payload[0]!.website = data.website;
  if (data.firstName) payload[0]!.first_name = data.firstName;
  if (data.lastName) payload[0]!.last_name = data.lastName;

  logger.debug(`Dropcontact enrich: ${data.companyName || data.website}`);

  const res = await fetch(`${BASE_URL}/batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Access-Token': getApiKey(),
    },
    body: JSON.stringify({
      data: payload,
      siren: false,
      language: 'en',
    }),
    signal: AbortSignal.timeout(30000), // Dropcontact can be slow
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Dropcontact API error ${res.status}: ${text}`);
  }

  return (await res.json()) as DropcontactEnrichResponse;
}

/**
 * Find the best email for a company via Dropcontact
 */
export async function dropcontactFindBestEmail(
  companyName: string,
  website?: string
): Promise<{ email: string; confidence: number; firstName?: string; lastName?: string } | null> {
  try {
    const result = await dropcontactEnrich({ companyName, website });

    if (result.error || !result.data || result.data.length === 0) {
      return null;
    }

    const contact = result.data[0]!;
    if (!contact.email?.email) return null;

    const confidence = contact.email.qualification === 'professional' ? 85
      : contact.email.qualification === 'personal' ? 70
      : 50;

    return {
      email: contact.email.email,
      confidence,
      firstName: contact.first_name ?? undefined,
      lastName: contact.last_name ?? undefined,
    };
  } catch (err) {
    logger.error(`Dropcontact find best email failed for ${companyName}: ${err instanceof Error ? err.message : 'Unknown'}`);
    return null;
  }
}
