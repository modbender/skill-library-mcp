/**
 * Twilio Lookup v2 API client for phone validation
 */

import { config, hasApiKey } from '../config/index.js';
import { createLogger } from '../utils/logger.js';
import type { TwilioLookupResponse } from '../types/index.js';
import type { PhoneLineType } from '../types/lead.types.js';

const logger = createLogger('twilio-client');
const BASE_URL = 'https://lookups.twilio.com/v2/PhoneNumbers';

function getAuth(): string {
  const sid = config.TWILIO_ACCOUNT_SID;
  const token = config.TWILIO_AUTH_TOKEN;
  if (!sid || !token) throw new Error('TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN not configured');
  return Buffer.from(`${sid}:${token}`).toString('base64');
}

export function isTwilioConfigured(): boolean {
  return hasApiKey('TWILIO_ACCOUNT_SID') && hasApiKey('TWILIO_AUTH_TOKEN');
}

/**
 * Lookup a phone number with line type intelligence
 */
export async function lookupPhone(phoneNumber: string): Promise<TwilioLookupResponse> {
  const encoded = encodeURIComponent(phoneNumber);
  const url = `${BASE_URL}/${encoded}?Fields=line_type_intelligence`;

  logger.debug(`Twilio lookup: ${phoneNumber}`);

  const res = await fetch(url, {
    headers: {
      Authorization: `Basic ${getAuth()}`,
    },
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Twilio API error ${res.status}: ${text}`);
  }

  return (await res.json()) as TwilioLookupResponse;
}

/**
 * Map Twilio line type to our PhoneLineType
 */
export function mapLineType(type: string | null | undefined): PhoneLineType {
  if (!type) return 'unknown';
  switch (type) {
    case 'mobile': return 'mobile';
    case 'landline': return 'landline';
    case 'fixedVoip':
    case 'nonFixedVoip':
    case 'voip': return 'voip';
    default: return 'unknown';
  }
}

/**
 * Validate a phone number and return simplified result
 */
export async function validatePhone(phoneNumber: string): Promise<{
  phoneNumber: string;
  valid: boolean;
  lineType: PhoneLineType;
  carrier: string | null;
  nationalFormat: string;
}> {
  const result = await lookupPhone(phoneNumber);
  const lineType = mapLineType(result.line_type_intelligence?.type);
  const carrier = result.line_type_intelligence?.carrier_name ?? null;

  return {
    phoneNumber: result.phone_number,
    valid: result.valid,
    lineType,
    carrier,
    nationalFormat: result.national_format,
  };
}

/**
 * Batch validate phones with rate limiting
 */
export async function batchValidatePhones(
  phones: string[],
  onProgress?: (completed: number, total: number) => void
): Promise<Map<string, { valid: boolean; lineType: PhoneLineType; carrier: string | null }>> {
  const results = new Map<string, { valid: boolean; lineType: PhoneLineType; carrier: string | null }>();

  for (let i = 0; i < phones.length; i++) {
    const phone = phones[i]!;
    try {
      const result = await validatePhone(phone);
      results.set(phone, { valid: result.valid, lineType: result.lineType, carrier: result.carrier });
    } catch (err) {
      logger.error(`Failed to validate ${phone}: ${err instanceof Error ? err.message : 'Unknown'}`);
      results.set(phone, { valid: false, lineType: 'unknown', carrier: null });
    }

    if (onProgress) onProgress(i + 1, phones.length);

    // Rate limit: Twilio allows ~100 req/s
    if (i < phones.length - 1) {
      await new Promise(r => setTimeout(r, 100));
    }
  }

  return results;
}
