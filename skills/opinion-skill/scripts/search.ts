// 搜索市场 (API + 本地缓存模糊搜索)
// 用法: bun run scripts/search.ts <keyword> [--limit <n>] [--refresh]

import { apiFetch } from "./config";
import { getMarkets, fuzzySearch, type CachedMarket, type SearchResult } from "./market-cache";

interface ApiResult {
  marketId: string;
  title: string;
  yesTokenId: string;
  noTokenId: string;
  parentEvent?: { title: string; eventMarketId: string };
}

function printMarket(m: { marketId: any; marketTitle?: string; title?: string; yesTokenId?: string; noTokenId?: string; statusEnum?: string; volume?: string; childMarkets?: any[]; score?: number; matchSource?: string; parentEvent?: any }) {
  const title = m.marketTitle || m.title || "Untitled";
  console.log(`Market: ${title}`);
  console.log(`  marketId: ${m.marketId}`);
  if (m.yesTokenId) console.log(`  yesTokenId: ${m.yesTokenId}`);
  if (m.noTokenId) console.log(`  noTokenId: ${m.noTokenId}`);
  if (m.statusEnum) console.log(`  status: ${m.statusEnum}`);
  if (m.volume) console.log(`  volume: $${Number(m.volume).toLocaleString()}`);
  if (m.childMarkets?.length) {
    console.log(`  childMarkets (${m.childMarkets.length}):`);
    for (const c of m.childMarkets.slice(0, 5)) {
      console.log(`    - ${c.marketTitle} (id: ${c.marketId}, yes: ${c.yesTokenId})`);
    }
    if (m.childMarkets.length > 5) console.log(`    ... +${m.childMarkets.length - 5} more`);
  }
  if (m.parentEvent) {
    console.log(`  Event: ${m.parentEvent.title} (eventMarketId: ${m.parentEvent.eventMarketId})`);
  }
  if (m.score !== undefined) console.log(`  relevance: ${m.score.toFixed(1)}`);
  console.log("---");
}

async function search(keyword: string, limit: number, refresh: boolean): Promise<void> {
  console.log(`\nSearching: "${keyword}"\n`);

  // 并行: API 搜索 + 缓存模糊搜索
  const [apiPromise, cachePromise] = [
    apiFetch<any>("/api/markets/search", { q: keyword, limit }).catch(() => null),
    getMarkets(refresh).then(m => fuzzySearch(m, keyword, limit)).catch(() => [] as SearchResult[]),
  ];

  const [apiResp, cacheResults] = await Promise.all([apiPromise, cachePromise]);

  // 合并去重 (以 marketId 为 key)
  const seen = new Set<string>();
  const merged: any[] = [];

  // API 结果优先
  if (apiResp?.success && apiResp.data?.length) {
    for (const m of apiResp.data) {
      const id = String(m.marketId);
      if (!seen.has(id)) {
        seen.add(id);
        merged.push(m);
      }
    }
  }

  // 缓存模糊搜索补充
  for (const m of cacheResults) {
    const id = String(m.marketId);
    if (!seen.has(id)) {
      seen.add(id);
      merged.push(m);
    }
  }

  if (merged.length === 0) {
    console.log("No markets found.");
    return;
  }

  console.log(`Found ${merged.length} market(s)\n`);
  for (const m of merged.slice(0, limit)) {
    printMarket(m);
  }
}

// CLI entry
const args = process.argv.slice(2);
let keyword = "";
let limit = 10;
let refresh = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--limit") { limit = parseInt(args[++i]); }
  else if (args[i] === "--refresh") { refresh = true; }
  else if (!args[i].startsWith("--") && !keyword) { keyword = args[i]; }
}

if (!keyword) {
  console.error("Usage: bun run scripts/search.ts <keyword> [--limit <n>] [--refresh]");
  process.exit(1);
}

search(keyword, limit, refresh).catch(console.error);
