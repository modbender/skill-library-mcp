import fetch from 'node-fetch';

const COINGECKO_NEAR =
  'https://api.coingecko.com/api/v3/simple/price?ids=near&vs_currencies=usd&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true';
const NEAR_RPC = 'https://rpc.mainnet.near.org';
const NEARBLOCKS_STATS = 'https://api.nearblocks.io/v1/stats';
const THREAD_POST_COUNT = 8;
const MAX_THREAD_POST_LEN = 280;
const NEWS_MAX_ITEMS = 12;

const SOURCE_SCORE: Record<string, number> = {
  'NEAR Blog': 100,
  'NEAR Foundation': 95,
  'near/nearcore releases': 90,
  'near/near-api-js releases': 85,
  Fallback: 1
};

type NewsItem = {
  title: string;
  source: string;
  url: string;
  published_at: string | null;
  summary: string | null;
};

type RankedNewsItem = NewsItem & {
  source_score: number;
  published_ts: number;
};

type Snapshot = {
  price_usd: number | null;
  change_24h_pct: number | null;
  market_cap_usd: number | null;
  volume_24h_usd: number | null;
  chain_id: string | null;
  latest_block_height: number | null;
  active_accounts_24h: number | null;
  quality_score_pct: number;
  missing_signals: string[];
  captured_at: string;
};

async function getJson<T>(url: string, init?: Record<string, unknown>): Promise<T | null> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 9000);
  try {
    const response = await fetch(url, { ...(init ?? {}), signal: controller.signal } as any);
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

async function getText(url: string): Promise<string | null> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 9000);
  try {
    const response = await fetch(url, { signal: controller.signal } as any);
    if (!response.ok) return null;
    return await response.text();
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

function normalizeTopic(topic: string): string {
  const clean = String(topic ?? '').replace(/\s+/g, ' ').trim();
  return clean ? clean.slice(0, 120) : 'NEAR ecosystem';
}

function fmt(value: number | null, digits: number = 2): string {
  if (value === null || !Number.isFinite(value)) return 'n/a';
  return value.toLocaleString('en-US', { maximumFractionDigits: digits });
}

function trimToLen(text: string, maxLen: number): string {
  if (text.length <= maxLen) {
    return text;
  }
  return `${text.slice(0, maxLen - 1).trimEnd()}…`;
}

function normalizeUrl(url: string): string {
  return url.trim().replace(/\/+$/, '').toLowerCase();
}

function toTimestamp(value: string | null): number {
  if (!value) {
    return 0;
  }
  const ts = Date.parse(value);
  return Number.isFinite(ts) ? ts : 0;
}

function finalizeThread(lines: string[], total: number): string[] {
  const output: string[] = [];
  for (let i = 1; i <= total; i += 1) {
    const raw = lines[i - 1] ?? `Execution note ${i}.`;
    const body = raw.replace(/^\d+\/\d+\s+/, '');
    output.push(trimToLen(`${i}/${total} ${body}`, MAX_THREAD_POST_LEN));
  }
  return output;
}

function decodeHtml(input: string): string {
  return input
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function stripHtml(input: string): string {
  return decodeHtml(input).replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function rssTag(block: string, tag: string): string | null {
  const m = block.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, 'i'));
  return m ? stripHtml(m[1]) : null;
}

function parseRss(xml: string, source: string, limit: number): NewsItem[] {
  const items = xml.match(/<item[\s\S]*?<\/item>/gi) ?? [];
  return items.slice(0, limit).map((it) => ({
    title: rssTag(it, 'title') ?? 'Untitled',
    source,
    url: rssTag(it, 'link') ?? '',
    published_at: rssTag(it, 'pubDate'),
    summary: rssTag(it, 'description')
  }));
}

async function collectRssNews(): Promise<NewsItem[]> {
  const feeds: Array<{ source: string; url: string }> = [
    { source: 'NEAR Blog', url: 'https://near.org/blog/rss.xml' },
    { source: 'NEAR Blog', url: 'https://pages.near.org/blog/rss.xml' },
    { source: 'NEAR Foundation', url: 'https://near.foundation/feed/' }
  ];

  const news: NewsItem[] = [];
  for (const feed of feeds) {
    const xml = await getText(feed.url);
    if (!xml || !xml.includes('<item')) {
      continue;
    }
    news.push(...parseRss(xml, feed.source, 6));
  }
  return news;
}

type GithubRelease = {
  name?: string;
  tag_name?: string;
  html_url?: string;
  published_at?: string;
  body?: string;
};

async function collectGithubReleaseNews(): Promise<NewsItem[]> {
  const endpoints: Array<{ source: string; url: string }> = [
    { source: 'near/nearcore releases', url: 'https://api.github.com/repos/near/nearcore/releases?per_page=3' },
    {
      source: 'near/near-api-js releases',
      url: 'https://api.github.com/repos/near/near-api-js/releases?per_page=3'
    }
  ];

  const items: NewsItem[] = [];
  for (const endpoint of endpoints) {
    const releases = await getJson<GithubRelease[]>(endpoint.url, {
      headers: {
        Accept: 'application/vnd.github+json'
      }
    });
    if (!Array.isArray(releases)) {
      continue;
    }
    for (const release of releases) {
      items.push({
        title: release.name || release.tag_name || 'Release update',
        source: endpoint.source,
        url: release.html_url ?? '',
        published_at: release.published_at ?? null,
        summary: release.body ? stripHtml(release.body).slice(0, 280) : null
      });
    }
  }
  return items;
}

function rankAndDeduplicateNews(items: NewsItem[]): RankedNewsItem[] {
  const dedup = new Map<string, RankedNewsItem>();

  for (const item of items) {
    const title = stripHtml(item.title || '');
    const url = item.url ? normalizeUrl(item.url) : '';
    if (!title || !url) {
      continue;
    }

    const candidate: RankedNewsItem = {
      title: trimToLen(title, 160),
      source: item.source,
      url,
      published_at: item.published_at,
      summary: item.summary ? trimToLen(stripHtml(item.summary), 280) : null,
      source_score: SOURCE_SCORE[item.source] ?? 10,
      published_ts: toTimestamp(item.published_at)
    };

    const key = `${url}|${candidate.title.toLowerCase()}`;
    const existing = dedup.get(key);
    if (!existing) {
      dedup.set(key, candidate);
      continue;
    }

    const existingRank = existing.source_score * 1_000_000_000 + existing.published_ts;
    const candidateRank = candidate.source_score * 1_000_000_000 + candidate.published_ts;
    if (candidateRank > existingRank) {
      dedup.set(key, candidate);
    }
  }

  return [...dedup.values()].sort((a, b) => {
    if (b.source_score !== a.source_score) {
      return b.source_score - a.source_score;
    }
    return b.published_ts - a.published_ts;
  });
}

async function fetchSnapshot(): Promise<Snapshot> {
  const [cg, rpc, stats] = await Promise.all([
    getJson<any>(COINGECKO_NEAR),
    getJson<any>(NEAR_RPC, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 'near-content', method: 'status', params: [] })
    }),
    getJson<any>(NEARBLOCKS_STATS)
  ]);

  const near = cg?.near ?? {};
  const rpcResult = rpc?.result ?? {};
  const row = stats?.stats?.[0] ?? {};

  const priceUsd = Number.isFinite(Number(near.usd)) ? Number(near.usd) : null;
  const change24h = Number.isFinite(Number(near.usd_24h_change)) ? Number(near.usd_24h_change) : null;
  const marketCapUsd = Number.isFinite(Number(near.usd_market_cap)) ? Number(near.usd_market_cap) : null;
  const volume24hUsd = Number.isFinite(Number(near.usd_24h_vol)) ? Number(near.usd_24h_vol) : null;
  const chainId = rpcResult.chain_id ?? null;
  const latestBlockHeight = Number.isFinite(Number(rpcResult?.sync_info?.latest_block_height))
    ? Number(rpcResult.sync_info.latest_block_height)
    : null;
  const activeAccounts24h = Number.isFinite(Number(row.active_accounts_24h)) ? Number(row.active_accounts_24h) : null;

  const signals: Array<{ name: string; value: unknown }> = [
    { name: 'price_usd', value: priceUsd },
    { name: 'change_24h_pct', value: change24h },
    { name: 'market_cap_usd', value: marketCapUsd },
    { name: 'volume_24h_usd', value: volume24hUsd },
    { name: 'chain_id', value: chainId },
    { name: 'latest_block_height', value: latestBlockHeight },
    { name: 'active_accounts_24h', value: activeAccounts24h }
  ];
  const missingSignals = signals.filter((s) => s.value === null).map((s) => s.name);
  const qualityScore = Math.round(((signals.length - missingSignals.length) / signals.length) * 100);

  return {
    price_usd: priceUsd,
    change_24h_pct: change24h,
    market_cap_usd: marketCapUsd,
    volume_24h_usd: volume24hUsd,
    chain_id: chainId,
    latest_block_height: latestBlockHeight,
    active_accounts_24h: activeAccounts24h,
    quality_score_pct: qualityScore,
    missing_signals: missingSignals,
    captured_at: new Date().toISOString()
  };
}

function hashtags(topic: string): string {
  const low = topic.toLowerCase();
  const tags = new Set<string>(['#NEAR', '#NEARProtocol']);
  if (low.includes('defi')) tags.add('#DeFi');
  if (low.includes('ai')) tags.add('#AI');
  if (low.includes('security')) tags.add('#Security');
  if (low.includes('dev') || low.includes('developer')) tags.add('#BuildOnNEAR');
  return [...tags].slice(0, 5).join(' ');
}

export async function near_content_thread(topic: string): Promise<string[]> {
  const t = normalizeTopic(topic);
  const s = await fetchSnapshot();
  const change = s.change_24h_pct === null ? '24h change unavailable' : `24h change ${s.change_24h_pct.toFixed(2)}%`;
  const h = hashtags(t);

  const draft = [
    `${t}: practical NEAR guide for builders and users. ${h}`,
    `Why it matters: ${t} improves clarity, onboarding, and execution speed in the ecosystem.`,
    `Market pulse: NEAR $${fmt(s.price_usd, 3)}, ${change}.`,
    `Network pulse: chain=${s.chain_id ?? 'n/a'}, block=${fmt(s.latest_block_height, 0)}.`,
    `Adoption signal: active accounts (24h) ${fmt(s.active_accounts_24h, 0)}.`,
    'Execution tip: ship a narrow MVP, then iterate weekly from user behavior and support tickets.',
    'Common pitfall: too much scope early. Optimize one repeated user workflow first.',
    `Reply with your ${t} use case and I can outline a 7-day NEAR execution plan.`
  ];

  return finalizeThread(draft, THREAD_POST_COUNT);
}

export async function near_content_update(): Promise<string> {
  const s = await fetchSnapshot();
  const lines = [
    'NEAR Daily Market Update',
    `Timestamp (UTC): ${s.captured_at}`,
    `Price: $${fmt(s.price_usd, 3)}`,
    `24h Change: ${s.change_24h_pct === null ? 'n/a' : `${s.change_24h_pct.toFixed(2)}%`}`,
    `Market Cap: $${fmt(s.market_cap_usd, 0)}`,
    `24h Volume: $${fmt(s.volume_24h_usd, 0)}`,
    `Chain: ${s.chain_id ?? 'n/a'}`,
    `Latest Block: ${fmt(s.latest_block_height, 0)}`,
    `Active Accounts (24h): ${fmt(s.active_accounts_24h, 0)}`,
    `Data Quality: ${s.quality_score_pct}% (${7 - s.missing_signals.length}/7 signals available)`,
    'Note: informational update, not financial advice.'
  ];
  if (s.missing_signals.length > 0) {
    lines.push(`Missing Signals: ${s.missing_signals.join(', ')}`);
  }
  return lines.join('\n');
}

export async function near_content_news(): Promise<NewsItem[]> {
  const [rssNews, githubNews] = await Promise.all([collectRssNews(), collectGithubReleaseNews()]);
  const ranked = rankAndDeduplicateNews([...rssNews, ...githubNews]);
  if (ranked.length > 0) {
    return ranked.slice(0, NEWS_MAX_ITEMS).map(({ source_score: _, published_ts: __, ...item }) => item);
  }

  return [
    {
      title: 'Fallback: NEAR Blog updates',
      source: 'Fallback',
      url: 'https://near.org/blog',
      published_at: null,
      summary: 'Used when feed endpoints are temporarily unavailable.'
    },
    {
      title: 'Fallback: nearcore releases',
      source: 'Fallback',
      url: 'https://github.com/near/nearcore/releases',
      published_at: null,
      summary: 'Fallback source for ecosystem technical updates.'
    }
  ];
}

export async function near_content_tutorial(topic: string): Promise<string> {
  const t = normalizeTopic(topic);
  return `# NEAR Tutorial: ${t}

## Goal
Build a practical ${t} flow on NEAR with one measurable outcome.

## Prerequisites
- NEAR wallet
- Node.js 18+
- Basic transaction/account understanding

## Step 1: Scope
Pick one user action and one success metric.

## Step 2: Environment
\`\`\`bash
npm install near-api-js
\`\`\`

## Step 3: Core path
Implement a minimal end-to-end flow: input -> validation -> action -> output.

## Step 4: Reliability
Add input validation, retry policy, and structured error logs.

## Step 5: Real scenarios
Test happy path, invalid input, and temporary RPC outage.

## Step 6: Ship and iterate
Publish changelog, collect feedback, prioritize reliability improvements first.
`;
}
