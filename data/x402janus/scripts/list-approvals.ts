#!/usr/bin/env npx tsx
/**
 * list-approvals.ts — x402janus token approval lister
 *
 * Lists all token approvals for a wallet with risk scoring.
 * Every API call pays via x402 micropayment (USDC on Base).
 * No API keys. x402 IS the auth.
 *
 * Usage:
 *   npx tsx list-approvals.ts <address> [options]
 *
 * Options:
 *   --chain <base|ethereum>       Chain (default: base)
 *   --risk <low|medium|high|critical>  Filter by risk level (comma-separated)
 *   --unlimited-only              Show only unlimited approvals
 *   --include-revoked             Include revoked approvals in history
 *   --format <table|csv|json>     Output format (default: table)
 *   --help, -h                    Show this help
 *
 * Required env:
 *   JANUS_API_URL   — Janus API base URL
 *   PRIVATE_KEY     — Agent wallet key; signs x402 USDC payment
 *
 * Optional env:
 *   BASE_RPC_URL    — RPC for signing transport (recommended: set your own)
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

// ── approval types ────────────────────────────────────────────────────────────

interface Approval {
  token: string;
  tokenSymbol: string;
  tokenName: string;
  spender: string;
  spenderName?: string;
  allowance: string;
  allowanceRaw: string;
  isUnlimited: boolean;
  riskScore: number;
  riskLevel: "low" | "medium" | "high" | "critical";
  riskFlags: string[];
  firstSeen: string;
  lastUsed?: string;
  transactionHash?: string;
  revoked: boolean;
  blockNumber: number;
}

interface ApprovalsResult {
  address: string;
  chain: string;
  timestamp: string;
  totalApprovals: number;
  activeApprovals: number;
  revokedApprovals: number;
  unlimitedApprovals: number;
  highRiskApprovals: number;
  approvals: Approval[];
}

// ── helpers ───────────────────────────────────────────────────────────────────

function isValidAddress(addr: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(addr);
}

function formatRisk(level: string): string {
  const emojis: Record<string, string> = {
    low: "🟢", medium: "🟡", high: "🟠", critical: "🔴",
  };
  return `${emojis[level] ?? "⚪"} ${level.toUpperCase()}`;
}

function formatAllowance(a: Approval): string {
  if (a.isUnlimited) return "∞ Unlimited";
  if (!a.allowanceRaw) return a.allowance;
  try {
    const raw = BigInt(a.allowanceRaw);
    if (raw === 0n) return "0";
  } catch { /* use API-formatted value */ }
  return a.allowance;
}

// ── API call ──────────────────────────────────────────────────────────────────

async function fetchApprovals(
  address: string,
  chain: string,
  includeRevoked: boolean
): Promise<ApprovalsResult> {
  const apiUrl = requireEnv("JANUS_API_URL").replace(/\/$/, "");
  const url = new URL(`${apiUrl}/api/guardian/approvals/${address}`);
  url.searchParams.set("chain", chain);
  if (includeRevoked) url.searchParams.set("includeRevoked", "true");

  const response = await fetchWithPayment(url.toString(), { method: "GET" });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Failed to fetch approvals: HTTP ${response.status} — ${body}`);
  }

  return response.json() as Promise<ApprovalsResult>;
}

// ── output ────────────────────────────────────────────────────────────────────

function filterApprovals(
  approvals: Approval[],
  riskFilter: string[],
  unlimitedOnly: boolean
): Approval[] {
  return approvals.filter((a) => {
    if (riskFilter.length > 0 && !riskFilter.includes(a.riskLevel)) return false;
    if (unlimitedOnly && !a.isUnlimited) return false;
    return true;
  });
}

function printTable(result: ApprovalsResult): void {
  console.log("\n🔲  x402janus — Token Approvals\n");
  console.log("═══════════════════════════════════════════════════════════════");
  console.log(`Address: ${result.address}`);
  console.log(`Chain:   ${result.chain}`);
  console.log(`Fetched: ${result.timestamp}`);
  console.log("───────────────────────────────────────────────────────────────");
  console.log(`Total:      ${result.totalApprovals}`);
  console.log(`Active:     ${result.activeApprovals}`);
  console.log(`Revoked:    ${result.revokedApprovals}`);
  console.log(`Unlimited:  ${result.unlimitedApprovals} ⚠️`);
  console.log(`High Risk:  ${result.highRiskApprovals} 🔴`);
  console.log("───────────────────────────────────────────────────────────────");

  if (result.approvals.length === 0) {
    console.log("\n✅ No approvals matching filters.");
    return;
  }

  const sorted = [...result.approvals].sort((a, b) => b.riskScore - a.riskScore);
  console.log("\n📋 Approvals (sorted by risk):\n");

  for (const a of sorted) {
    const status = a.revoked ? "❌ REVOKED" : a.isUnlimited ? "⚠️  UNLIMITED" : "✅ Active";
    console.log(`${formatRisk(a.riskLevel)} | ${status}`);
    console.log(`  Token:     ${a.tokenSymbol} (${a.token})`);
    console.log(`  Spender:   ${a.spenderName ?? "Unknown"} (${a.spender})`);
    console.log(`  Allowance: ${formatAllowance(a)}`);
    if (a.riskFlags.length > 0) console.log(`  Flags:     ${a.riskFlags.join(", ")}`);
    if (a.lastUsed) console.log(`  Last Used: ${a.lastUsed}`);
    console.log();
  }
}

function printCSV(result: ApprovalsResult): void {
  const headers = [
    "token_address","token_symbol","spender_address","spender_name",
    "allowance","is_unlimited","risk_score","risk_level","risk_flags",
    "first_seen","last_used","revoked","transaction_hash",
  ];
  console.log(headers.join(","));
  for (const a of result.approvals) {
    const row = [
      a.token, `"${a.tokenSymbol}"`, a.spender, `"${a.spenderName ?? ""}"`,
      a.allowanceRaw, a.isUnlimited, a.riskScore, a.riskLevel,
      `"${a.riskFlags.join(";")}"`, a.firstSeen, a.lastUsed ?? "",
      a.revoked, a.transactionHash ?? "",
    ];
    console.log(row.join(","));
  }
}

// ── main ─────────────────────────────────────────────────────────────────────

async function main() {
  const { values, positionals } = parseArgs({
    args: process.argv.slice(2),
    options: {
      chain:             { type: "string",  default: "base" },
      risk:              { type: "string" },
      "unlimited-only":  { type: "boolean", default: false },
      "include-revoked": { type: "boolean", default: false },
      format:            { type: "string",  default: "table" },
      json:              { type: "boolean", default: false },
      help:              { type: "boolean", short: "h", default: false },
    },
    allowPositionals: true,
  });

  if (values.help) {
    console.log(`
x402janus — list token approvals via x402 micropayment

Usage: npx tsx list-approvals.ts <address> [options]

Arguments:
  address                        Wallet address (required, EVM 0x…)

Options:
  --chain <base|ethereum>        Chain (default: base)
  --risk <levels>                Filter: low,medium,high,critical
  --unlimited-only               Show only unlimited approvals
  --include-revoked              Include revoked approvals
  --format <table|csv|json>      Output format (default: table)
  --help, -h                     Show this help

Required env:
  JANUS_API_URL                  Janus API endpoint
  PRIVATE_KEY                    Agent wallet key — signs x402 USDC payment

Optional env:
  BASE_RPC_URL                   RPC endpoint (recommended: set your own)

Examples:
  npx tsx list-approvals.ts 0x742d... --risk high,critical
  npx tsx list-approvals.ts 0x742d... --unlimited-only --format csv
`);
    process.exit(0);
  }

  requireEnv("JANUS_API_URL");
  requireEnv("PRIVATE_KEY");

  const address = positionals[0];
  if (!address) {
    console.error("Error: wallet address required");
    console.error("Usage: npx tsx list-approvals.ts <address>");
    process.exit(1);
  }
  if (!isValidAddress(address)) {
    console.error(`Error: invalid Ethereum address: ${address}`);
    process.exit(1);
  }

  const chain = (values.chain ?? "base").toLowerCase();
  if (chain !== "base" && chain !== "ethereum") {
    console.error(`Error: unsupported chain '${chain}' — use 'base' or 'ethereum'`);
    process.exit(1);
  }

  const riskFilter = values.risk
    ? values.risk.split(",").map((r) => r.trim().toLowerCase())
    : [];

  const validFormats = ["table", "csv", "json"];
  const format = values.json ? "json" : (values.format ?? "table").toLowerCase();
  if (!validFormats.includes(format)) {
    console.error(`Error: invalid format '${format}' — use: ${validFormats.join(", ")}`);
    process.exit(1);
  }

  try {
    const result = await fetchApprovals(address, chain, values["include-revoked"]);
    result.approvals = filterApprovals(result.approvals, riskFilter, values["unlimited-only"]);

    switch (format) {
      case "json": console.log(JSON.stringify(result, null, 2)); break;
      case "csv":  printCSV(result); break;
      default:     printTable(result);
    }

    const highRisk = result.approvals.filter(
      (a) => a.riskLevel === "high" || a.riskLevel === "critical"
    );
    if (highRisk.length > 0) process.exit(2);
  } catch (err) {
    console.error("Error:", err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
}

main();
