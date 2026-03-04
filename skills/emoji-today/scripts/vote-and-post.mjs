#!/usr/bin/env node

/**
 * vote-and-post.mjs — Vote and mint in the daily emoji.today election via x402.
 *
 * Subcommands:
 *   vote --emoji "🎉"                            — Cast vote ($0.01 USDC via x402)
 *   mint --emoji "🎉" [--mint-to 0x...]           — Mint vote NFT ($1.00 USDC via x402)
 *
 * Legacy (no subcommand):
 *   node vote-and-post.mjs "🎉"                   — Same as vote --emoji "🎉"
 *
 * Environment:
 *   EVM_PRIVATE_KEY  — Private key for signing votes + paying USDC on Base
 *   FARCASTER_FID    — Your Farcaster ID (numeric)
 *   EMOJI_TODAY_URL  — API base URL (default: https://emoji.today)
 *   MINT_TO_ADDRESS  — Default recipient for minted NFTs (defaults to sender wallet)
 */

import { config } from "dotenv";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { privateKeyToAccount } from "viem/accounts";

const __dirname = dirname(fileURLToPath(import.meta.url));

// Load .env from scripts dir, then from skill root, then from cwd
config({ path: join(__dirname, ".env") });
config({ path: join(__dirname, "..", ".env") });
config();

const PRIVATE_KEY = process.env.EVM_PRIVATE_KEY;
const FID = process.env.FARCASTER_FID;
const BASE_URL = process.env.EMOJI_TODAY_URL || "https://emoji.today";

if (!PRIVATE_KEY) {
  console.error("EVM_PRIVATE_KEY is required. Set it in your environment or .env file.");
  process.exit(1);
}
if (!FID) {
  console.error("FARCASTER_FID is required. Set it in your environment or .env file.");
  process.exit(1);
}

// ── Parse CLI args ────────────────────────────────────────────────────
const args = process.argv.slice(2);
const cmd = args[0];

function getArg(name) {
  const idx = args.indexOf(`--${name}`);
  if (idx === -1 || idx + 1 >= args.length) return null;
  return args[idx + 1];
}

// ── Wallet helper ────────────────────────────────────────────────────
let _account;
function getAccount() {
  if (_account) return _account;
  _account = privateKeyToAccount(PRIVATE_KEY.startsWith("0x") ? PRIVATE_KEY : `0x${PRIVATE_KEY}`);
  return _account;
}

// ── x402 payment fetch ────────────────────────────────────────────────
async function fetchWithX402(url, opts = {}) {
  const { wrapFetchWithPaymentFromConfig } = await import("@x402/fetch");
  const { ExactEvmScheme } = await import("@x402/evm");

  const account = getAccount();

  const payFetch = wrapFetchWithPaymentFromConfig(fetch, {
    schemes: [
      {
        network: "eip155:*",
        client: new ExactEvmScheme(account),
      },
    ],
  });

  return payFetch(url, opts);
}

// ── Subcommand: vote ──────────────────────────────────────────────────
async function vote(emoji) {
  const account = getAccount();
  const fid = parseInt(FID, 10);

  // Sign the vote message: "emoji.today:{fid}:{YYYY-MM-DD}"
  const today = new Date().toISOString().split("T")[0];
  const message = `emoji.today:${fid}:${today}`;
  const signature = await account.signMessage({ message });

  const res = await fetchWithX402(`${BASE_URL}/api/vote`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emoji, fid, signature }),
  });

  if (!res.ok) {
    const errBody = await res.text();
    console.error(`Vote API error ${res.status}: ${errBody}`);
    process.exit(1);
  }

  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

// ── Subcommand: mint ──────────────────────────────────────────────────
async function mint(emoji) {
  const account = getAccount();
  const fid = parseInt(FID, 10);

  // Recipient: --mint-to flag > MINT_TO_ADDRESS env > sender wallet
  const mintTo = getArg("mint-to") || process.env.MINT_TO_ADDRESS || account.address;

  const res = await fetchWithX402(`${BASE_URL}/api/vote/mint`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emoji, voter: fid.toString(), mintTo }),
  });

  if (!res.ok) {
    const errBody = await res.text();
    console.error(`Mint API error ${res.status}: ${errBody}`);
    process.exit(1);
  }

  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

// ── Router ────────────────────────────────────────────────────────────
async function main() {
  if (cmd === "vote") {
    const emoji = getArg("emoji");
    if (!emoji) { console.error("Usage: vote --emoji <emoji>"); process.exit(1); }
    await vote(emoji);
  } else if (cmd === "mint") {
    const emoji = getArg("emoji");
    if (!emoji) { console.error("Usage: mint --emoji <emoji> [--mint-to <address>]"); process.exit(1); }
    await mint(emoji);
  } else if (cmd && !cmd.startsWith("--")) {
    // Legacy: node vote-and-post.mjs "🔥"
    await vote(cmd);
  } else {
    console.error("Usage:");
    console.error('  vote --emoji "🎉"                    — Cast vote ($0.01 USDC via x402)');
    console.error('  mint --emoji "🎉" [--mint-to 0x...]   — Mint vote NFT ($1.00 USDC via x402)');
    console.error('  "🎉"                                  — Legacy: same as vote');
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("Error:", err.message || err);
  process.exit(1);
});
