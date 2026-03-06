import { parseFeedItems, type Article } from "./parse";

export interface FeedSource {
  name: string;
  xmlUrl: string;
  htmlUrl: string;
}

const USER_AGENTS = [
  "sec-daily-digest/1.0 (+rss-reader; security-research)",
  "Mozilla/5.0 (compatible; sec-daily-digest/1.0; +https://github.com/zer0yu/CyberSecurityRSS)",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) sec-daily-digest/1.0",
];

export function buildFetchHeaders(seed: number): Record<string, string> {
  return {
    "User-Agent": USER_AGENTS[Math.abs(seed) % USER_AGENTS.length]!,
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
  };
}

async function sleep(ms: number): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

export async function fetchFeed(
  feed: FeedSource,
  options?: {
    timeoutMs?: number;
    retries?: number;
    fetcher?: typeof fetch;
    seed?: number;
  },
): Promise<Article[]> {
  const fetcher = options?.fetcher ?? fetch;
  const timeoutMs = options?.timeoutMs ?? 15_000;
  const retries = options?.retries ?? 2;
  const seed = options?.seed ?? 0;

  for (let attempt = 0; attempt <= retries; attempt += 1) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetcher(feed.xmlUrl, {
        signal: controller.signal,
        headers: buildFetchHeaders(seed + attempt),
      });
      clearTimeout(timeout);

      if (!response.ok) {
        if ((response.status === 403 || response.status === 429) && attempt < retries) {
          await sleep(250 + attempt * 300);
          continue;
        }
        throw new Error(`HTTP ${response.status}`);
      }

      const xml = await response.text();
      return parseFeedItems(xml, feed.name, feed.htmlUrl);
    } catch (error) {
      clearTimeout(timeout);
      if (attempt >= retries) {
        console.warn(`[rss] failed ${feed.name}: ${error instanceof Error ? error.message : String(error)}`);
        return [];
      }
      await sleep(150 + attempt * 200);
    }
  }

  return [];
}

export async function fetchAllFeeds(
  feeds: FeedSource[],
  options?: {
    concurrency?: number;
    fetcher?: typeof fetch;
  },
): Promise<Article[]> {
  const concurrency = options?.concurrency ?? 10;
  const all: Article[] = [];

  for (let i = 0; i < feeds.length; i += concurrency) {
    const batch = feeds.slice(i, i + concurrency);
    const results = await Promise.all(
      batch.map((feed, index) =>
        fetchFeed(feed, {
          fetcher: options?.fetcher,
          seed: i + index,
        }),
      ),
    );
    for (const items of results) {
      all.push(...items);
    }
  }

  return all;
}
