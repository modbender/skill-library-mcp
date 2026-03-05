#!/usr/bin/env npx tsx
/**
 * start-monitoring.ts — x402janus monitoring subscription
 *
 * Subscribes a wallet to real-time Janus monitoring via webhook or Telegram.
 * Every API call pays via x402 micropayment (USDC on Base).
 * No API keys. x402 IS the auth.
 *
 * Usage:
 *   npx tsx start-monitoring.ts <address> --webhook <url>
 *   npx tsx start-monitoring.ts <address> --telegram <username>
 *
 * Options:
 *   --webhook <url>              Webhook URL for alerts
 *   --telegram <username>        Telegram username for alerts
 *   --min-risk <level>           Minimum risk level (low|medium|high|critical, default: medium)
 *   --alert-types <types>        Comma-separated types (default: all)
 *   --json                       Output as JSON
 *   --help, -h                   Show this help
 *
 * Required env:
 *   JANUS_API_URL   — Janus API base URL
 *   PRIVATE_KEY     — Agent wallet key; signs x402 USDC payment
 *
 * Optional env:
 *   BASE_RPC_URL    — RPC for signing transport (recommended: set your own)
 *   WEBHOOK_SECRET  — Secret for webhook signature verification
 */

import { parseArgs } from "util";
import { createWalletClient, http, toHex } from "viem";
import { randomBytes } from "node:crypto";
import { privateKeyToAccount } from "viem/accounts";
import { base } from "viem/chains";

// ── env ──────────────────────────────────────────────────────────────────────

function requireEnv(name: string): string {
  const val = process.env[name];
  if (!val) {
    console.error(`Error: ${name} is required but not set.`);
    if (name === "PRIVATE_KEY") {
      console.error("  PRIVATE_KEY signs x402 micropayments — no API keys exist.");
    }
    if (name === "JANUS_API_URL") {
      console.error("  JANUS_API_URL is the Janus API endpoint (e.g. https://x402janus.com).");
    }
    process.exit(1);
  }
  return val;
}

// ── x402 payment ─────────────────────────────────────────────────────────────

interface X402Accept {
  scheme: string;
  network: string;
  maxAmountRequired: string;
  asset: `0x${string}`;
  payTo: `0x${string}`;
  maxTimeoutSeconds: number;
  extra?: { name?: string; version?: string };
}

interface X402Challenge {
  accepts: X402Accept[];
}

function randomNonce(): `0x${string}` {
  return toHex(randomBytes(32)) as `0x${string}`;
}

async function buildPaymentHeader(challenge: X402Challenge): Promise<string> {
  if (!challenge?.accepts?.length) {
    throw new Error("x402 challenge missing accepts[] — cannot sign payment.");
  }

  const accept = challenge.accepts[0];
  const privateKey = requireEnv("PRIVATE_KEY");
  const rpcUrl = process.env.BASE_RPC_URL;

  const account = privateKeyToAccount(privateKey as `0x${string}`);
  const walletClient = createWalletClient({
    account,
    chain: base,
    transport: http(rpcUrl),
  });

  const nonce = randomNonce();
  const now = Math.floor(Date.now() / 1000);
  // FIX: narrow authorization window — 5 min retroactive start, 5 min forward expiry
  const validAfter = BigInt(now - 300);
  const validBefore = BigInt(now + Math.min(300, accept.maxTimeoutSeconds));
  const value = BigInt(accept.maxAmountRequired);

  // FIX: read token name/version from 402 response instead of hardcoding
  const tokenName = accept.extra?.name ?? "USD Coin";
  const tokenVersion = accept.extra?.version ?? "2";

  const signature = await walletClient.signTypedData({
    domain: {
      name: tokenName,
      version: tokenVersion,
      chainId: 8453,
      verifyingContract: accept.asset,
    },
    types: {
      TransferWithAuthorization: [
        { name: "from", type: "address" },
        { name: "to", type: "address" },
        { name: "value", type: "uint256" },
        { name: "validAfter", type: "uint256" },
        { name: "validBefore", type: "uint256" },
        { name: "nonce", type: "bytes32" },
      ],
    },
    primaryType: "TransferWithAuthorization",
    message: {
      from: account.address,
      to: accept.payTo,
      value,
      validAfter,
      validBefore,
      nonce,
    },
  });

  const payload = {
    scheme: accept.scheme,
    network: accept.network,
    payload: {
      signature,
      authorization: {
        from: account.address,
        to: accept.payTo,
        value: accept.maxAmountRequired,
        validAfter: validAfter.toString(),
        validBefore: validBefore.toString(),
        nonce,
      },
    },
  };

  return Buffer.from(JSON.stringify(payload)).toString("base64");
}

async function fetchWithPayment(
  url: string,
  options: RequestInit = {},
  timeoutMs = 30_000
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const first = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(options.headers as Record<string, string> | undefined),
      },
    });

    if (first.status !== 402) return first;

    let challenge: X402Challenge;
    try {
      challenge = await first.json();
    } catch {
      throw new Error("Received 402 but could not parse x402 challenge payload.");
    }

    let paymentHeader: string;
    try {
      paymentHeader = await buildPaymentHeader(challenge);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("insufficient") || msg.includes("balance")) {
        console.error("\n⚠️  Agent wallet needs USDC on Base to pay for scans.");
        console.error("   Fund the agent wallet with USDC on Base, then retry.");
        process.exit(2);
      }
      throw err;
    }

    const second = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(options.headers as Record<string, string> | undefined),
        "X-PAYMENT": paymentHeader,
      },
    });

    if (second.status === 402) {
      console.error("\n⚠️  Agent wallet needs USDC on Base to pay for scans.");
      console.error("   Payment was rejected — check USDC balance on Base and retry.");
      process.exit(2);
    }

    return second;
  } finally {
    clearTimeout(timer);
  }
}

// ── subscription ──────────────────────────────────────────────────────────────

interface SubscriptionResult {
  subscriptionId: string;
  walletAddress: string;
  chain: string;
  status: "active" | "pending" | "paused";
  createdAt: string;
  expiresAt: string;
  webhook?: { url: string; events: string[]; minRiskLevel: string };
  telegram?: { username: string; chatId: string };
  pricing: { amount: string; currency: string; period: string };
}

function isValidAddress(addr: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(addr);
}

function isValidUrl(url: string): boolean {
  try { new URL(url); return true; } catch { return false; }
}

async function subscribe(
  address: string,
  opts: {
    chain: string;
    webhook?: string;
    telegram?: string;
    minRisk: string;
    alertTypes: string[];
  }
): Promise<SubscriptionResult> {
  const apiUrl = requireEnv("JANUS_API_URL").replace(/\/$/, "");
  const url = `${apiUrl}/api/guardian/subscribe`;

  const body: Record<string, unknown> = {
    walletAddress: address,
    chain: opts.chain,
    minRiskLevel: opts.minRisk,
    alertTypes: opts.alertTypes,
  };

  if (opts.webhook) {
    body.webhook = {
      url: opts.webhook,
      secret: process.env.WEBHOOK_SECRET ?? undefined,
    };
  }
  if (opts.telegram) {
    body.telegram = { username: opts.telegram.replace(/^@/, "") };
  }

  const response = await fetchWithPayment(url, {
    method: "POST",
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Subscription failed: HTTP ${response.status} — ${text}`);
  }

  return response.json() as Promise<SubscriptionResult>;
}

// ── output ────────────────────────────────────────────────────────────────────

function printResults(result: SubscriptionResult, json: boolean): void {
  if (json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log("\n🔲  x402janus — Monitoring Subscription\n");
  console.log("═══════════════════════════════════════════");
  console.log(`Subscription ID: ${result.subscriptionId}`);
  console.log(`Wallet:          ${result.walletAddress}`);
  console.log(`Chain:           ${result.chain}`);
  console.log(`Status:          ${result.status.toUpperCase()}`);
  console.log(`Created:         ${result.createdAt}`);
  console.log(`Expires:         ${result.expiresAt}`);
  console.log("───────────────────────────────────────────");

  if (result.webhook) {
    console.log("\n📡 Webhook:");
    console.log(`  URL:      ${result.webhook.url}`);
    console.log(`  Events:   ${result.webhook.events.join(", ")}`);
    console.log(`  Min Risk: ${result.webhook.minRiskLevel}`);
  }

  if (result.telegram) {
    console.log("\n💬 Telegram:");
    console.log(`  Username: @${result.telegram.username}`);
    console.log(`  Chat ID:  ${result.telegram.chatId}`);
  }

  console.log("\n💰 Pricing:");
  console.log(`  Amount: ${result.pricing.amount} ${result.pricing.currency}`);
  console.log(`  Period: ${result.pricing.period}`);

  console.log("\n✅ Subscription active — alerts for:");
  console.log("   • New token approvals");
  console.log("   • Approval usage");
  console.log("   • Risk score increases");
  console.log("   • Suspicious transactions");
  console.log("   • Contract interactions");
  console.log("═══════════════════════════════════════════\n");
}

// ── main ─────────────────────────────────────────────────────────────────────

async function main() {
  const { values, positionals } = parseArgs({
    args: process.argv.slice(2),
    options: {
      webhook:         { type: "string" },
      telegram:        { type: "string" },
      "min-risk":      { type: "string", default: "medium" },
      "alert-types":   { type: "string" },
      json:            { type: "boolean", default: false },
      help:            { type: "boolean", short: "h", default: false },
    },
    allowPositionals: true,
  });

  if (values.help) {
    console.log(`
x402janus — monitoring subscription via x402 micropayment

Usage:
  npx tsx start-monitoring.ts <address> --webhook <url>
  npx tsx start-monitoring.ts <address> --telegram <username>

Arguments:
  address                  Wallet address to monitor (required, EVM 0x…)

Options:
  --webhook <url>          Webhook URL for alerts
  --telegram <username>    Telegram @username for alerts
  --min-risk <level>       Minimum alert risk: low|medium|high|critical (default: medium)
  --alert-types <types>    Comma-separated: approval,transfer,risk,contract,suspicious
  --json                   Output as JSON
  --help, -h               Show this help

Required env:
  JANUS_API_URL            Janus API endpoint
  PRIVATE_KEY              Agent wallet key — signs x402 USDC payment

Optional env:
  BASE_RPC_URL             RPC (recommended: set your own)
  WEBHOOK_SECRET           Secret for webhook signature verification
`);
    process.exit(0);
  }

  requireEnv("JANUS_API_URL");
  requireEnv("PRIVATE_KEY");

  const address = positionals[0];
  if (!address) {
    console.error("Error: wallet address required");
    console.error("Usage: npx tsx start-monitoring.ts <address> --webhook <url>");
    process.exit(1);
  }
  if (!isValidAddress(address)) {
    console.error(`Error: invalid Ethereum address: ${address}`);
    process.exit(1);
  }
  if (!values.webhook && !values.telegram) {
    console.error("Error: --webhook or --telegram required");
    process.exit(1);
  }
  if (values.webhook && !isValidUrl(values.webhook)) {
    console.error(`Error: invalid webhook URL: ${values.webhook}`);
    process.exit(1);
  }

  const minRisk = (values["min-risk"] ?? "medium").toLowerCase();
  const validRiskLevels = ["low", "medium", "high", "critical"];
  if (!validRiskLevels.includes(minRisk)) {
    console.error(`Error: invalid risk level '${minRisk}' — use: ${validRiskLevels.join(", ")}`);
    process.exit(1);
  }

  const alertTypes = values["alert-types"]
    ? values["alert-types"].split(",").map((t) => t.trim())
    : ["all"];

  try {
    const result = await subscribe(address, {
      chain: "base",
      webhook: values.webhook,
      telegram: values.telegram,
      minRisk,
      alertTypes,
    });
    printResults(result, values.json);
  } catch (err) {
    console.error("Error:", err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
}

main();
