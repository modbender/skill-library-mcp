/**
 * Lead scoring system - composite 0-100 score
 *
 * Signals:
 *   +25  Has verified email
 *   +15  Has phone number
 *   +10  Has website
 *   +10  Rating >= 4.0
 *   +10  Review count > 50
 *   +5   Has full address
 *   +10  Contact name found
 *   +5   Non-generic email (personal)
 *   +5   Phone is mobile (higher reachability)
 *   +5   Multiple sources confirmed
 */

import { createLogger } from '../utils/logger.js';
import { findLeads, updateLead } from '../storage/lead.repository.js';
import type { Lead } from '../types/index.js';

const logger = createLogger('lead-scorer');

export interface ScoreBreakdown {
  total: number;
  signals: { name: string; points: number; met: boolean }[];
}

/**
 * Generic email prefixes (score penalty)
 */
const GENERIC_PREFIXES = [
  'info@', 'contact@', 'hello@', 'support@', 'sales@',
  'admin@', 'office@', 'mail@', 'help@', 'enquiries@',
  'inquiries@', 'feedback@', 'noreply@', 'no-reply@',
];

/**
 * Calculate a lead's score with breakdown
 */
export function scoreLead(lead: Lead): ScoreBreakdown {
  const signals: ScoreBreakdown['signals'] = [];
  let total = 0;

  // Has verified email (+25)
  const hasVerifiedEmail = lead.emailVerified === true;
  signals.push({ name: 'Verified email', points: 25, met: hasVerifiedEmail });
  if (hasVerifiedEmail) total += 25;

  // Has phone (+15)
  const hasPhone = Boolean(lead.phone);
  signals.push({ name: 'Has phone', points: 15, met: hasPhone });
  if (hasPhone) total += 15;

  // Has website (+10)
  const hasWebsite = Boolean(lead.website);
  signals.push({ name: 'Has website', points: 10, met: hasWebsite });
  if (hasWebsite) total += 10;

  // Rating >= 4.0 (+10)
  const goodRating = (lead.rating ?? 0) >= 4.0;
  signals.push({ name: 'Rating >= 4.0', points: 10, met: goodRating });
  if (goodRating) total += 10;

  // Review count > 50 (+10)
  const manyReviews = (lead.reviewCount ?? 0) > 50;
  signals.push({ name: 'Reviews > 50', points: 10, met: manyReviews });
  if (manyReviews) total += 10;

  // Full address (+5)
  const hasFullAddress = Boolean(lead.address && lead.city && lead.state);
  signals.push({ name: 'Full address', points: 5, met: hasFullAddress });
  if (hasFullAddress) total += 5;

  // Contact name (+10)
  const hasContact = Boolean(lead.contactName);
  signals.push({ name: 'Contact name', points: 10, met: hasContact });
  if (hasContact) total += 10;

  // Non-generic email (+5)
  const hasNonGenericEmail = Boolean(
    lead.email &&
    !GENERIC_PREFIXES.some(prefix => lead.email!.toLowerCase().startsWith(prefix))
  );
  signals.push({ name: 'Personal email', points: 5, met: hasNonGenericEmail });
  if (hasNonGenericEmail) total += 5;

  // Mobile phone (+5)
  const hasMobilePhone = lead.phoneType === 'mobile';
  signals.push({ name: 'Mobile phone', points: 5, met: hasMobilePhone });
  if (hasMobilePhone) total += 5;

  // Multi-source confirmed (+5)
  const multiSource = (lead.metadata?.mergedFrom?.length ?? 0) > 0;
  signals.push({ name: 'Multi-source', points: 5, met: multiSource });
  if (multiSource) total += 5;

  return { total: Math.min(100, total), signals };
}

/**
 * Score a single lead and persist
 */
export function scoreAndUpdateLead(lead: Lead): ScoreBreakdown {
  const breakdown = scoreLead(lead);
  updateLead(lead.id, { leadScore: breakdown.total });
  return breakdown;
}

export interface ScoringStats {
  total: number;
  scored: number;
  averageScore: number;
  distribution: { range: string; count: number }[];
}

/**
 * Score all leads matching filters
 */
export function scoreAllLeads(
  options: { trade?: string; source?: string; limit?: number } = {},
  onProgress?: (completed: number, total: number) => void
): ScoringStats {
  const leads = findLeads({
    trade: options.trade as Lead['trade'],
    source: options.source as Lead['source'],
    limit: options.limit || 10000,
  });

  let totalScore = 0;
  const distribution = { '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0 };

  for (let i = 0; i < leads.length; i++) {
    const lead = leads[i]!;
    const breakdown = scoreAndUpdateLead(lead);
    totalScore += breakdown.total;

    if (breakdown.total <= 20) distribution['0-20']++;
    else if (breakdown.total <= 40) distribution['21-40']++;
    else if (breakdown.total <= 60) distribution['41-60']++;
    else if (breakdown.total <= 80) distribution['61-80']++;
    else distribution['81-100']++;

    if (onProgress) onProgress(i + 1, leads.length);
  }

  logger.info(`Scored ${leads.length} leads, avg score: ${leads.length > 0 ? Math.round(totalScore / leads.length) : 0}`);

  return {
    total: leads.length,
    scored: leads.length,
    averageScore: leads.length > 0 ? Math.round(totalScore / leads.length) : 0,
    distribution: Object.entries(distribution).map(([range, count]) => ({ range, count })),
  };
}
