// @elvatis/openclaw-rss-feeds - RSS/Atom feed fetcher
import Parser from 'rss-parser';
import type { FeedConfig, FeedItem, FirmwareEntry, RetryConfig } from './types';

// Determine firmware release type from version string
function getFirmwareType(version: string): 'Major' | 'Feature' | 'Patch' {
  const parts = version.split('.');
  const lastPart = parts[parts.length - 1];
  if (lastPart === '0') return 'Major';
  if (lastPart === '2' || lastPart === '4') return 'Feature';
  return 'Patch';
}

// Extract version from a title string (e.g. "FortiGate 7.4.2" → "7.4.2")
function extractVersion(title: string): string | undefined {
  const match = title.match(/(\d+\.\d+\.\d+(?:\.\d+)?)/);
  return match ? match[1] : undefined;
}

// Extract product slug from title (e.g. "FortiGate" → "fortigate")
function extractProduct(title: string): string {
  const match = title.match(/^([A-Za-z]+(?:-[A-Za-z0-9]+)?)/);
  return match ? match[1].toLowerCase() : 'unknown';
}

// Build a documentation URL from a template, substituting {product} and {version}
function buildDocsUrl(template: string, product: string, version: string): string {
  return template
    .replace(/\{product\}/g, product)
    .replace(/\{version\}/g, version);
}

// Check if a title/content matches any of the configured keywords (case-insensitive)
function matchesKeywords(text: string, keywords?: string[]): boolean {
  if (!keywords || keywords.length === 0) return true;
  const lower = text.toLowerCase();
  return keywords.some(kw => lower.includes(kw.toLowerCase()));
}

// Default retry settings
const RETRY_DEFAULTS: Required<RetryConfig> = {
  maxRetries: 3,
  initialDelayMs: 1000,
  backoffMultiplier: 2,
};

function resolveRetryConfig(retry?: RetryConfig): Required<RetryConfig> {
  if (!retry) return RETRY_DEFAULTS;
  return {
    maxRetries: retry.maxRetries ?? RETRY_DEFAULTS.maxRetries,
    initialDelayMs: retry.initialDelayMs ?? RETRY_DEFAULTS.initialDelayMs,
    backoffMultiplier: retry.backoffMultiplier ?? RETRY_DEFAULTS.backoffMultiplier,
  };
}

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchWithRetry<T>(
  fn: () => Promise<T>,
  config: Required<RetryConfig>
): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (attempt < config.maxRetries) {
        const waitMs = config.initialDelayMs * Math.pow(config.backoffMultiplier, attempt);
        await delay(waitMs);
      }
    }
  }
  throw lastError;
}

export interface FetchFeedResult {
  items: FeedItem[];
  firmware: FirmwareEntry[];
}

export async function fetchFeed(
  feedConfig: FeedConfig,
  startDate: Date,
  endDate: Date,
  retry?: RetryConfig
): Promise<FetchFeedResult> {
  type CustomItem = {
    'content:encoded'?: string;
    'dc:date'?: string;
  };

  const parser = new Parser<Record<string, unknown>, CustomItem>({
    customFields: {
      item: ['content:encoded', 'dc:date'],
    },
    timeout: 20000,
  });

  const retryConfig = resolveRetryConfig(retry);
  const feed = await fetchWithRetry(() => parser.parseURL(feedConfig.url), retryConfig);

  const items: FeedItem[] = [];
  const firmware: FirmwareEntry[] = [];
  const seenKeys = new Set<string>();

  for (const raw of feed.items) {
    const title = (raw.title ?? '').trim();
    const link = (raw.link ?? '').trim();
    const content = (raw['content:encoded'] ?? raw.content ?? raw.contentSnippet ?? '').trim() as string;

    // Resolve publication date
    let pubDate: Date | undefined;
    if (raw.isoDate) {
      pubDate = new Date(raw.isoDate);
    } else if (raw.pubDate) {
      pubDate = new Date(raw.pubDate as string);
    } else if ((raw as Record<string, unknown>)['dc:date']) {
      pubDate = new Date((raw as Record<string, unknown>)['dc:date'] as string);
    }

    if (!pubDate || isNaN(pubDate.getTime())) continue;
    if (pubDate < startDate || pubDate >= endDate) continue;

    // Keyword filtering (title + content)
    const searchText = `${title} ${content}`;
    if (!matchesKeywords(searchText, feedConfig.keywords)) continue;

    // Dedup by title+link
    const dedupKey = `${title}::${link}`;
    if (seenKeys.has(dedupKey)) continue;
    seenKeys.add(dedupKey);

    const version = extractVersion(title);
    const rawProduct = extractProduct(title);

    const item: FeedItem = {
      title,
      link,
      pubDate,
      version,
      product: rawProduct,
      content,
      feedId: feedConfig.id,
      feedName: feedConfig.name,
    };

    // If the item has a version, treat it as a firmware/release entry
    if (version) {
      const firmwareKey = `${rawProduct}-${version}`;
      if (!seenKeys.has(firmwareKey)) {
        seenKeys.add(firmwareKey);

        // Build docs URL from template if configured
        const docsUrl = feedConfig.docsUrlTemplate
          ? buildDocsUrl(feedConfig.docsUrlTemplate, rawProduct, version)
          : undefined;

        firmware.push({
          product: rawProduct.toUpperCase(),
          version,
          type: getFirmwareType(version),
          pubDate: pubDate.toISOString(),
          docsUrl,
          feedId: feedConfig.id,
          feedName: feedConfig.name,
        });

        item.docsUrl = docsUrl;
      }
    }

    items.push(item);
  }

  // Sort firmware: by product asc, version desc
  firmware.sort((a, b) => {
    if (a.product !== b.product) return a.product.localeCompare(b.product);
    const aParts = a.version.split('.').map(Number);
    const bParts = b.version.split('.').map(Number);
    for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
      const diff = (bParts[i] ?? 0) - (aParts[i] ?? 0);
      if (diff !== 0) return diff;
    }
    return 0;
  });

  return { items, firmware };
}
