import { DEFAULT_WATCHLIST } from "./defaults.mjs";
import { readJsonOrDefault, resolveSkillPath, writeJson } from "./loader.mjs";

export function getWatchlistPath() {
  return resolveSkillPath("config", "watchlist.json");
}

function normalizeItem(item, defaultMarket = "GLOBAL") {
  if (typeof item === "string") {
    return { symbol: item, market: defaultMarket };
  }
  return {
    symbol: String(item?.symbol || "").trim(),
    market: String(item?.market || defaultMarket).toUpperCase(),
    note: item?.note || null,
  };
}

function dedupe(items = []) {
  const seen = new Set();
  const out = [];
  for (const item of items) {
    const normalized = normalizeItem(item);
    if (!normalized.symbol) continue;
    const key = `${normalized.symbol.toUpperCase()}#${normalized.market}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(normalized);
  }
  return out;
}

export async function loadWatchlist() {
  const data = await readJsonOrDefault(getWatchlistPath(), DEFAULT_WATCHLIST);
  return {
    ...DEFAULT_WATCHLIST,
    ...data,
    holdings: dedupe(data?.holdings || []),
    watchlist: dedupe(data?.watchlist || []),
  };
}

export async function saveWatchlist(value) {
  const normalized = {
    ...DEFAULT_WATCHLIST,
    ...value,
    updatedAt: new Date().toISOString(),
    holdings: dedupe(value?.holdings || []),
    watchlist: dedupe(value?.watchlist || []),
  };
  await writeJson(getWatchlistPath(), normalized);
  return normalized;
}

export async function addWatchSymbol(symbol, market = "GLOBAL", bucket = "watchlist") {
  const state = await loadWatchlist();
  const target = bucket === "holdings" ? "holdings" : "watchlist";
  state[target] = [...state[target], normalizeItem({ symbol, market })];
  return saveWatchlist(state);
}

export async function removeWatchSymbol(symbol, market = "GLOBAL", bucket = "watchlist") {
  const state = await loadWatchlist();
  const target = bucket === "holdings" ? "holdings" : "watchlist";
  const normalizedSymbol = String(symbol || "").trim().toUpperCase();
  const normalizedMarket = String(market || "GLOBAL").toUpperCase();
  state[target] = state[target].filter(
    (item) => !(item.symbol.toUpperCase() === normalizedSymbol && item.market.toUpperCase() === normalizedMarket),
  );
  return saveWatchlist(state);
}
