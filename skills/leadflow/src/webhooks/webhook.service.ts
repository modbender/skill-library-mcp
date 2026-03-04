/**
 * Webhook output service - POST leads to external URLs
 */

import { createLogger } from '../utils/logger.js';
import { findLeads } from '../storage/lead.repository.js';
import type { Lead, LeadFilters } from '../types/index.js';

const logger = createLogger('webhook');

export interface WebhookPayload {
  event: 'leads.export' | 'lead.enriched' | 'lead.verified';
  timestamp: string;
  data: WebhookLeadData | WebhookLeadData[];
}

export interface WebhookLeadData {
  id: string;
  companyName: string;
  contactName?: string;
  email?: string;
  phone?: string;
  website?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  trade: string;
  source: string;
  rating?: number;
  reviewCount?: number;
  status: string;
  leadScore?: number;
  emailVerified?: boolean;
  emailVerificationStatus?: string;
  phoneType?: string;
  phoneCarrier?: string;
}

function leadToWebhookData(lead: Lead): WebhookLeadData {
  return {
    id: lead.id,
    companyName: lead.companyName,
    contactName: lead.contactName,
    email: lead.email,
    phone: lead.phone,
    website: lead.website,
    address: lead.address,
    city: lead.city,
    state: lead.state,
    zipCode: lead.zipCode,
    trade: lead.trade,
    source: lead.source,
    rating: lead.rating,
    reviewCount: lead.reviewCount,
    status: lead.status,
    leadScore: lead.leadScore,
    emailVerified: lead.emailVerified,
    emailVerificationStatus: lead.emailVerificationStatus,
    phoneType: lead.phoneType,
    phoneCarrier: lead.phoneCarrier,
  };
}

export interface WebhookResult {
  success: boolean;
  statusCode?: number;
  leadsPosted: number;
  error?: string;
}

/**
 * Send leads to a webhook URL
 */
export async function sendWebhook(
  url: string,
  leads: Lead[],
  event: WebhookPayload['event'] = 'leads.export'
): Promise<WebhookResult> {
  const payload: WebhookPayload = {
    event,
    timestamp: new Date().toISOString(),
    data: leads.length === 1 ? leadToWebhookData(leads[0]!) : leads.map(leadToWebhookData),
  };

  logger.info(`Sending ${leads.length} leads to webhook: ${url}`);

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'LeadFlow/1.0',
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(30000),
    });

    if (!res.ok) {
      const body = await res.text().catch(() => '');
      logger.error(`Webhook failed: ${res.status} ${body}`);
      return { success: false, statusCode: res.status, leadsPosted: 0, error: `HTTP ${res.status}` };
    }

    logger.info(`Webhook success: ${res.status}, ${leads.length} leads posted`);
    return { success: true, statusCode: res.status, leadsPosted: leads.length };
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Unknown error';
    logger.error(`Webhook error: ${msg}`);
    return { success: false, leadsPosted: 0, error: msg };
  }
}

/**
 * Send leads matching filters to a webhook with batching
 */
export async function sendLeadsToWebhook(
  url: string,
  filters?: LeadFilters,
  options?: { batchSize?: number; event?: WebhookPayload['event'] }
): Promise<WebhookResult> {
  const leads = findLeads(filters);

  if (leads.length === 0) {
    return { success: true, leadsPosted: 0 };
  }

  const batchSize = options?.batchSize ?? 100;
  const event = options?.event ?? 'leads.export';
  let totalPosted = 0;

  for (let i = 0; i < leads.length; i += batchSize) {
    const batch = leads.slice(i, i + batchSize);
    const result = await sendWebhook(url, batch, event);

    if (!result.success) {
      return { ...result, leadsPosted: totalPosted };
    }

    totalPosted += batch.length;

    // Small delay between batches
    if (i + batchSize < leads.length) {
      await new Promise(r => setTimeout(r, 500));
    }
  }

  return { success: true, leadsPosted: totalPosted };
}
