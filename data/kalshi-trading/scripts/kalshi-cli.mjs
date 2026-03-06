#!/usr/bin/env node

/**
 * Kalshi CLI — self-contained, zero-dependency Node.js script (ESM).
 *
 * Usage: node kalshi-cli.mjs <command> [args...]
 *
 * Commands:
 *   balance                          Account balance
 *   portfolio                        Balance + open positions
 *   trending                         Top markets by 24h volume
 *   search <query>                   Search markets by keyword
 *   market <ticker>                  Single market details
 *   orderbook <ticker>               Bid/ask levels
 *   buy <ticker> <yes|no> <count> <price>   Place buy order (price in cents)
 *   sell <ticker> <yes|no> <count> <price>  Place sell order (price in cents)
 *   cancel <orderId>                 Cancel resting order
 *   orders [resting|canceled|executed]  List orders
 *   fills [ticker]                   List recent fills
 *
 * Env vars:
 *   KALSHI_API_KEY_ID         API key UUID
 *   KALSHI_PRIVATE_KEY_PATH   Path to RSA private key PEM
 */

import crypto from "node:crypto";
import fs from "node:fs";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BASE_URL = "https://api.elections.kalshi.com/trade-api/v2";
const TIMEOUT_MS = 15_000;

function loadCredentials() {
  const apiKeyId = process.env.KALSHI_API_KEY_ID;
  const keyPath = process.env.KALSHI_PRIVATE_KEY_PATH;
  if (!apiKeyId || !keyPath) {
    throw new Error("Missing env vars: KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY_PATH are required");
  }
  const pem = fs.readFileSync(keyPath, "utf-8");
  const privateKey = crypto.createPrivateKey(pem);
  return { apiKeyId, privateKey };
}

// ---------------------------------------------------------------------------
// RSA-PSS Signing
// ---------------------------------------------------------------------------

function signRequest(credentials, method, path, timestampMs) {
  const ts = String(timestampMs ?? Date.now());
  // Strip query params for signing
  const idx = path.indexOf("?");
  const cleanPath = idx === -1 ? path : path.substring(0, idx);
  const message = `${ts}${method.toUpperCase()}${cleanPath}`;

  const signature = crypto.sign("sha256", Buffer.from(message, "utf-8"), {
    key: credentials.privateKey,
    padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
    saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST,
  });

  return {
    "KALSHI-ACCESS-KEY": credentials.apiKeyId,
    "KALSHI-ACCESS-TIMESTAMP": ts,
    "KALSHI-ACCESS-SIGNATURE": signature.toString("base64"),
  };
}

// ---------------------------------------------------------------------------
// HTTP Client
// ---------------------------------------------------------------------------

async function request(credentials, method, endpoint, params, body) {
  const url = new URL(`${BASE_URL}${endpoint}`);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const signingPath = url.pathname;
  const authHeaders = signRequest(credentials, method.toUpperCase(), signingPath);

  const headers = {
    ...authHeaders,
    Accept: "application/json",
  };

  const init = {
    method: method.toUpperCase(),
    headers,
    signal: AbortSignal.timeout(TIMEOUT_MS),
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(body);
  }

  const res = await fetch(url.toString(), init);

  if (!res.ok) {
    let errorBody;
    try {
      errorBody = await res.json();
    } catch {
      errorBody = await res.text();
    }
    const msg =
      typeof errorBody === "string" ? errorBody : `${errorBody.code}: ${errorBody.message}`;
    throw new Error(`Kalshi API ${res.status} on ${endpoint}: ${msg}`);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// API Methods
// ---------------------------------------------------------------------------

async function getBalance(creds) {
  const raw = await request(creds, "GET", "/portfolio/balance");
  return {
    balance_cents: raw.balance,
    portfolio_value_cents: raw.portfolio_value,
    balance_dollars: (raw.balance / 100).toFixed(2),
    portfolio_value_dollars: (raw.portfolio_value / 100).toFixed(2),
  };
}

async function getPositionsAll(creds) {
  const allMarket = [];
  const allEvent = [];
  let cursor;
  do {
    const params = { limit: 1000 };
    if (cursor) params.cursor = cursor;
    const res = await request(creds, "GET", "/portfolio/positions", params);
    allMarket.push(...(res.market_positions || []));
    allEvent.push(...(res.event_positions || []));
    cursor = res.cursor || undefined;
  } while (cursor);
  return { market_positions: allMarket, event_positions: allEvent };
}

async function getPortfolio(creds) {
  const [balance, positions] = await Promise.all([getBalance(creds), getPositionsAll(creds)]);
  return { ...balance, positions: positions.market_positions };
}

async function getEvents(creds, params) {
  return request(creds, "GET", "/events", params);
}

async function getTrendingMarkets(creds, limit = 15) {
  const allEntries = [];
  let cursor;
  let page = 0;
  do {
    const params = {
      status: "open",
      with_nested_markets: true,
      limit: 200,
    };
    if (cursor) params.cursor = cursor;
    const data = await getEvents(creds, params);
    for (const event of data.events || []) {
      for (const m of event.markets || []) {
        allEntries.push({
          market: m,
          series_ticker: event.series_ticker,
          vol24h: parseFloat(m.volume_24h_fp || "0") || 0,
        });
      }
    }
    cursor = data.cursor || undefined;
    page++;
  } while (cursor && page < 3);

  // Deduplicate: pick highest vol24h market per event
  const byEvent = new Map();
  for (const entry of allEntries) {
    const key = entry.market.event_ticker;
    if (!byEvent.has(key) || entry.vol24h > byEvent.get(key).vol24h) {
      byEvent.set(key, entry);
    }
  }

  const sorted = [...byEvent.values()].sort((a, b) => b.vol24h - a.vol24h);
  return sorted.slice(0, limit).map((e) => ({
    ticker: e.market.ticker,
    event_ticker: e.market.event_ticker,
    title: e.market.title,
    subtitle: e.market.subtitle,
    yes_bid: e.market.yes_bid_dollars,
    yes_ask: e.market.yes_ask_dollars,
    last_price: e.market.last_price_dollars,
    volume_24h: e.market.volume_24h_fp,
    volume: e.market.volume_fp,
    close_time: e.market.close_time,
  }));
}

async function searchMarkets(creds, query, limit = 20) {
  const data = await getEvents(creds, {
    limit: 200,
    with_nested_markets: true,
    status: "open",
  });

  const queryLower = query.toLowerCase();
  const queryTerms = queryLower.split(/\s+/).filter((t) => t.length > 0);
  const scored = [];

  for (const event of data.events || []) {
    const eventTitle = (event.title || "").toLowerCase();
    for (const m of event.markets || []) {
      const title = (m.title || "").toLowerCase();
      const subtitle = (m.subtitle || "").toLowerCase();
      const ticker = (m.ticker || "").toLowerCase();
      const combined = `${eventTitle} ${title} ${subtitle} ${ticker}`;

      const matchCount = queryTerms.filter((t) => combined.includes(t)).length;
      if (matchCount === 0) continue;

      let score = matchCount / queryTerms.length;
      if (matchCount === queryTerms.length) score += 1;
      if (combined.includes(queryLower)) score += 1;

      scored.push({ market: m, score });
    }
  }

  const volumeOf = (m) => parseFloat(m.volume_fp || "0") || 0;
  scored.sort((a, b) => b.score - a.score || volumeOf(b.market) - volumeOf(a.market));

  return scored.slice(0, limit).map((s) => ({
    ticker: s.market.ticker,
    event_ticker: s.market.event_ticker,
    title: s.market.title,
    subtitle: s.market.subtitle,
    yes_bid: s.market.yes_bid_dollars,
    yes_ask: s.market.yes_ask_dollars,
    last_price: s.market.last_price_dollars,
    volume_24h: s.market.volume_24h_fp,
    close_time: s.market.close_time,
  }));
}

async function getMarket(creds, ticker) {
  const data = await request(creds, "GET", `/markets/${encodeURIComponent(ticker)}`);
  const m = data.market;
  return {
    ticker: m.ticker,
    event_ticker: m.event_ticker,
    title: m.title,
    subtitle: m.subtitle,
    status: m.status,
    result: m.result,
    yes_bid: m.yes_bid_dollars,
    yes_ask: m.yes_ask_dollars,
    no_bid: m.no_bid_dollars,
    no_ask: m.no_ask_dollars,
    last_price: m.last_price_dollars,
    volume: m.volume_fp,
    volume_24h: m.volume_24h_fp,
    open_interest: m.open_interest_fp,
    liquidity: m.liquidity_dollars,
    close_time: m.close_time,
    rules_primary: m.rules_primary,
  };
}

async function getOrderbook(creds, ticker) {
  const data = await request(creds, "GET", `/markets/${encodeURIComponent(ticker)}/orderbook`, {
    depth: 10,
  });
  const book = data.orderbook;
  const parseLevel = (arr) => {
    if (!Array.isArray(arr)) return [];
    return arr.map((level) => ({ price: level[0], quantity: level[1] }));
  };
  return { ticker, yes: parseLevel(book.yes), no: parseLevel(book.no) };
}

async function createOrder(creds, ticker, action, side, count, priceCents) {
  const body = {
    ticker,
    action,
    side,
    count: parseInt(count, 10),
    type: "limit",
  };
  if (side === "yes") {
    body.yes_price = parseInt(priceCents, 10);
  } else {
    body.no_price = parseInt(priceCents, 10);
  }
  return request(creds, "POST", "/portfolio/orders", undefined, body);
}

async function cancelOrder(creds, orderId) {
  return request(creds, "DELETE", `/portfolio/orders/${encodeURIComponent(orderId)}`);
}

async function getOrders(creds, status) {
  const params = { limit: 100 };
  if (status) params.status = status;
  return request(creds, "GET", "/portfolio/orders", params);
}

async function getFills(creds, ticker) {
  const params = { limit: 100 };
  if (ticker) params.ticker = ticker;
  return request(creds, "GET", "/portfolio/fills", params);
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    console.error(
      "Usage: kalshi-cli.mjs <command> [args...]\n" +
        "Commands: balance, portfolio, trending, search, market, orderbook, buy, sell, cancel, orders, fills",
    );
    process.exit(1);
  }

  const creds = loadCredentials();

  let result;

  switch (command) {
    case "balance":
      result = await getBalance(creds);
      break;

    case "portfolio":
      result = await getPortfolio(creds);
      break;

    case "trending":
      result = await getTrendingMarkets(creds, parseInt(args[1] || "15", 10));
      break;

    case "search":
      if (!args[1]) {
        console.error("Usage: kalshi-cli.mjs search <query>");
        process.exit(1);
      }
      result = await searchMarkets(creds, args.slice(1).join(" "));
      break;

    case "market":
      if (!args[1]) {
        console.error("Usage: kalshi-cli.mjs market <ticker>");
        process.exit(1);
      }
      result = await getMarket(creds, args[1]);
      break;

    case "orderbook":
      if (!args[1]) {
        console.error("Usage: kalshi-cli.mjs orderbook <ticker>");
        process.exit(1);
      }
      result = await getOrderbook(creds, args[1]);
      break;

    case "buy":
    case "sell": {
      const [, ticker, side, count, price] = args;
      if (!ticker || !side || !count || !price) {
        console.error(`Usage: kalshi-cli.mjs ${command} <ticker> <yes|no> <count> <price>`);
        process.exit(1);
      }
      if (side !== "yes" && side !== "no") {
        console.error('Side must be "yes" or "no"');
        process.exit(1);
      }
      result = await createOrder(creds, ticker, command, side, count, price);
      break;
    }

    case "cancel":
      if (!args[1]) {
        console.error("Usage: kalshi-cli.mjs cancel <orderId>");
        process.exit(1);
      }
      result = await cancelOrder(creds, args[1]);
      break;

    case "orders":
      result = await getOrders(creds, args[1]);
      break;

    case "fills":
      result = await getFills(creds, args[1]);
      break;

    default:
      console.error(`Unknown command: ${command}`);
      process.exit(1);
  }

  console.log(JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
