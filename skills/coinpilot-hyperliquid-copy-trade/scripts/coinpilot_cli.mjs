#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";

const getApiBaseUrl = () =>
  process.env.COINPILOT_API_BASE_URL || "https://api.coinpilot.bot";
const HYPERLIQUID_API_ENDPOINT = "https://api.hyperliquid.xyz";
const DEFAULT_WALLETS_PATH =
  process.env.COINPILOT_CONFIG_PATH ||
  path.resolve(process.cwd(), "tmp/coinpilot.json");
const RATE_LIMIT_MS = 200;

let lastRequestAt = 0;
let coinpilotQueue = Promise.resolve();

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const throttle = async () => {
  const now = Date.now();
  const wait = RATE_LIMIT_MS - (now - lastRequestAt);
  if (wait > 0) await sleep(wait);
  lastRequestAt = Date.now();
};

const withCoinpilotLock = async (fn) => {
  const start = coinpilotQueue;
  let release;
  coinpilotQueue = new Promise((resolve) => {
    release = resolve;
  });
  return start.then(fn).finally(release);
};

const readJson = async (filePath) => {
  const raw = await fs.readFile(filePath, "utf8");
  return JSON.parse(raw);
};

const validateWallets = (data) => {
  if (!data || typeof data !== "object")
    throw new Error("coinpilot.json must be an object");
  if (!data.apiKey || typeof data.apiKey !== "string")
    throw new Error("Missing apiKey");
  if (!data.userId || typeof data.userId !== "string")
    throw new Error("Missing userId");
  if (!Array.isArray(data.wallets) || data.wallets.length < 2) {
    throw new Error("wallets must be an array with at least 2 entries");
  }

  const primaryWallets = data.wallets.filter((wallet) => wallet.isPrimary);
  if (primaryWallets.length !== 1) {
    throw new Error("Exactly one wallet must have isPrimary: true");
  }

  const primary = primaryWallets[0];
  if (primary.index !== 0) {
    throw new Error("Primary wallet must have index 0");
  }

  for (const wallet of data.wallets) {
    if (typeof wallet.index !== "number")
      throw new Error("wallet.index must be a number");
    if (!wallet.address || typeof wallet.address !== "string") {
      throw new Error("wallet.address must be a string");
    }
    if (!wallet.privateKey || typeof wallet.privateKey !== "string") {
      throw new Error("wallet.privateKey must be a string");
    }
    if (typeof wallet.isPrimary !== "boolean") {
      throw new Error("wallet.isPrimary must be a boolean");
    }
  }
  return data;
};

const getPrimaryWallet = (wallets) =>
  wallets.wallets.find((wallet) => wallet.isPrimary);

const findWalletByAddress = (wallets, address) =>
  wallets.wallets.find(
    (wallet) => wallet.address.toLowerCase() === address.toLowerCase(),
  );

const findWalletByIndex = (wallets, index) =>
  wallets.wallets.find((wallet) => wallet.index === index);

const parseArgs = (argv) => {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      args._.push(token);
      continue;
    }
    const key = token.replace(/^--/, "");
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
    } else {
      args[key] = next;
      i += 1;
    }
  }
  return args;
};

const toNumber = (value, field) => {
  if (value === undefined) return undefined;
  const parsed = Number(value);
  if (Number.isNaN(parsed)) throw new Error(`${field} must be a number`);
  return parsed;
};

const toBoolean = (value) => {
  if (value === undefined) return undefined;
  if (value === true) return true;
  if (value === "true") return true;
  if (value === "false") return false;
  return undefined;
};

const formatOutput = (data) => {
  console.log(JSON.stringify(data, null, 2));
};

const requestCoinpilot = async (
  method,
  route,
  wallets,
  body,
  query,
  extraHeaders,
) => {
  return withCoinpilotLock(async () => {
    await throttle();
    const primary = getPrimaryWallet(wallets);
    const baseUrl = getApiBaseUrl();
    const url = new URL(route, baseUrl);
    if (query) {
      for (const [key, value] of Object.entries(query)) {
        if (value === undefined || value === "") continue;
        url.searchParams.set(key, String(value));
      }
    }
    console.log(`[coinpilot] ${method} ${url.toString()}`);
    const headers = {
      "Content-Type": "application/json",
      "x-api-key": wallets.apiKey,
      "x-wallet-private-key": primary.privateKey,
      ...extraHeaders,
    };
    const res = await fetch(url.toString(), {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    const contentType = res.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await res.json()
      : await res.text();
    if (!res.ok) {
      const message =
        typeof payload === "string" ? payload : JSON.stringify(payload);
      throw new Error(
        `Coinpilot ${method} ${route} failed (${res.status}): ${message}`,
      );
    }
    if (payload && typeof payload === "object" && "success" in payload) {
      if (payload.success === false) {
        const message = payload.error
          ? String(payload.error)
          : JSON.stringify(payload);
        throw new Error(`Coinpilot ${method} ${route} failed: ${message}`);
      }
      if ("data" in payload) {
        const keys = Object.keys(payload);
        const hasOnlyData =
          keys.length === 2 &&
          keys.includes("success") &&
          keys.includes("data");
        if (hasOnlyData) return payload.data;
      }
    }
    // console.log(`[coinpilot] ${method} ${route} response:`, payload);
    return payload;
  });
};

const requestHyperliquid = async (payload) => {
  const url = new URL("/info", HYPERLIQUID_API_ENDPOINT);
  const res = await fetch(url.toString(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(
      `Hyperliquid request failed (${res.status}): ${JSON.stringify(data)}`,
    );
  }
  return data;
};

const resolveFollowerWallet = async (wallets, args, primaryAddress) => {
  if (args["follower-private-key"]) {
    return {
      address: args["follower-wallet"] || "unknown",
      privateKey: args["follower-private-key"],
    };
  }

  if (args["follower-index"] !== undefined) {
    const index = Number(args["follower-index"]);
    if (Number.isNaN(index))
      throw new Error("--follower-index must be a number");
    const follower = findWalletByIndex(wallets, index);
    if (!follower) throw new Error(`No wallet found at index ${index}`);
    return follower;
  }

  if (args["follower-wallet"]) {
    const follower = findWalletByAddress(wallets, args["follower-wallet"]);
    if (!follower)
      throw new Error(`No wallet found for ${args["follower-wallet"]}`);
    return follower;
  }

  if (args["use-prepare-wallet"]) {
    const prepared = await requestCoinpilot(
      "GET",
      `/experimental/${primaryAddress}/subscriptions/prepare-wallet`,
      wallets,
    );
    const follower = findWalletByAddress(wallets, prepared.address);
    if (!follower) {
      throw new Error(
        `Prepared wallet ${prepared.address} not found in coinpilot.json`,
      );
    }
    return follower;
  }

  throw new Error(
    "Specify --follower-index, --follower-wallet, --follower-private-key, or --use-prepare-wallet",
  );
};

const printHelp = () => {
  console.log(`
Usage: node scripts/coinpilot_cli.mjs <command> [options]

Commands:
  validate                     Validate coinpilot.json (use --online to call /experimental/:wallet/me)
  lead-metrics                 Get metrics for a lead wallet
  lead-periods                 Get period metrics for a lead wallet
  lead-data                    Query lead wallet performance data
  lead-categories              List lead categories
  lead-category                Get category rankings
  prepare-wallet               Get an available follower wallet
  start                        Start copy trading (experimental)
  stop                         Stop copy trading (experimental)
  renew-api-wallet             Renew API wallet for a subscription (experimental)
  list-subscriptions           List subscriptions for the user
  update-config                Update subscription config/leverages
  close-all                    Close all positions for a subscription
  close                        Close a single position for a subscription
  activities                   Get subscription activity feed
  history                      Get subscription history
  hl-account                   Hyperliquid clearinghouseState for a wallet
  hl-portfolio                 Hyperliquid portfolio for a wallet

Common options:
  --wallets <path>             Path to coinpilot.json (default: tmp/coinpilot.json)
  --base-url <url>             Coinpilot base URL override

Examples:
  node scripts/coinpilot_cli.mjs validate --online
  node scripts/coinpilot_cli.mjs lead-metrics --wallet 0xabc...
  node scripts/coinpilot_cli.mjs start --lead-wallet 0xlead... --allocation 200 --follower-index 1
    (allocation must be >= 5 USDC)
  node scripts/coinpilot_cli.mjs stop --subscription-id 123 --follower-index 1
  node scripts/coinpilot_cli.mjs renew-api-wallet --subscription-id 123 --follower-index 1
`);
};

const main = async () => {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0];

  if (!command || args.help || args.h) {
    printHelp();
    return;
  }

  const walletsPath = args.wallets || DEFAULT_WALLETS_PATH;
  // console.log(`[coinpilot] wallets path: ${walletsPath}`);
  const wallets = validateWallets(await readJson(walletsPath));

  if (args["base-url"]) {
    process.env.COINPILOT_API_BASE_URL = args["base-url"];
  }

  const primary = getPrimaryWallet(wallets);
  const primaryAddress = primary.address;

  if (command === "validate") {
    if (!args.online) {
      console.log("coinpilot.json format looks valid.");
      return;
    }
    const result = await requestCoinpilot(
      "GET",
      `/experimental/${primaryAddress}/me`,
      wallets,
    );
    const apiUserId = result?.userId ?? result?.data?.userId;
    if (apiUserId !== wallets.userId) {
      throw new Error(
        `UserId mismatch: coinpilot.json has ${wallets.userId}, API returned ${apiUserId}`,
      );
    }
    console.log("coinpilot.json verified against /experimental/:wallet/me.");
    return;
  }

  if (command === "lead-metrics") {
    if (!args.wallet) throw new Error("--wallet is required");
    const data = await requestCoinpilot(
      "GET",
      `/lead-wallets/metrics/wallets/${args.wallet}`,
      wallets,
    );
    formatOutput(data);
    return;
  }

  if (command === "lead-periods") {
    if (!args.wallet) throw new Error("--wallet is required");
    const data = await requestCoinpilot(
      "GET",
      `/lead-wallets/metrics/wallets/${args.wallet}/periods`,
      wallets,
    );
    formatOutput(data);
    return;
  }

  if (command === "lead-data") {
    const data = await requestCoinpilot(
      "GET",
      "/lead-wallets/data",
      wallets,
      undefined,
      {
        period: args.period,
        sortBy: args["sort-by"],
        sortOrder: args["sort-order"],
        type: args.type,
        search: args.search,
        watchlist: args.watchlist,
        page: args.page,
        limit: args.limit,
      },
    );
    formatOutput(data);
    return;
  }

  if (command === "lead-categories") {
    const data = await requestCoinpilot(
      "GET",
      "/lead-wallets/metrics/categories",
      wallets,
      undefined,
      { limit: args.limit },
    );
    formatOutput(data);
    return;
  }

  if (command === "lead-category") {
    if (!args.category) throw new Error("--category is required");
    const data = await requestCoinpilot(
      "GET",
      `/lead-wallets/metrics/categories/${args.category}`,
      wallets,
      undefined,
      {
        period: args.period,
        sortBy: args["sort-by"],
        sortOrder: args["sort-order"],
        search: args.search,
        page: args.page,
        limit: args.limit,
      },
    );
    formatOutput(data);
    return;
  }

  if (command === "prepare-wallet") {
    const data = await requestCoinpilot(
      "GET",
      `/experimental/${primaryAddress}/subscriptions/prepare-wallet`,
      wallets,
    );
    formatOutput(data);
    return;
  }

  if (command === "start") {
    if (!args["lead-wallet"]) throw new Error("--lead-wallet is required");
    const allocation = toNumber(args.allocation, "allocation");
    if (!allocation) throw new Error("--allocation is required");
    if (allocation < 5) throw new Error("--allocation must be >= 5 USDC");

    const follower = await resolveFollowerWallet(wallets, args, primaryAddress);

    const config = {
      allocation,
      stopLossPercent: toNumber(args["stop-loss-percent"], "stop-loss-percent"),
      takeProfitPercent: toNumber(
        args["take-profit-percent"],
        "take-profit-percent",
      ),
      inverseCopy: toBoolean(args["inverse-copy"]),
      forceCopyExisting: toBoolean(args["force-copy-existing"]),
      maxLeverage: toNumber(args["max-leverage"], "max-leverage"),
      maxMarginPercentage: toNumber(
        args["max-margin-percentage"],
        "max-margin-percentage",
      ),
    };

    Object.keys(config).forEach((key) => {
      if (config[key] === undefined) delete config[key];
    });

    const body = {
      primaryWalletPrivateKey: primary.privateKey,
      followerWalletPrivateKey: follower.privateKey,
      subscription: {
        leadWallet: args["lead-wallet"],
        leadWalletName: args["lead-wallet-name"],
        followerWallet: follower.address,
        config,
      },
    };

    const data = await requestCoinpilot(
      "POST",
      `/experimental/${primaryAddress}/subscriptions/start`,
      wallets,
      body,
    );
    formatOutput(data);
    return;
  }

  if (command === "stop") {
    if (!args["subscription-id"])
      throw new Error("--subscription-id is required");
    const follower = await resolveFollowerWallet(wallets, args, primaryAddress);
    const body = {
      followerWalletPrivateKey: follower.privateKey,
      subscriptionId: args["subscription-id"],
    };
    const data = await requestCoinpilot(
      "POST",
      `/experimental/${primaryAddress}/subscriptions/stop`,
      wallets,
      body,
    );
    formatOutput(data);
    return;
  }

  if (command === "renew-api-wallet") {
    if (!args["subscription-id"])
      throw new Error("--subscription-id is required");
    const follower = await resolveFollowerWallet(wallets, args, primaryAddress);
    const body = {
      followerWalletPrivateKey: follower.privateKey,
    };
    const data = await requestCoinpilot(
      "POST",
      `/experimental/${primaryAddress}/subscriptions/${args["subscription-id"]}/renew-api-wallet`,
      wallets,
      body,
    );
    formatOutput(data);
    return;
  }

  if (command === "list-subscriptions") {
    const data = await requestCoinpilot(
      "GET",
      `/users/${wallets.userId}/subscriptions`,
      wallets,
    );
    formatOutput(data);
    return;
  }

  if (command === "update-config") {
    if (!args["subscription-id"])
      throw new Error("--subscription-id is required");
    if (!args.payload) throw new Error("--payload <path> is required");
    const payload = await readJson(args.payload);
    if (!payload.config || !payload.leverages) {
      throw new Error("payload must include config and leverages");
    }
    const data = await requestCoinpilot(
      "PATCH",
      `/users/${wallets.userId}/subscriptions/${args["subscription-id"]}`,
      wallets,
      payload,
    );
    formatOutput(data);
    return;
  }

  if (command === "close-all") {
    if (!args["subscription-id"])
      throw new Error("--subscription-id is required");
    const data = await requestCoinpilot(
      "POST",
      `/users/${wallets.userId}/subscriptions/${args["subscription-id"]}/close-all`,
      wallets,
      {},
    );
    formatOutput(data);
    return;
  }

  if (command === "close") {
    if (!args["subscription-id"])
      throw new Error("--subscription-id is required");
    if (!args.coin) throw new Error("--coin is required");
    const percentage = toNumber(args.percentage, "percentage") ?? 1;
    if (percentage < 0 || percentage > 1) {
      throw new Error("--percentage must be between 0 and 1");
    }
    const body = {
      coin: args.coin,
      percentage,
    };
    const data = await requestCoinpilot(
      "POST",
      `/users/${wallets.userId}/subscriptions/${args["subscription-id"]}/close`,
      wallets,
      body,
    );
    formatOutput(data);
    return;
  }

  if (command === "activities") {
    if (!args["subscription-id"])
      throw new Error("--subscription-id is required");
    const data = await requestCoinpilot(
      "GET",
      `/users/${wallets.userId}/subscriptions/${args["subscription-id"]}/activities`,
      wallets,
      undefined,
      { cursor: args.cursor, size: args.size },
    );
    formatOutput(data);
    return;
  }

  if (command === "history") {
    const data = await requestCoinpilot(
      "GET",
      `/users/${wallets.userId}/subscriptions/history`,
      wallets,
    );
    formatOutput(data);
    return;
  }

  if (command === "hl-account") {
    if (!args.wallet) throw new Error("--wallet is required");
    const data = await requestHyperliquid({
      type: "clearinghouseState",
      user: args.wallet,
    });
    formatOutput(data);
    return;
  }

  if (command === "hl-portfolio") {
    if (!args.wallet) throw new Error("--wallet is required");
    const data = await requestHyperliquid({
      type: "portfolio",
      user: args.wallet,
    });
    formatOutput(data);
    return;
  }

  throw new Error(`Unknown command: ${command}`);
};

main().catch((err) => {
  console.error(err.message || err);
  process.exitCode = 1;
});
