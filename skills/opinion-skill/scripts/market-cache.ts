// 市场本地缓存 + 模糊搜索
// 从 OpenAPI 全量拉取市场数据，缓存到本地磁盘，支持离线模糊搜索

import { mkdirSync, existsSync, readFileSync, writeFileSync } from "fs";

const OPENAPI_BASE = "https://openapi.opinion.trade/openapi";
const CACHE_DIR = "/root/opinionskills/scripts/.cache";
const CACHE_FILE = `${CACHE_DIR}/markets.json`;
const CACHE_TTL = 10 * 60 * 1000; // 10 分钟

const PAGE_LIMIT = 20; // OpenAPI 单页最大值

export interface CachedMarket {
  marketId: number;
  marketTitle: string;
  status: number;
  statusEnum: string;
  marketType: number; // 0=Binary, 1=Categorical
  yesTokenId?: string;
  noTokenId?: string;
  volume?: string;
  volume24h?: string;
  childMarkets?: CachedMarket[];
  collection?: any;
  createdAt?: number;
  cutoffAt?: number;
}

interface CacheEnvelope {
  timestamp: number;
  total: number;
  markets: CachedMarket[];
}

export interface SearchResult extends CachedMarket {
  score: number;
  matchSource: "cache";
}

// ── OpenAPI fetch ──

async function openapiFetch(path: string, params?: Record<string, any>): Promise<any> {
  // path 是相对路径如 "/market", 拼接到 OPENAPI_BASE 末尾
  const base = OPENAPI_BASE.endsWith("/") ? OPENAPI_BASE : OPENAPI_BASE + "/";
  const url = new URL(path.replace(/^\//, ""), base);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    }
  }
  const headers: Record<string, string> = {};
  const apiKey = process.env.API_KEY;
  if (apiKey) headers["apikey"] = apiKey;

  const resp = await fetch(url.toString(), { headers, signal: AbortSignal.timeout(30000) });
  if (!resp.ok) throw new Error(`OpenAPI ${resp.status}: ${resp.statusText}`);
  return resp.json();
}

// ── 全量拉取 ──

async function fetchAllMarkets(): Promise<CachedMarket[]> {
  const all: CachedMarket[] = [];
  let page = 1;
  let total = Infinity;

  while (all.length < total) {
    const resp = await openapiFetch("/market", {
      page,
      limit: PAGE_LIMIT,
      status: "activated",
      marketType: 2, // all types
      sortBy: 3,     // volume desc
    });
    if ((resp.errno ?? resp.code) !== 0) throw new Error(`OpenAPI error: ${resp.errmsg ?? resp.msg}`);

    const result = resp.result;
    total = result.total;
    const list: CachedMarket[] = result.list ?? [];
    if (list.length === 0) break;

    all.push(...list);
    page++;
  }
  return all;
}

// ── 缓存读写 ──

function readCache(): CacheEnvelope | null {
  if (!existsSync(CACHE_FILE)) return null;
  try {
    const raw = readFileSync(CACHE_FILE, "utf-8");
    return JSON.parse(raw) as CacheEnvelope;
  } catch { return null; }
}

function writeCache(markets: CachedMarket[]): void {
  mkdirSync(CACHE_DIR, { recursive: true });
  const envelope: CacheEnvelope = { timestamp: Date.now(), total: markets.length, markets };
  writeFileSync(CACHE_FILE, JSON.stringify(envelope));
}

export async function getMarkets(forceRefresh = false): Promise<CachedMarket[]> {
  if (!forceRefresh) {
    const cached = readCache();
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.markets;
    }
  }
  console.error(`[cache] Fetching all markets from OpenAPI...`);
  const markets = await fetchAllMarkets();
  writeCache(markets);
  console.error(`[cache] Cached ${markets.length} markets`);
  return markets;
}

// ── 模糊搜索 ──

function normalize(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, " ").trim();
}

function fuzzyScore(text: string, keyword: string): number {
  const t = normalize(text);
  const k = normalize(keyword);
  if (!t || !k) return 0;

  // 精确包含
  if (t === k) return 100;
  if (t.startsWith(k)) return 90;
  if (t.includes(k)) return 80;

  // 多词匹配: keyword 拆词, 每个词都在 text 中
  const kWords = k.split(/\s+/).filter(Boolean);
  if (kWords.length > 1) {
    const allMatch = kWords.every(w => t.includes(w));
    if (allMatch) return 70;
    const matchCount = kWords.filter(w => t.includes(w)).length;
    if (matchCount > 0) return 50 + (matchCount / kWords.length) * 15;
  }

  // 子序列匹配
  let ti = 0, ki = 0, matched = 0;
  while (ti < t.length && ki < k.length) {
    if (t[ti] === k[ki]) { matched++; ki++; }
    ti++;
  }
  if (ki === k.length) return 30 + (matched / t.length) * 20;

  // 部分字符匹配
  if (matched > 0) return (matched / k.length) * 25;

  return 0;
}

function scoreMarket(m: CachedMarket, keyword: string): number {
  let best = fuzzyScore(m.marketTitle || "", keyword);

  // 也搜索子市场标题
  if (m.childMarkets) {
    for (const child of m.childMarkets) {
      best = Math.max(best, fuzzyScore(child.marketTitle || "", keyword) * 0.95);
    }
  }
  return best;
}

export function fuzzySearch(markets: CachedMarket[], keyword: string, limit: number): SearchResult[] {
  const scored: SearchResult[] = [];
  for (const m of markets) {
    const score = scoreMarket(m, keyword);
    if (score > 10) {
      scored.push({ ...m, score, matchSource: "cache" });
    }
  }
  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, limit);
}

// ── 刷新缓存 CLI ──

if (import.meta.main) {
  getMarkets(true)
    .then(m => console.log(`Done. ${m.length} markets cached to ${CACHE_FILE}`))
    .catch(console.error);
}
