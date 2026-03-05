#!/usr/bin/env node

const BASE_URL = process.env.DEXSCREENER_BASE_URL || "https://api.dexscreener.com";
const TIMEOUT_MS = Number(process.env.DEXSCREENER_TIMEOUT_MS || 15000);

function usage() {
  console.error(
    [
      "Usage:",
      "  dexscreener-cli.mjs search_pairs --query <text> [--limit <n>]",
      "  dexscreener-cli.mjs get_pair --chain <chainId> --pair <pairAddress>",
      "  dexscreener-cli.mjs pairs_by_tokens --token-addresses <a,b,...> [--limit <n>]",
      "  dexscreener-cli.mjs latest_token_profiles [--limit <n>]",
      "  dexscreener-cli.mjs latest_boosted_tokens [--limit <n>]",
      "  dexscreener-cli.mjs top_boosted_tokens [--limit <n>]",
      "  dexscreener-cli.mjs token_orders --chain <chainId> --token <tokenAddress> [--limit <n>]",
    ].join("\n"),
  );
}

function getArg(args, key) {
  const i = args.indexOf(key);
  if (i === -1) return undefined;
  const next = args[i + 1];
  if (!next || next.startsWith("--")) return undefined;
  return next;
}

function requireArg(args, key) {
  const value = getArg(args, key);
  if (!value) {
    throw new Error(`Missing required arg: ${key}`);
  }
  return value;
}

function parseLimit(args, fallback = 20, max = 200) {
  const raw = getArg(args, "--limit");
  if (!raw) return fallback;
  const n = Number(raw);
  if (!Number.isFinite(n) || n <= 0) {
    throw new Error("Invalid --limit (must be > 0)");
  }
  return Math.min(Math.floor(n), max);
}

function maybeSlice(value, limit) {
  if (Array.isArray(value)) return value.slice(0, limit);
  if (value && typeof value === "object" && Array.isArray(value.pairs)) {
    return { ...value, pairs: value.pairs.slice(0, limit) };
  }
  return value;
}

async function fetchJson(path, query) {
  const url = new URL(path, BASE_URL);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v != null && v !== "") url.searchParams.set(k, String(v));
    }
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(url, { signal: controller.signal });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new Error(`DexScreener HTTP ${res.status}: ${body || res.statusText}`);
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

  let out;
  if (command === "search_pairs") {
    const query = requireArg(args, "--query");
    const limit = parseLimit(args, 20);
    out = maybeSlice(await fetchJson("/latest/dex/search", { q: query }), limit);
  } else if (command === "get_pair") {
    const chain = requireArg(args, "--chain");
    const pair = requireArg(args, "--pair");
    out = await fetchJson(`/latest/dex/pairs/${encodeURIComponent(chain)}/${encodeURIComponent(pair)}`);
  } else if (command === "pairs_by_tokens") {
    const tokenAddresses = requireArg(args, "--token-addresses");
    const limit = parseLimit(args, 20);
    out = maybeSlice(
      await fetchJson(`/latest/dex/tokens/${encodeURIComponent(tokenAddresses)}`),
      limit,
    );
  } else if (command === "latest_token_profiles") {
    const limit = parseLimit(args, 20);
    out = maybeSlice(await fetchJson("/token-profiles/latest/v1"), limit);
  } else if (command === "latest_boosted_tokens") {
    const limit = parseLimit(args, 20);
    out = maybeSlice(await fetchJson("/token-boosts/latest/v1"), limit);
  } else if (command === "top_boosted_tokens") {
    const limit = parseLimit(args, 20);
    out = maybeSlice(await fetchJson("/token-boosts/top/v1"), limit);
  } else if (command === "token_orders") {
    const chain = requireArg(args, "--chain");
    const token = requireArg(args, "--token");
    const limit = parseLimit(args, 20);
    out = maybeSlice(
      await fetchJson(`/orders/v1/${encodeURIComponent(chain)}/${encodeURIComponent(token)}`),
      limit,
    );
  } else {
    throw new Error(`Unknown command: ${command}`);
  }

  process.stdout.write(`${JSON.stringify(out, null, 2)}\n`);
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exit(1);
});
