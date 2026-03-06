#!/usr/bin/env node

/**
 * PocketLens CLI helper for OpenClaw skill.
 *
 * Usage:
 *   node pocket-lens.mjs create-transaction '<json>'
 *   node pocket-lens.mjs list-categories
 *   node pocket-lens.mjs verify-connection
 *   node pocket-lens.mjs spending-summary [--month YYYY-MM]
 *   node pocket-lens.mjs card-bills [--month YYYY-MM]
 *
 * Environment variables:
 *   POCKET_LENS_API_KEY  - Required. API key with appropriate permissions.
 *   POCKET_LENS_API_URL  - Optional. Defaults to https://pocketlens.app
 *
 * Requires Node.js 18+ (uses built-in fetch).
 */

const API_KEY = process.env.POCKET_LENS_API_KEY;
const API_URL = (process.env.POCKET_LENS_API_URL || "https://pocketlens.app").replace(
  /\/$/,
  ""
);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function exitWithError(message, code = 1) {
  console.error(JSON.stringify({ success: false, error: message }));
  process.exit(code);
}

function headers() {
  return {
    Authorization: `Bearer ${API_KEY}`,
    "Content-Type": "application/json",
    Accept: "application/json",
  };
}

/**
 * Parse --month YYYY-MM flag from command arguments.
 * Returns the month string or null if not provided.
 */
function parseMonthFlag(args) {
  const idx = args.indexOf("--month");
  if (idx === -1 || idx + 1 >= args.length) {
    return null;
  }
  const month = args[idx + 1];
  if (!/^\d{4}-\d{2}$/.test(month)) {
    exitWithError(
      `Invalid --month value: "${month}". Expected format: YYYY-MM (e.g. 2026-02)`
    );
  }
  return month;
}

async function request(method, path, body) {
  const url = `${API_URL}${path}`;
  const opts = { method, headers: headers() };

  if (body !== undefined) {
    opts.body = typeof body === "string" ? body : JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(url, opts);
  } catch (err) {
    exitWithError(`Network error: ${err.message}`);
  }

  let data;
  try {
    data = await res.json();
  } catch {
    exitWithError(`Invalid response from server (status ${res.status})`);
  }

  if (!res.ok) {
    const errorMsg = data.error || `HTTP ${res.status}`;
    console.error(
      JSON.stringify({
        success: false,
        error: errorMsg,
        status: res.status,
        ...(data.details ? { details: data.details } : {}),
      })
    );
    process.exit(1);
  }

  return data;
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

async function createTransaction(jsonArg) {
  if (!jsonArg) {
    exitWithError("Usage: create-transaction '<json>' -- JSON with a transactions array or a single transaction object");
  }

  let parsed;
  try {
    parsed = JSON.parse(jsonArg);
  } catch {
    exitWithError("Invalid JSON argument. Provide a valid JSON string.");
  }

  // Normalize: accept a single object or an object with a transactions array
  let txArray;
  if (Array.isArray(parsed)) {
    txArray = parsed;
  } else if (Array.isArray(parsed.transactions)) {
    txArray = parsed.transactions;
  } else if (typeof parsed === "object" && parsed.merchant) {
    txArray = [parsed];
  } else {
    exitWithError(
      'JSON must be a transaction object, an array, or {"transactions": [...]}'
    );
  }

  // Validate required fields
  for (let i = 0; i < txArray.length; i++) {
    const tx = txArray[i];
    if (!tx.merchant || typeof tx.merchant !== "string") {
      exitWithError(`Transaction ${i}: missing or invalid "merchant" (string required)`);
    }
    if (typeof tx.amount !== "number" || !Number.isInteger(tx.amount)) {
      exitWithError(`Transaction ${i}: missing or invalid "amount" (integer required)`);
    }
    if (!tx.date || typeof tx.date !== "string") {
      exitWithError(`Transaction ${i}: missing or invalid "date" (ISO 8601 string required)`);
    }
    // Default source
    if (!tx.source) {
      tx.source = "openclaw";
    }
  }

  const payload = { transactions: txArray };
  const result = await request("POST", "/api/external/transactions", payload);
  console.log(JSON.stringify(result, null, 2));
}

async function listCategories() {
  const result = await request("GET", "/api/external/categories");
  console.log(JSON.stringify(result, null, 2));
}

async function verifyConnection() {
  const result = await request("GET", "/api/external/me");
  console.log(JSON.stringify(result, null, 2));
}

async function spendingSummary(args) {
  const month = parseMonthFlag(args);
  const query = month ? `?month=${month}` : "";
  const result = await request("GET", `/api/external/spending/summary${query}`);
  console.log(JSON.stringify(result, null, 2));
}

async function cardBills(args) {
  const month = parseMonthFlag(args);
  const query = month ? `?month=${month}` : "";
  const result = await request("GET", `/api/external/spending/bills${query}`);
  console.log(JSON.stringify(result, null, 2));
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function showHelp() {
  console.log(
    [
      "PocketLens CLI - OpenClaw Skill Helper",
      "",
      "Usage:",
      '  node pocket-lens.mjs create-transaction \'{"merchant":"...", "amount":5500, "date":"..."}\'',
      "  node pocket-lens.mjs list-categories",
      "  node pocket-lens.mjs verify-connection",
      "  node pocket-lens.mjs spending-summary [--month YYYY-MM]",
      "  node pocket-lens.mjs card-bills [--month YYYY-MM]",
      "",
      "Environment:",
      "  POCKET_LENS_API_KEY   API key (required, from Settings > API Keys)",
      "  POCKET_LENS_API_URL   Base URL (optional, default: https://pocketlens.app)",
    ].join("\n")
  );
}

async function main() {
  const [command, ...args] = process.argv.slice(2);

  // Allow help without API key
  if (command === "help" || command === "--help" || command === "-h" || !command) {
    if (!command) {
      showHelp();
      process.exit(1);
    }
    showHelp();
    return;
  }

  // All other commands require the API key
  if (!API_KEY) {
    exitWithError(
      "POCKET_LENS_API_KEY environment variable is not set. " +
        "Get your API key from PocketLens Settings > API Keys."
    );
  }

  switch (command) {
    case "create-transaction":
      await createTransaction(args.join(" "));
      break;

    case "list-categories":
      await listCategories();
      break;

    case "verify-connection":
    case "verify":
    case "me":
      await verifyConnection();
      break;

    case "spending-summary":
    case "spending":
      await spendingSummary(args);
      break;

    case "card-bills":
    case "bills":
      await cardBills(args);
      break;

    default:
      exitWithError(
        `Unknown command: ${command}. ` +
          "Use: create-transaction, list-categories, verify-connection, spending-summary, card-bills, or help"
      );
  }
}

main();
