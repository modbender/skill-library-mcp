/**
 * ZeroBounce API client for email verification
 */

import { config, hasApiKey } from '../config/index.js';
import { createLogger } from '../utils/logger.js';
import type { ZeroBounceValidateResponse } from '../types/index.js';
import type { EmailVerificationTag } from '../types/lead.types.js';

const logger = createLogger('zerobounce-client');
const BASE_URL = 'https://api.zerobounce.net/v2';

function getApiKey(): string {
  const key = config.ZEROBOUNCE_API_KEY;
  if (!key) throw new Error('ZEROBOUNCE_API_KEY not configured');
  return key;
}

export function isZeroBounceConfigured(): boolean {
  return hasApiKey('ZEROBOUNCE_API_KEY');
}

/**
 * Validate a single email address
 */
export async function validateEmail(email: string): Promise<ZeroBounceValidateResponse> {
  const params = new URLSearchParams({
    api_key: getApiKey(),
    email,
  });

  logger.debug(`ZeroBounce validate: ${email}`);

  const res = await fetch(`${BASE_URL}/validate?${params}`, {
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`ZeroBounce API error ${res.status}: ${text}`);
  }

  return (await res.json()) as ZeroBounceValidateResponse;
}

/**
 * Map ZeroBounce status to our verification tag
 */
export function mapZeroBounceStatus(status: ZeroBounceValidateResponse['status']): EmailVerificationTag {
  switch (status) {
    case 'valid': return 'valid';
    case 'invalid': return 'invalid';
    case 'catch-all': return 'catch_all';
    case 'spamtrap': return 'spam_trap';
    case 'abuse': return 'abuse';
    case 'do_not_mail': return 'do_not_mail';
    case 'unknown':
    default: return 'unknown';
  }
}

/**
 * Verify an email and return a simplified result
 */
export async function verifyEmail(email: string): Promise<{
  email: string;
  isValid: boolean;
  status: EmailVerificationTag;
  freeEmail: boolean;
  didYouMean: string | null;
  domainAgeDays: number | null;
}> {
  const result = await validateEmail(email);
  const tag = mapZeroBounceStatus(result.status);

  return {
    email: result.address,
    isValid: tag === 'valid',
    status: tag,
    freeEmail: result.free_email,
    didYouMean: result.did_you_mean,
    domainAgeDays: result.domain_age_days ? parseInt(result.domain_age_days, 10) : null,
  };
}

/**
 * Batch verify emails (calls validateEmail sequentially with rate limiting)
 */
export async function batchVerifyEmails(
  emails: string[],
  onProgress?: (completed: number, total: number) => void
): Promise<Map<string, { isValid: boolean; status: EmailVerificationTag }>> {
  const results = new Map<string, { isValid: boolean; status: EmailVerificationTag }>();

  for (let i = 0; i < emails.length; i++) {
    const email = emails[i]!;
    try {
      const result = await verifyEmail(email);
      results.set(email, { isValid: result.isValid, status: result.status });
    } catch (err) {
      logger.error(`Failed to verify ${email}: ${err instanceof Error ? err.message : 'Unknown'}`);
      results.set(email, { isValid: false, status: 'unknown' });
    }

    if (onProgress) onProgress(i + 1, emails.length);

    // Rate limit: ZeroBounce allows ~10 req/s on paid plans
    if (i < emails.length - 1) {
      await new Promise(r => setTimeout(r, 150));
    }
  }

  return results;
}
