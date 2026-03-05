import { executeTool, resolveToolPayload, searchTools } from "../../infra/qveris-client.mjs";

const RADAR_SOURCES = [
  {
    name: "caidazi_news",
    prefix: "caidazi.news.query",
    searchQuery: "caidazi finance news API",
    defaultParams: (limit) => ({
      input: "行业 热点 赛道 主题",
      size: Math.max(3, Math.min(10, limit)),
      sortOrder: "desc",
      highlight: "true",
      timeSensitive: true,
    }),
  },
  {
    name: "caidazi_report",
    prefix: "caidazi.report.query",
    searchQuery: "caidazi investment report query API",
    defaultParams: (limit) => ({
      input: "行业 景气度 研报",
      size: Math.max(3, Math.min(10, limit)),
      sortOrder: "desc",
      highlight: "true",
    }),
  },
  {
    name: "caidazi_wechat",
    prefix: "caidazi.search.hybrid_v2.query",
    searchQuery: "caidazi wechat hybrid search API",
    defaultParams: (limit) => ({
      input: "行业 热点 主线",
      sourceType: "wechat,news,report",
      size: Math.max(3, Math.min(10, limit)),
      sortOrder: "desc",
      highlight: "true",
      timeSensitive: true,
    }),
  },
  {
    name: "x_hot_topics",
    prefix: "qveris_social.x_domain_hot_topics",
    searchQuery: "X Finance domain hot topics API",
    defaultParams: (limit) => ({
      domains: ["Finance"],
      limit: Math.max(5, Math.min(20, limit)),
      min_engagement: 30,
    }),
  },
  {
    name: "alpha_news_sentiment",
    prefix: "alphavantage.news_sentiment.query.v1",
    searchQuery: "alpha vantage global market news sentiment API",
    defaultParams: (limit) => ({
      function: "NEWS_SENTIMENT",
      topics: "financial_markets,economy_macro,technology",
      sort: "LATEST",
      limit: Math.max(5, Math.min(50, limit)),
    }),
  },
  {
    name: "finnhub_market_news",
    prefix: "finnhub.market.news.list.v1",
    searchQuery: "finnhub market news API",
    defaultParams: () => ({
      category: "general",
    }),
  },
];

function toNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function pickFirst(...values) {
  for (const v of values) {
    if (v == null) continue;
    if (typeof v === "string" && v.trim() === "") continue;
    return v;
  }
  return null;
}

function extractTopicArrays(content) {
  if (!content) return [];
  const arrays = [];
  if (Array.isArray(content)) arrays.push(content);
  if (Array.isArray(content?.feed)) arrays.push(content.feed);
  if (Array.isArray(content?.topics)) arrays.push(content.topics);
  if (Array.isArray(content?.data)) arrays.push(content.data);
  if (Array.isArray(content?.results)) arrays.push(content.results);
  if (Array.isArray(content?.posts)) arrays.push(content.posts);
  if (Array.isArray(content?.items)) arrays.push(content.items);
  if (Array.isArray(content?.hits)) arrays.push(content.hits);
  if (Array.isArray(content?.data?.hits)) arrays.push(content.data.hits);
  if (Array.isArray(content?.by_domain?.Finance)) arrays.push(content.by_domain.Finance);
  if (Array.isArray(content?.news)) arrays.push(content.news);
  if (Array.isArray(content?.articles)) arrays.push(content.articles);
  return arrays;
}

function extractTickers(obj) {
  const tickers = [];
  if (Array.isArray(obj?.ticker_sentiment)) {
    for (const ts of obj.ticker_sentiment) {
      if (ts?.ticker) tickers.push(ts.ticker);
    }
  }
  if (Array.isArray(obj?.tickers)) {
    for (const t of obj.tickers) {
      if (typeof t === "string") tickers.push(t);
      else if (t?.ticker) tickers.push(t.ticker);
    }
  }
  if (obj?.related && typeof obj.related === "string") {
    const parts = obj.related.split(",").map((s) => s.trim()).filter(Boolean);
    tickers.push(...parts);
  }
  const tickerMatch = String(obj?.title || obj?.headline || "").match(/\$([A-Z]{1,5})/g);
  if (tickerMatch) {
    for (const m of tickerMatch) tickers.push(m.replace("$", ""));
  }
  return [...new Set(tickers)].slice(0, 5);
}

function normalizeTopic(rawItem, sourceName) {
  const sourceObj = rawItem?.source && typeof rawItem.source === "object" ? rawItem.source : rawItem;
  const title = pickFirst(
    sourceObj?.title,
    sourceObj?.headline,
    sourceObj?.topic,
    sourceObj?.name,
    sourceObj?.summary,
    sourceObj?.banner_image ? null : sourceObj?.text,
    sourceObj?.full_text,
  );
  if (!title) return null;
  const category = pickFirst(
    sourceObj?.topics?.[0]?.topic,
    sourceObj?.category,
    sourceObj?.theme,
    sourceObj?.tag,
    sourceName === "alpha_news_sentiment" ? "global_markets" : null,
    sourceName === "finnhub_market_news" ? "market_news" : null,
    sourceName === "caidazi_report" ? "research" : null,
    sourceName === "caidazi_news" ? "cn_news" : null,
    sourceName === "caidazi_wechat" ? "cn_wechat" : null,
    sourceName === "x_hot_topics" ? "social" : null,
  );
  const publishTime = pickFirst(
    sourceObj?.time_published,
    sourceObj?.publishTime,
    sourceObj?.published_at,
    sourceObj?.datetime,
    sourceObj?.created_at,
    sourceObj?.time,
    sourceObj?.effectiveTime,
  );
  const sentiment = toNumber(
    pickFirst(
      sourceObj?.overall_sentiment_score,
      sourceObj?.sentiment_score,
      sourceObj?.sentiment,
    ),
  );
  const url = pickFirst(
    sourceObj?.url,
    sourceObj?.link,
    sourceObj?.source_url,
  );
  const tickers = extractTickers(sourceObj);
  return {
    title: String(title).trim(),
    category: category ? String(category).trim().toLowerCase().replace(/\s+/g, "_") : null,
    source: sourceName,
    publishTime: publishTime || null,
    sentiment,
    tickers: tickers.length > 0 ? tickers : null,
    url: url || null,
  };
}

const SOURCE_QUALITY_WEIGHTS = {
  alpha_news_sentiment: 100,
  finnhub_market_news: 95,
  caidazi_report: 90,
  caidazi_news: 85,
  caidazi_wechat: 80,
  x_hot_topics: 30,
  fallback_generated: 10,
};

function isLowQualityContent(title) {
  if (!title) return true;
  const t = String(title).trim();
  if (t.length < 15) return true;
  if (/^@\w+\s*[\p{Emoji}\s]*$/u.test(t)) return true;
  if (/^[\p{Emoji}\s]+$/u.test(t)) return true;
  if (/^(Yes|No|Yup|Nope|Exactly|True|False|💯|😂|👍|🔥)\s*$/i.test(t)) return true;
  if (t.startsWith("@") && t.length < 30 && !t.includes(" ")) return true;
  return false;
}

function dedupeAndSortTopics(items = [], limit = 10) {
  const seen = new Set();
  const deduped = [];
  for (const item of items) {
    if (!item || !item.title) continue;
    if (isLowQualityContent(item.title)) continue;
    const key = String(item.title).trim().toLowerCase().slice(0, 80);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    deduped.push(item);
  }
  deduped.sort((a, b) => {
    const wa = SOURCE_QUALITY_WEIGHTS[a.source] ?? 50;
    const wb = SOURCE_QUALITY_WEIGHTS[b.source] ?? 50;
    if (wa !== wb) return wb - wa;
    const ta = a.publishTime ? new Date(a.publishTime).getTime() : 0;
    const tb = b.publishTime ? new Date(b.publishTime).getTime() : 0;
    return tb - ta;
  });
  return deduped.slice(0, limit);
}

// Note: Analysis (theme clustering, investment logic, suggestions) is delegated to OpenClaw's LLM
// via the Hot Topic Analysis Guide in SKILL.md. This function only outputs structured data.

async function runSource(source, args, limit) {
  const timeoutMs = args.timeoutMs || 25_000;
  const maxSize = args.maxSize || 30_000;
  try {
    const searchResult = await searchTools(source.searchQuery, 15, timeoutMs);
    const tools = Array.isArray(searchResult?.results) ? searchResult.results : [];
    const preferred = tools.find((t) => String(t?.tool_id || "").startsWith(source.prefix));
    const selected = preferred || tools[0] || null;
    if (!selected?.tool_id) {
      return {
        source: source.name,
        ok: false,
        error: "no tool found",
        toolId: null,
        searchId: searchResult?.search_id || null,
        topics: [],
      };
    }
    const params = source.defaultParams(limit);
    const raw = await executeTool(selected.tool_id, searchResult?.search_id || null, params, maxSize, timeoutMs);
    const extracted = await resolveToolPayload(raw, {
      fetchFullContent: true,
      timeoutMs,
      fullContentAllowedHosts: ["qveris.ai"],
    });
    const content = extracted?.content ?? raw?.result ?? raw?.data ?? raw ?? {};
    const arrays = extractTopicArrays(content);
    const normalized = [];
    for (const arr of arrays) {
      for (const item of arr) {
        const n = normalizeTopic(item, source.name);
        if (n) normalized.push(n);
      }
    }
    return {
      source: source.name,
      ok: normalized.length > 0,
      error: normalized.length > 0 ? null : "empty content",
      toolId: selected.tool_id,
      searchId: searchResult?.search_id || null,
      contentMode: extracted?.meta?.contentMode || "payload",
      hasTruncatedContent: Boolean(extracted?.meta?.hasTruncatedContent),
      topics: normalized,
    };
  } catch (error) {
    return {
      source: source.name,
      ok: false,
      error: error?.message || String(error),
      toolId: null,
      searchId: null,
      topics: [],
    };
  }
}

export async function radarCommand(args = {}) {
  const market = String(args.market || "GLOBAL").toUpperCase();
  const limit = Math.max(5, Number(args.limit || 10));
  const sourceResults = await Promise.all(RADAR_SOURCES.map((source) => runSource(source, args, limit)));
  const merged = sourceResults.flatMap((x) => x.topics || []);
  let topics = dedupeAndSortTopics(merged, limit);
  if (topics.length === 0) {
    topics = [
      {
        title: "全球宏观与流动性预期",
        topic: "宏观流动性",
        source: "fallback_generated",
        publishTime: new Date().toISOString(),
        engagement: null,
      },
    ];
  }
  return {
    mode: "radar",
    market,
    generatedAt: new Date().toISOString(),
    topicCount: topics.length,
    topics,
    meta: {
      sourceStats: sourceResults.map((x) => ({
        source: x.source,
        ok: x.ok,
        count: (x.topics || []).length,
        toolId: x.toolId,
        searchId: x.searchId,
        error: x.error,
      })),
      sourceCount: sourceResults.length,
      note: "Analysis delegated to OpenClaw LLM via SKILL.md Hot Topic Analysis Guide",
    },
  };
}
