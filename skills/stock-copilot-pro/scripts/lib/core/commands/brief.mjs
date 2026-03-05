import { loadWatchlist } from "../../config/watchlist.mjs";
import { radarCommand } from "./radar.mjs";

function flattenSymbols(watchlist, maxItems = 8) {
  const all = [...(watchlist.holdings || []), ...(watchlist.watchlist || [])];
  const seen = new Set();
  const out = [];
  for (const item of all) {
    const key = `${item.symbol}#${item.market}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(item);
    if (out.length >= maxItems) break;
  }
  return out;
}

function indexUniverseForMarket(market = "GLOBAL") {
  const m = String(market || "GLOBAL").toUpperCase();
  if (m === "CN") {
    return [
      { symbol: "000001.SS", market: "CN", name: "上证指数" },
      { symbol: "399001.SZ", market: "CN", name: "深证成指" },
    ];
  }
  if (m === "HK") {
    return [
      { symbol: "HSI", market: "HK", name: "恒生指数" },
      { symbol: "HSCEI", market: "HK", name: "国企指数" },
    ];
  }
  if (m === "US") {
    return [
      { symbol: "SPY", market: "US", name: "标普500代理" },
      { symbol: "QQQ", market: "US", name: "纳斯达克100代理" },
    ];
  }
  return [
    { symbol: "SPY", market: "US", name: "标普500代理" },
    { symbol: "QQQ", market: "US", name: "纳斯达克100代理" },
    { symbol: "0700.HK", market: "HK", name: "港股风向代理" },
  ];
}

async function buildMarketOverview(args, analyzeSymbol) {
  const indices = indexUniverseForMarket(args.market);
  const rows = [];
  for (const idx of indices) {
    try {
      const result = await analyzeSymbol(idx.symbol, {
        ...args,
        market: idx.market,
        mode: "basic",
        skipQuestionnaire: true,
        summaryOnly: true,
      });
      const quote = result?.data?.quote?.parsed || {};
      rows.push({
        name: idx.name,
        symbol: result?.symbol || idx.symbol,
        market: result?.market || idx.market,
        price: quote.price ?? null,
        percentChange: quote.percentChange ?? null,
        timestamp: quote.timestamp ?? null,
      });
    } catch (error) {
      rows.push({
        name: idx.name,
        symbol: idx.symbol,
        market: idx.market,
        error: error?.message || String(error),
      });
    }
  }
  const valid = rows.filter((x) => !x.error && x.price != null);
  const up = valid.filter((x) => Number(x.percentChange) > 0).length;
  const down = valid.filter((x) => Number(x.percentChange) < 0).length;
  return {
    indices: rows,
    sentiment:
      valid.length === 0
        ? "unknown"
        : up >= down
          ? "risk_on"
          : "risk_off",
  };
}

function summarizeBriefDataSources(radarMeta, reports) {
  const rows = [];
  const sourceStats = radarMeta?.sourceStats || [];
  for (const stat of sourceStats) {
    if (!stat?.ok || !stat?.toolId) continue;
    rows.push({
      scope: "radar",
      source: stat.source || "unknown",
      toolId: stat.toolId,
    });
  }
  for (const report of reports || []) {
    for (const ds of report?.dataSources || []) {
      if (!ds?.toolId) continue;
      rows.push({
        scope: `holding:${report.symbol || "unknown"}`,
        source: ds.provider || "unknown",
        toolId: ds.toolId,
      });
    }
  }
  const uniq = new Map();
  for (const row of rows) {
    const key = `${row.scope}#${row.toolId}`;
    if (!uniq.has(key)) uniq.set(key, row);
  }
  return [...uniq.values()];
}

export async function briefCommand(args = {}, context = {}) {
  const type = String(args.briefType || args.type || "morning").toLowerCase();
  const maxItems = Math.max(1, Number(args.maxItems || 8));
  const analyzeSymbol = context.analyzeSymbol;
  if (typeof analyzeSymbol !== "function") {
    throw new Error("brief command requires analyzeSymbol context");
  }

  const state = await loadWatchlist();
  const symbols = flattenSymbols(state, maxItems);
  const reports = [];
  const marketOverview = await buildMarketOverview(args, analyzeSymbol);
  const radar = await radarCommand({
    ...args,
    market: args.market || "GLOBAL",
    limit: Math.max(5, Number(args.limit || 8)),
  });
  const highlights = (radar?.topics || []).slice(0, 5).map((item) => ({
    title: item.title || "未命名热点",
    source: item.source || "unknown",
    category: item.category || null,
    publishTime: item.publishTime || null,
    tickers: item.tickers || null,
    sentiment: item.sentiment ?? null,
  }));

  for (const item of symbols) {
    try {
      const result = await analyzeSymbol(item.symbol, {
        ...args,
        market: item.market || args.market || "GLOBAL",
        mode: "basic",
        skipQuestionnaire: true,
        summaryOnly: true,
      });
      reports.push({
        symbol: result.symbol,
        market: result.market,
        price: result?.data?.quote?.parsed?.price ?? null,
        percentChange: result?.data?.quote?.parsed?.percentChange ?? null,
        grade: result.analysis?.scorecard?.grade || "N/A",
        score: result.analysis?.scorecard?.composite ?? null,
        signal: result.analysis?.recommendation?.signal || "N/A",
        risk: result.analysis?.chaseRisk?.risk || "unknown",
        dataSources: result?.dataSources || [],
      });
    } catch (error) {
      reports.push({
        symbol: item.symbol,
        market: item.market || "GLOBAL",
        error: error?.message || String(error),
      });
    }
  }

  const dataSources = summarizeBriefDataSources(radar?.meta || null, reports);

  return {
    mode: "brief",
    type,
    generatedAt: new Date().toISOString(),
    coverage: {
      holdings: (state.holdings || []).length,
      watchlist: (state.watchlist || []).length,
      analyzed: reports.length,
    },
    marketOverview,
    highlights,
    radarMeta: radar?.meta || null,
    dataSources,
    meta: {
      note: "Analysis delegated to OpenClaw LLM via SKILL.md Daily Brief Analysis Guide",
      guide: "Daily Brief Analysis Guide",
    },
    reports,
  };
}
