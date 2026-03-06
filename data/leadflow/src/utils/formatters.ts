/**
 * Data formatting utilities
 */

import { parsePhoneNumber, isValidPhoneNumber } from 'libphonenumber-js';

/**
 * Normalize a phone number to E.164 format
 */
export function normalizePhone(phone: string | undefined): string | undefined {
  if (!phone) return undefined;

  try {
    // Try parsing as US number
    if (isValidPhoneNumber(phone, 'US')) {
      const parsed = parsePhoneNumber(phone, 'US');
      return parsed.format('E.164');
    }

    // Try parsing without country hint
    if (isValidPhoneNumber(phone)) {
      const parsed = parsePhoneNumber(phone);
      return parsed.format('E.164');
    }

    // If invalid, just strip non-digits and add +1 if 10 digits
    const digits = phone.replace(/\D/g, '');
    if (digits.length === 10) {
      return `+1${digits}`;
    }
    if (digits.length === 11 && digits.startsWith('1')) {
      return `+${digits}`;
    }

    return undefined;
  } catch {
    return undefined;
  }
}

/**
 * Format a phone number for display
 */
export function formatPhoneDisplay(phone: string | undefined): string {
  if (!phone) return '';

  try {
    const parsed = parsePhoneNumber(phone, 'US');
    return parsed.formatNational();
  } catch {
    // Fallback: format as (XXX) XXX-XXXX
    const digits = phone.replace(/\D/g, '');
    if (digits.length === 10) {
      return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
    }
    if (digits.length === 11 && digits.startsWith('1')) {
      return `(${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`;
    }
    return phone;
  }
}

/**
 * Normalize a company name for deduplication
 */
export function normalizeCompanyName(name: string): string {
  return name
    .toLowerCase()
    .replace(
      /\b(llc|inc|corp|corporation|co|ltd|company|enterprises?|services?|solutions?|group)\b\.?/gi,
      ''
    )
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Address abbreviation mappings
 */
const ADDRESS_ABBREVIATIONS: Record<string, string> = {
  street: 'st',
  st: 'st',
  avenue: 'ave',
  ave: 'ave',
  road: 'rd',
  rd: 'rd',
  drive: 'dr',
  dr: 'dr',
  lane: 'ln',
  ln: 'ln',
  boulevard: 'blvd',
  blvd: 'blvd',
  court: 'ct',
  ct: 'ct',
  place: 'pl',
  pl: 'pl',
  circle: 'cir',
  cir: 'cir',
  highway: 'hwy',
  hwy: 'hwy',
  parkway: 'pkwy',
  pkwy: 'pkwy',
  apartment: 'apt',
  apt: 'apt',
  suite: 'ste',
  ste: 'ste',
  floor: 'fl',
  fl: 'fl',
  building: 'bldg',
  bldg: 'bldg',
  north: 'n',
  n: 'n',
  south: 's',
  s: 's',
  east: 'e',
  e: 'e',
  west: 'w',
  w: 'w',
};

/**
 * Normalize an address for deduplication
 */
export function normalizeAddress(address: string | undefined): string | undefined {
  if (!address) return undefined;

  let normalized = address.toLowerCase();

  // Replace common abbreviations
  for (const [full, abbrev] of Object.entries(ADDRESS_ABBREVIATIONS)) {
    normalized = normalized.replace(
      new RegExp(`\\b${full}\\.?\\b`, 'gi'),
      abbrev
    );
  }

  // Remove extra whitespace and punctuation
  normalized = normalized
    .replace(/[.,#]/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  return normalized || undefined;
}

/**
 * Extract domain from a URL or website string
 */
export function extractDomain(url: string | undefined): string | undefined {
  if (!url) return undefined;

  try {
    // Add protocol if missing
    let fullUrl = url;
    if (!fullUrl.startsWith('http://') && !fullUrl.startsWith('https://')) {
      fullUrl = `https://${fullUrl}`;
    }

    const parsed = new URL(fullUrl);
    return parsed.hostname.replace(/^www\./, '');
  } catch {
    // Try to extract domain from string
    const match = url.match(
      /(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)/
    );
    return match?.[1];
  }
}

/**
 * Format a full address from components
 */
export function formatFullAddress(parts: {
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
}): string {
  return [parts.address, parts.city, parts.state, parts.zipCode]
    .filter(Boolean)
    .join(', ');
}

/**
 * Parse a contact name into first and last names
 */
export function parseContactName(name: string): {
  firstName: string;
  lastName: string;
} {
  const parts = name.trim().split(/\s+/);

  if (parts.length === 1) {
    return { firstName: parts[0] ?? '', lastName: '' };
  }

  const firstName = parts[0] ?? '';
  const lastName = parts.slice(1).join(' ');

  return { firstName, lastName };
}
