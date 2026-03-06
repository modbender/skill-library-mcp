/**
 * Lead repository - CRUD operations for leads
 */

import { nanoid } from 'nanoid';
import type { SqlValue } from 'sql.js';
import { query, execute, getChanges, saveDatabase } from './sqlite.client.js';
import {
  normalizeCompanyName,
  normalizePhone,
  normalizeAddress,
} from '../utils/formatters.js';
import { createLogger } from '../utils/logger.js';
import type {
  Lead,
  RawLead,
  LeadFilters,
  LeadStatus,
  LeadMetadata,
} from '../types/index.js';

const logger = createLogger('lead-repository');

/**
 * Database row type
 */
interface LeadRow {
  id: string;
  company_name: string;
  contact_name: string | null;
  email: string | null;
  phone: string | null;
  website: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  trade: string;
  source: string;
  source_url: string | null;
  source_id: string | null;
  rating: number | null;
  review_count: number | null;
  normalized_name: string;
  normalized_phone: string | null;
  normalized_address: string | null;
  status: string;
  notes: string;
  confidence: number;
  duplicate_of: string | null;
  metadata: string;
  scraped_at: string;
  enriched_at: string | null;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
  // Verification & scoring columns
  email_verified: number | null;
  email_verification_status: string | null;
  phone_verified: number | null;
  phone_type: string | null;
  phone_carrier: string | null;
  lead_score: number | null;
}

/**
 * Convert a database row to a Lead object
 */
function rowToLead(row: LeadRow): Lead {
  return {
    id: row.id,
    companyName: row.company_name,
    contactName: row.contact_name ?? undefined,
    email: row.email ?? undefined,
    phone: row.phone ?? undefined,
    website: row.website ?? undefined,
    address: row.address ?? undefined,
    city: row.city ?? undefined,
    state: row.state ?? undefined,
    zipCode: row.zip_code ?? undefined,
    trade: row.trade as Lead['trade'],
    source: row.source as Lead['source'],
    sourceUrl: row.source_url ?? undefined,
    sourceId: row.source_id ?? undefined,
    rating: row.rating ?? undefined,
    reviewCount: row.review_count ?? undefined,
    normalizedName: row.normalized_name,
    normalizedPhone: row.normalized_phone ?? undefined,
    normalizedAddress: row.normalized_address ?? undefined,
    status: row.status as LeadStatus,
    notes: row.notes,
    confidence: row.confidence,
    duplicateOf: row.duplicate_of ?? undefined,
    metadata: JSON.parse(row.metadata) as LeadMetadata,
    scrapedAt: new Date(row.scraped_at),
    enrichedAt: row.enriched_at ? new Date(row.enriched_at) : undefined,
    verifiedAt: row.verified_at ? new Date(row.verified_at) : undefined,
    emailVerified: row.email_verified ? true : undefined,
    emailVerificationStatus: row.email_verification_status as Lead['emailVerificationStatus'],
    phoneVerified: row.phone_verified ? true : undefined,
    phoneType: row.phone_type as Lead['phoneType'],
    phoneCarrier: row.phone_carrier ?? undefined,
    leadScore: row.lead_score ?? undefined,
  };
}

/**
 * Create a new lead from raw scraped data
 */
export async function createLead(raw: RawLead): Promise<Lead> {
  const id = nanoid();
  const normalizedName = normalizeCompanyName(raw.companyName);
  const normalizedPhoneValue = normalizePhone(raw.phone);
  const normalizedAddressValue = normalizeAddress(raw.address);

  const lead: Lead = {
    ...raw,
    id,
    normalizedName,
    normalizedPhone: normalizedPhoneValue,
    normalizedAddress: normalizedAddressValue,
    status: 'New' as LeadStatus,
    notes: '',
    confidence: 0,
    metadata: {},
  };

  execute(
    `INSERT INTO leads (
      id, company_name, contact_name, email, phone, website,
      address, city, state, zip_code, trade, source,
      source_url, source_id, rating, review_count,
      normalized_name, normalized_phone, normalized_address,
      status, notes, confidence, duplicate_of, metadata, scraped_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      lead.id,
      lead.companyName,
      lead.contactName ?? null,
      lead.email ?? null,
      lead.phone ?? null,
      lead.website ?? null,
      lead.address ?? null,
      lead.city ?? null,
      lead.state ?? null,
      lead.zipCode ?? null,
      lead.trade,
      lead.source,
      lead.sourceUrl ?? null,
      lead.sourceId ?? null,
      lead.rating ?? null,
      lead.reviewCount ?? null,
      lead.normalizedName,
      lead.normalizedPhone ?? null,
      lead.normalizedAddress ?? null,
      lead.status,
      lead.notes,
      lead.confidence,
      lead.duplicateOf ?? null,
      JSON.stringify(lead.metadata),
      lead.scrapedAt.toISOString(),
    ]
  );

  logger.debug(`Created lead: ${lead.id} - ${lead.companyName}`);
  return lead;
}

/**
 * Get a lead by ID
 */
export function getLeadById(id: string): Lead | null {
  const rows = query<LeadRow>('SELECT * FROM leads WHERE id = ?', [id]);
  return rows[0] ? rowToLead(rows[0]) : null;
}

/**
 * Find leads matching filters
 */
export function findLeads(filters: LeadFilters = {}): Lead[] {
  const conditions: string[] = [];
  const params: SqlValue[] = [];

  if (filters.status) {
    const statuses = Array.isArray(filters.status)
      ? filters.status
      : [filters.status];
    conditions.push(`status IN (${statuses.map(() => '?').join(', ')})`);
    params.push(...statuses);
  }

  if (filters.trade) {
    const trades = Array.isArray(filters.trade)
      ? filters.trade
      : [filters.trade];
    conditions.push(`trade IN (${trades.map(() => '?').join(', ')})`);
    params.push(...trades);
  }

  if (filters.source) {
    const sources = Array.isArray(filters.source)
      ? filters.source
      : [filters.source];
    conditions.push(`source IN (${sources.map(() => '?').join(', ')})`);
    params.push(...sources);
  }

  if (filters.hasEmail !== undefined) {
    conditions.push(filters.hasEmail ? 'email IS NOT NULL' : 'email IS NULL');
  }

  if (filters.hasPhone !== undefined) {
    conditions.push(filters.hasPhone ? 'phone IS NOT NULL' : 'phone IS NULL');
  }

  if (filters.hasWebsite !== undefined) {
    conditions.push(filters.hasWebsite ? "website IS NOT NULL AND website != ''" : "(website IS NULL OR website = '')");
  }

  // Needs enrichment = has website but no email
  if (filters.needsEnrichment !== undefined && filters.needsEnrichment) {
    conditions.push("website IS NOT NULL AND website != '' AND (email IS NULL OR email = '')");
  }

  if (filters.minConfidence !== undefined) {
    conditions.push('confidence >= ?');
    params.push(filters.minConfidence);
  }

  let sql = 'SELECT * FROM leads';
  if (conditions.length > 0) {
    sql += ` WHERE ${conditions.join(' AND ')}`;
  }
  sql += ' ORDER BY created_at DESC';

  if (filters.limit) {
    sql += ' LIMIT ?';
    params.push(filters.limit);
  }

  if (filters.offset) {
    sql += ' OFFSET ?';
    params.push(filters.offset);
  }

  const rows = query<LeadRow>(sql, params);
  return rows.map(rowToLead);
}

/**
 * Update a lead
 */
export function updateLead(
  id: string,
  updates: Partial<Omit<Lead, 'id'>>
): boolean {
  const setClauses: string[] = [];
  const params: SqlValue[] = [];

  const fieldMap: Record<string, string> = {
    companyName: 'company_name',
    contactName: 'contact_name',
    zipCode: 'zip_code',
    sourceUrl: 'source_url',
    sourceId: 'source_id',
    reviewCount: 'review_count',
    normalizedName: 'normalized_name',
    normalizedPhone: 'normalized_phone',
    normalizedAddress: 'normalized_address',
    duplicateOf: 'duplicate_of',
    scrapedAt: 'scraped_at',
    enrichedAt: 'enriched_at',
    verifiedAt: 'verified_at',
    emailVerified: 'email_verified',
    emailVerificationStatus: 'email_verification_status',
    phoneVerified: 'phone_verified',
    phoneType: 'phone_type',
    phoneCarrier: 'phone_carrier',
    leadScore: 'lead_score',
  };

  for (const [key, value] of Object.entries(updates)) {
    if (key === 'metadata') {
      setClauses.push('metadata = ?');
      params.push(JSON.stringify(value));
    } else if (value instanceof Date) {
      const column = fieldMap[key] ?? key;
      setClauses.push(`${column} = ?`);
      params.push(value.toISOString());
    } else if (typeof value === 'boolean') {
      const column = fieldMap[key] ?? key;
      setClauses.push(`${column} = ?`);
      params.push(value ? 1 : 0);
    } else if (typeof value === 'string' || typeof value === 'number' || value === null) {
      const column = fieldMap[key] ?? key;
      setClauses.push(`${column} = ?`);
      params.push(value);
    } else if (value === undefined) {
      const column = fieldMap[key] ?? key;
      setClauses.push(`${column} = ?`);
      params.push(null);
    }
  }

  if (setClauses.length === 0) return false;

  setClauses.push('updated_at = datetime("now")');
  params.push(id);

  execute(
    `UPDATE leads SET ${setClauses.join(', ')} WHERE id = ?`,
    params
  );

  return getChanges() > 0;
}

/**
 * Delete a lead
 */
export function deleteLead(id: string): boolean {
  execute('DELETE FROM leads WHERE id = ?', [id]);
  return getChanges() > 0;
}

/**
 * Find potential duplicate leads
 */
export function findPotentialDuplicates(lead: Lead | RawLead): Lead[] {
  const normalizedName =
    'normalizedName' in lead
      ? lead.normalizedName
      : normalizeCompanyName(lead.companyName);
  const normalizedPhoneValue =
    'normalizedPhone' in lead ? lead.normalizedPhone : normalizePhone(lead.phone);

  const conditions: string[] = [];
  const params: SqlValue[] = [];

  // Match by normalized name
  conditions.push('normalized_name = ?');
  params.push(normalizedName);

  // Or match by phone
  if (normalizedPhoneValue) {
    conditions.push('normalized_phone = ?');
    params.push(normalizedPhoneValue);
  }

  // Or match by website
  if (lead.website) {
    conditions.push('website = ?');
    params.push(lead.website);
  }

  // Or match by source ID
  if (lead.sourceId) {
    conditions.push('(source = ? AND source_id = ?)');
    params.push(lead.source, lead.sourceId);
  }

  // Exclude duplicates and the lead itself
  const excludeId = 'id' in lead ? lead.id : null;
  let sql = `SELECT * FROM leads WHERE (${conditions.join(' OR ')}) AND status != 'Duplicate'`;
  if (excludeId) {
    sql += ' AND id != ?';
    params.push(excludeId);
  }

  const rows = query<LeadRow>(sql, params);
  return rows.map(rowToLead);
}

/**
 * Count leads by status
 */
export function countLeadsByStatus(): Record<string, number> {
  const rows = query<{ status: string; count: number }>(
    'SELECT status, COUNT(*) as count FROM leads GROUP BY status'
  );

  const counts: Record<string, number> = {};
  for (const row of rows) {
    counts[row.status] = row.count;
  }
  return counts;
}

/**
 * Count leads by source
 */
export function countLeadsBySource(): Record<string, number> {
  const rows = query<{ source: string; count: number }>(
    'SELECT source, COUNT(*) as count FROM leads GROUP BY source'
  );

  const counts: Record<string, number> = {};
  for (const row of rows) {
    counts[row.source] = row.count;
  }
  return counts;
}

/**
 * Count leads by trade
 */
export function countLeadsByTrade(): Record<string, number> {
  const rows = query<{ trade: string; count: number }>(
    'SELECT trade, COUNT(*) as count FROM leads GROUP BY trade'
  );

  const counts: Record<string, number> = {};
  for (const row of rows) {
    counts[row.trade] = row.count;
  }
  return counts;
}

/**
 * Get total lead count
 */
export function getTotalLeadCount(): number {
  const rows = query<{ count: number }>('SELECT COUNT(*) as count FROM leads');
  return rows[0]?.count ?? 0;
}

/**
 * Save changes to disk
 */
export async function persistChanges(): Promise<void> {
  await saveDatabase();
}

// ============================================================================
// Analytics Queries
// ============================================================================

/**
 * Get leads grouped by date for timeline charts
 */
export function getLeadsByDate(
  startDate: Date,
  endDate: Date,
  groupBy: 'day' | 'week' | 'month' = 'day'
): { date: string; count: number }[] {
  let dateFormat: string;
  switch (groupBy) {
    case 'week':
      dateFormat = '%Y-W%W';
      break;
    case 'month':
      dateFormat = '%Y-%m';
      break;
    default:
      dateFormat = '%Y-%m-%d';
  }

  const rows = query<{ date: string; count: number }>(
    `SELECT strftime('${dateFormat}', scraped_at) as date, COUNT(*) as count
     FROM leads
     WHERE scraped_at >= ? AND scraped_at <= ?
     GROUP BY strftime('${dateFormat}', scraped_at)
     ORDER BY date ASC`,
    [startDate.toISOString(), endDate.toISOString()]
  );

  return rows;
}

/**
 * Get data quality metrics
 */
export function getDataQualityMetrics(): {
  totalLeads: number;
  withEmail: number;
  withPhone: number;
  withAddress: number;
  withWebsite: number;
  duplicateCount: number;
  enrichedCount: number;
  verifiedCount: number;
  averageConfidence: number;
} {
  const rows = query<{
    total: number;
    with_email: number;
    with_phone: number;
    with_address: number;
    with_website: number;
    duplicate_count: number;
    enriched_count: number;
    verified_count: number;
    avg_confidence: number;
  }>(
    `SELECT
      COUNT(*) as total,
      SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) as with_email,
      SUM(CASE WHEN phone IS NOT NULL AND phone != '' THEN 1 ELSE 0 END) as with_phone,
      SUM(CASE WHEN address IS NOT NULL AND address != '' THEN 1 ELSE 0 END) as with_address,
      SUM(CASE WHEN website IS NOT NULL AND website != '' THEN 1 ELSE 0 END) as with_website,
      SUM(CASE WHEN status = 'Duplicate' THEN 1 ELSE 0 END) as duplicate_count,
      SUM(CASE WHEN status = 'Enriched' THEN 1 ELSE 0 END) as enriched_count,
      SUM(CASE WHEN status = 'Verified' THEN 1 ELSE 0 END) as verified_count,
      AVG(confidence) as avg_confidence
    FROM leads`
  );

  const result = rows[0];
  return {
    totalLeads: result?.total ?? 0,
    withEmail: result?.with_email ?? 0,
    withPhone: result?.with_phone ?? 0,
    withAddress: result?.with_address ?? 0,
    withWebsite: result?.with_website ?? 0,
    duplicateCount: result?.duplicate_count ?? 0,
    enrichedCount: result?.enriched_count ?? 0,
    verifiedCount: result?.verified_count ?? 0,
    averageConfidence: result?.avg_confidence ?? 0,
  };
}

/**
 * Get source comparison metrics
 */
export function getSourceComparison(): {
  source: string;
  total: number;
  withEmail: number;
  withPhone: number;
  withWebsite: number;
  averageRating: number;
  duplicateCount: number;
}[] {
  const rows = query<{
    source: string;
    total: number;
    with_email: number;
    with_phone: number;
    with_website: number;
    avg_rating: number;
    duplicate_count: number;
  }>(
    `SELECT
      source,
      COUNT(*) as total,
      SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) as with_email,
      SUM(CASE WHEN phone IS NOT NULL AND phone != '' THEN 1 ELSE 0 END) as with_phone,
      SUM(CASE WHEN website IS NOT NULL AND website != '' THEN 1 ELSE 0 END) as with_website,
      AVG(rating) as avg_rating,
      SUM(CASE WHEN status = 'Duplicate' THEN 1 ELSE 0 END) as duplicate_count
    FROM leads
    GROUP BY source
    ORDER BY total DESC`
  );

  return rows.map(row => ({
    source: row.source,
    total: row.total,
    withEmail: row.with_email,
    withPhone: row.with_phone,
    withWebsite: row.with_website,
    averageRating: row.avg_rating ?? 0,
    duplicateCount: row.duplicate_count,
  }));
}

/**
 * Get trend data comparing current period to previous period
 */
export function getTrendData(
  periodDays: number = 7
): {
  currentPeriod: number;
  previousPeriod: number;
  changePercent: number;
  currentWithEmail: number;
  previousWithEmail: number;
  emailChangePercent: number;
} {
  const now = new Date();
  const currentStart = new Date(now.getTime() - periodDays * 24 * 60 * 60 * 1000);
  const previousStart = new Date(currentStart.getTime() - periodDays * 24 * 60 * 60 * 1000);

  const rows = query<{
    period: string;
    count: number;
    with_email: number;
  }>(
    `SELECT
      CASE
        WHEN scraped_at >= ? THEN 'current'
        WHEN scraped_at >= ? AND scraped_at < ? THEN 'previous'
      END as period,
      COUNT(*) as count,
      SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) as with_email
    FROM leads
    WHERE scraped_at >= ?
    GROUP BY period`,
    [
      currentStart.toISOString(),
      previousStart.toISOString(),
      currentStart.toISOString(),
      previousStart.toISOString(),
    ]
  );

  const current = rows.find(r => r.period === 'current');
  const previous = rows.find(r => r.period === 'previous');

  const currentPeriod = current?.count ?? 0;
  const previousPeriod = previous?.count ?? 0;
  const currentWithEmail = current?.with_email ?? 0;
  const previousWithEmail = previous?.with_email ?? 0;

  const changePercent = previousPeriod > 0
    ? ((currentPeriod - previousPeriod) / previousPeriod) * 100
    : currentPeriod > 0 ? 100 : 0;

  const emailChangePercent = previousWithEmail > 0
    ? ((currentWithEmail - previousWithEmail) / previousWithEmail) * 100
    : currentWithEmail > 0 ? 100 : 0;

  return {
    currentPeriod,
    previousPeriod,
    changePercent,
    currentWithEmail,
    previousWithEmail,
    emailChangePercent,
  };
}

/**
 * Get recent activity (leads per day for last N days)
 */
export function getRecentActivity(days: number = 30): { date: string; count: number }[] {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  return getLeadsByDate(startDate, new Date(), 'day');
}
