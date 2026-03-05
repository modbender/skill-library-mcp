#!/usr/bin/env node

const BASE_URL = new URL("https://api.geckoterminal.com/api/v2/");
const BASE_ORIGIN = BASE_URL.origin;
const BASE_PATH_PREFIX = BASE_URL.pathname.endsWith("/")
  ? BASE_URL.pathname
  : `${BASE_URL.pathname}/`;
const TIMEOUT_MS = Number(process.env.GECKOTERMINAL_TIMEOUT_MS || 15000);

function usage() {
  console.error([
    "Usage:",
    "  geckoterminal-cli.mjs api_get --path <path> [--query-json '{\"k\":\"v\"}']",
    "  geckoterminal-cli.mjs get_networks [--page <n>]",
    "  geckoterminal-cli.mjs get_dexes --network <network> [--page <n>]",
    "  geckoterminal-cli.mjs get_global_trending_pools [--duration 5m|1h|6h|24h] [--page <n>] [--include <csv>] [--include-gt-community-data true|false]",
    "  geckoterminal-cli.mjs get_network_trending_pools --network <network> [--duration ...] [--page <n>] [--include <csv>] [--include-gt-community-data true|false]",
    "  geckoterminal-cli.mjs get_global_new_pools [--page <n>] [--include <csv>] [--include-gt-community-data true|false]",
    "  geckoterminal-cli.mjs get_network_new_pools --network <network> [--page <n>] [--include <csv>] [--include-gt-community-data true|false]",
    "  geckoterminal-cli.mjs get_top_pools --network <network> [--page <n>] [--include <csv>] [--sort <field>] [--include-gt-community-data true|false]",
    "  geckoterminal-cli.mjs get_dex_pools --network <network> --dex <dex> [--page <n>] [--include <csv>] [--sort <field>] [--include-gt-community-data true|false]",
    "  geckoterminal-cli.mjs search_pools --query <text> [--network <network>] [--page <n>] [--include <csv>]",
    "  geckoterminal-cli.mjs get_pool --network <network> --pool <poolAddress> [--include <csv>] [--include-volume-breakdown true|false] [--include-composition true|false]",
    "  geckoterminal-cli.mjs get_multi_pools --network <network> --pool-addresses <a,b,...> [--include <csv>] [--include-volume-breakdown true|false] [--include-composition true|false]",
    "  geckoterminal-cli.mjs get_token --network <network> --token <tokenAddress> [--include <csv>] [--include-composition true|false] [--include-inactive-source true|false]",
    "  geckoterminal-cli.mjs get_multi_tokens --network <network> --token-addresses <a,b,...> [--include <csv>] [--include-composition true|false] [--include-inactive-source true|false]",
    "  geckoterminal-cli.mjs get_token_info --network <network> --token <tokenAddress>",
    "  geckoterminal-cli.mjs get_token_pools --network <network> --token <tokenAddress> [--page <n>] [--include <csv>] [--sort <field>] [--include-inactive-source true|false]",
    "  geckoterminal-cli.mjs get_pool_info --network <network> --pool <poolAddress>",
    "  geckoterminal-cli.mjs get_pool_trades --network <network> --pool <poolAddress> [--page <n>] [--trade-volume-usd-gt <n>] [--token base|quote]",
    "  geckoterminal-cli.mjs get_pool_ohlcv --network <network> --pool <poolAddress> --timeframe minute|hour|day [--aggregate <n>] [--before-timestamp <unix>] [--limit <n>] [--currency usd|token] [--token base|quote] [--include-empty-intervals true|false]",
    "  geckoterminal-cli.mjs get_recently_updated_token_info [--network <network>] [--page <n>] [--include <csv>]",
    "  geckoterminal-cli.mjs get_simple_token_prices --network <network> --token-addresses <a,b,...> [--include-market-cap true|false] [--mcap-fdv-fallback true|false] [--include-24hr-vol true|false] [--include-24hr-price-change true|false] [--include-total-reserve-in-usd true|false] [--include-inactive-source true|false]",
  ].join("\n"));
}

function arg(args, key) {
  const i = args.indexOf(key);
  if (i === -1) return undefined;
  const v = args[i + 1];
  if (!v || v.startsWith("--")) return undefined;
  return v;
}

function req(args, key) {
  const v = arg(args, key);
  if (!v) throw new Error(`Missing required arg: ${key}`);
  return v;
}

function intArg(args, key, fallback) {
  const raw = arg(args, key);
  if (!raw) return fallback;
  const n = Number(raw);
  if (!Number.isFinite(n)) throw new Error(`Invalid number for ${key}`);
  return Math.floor(n);
}

function boolArg(args, key, fallback) {
  const raw = arg(args, key);
  if (!raw) return fallback;
  if (raw === "true") return true;
  if (raw === "false") return false;
  throw new Error(`Invalid boolean for ${key}: use true|false`);
}

function queryFromJson(args) {
  const raw = arg(args, "--query-json");
  if (!raw) return undefined;
  const parsed = JSON.parse(raw);
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("--query-json must be a JSON object");
  }
  return parsed;
}

function cleanObj(obj) {
  return Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== undefined && v !== null && v !== ""));
}

function normalizeApiPath(path) {
  const raw = String(path ?? "").trim();
  if (!raw) throw new Error("Path is required");
  if (raw.includes("?") || raw.includes("#")) {
    throw new Error("Path must not include querystring or fragment; use --query-json");
  }
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(raw) || raw.startsWith("//")) {
    throw new Error("Absolute URLs are not allowed");
  }
  const normalized = raw.replace(/^\/+/, "");
  if (!normalized) throw new Error("Path must point to an API resource");
  if (normalized.split("/").some((part) => part === "." || part === "..")) {
    throw new Error("Path traversal segments are not allowed");
  }
  return normalized;
}

async function get(path, query) {
  const normalizedPath = normalizeApiPath(path);
  const url = new URL(normalizedPath, BASE_URL);

  if (url.origin !== BASE_ORIGIN || !url.pathname.startsWith(BASE_PATH_PREFIX)) {
    throw new Error("Refusing outbound request outside GeckoTerminal API v2");
  }

  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, { method: "GET", signal: controller.signal, headers: { accept: "application/json" } });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new Error(`GeckoTerminal HTTP ${res.status}: ${body || res.statusText}`);
    }
    return await res.json();
  } finally {
    clearTimeout(timeout);
  }
}

async function main() {
  const [, , command, ...args] = process.argv;
  if (!command || command === "--help" || command === "-h") {
    usage();
    process.exit(command ? 0 : 1);
  }

  let path;
  let query;

  switch (command) {
    case "api_get":
      path = req(args, "--path");
      query = queryFromJson(args);
      break;
    case "get_networks":
      path = "/networks";
      query = cleanObj({ page: intArg(args, "--page", undefined) });
      break;
    case "get_dexes":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/dexes`;
      query = cleanObj({ page: intArg(args, "--page", undefined) });
      break;
    case "get_global_trending_pools":
      path = "/networks/trending_pools";
      query = cleanObj({
        duration: arg(args, "--duration") || "5m",
        page: intArg(args, "--page", 1),
        include: arg(args, "--include"),
        include_gt_community_data: boolArg(args, "--include-gt-community-data", undefined),
      });
      break;
    case "get_network_trending_pools":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/trending_pools`;
      query = cleanObj({
        duration: arg(args, "--duration") || "5m",
        page: intArg(args, "--page", 1),
        include: arg(args, "--include"),
        include_gt_community_data: boolArg(args, "--include-gt-community-data", undefined),
      });
      break;
    case "get_global_new_pools":
      path = "/networks/new_pools";
      query = cleanObj({
        page: intArg(args, "--page", 1),
        include: arg(args, "--include"),
        include_gt_community_data: boolArg(args, "--include-gt-community-data", undefined),
      });
      break;
    case "get_network_new_pools":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/new_pools`;
      query = cleanObj({
        page: intArg(args, "--page", 1),
        include: arg(args, "--include"),
        include_gt_community_data: boolArg(args, "--include-gt-community-data", undefined),
      });
      break;
    case "get_top_pools":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/pools`;
      query = cleanObj({
        page: intArg(args, "--page", 1),
        include: arg(args, "--include"),
        sort: arg(args, "--sort"),
        include_gt_community_data: boolArg(args, "--include-gt-community-data", undefined),
      });
      break;
    case "get_dex_pools":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/dexes/${encodeURIComponent(req(args, "--dex"))}/pools`;
      query = cleanObj({
        page: intArg(args, "--page", 1),
        include: arg(args, "--include"),
        sort: arg(args, "--sort"),
        include_gt_community_data: boolArg(args, "--include-gt-community-data", undefined),
      });
      break;
    case "search_pools":
      path = "/search/pools";
      query = cleanObj({
        query: req(args, "--query"),
        network: arg(args, "--network"),
        include: arg(args, "--include"),
        page: intArg(args, "--page", 1),
      });
      break;
    case "get_pool":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/pools/${encodeURIComponent(req(args, "--pool"))}`;
      query = cleanObj({
        include: arg(args, "--include"),
        include_volume_breakdown: boolArg(args, "--include-volume-breakdown", undefined),
        include_composition: boolArg(args, "--include-composition", undefined),
      });
      break;
    case "get_multi_pools":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/pools/multi/${encodeURIComponent(req(args, "--pool-addresses"))}`;
      query = cleanObj({
        include: arg(args, "--include"),
        include_volume_breakdown: boolArg(args, "--include-volume-breakdown", undefined),
        include_composition: boolArg(args, "--include-composition", undefined),
      });
      break;
    case "get_token":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/tokens/${encodeURIComponent(req(args, "--token"))}`;
      query = cleanObj({
        include: arg(args, "--include"),
        include_composition: boolArg(args, "--include-composition", undefined),
        include_inactive_source: boolArg(args, "--include-inactive-source", undefined),
      });
      break;
    case "get_multi_tokens":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/tokens/multi/${encodeURIComponent(req(args, "--token-addresses"))}`;
      query = cleanObj({
        include: arg(args, "--include"),
        include_composition: boolArg(args, "--include-composition", undefined),
        include_inactive_source: boolArg(args, "--include-inactive-source", undefined),
      });
      break;
    case "get_token_info":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/tokens/${encodeURIComponent(req(args, "--token"))}/info`;
      break;
    case "get_token_pools":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/tokens/${encodeURIComponent(req(args, "--token"))}/pools`;
      query = cleanObj({
        page: intArg(args, "--page", 1),
        include: arg(args, "--include"),
        sort: arg(args, "--sort"),
        include_inactive_source: boolArg(args, "--include-inactive-source", undefined),
      });
      break;
    case "get_pool_info":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/pools/${encodeURIComponent(req(args, "--pool"))}/info`;
      break;
    case "get_pool_trades":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/pools/${encodeURIComponent(req(args, "--pool"))}/trades`;
      query = cleanObj({
        page: intArg(args, "--page", 1),
        trade_volume_in_usd_greater_than: arg(args, "--trade-volume-usd-gt"),
        token: arg(args, "--token"),
      });
      break;
    case "get_pool_ohlcv":
      path = `/networks/${encodeURIComponent(req(args, "--network"))}/pools/${encodeURIComponent(req(args, "--pool"))}/ohlcv/${encodeURIComponent(req(args, "--timeframe"))}`;
      query = cleanObj({
        aggregate: arg(args, "--aggregate"),
        before_timestamp: arg(args, "--before-timestamp"),
        limit: intArg(args, "--limit", 100),
        currency: arg(args, "--currency") || "usd",
        token: arg(args, "--token") || "base",
        include_empty_intervals: boolArg(args, "--include-empty-intervals", false),
      });
      break;
    case "get_recently_updated_token_info":
      path = "/tokens/info_recently_updated";
      query = cleanObj({
        network: arg(args, "--network"),
        page: intArg(args, "--page", 1),
        include: arg(args, "--include"),
      });
      break;
    case "get_simple_token_prices":
      path = `/simple/networks/${encodeURIComponent(req(args, "--network"))}/token_price/${encodeURIComponent(req(args, "--token-addresses"))}`;
      query = cleanObj({
        include_market_cap: boolArg(args, "--include-market-cap", undefined),
        mcap_fdv_fallback: boolArg(args, "--mcap-fdv-fallback", undefined),
        include_24hr_vol: boolArg(args, "--include-24hr-vol", undefined),
        include_24hr_price_change: boolArg(args, "--include-24hr-price-change", undefined),
        include_total_reserve_in_usd: boolArg(args, "--include-total-reserve-in-usd", undefined),
        include_inactive_source: boolArg(args, "--include-inactive-source", undefined),
      });
      break;
    default:
      throw new Error(`Unknown command: ${command}`);
  }

  const out = await get(path, query);
  process.stdout.write(`${JSON.stringify(out, null, 2)}\n`);
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exit(1);
});
