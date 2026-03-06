/**
 * Email scraper - extracts emails from company websites
 */

import { createLogger } from '../utils/logger.js';

const logger = createLogger('email-scraper');

// Common contact page paths to check
const CONTACT_PATHS = [
  '',
  '/contact',
  '/contact-us',
  '/contactus',
  '/about',
  '/about-us',
  '/aboutus',
  '/team',
  '/our-team',
  '/staff',
];

// Email regex pattern
const EMAIL_REGEX = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;

// Common generic emails to filter out
const GENERIC_EMAILS = new Set([
  'info@',
  'contact@',
  'hello@',
  'support@',
  'sales@',
  'admin@',
  'noreply@',
  'no-reply@',
  'webmaster@',
  'postmaster@',
  'mail@',
  'email@',
  'enquiries@',
  'inquiries@',
  'office@',
  'help@',
  'feedback@',
  'privacy@',
  'legal@',
  'billing@',
  'abuse@',
]);

// Domains to exclude (not real company emails)
const EXCLUDED_DOMAINS = new Set([
  'example.com',
  'test.com',
  'email.com',
  'mail.com',
  'domain.com',
  'yourcompany.com',
  'company.com',
  'sentry.io',
  'wixpress.com',
  'squarespace.com',
  'godaddy.com',
  'wordpress.com',
  'weebly.com',
  'shopify.com',
]);

export interface ScrapeResult {
  success: boolean;
  emails: ExtractedEmail[];
  pagesScanned: number;
  error?: string;
}

export interface ExtractedEmail {
  email: string;
  source: string; // URL where found
  isGeneric: boolean;
  confidence: number; // 0-100
}

/**
 * Scrape a website for email addresses
 */
export async function scrapeWebsiteForEmails(websiteUrl: string): Promise<ScrapeResult> {
  const emails = new Map<string, ExtractedEmail>();
  let pagesScanned = 0;

  try {
    // Normalize URL
    let baseUrl = websiteUrl.trim();
    if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {
      baseUrl = 'https://' + baseUrl;
    }
    // Remove trailing slash
    baseUrl = baseUrl.replace(/\/$/, '');

    const urlObj = new URL(baseUrl);
    const domain = urlObj.hostname.replace('www.', '');

    logger.debug(`Scraping ${baseUrl} for emails`);

    // Try each contact path
    for (const path of CONTACT_PATHS) {
      const pageUrl = baseUrl + path;

      try {
        const pageEmails = await scrapePageForEmails(pageUrl, domain);
        pagesScanned++;

        for (const extracted of pageEmails) {
          // Deduplicate by email address, keep highest confidence
          const existing = emails.get(extracted.email.toLowerCase());
          if (!existing || extracted.confidence > existing.confidence) {
            emails.set(extracted.email.toLowerCase(), extracted);
          }
        }

        // If we found a good non-generic email, we can stop
        const goodEmails = Array.from(emails.values()).filter(e => !e.isGeneric && e.confidence >= 70);
        if (goodEmails.length >= 1) {
          logger.debug(`Found good email on ${pageUrl}, stopping search`);
          break;
        }
      } catch (err) {
        // Page fetch failed, continue to next path
        logger.debug(`Failed to fetch ${pageUrl}: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }

      // Rate limit between requests
      await sleep(200);
    }

    const emailList = Array.from(emails.values())
      .sort((a, b) => {
        // Prioritize non-generic emails
        if (a.isGeneric !== b.isGeneric) return a.isGeneric ? 1 : -1;
        // Then by confidence
        return b.confidence - a.confidence;
      });

    return {
      success: true,
      emails: emailList,
      pagesScanned,
    };
  } catch (err) {
    logger.error(`Failed to scrape ${websiteUrl}: ${err instanceof Error ? err.message : 'Unknown error'}`);
    return {
      success: false,
      emails: [],
      pagesScanned,
      error: err instanceof Error ? err.message : 'Unknown error',
    };
  }
}

/**
 * Scrape a single page for emails
 */
async function scrapePageForEmails(url: string, expectedDomain: string): Promise<ExtractedEmail[]> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000); // 10s timeout

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
      },
      redirect: 'follow',
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const html = await response.text();
    return extractEmailsFromHtml(html, url, expectedDomain);
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Extract emails from HTML content
 */
function extractEmailsFromHtml(html: string, sourceUrl: string, expectedDomain: string): ExtractedEmail[] {
  const emails: ExtractedEmail[] = [];
  const found = new Set<string>();

  // Find all email addresses
  const matches = html.match(EMAIL_REGEX) || [];

  for (const email of matches) {
    const lowerEmail = email.toLowerCase();

    // Skip if already found
    if (found.has(lowerEmail)) continue;
    found.add(lowerEmail);

    // Extract domain from email
    const emailDomain = lowerEmail.split('@')[1];
    if (!emailDomain) continue;

    // Skip excluded domains
    if (EXCLUDED_DOMAINS.has(emailDomain)) continue;

    // Skip image files that look like emails
    if (lowerEmail.match(/\.(png|jpg|jpeg|gif|svg|webp|ico)$/i)) continue;

    // Check if it's a generic email
    const isGeneric = Array.from(GENERIC_EMAILS).some(prefix => lowerEmail.startsWith(prefix));

    // Calculate confidence
    let confidence = 50;

    // Bonus if email domain matches website domain
    if (emailDomain === expectedDomain || emailDomain === 'www.' + expectedDomain) {
      confidence += 30;
    }

    // Bonus for non-generic emails
    if (!isGeneric) {
      confidence += 15;
    }

    // Bonus if found in mailto: link
    if (html.includes(`mailto:${email}`)) {
      confidence += 5;
    }

    emails.push({
      email,
      source: sourceUrl,
      isGeneric,
      confidence: Math.min(100, confidence),
    });
  }

  return emails;
}

/**
 * Sleep helper
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Batch scrape multiple websites
 */
export async function batchScrapeEmails(
  websites: { id: string; url: string }[],
  onProgress?: (completed: number, total: number) => void
): Promise<Map<string, ScrapeResult>> {
  const results = new Map<string, ScrapeResult>();
  const total = websites.length;

  for (let i = 0; i < websites.length; i++) {
    const { id, url } = websites[i]!;

    const result = await scrapeWebsiteForEmails(url);
    results.set(id, result);

    if (onProgress) {
      onProgress(i + 1, total);
    }

    // Rate limit between websites
    if (i < websites.length - 1) {
      await sleep(500);
    }
  }

  return results;
}
