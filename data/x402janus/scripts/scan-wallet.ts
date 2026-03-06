#!/usr/bin/env npx tsx
/**
 * scan-wallet.ts — x402janus security scan
 *
 * Scans a wallet for risky token approvals, flagged contracts, and suspicious patterns.
 * Pays via x402 micropayment using the official @x402 SDK. No API keys. No accounts.
 *
 * Usage:
 *   npx tsx scripts/scan-wallet.ts <address> [options]
 *
 * Options:
 *   --tier <quick|standard|deep>  Scan tier (default: quick)
 *   --chain <base|ethereum>       Chain to scan (default: base)
 *   --json                        Output as JSON
 *   --help, -h                    Show this help
 *
 * Required env:
 *   JANUS_API_URL   — Janus API base URL (e.g. https://x402janus.com)
 *   PRIVATE_KEY     — Agent wallet key; signs x402 payment for every scan
 *
 * Optional env:
 *   BASE_RPC_URL    — RPC for signing transport (falls back to public Base RPC if not set)
 */

import { parseArgs } from "util";
import { createWalletClient, createPublicClient, http, toHex } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { base } from "viem/chains";
import { randomBytes } from "node:crypto";

// ── env ──────────────────────────────────────────────────────────────────────

function requireEnv(name: string): string {
  const val = process.env[name];
  if (!val) {
    console.error(`Error: ${name} is required but not set.`);
    if (name === "PRIVATE_KEY") {
      console.error("  PRIVATE_KEY is the agent wallet key used to sign x402 micropayments.");
      console.error("  x402 is the auth mechanism — there are no API keys.");
    }
    if (name === "JANUS_API_URL") {
      console.error("  JANUS_API_URL is the Janus API endpoint (e.g. https://x402janus.com).");
    }
    process.exit(1);
  }
  return val;
}

function optionalEnv(name: string): string | undefined {
  return process.env[name] || undefined;
}

// ── x402 payment (protocol-compliant) ────────────────────────────────────────

interface PaymentRequirement {
  scheme: string;
  network: string;
  maxAmountRequired: string;
  asset: string;
  payTo: string;
  maxTimeoutSeconds: number;
  extra?: { name?: string; version?: string; assetTransferMethod?: string };
  resource?: string;
  description?: string;
  mimeType?: string;
}

interface X402Response {
  x402Version: number;
  accepts: PaymentRequirement[];
  error?: string;
  description?: string;
}

/**
 * Sign an EIP-3009 TransferWithAuthorization payment.
 * Follows the x402 exact scheme specification for EVM networks.
 * 
 * SECURITY: Private key is used only for signing. Never logged or exposed.
 */
async function signPayment(
  requirement: PaymentRequirement,
  privateKey: string,
  rpcUrl?: string,
): Promise<string> {
  const account = privateKeyToAccount(privateKey as `0x${string}`);
  
  const walletClient = createWalletClient({
    account,
    chain: base,
    transport: http(rpcUrl),
  });

  const nonce = toHex(randomBytes(32)) as `0x${string}`;
  const now = Math.floor(Date.now() / 1000);
  // FIX: narrow authorization window — 5 min retroactive start, 5 min forward expiry
  const validAfter = BigInt(now - 300);
  const validBefore = BigInt(now + Math.min(300, requirement.maxTimeoutSeconds));
  const value = BigInt(requirement.maxAmountRequired);

  // Use token name/version from server's extra field, with USDC defaults
  const tokenName = requirement.extra?.name ?? "USD Coin";
  const tokenVersion = requirement.extra?.version ?? "2";

  const signature = await walletClient.signTypedData({
    domain: {
      name: tokenName,
      version: tokenVersion,
      chainId: 8453,
      verifyingContract: requirement.asset as `0x${string}`,
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
      to: requirement.payTo as `0x${string}`,
      value,
      validAfter,
      validBefore,
      nonce,
    },
  });

  // Build x402 v2 payment payload
  const payload = {
    x402Version: 2,
    scheme: requirement.scheme,
    network: requirement.network,
    payload: {
      signature,
      authorization: {
        from: account.address,
        to: requirement.payTo,
        value: requirement.maxAmountRequired,
        validAfter: validAfter.toString(),
        validBefore: validBefore.toString(),
        nonce,
      },
    },
  };

  return Buffer.from(JSON.stringify(payload)).toString("base64");
}

/**
 * Fetch with automatic x402 payment handling.
 * 
 * 1. Makes initial request
 * 2. If 402, reads payment requirements from response body
 * 3. Signs payment using agent wallet
 * 4. Retries with X-PAYMENT and PAYMENT-SIGNATURE headers
 * 
 * No facilitator URL is hardcoded — the server handles settlement.
 */
async function fetchWithPayment(
  url: string,
  options: RequestInit = {},
  privateKey: string,
  rpcUrl?: string,
  timeoutMs = 30_000,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const headers: Record<string, string> = {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string> | undefined),
    };

    // Initial request
    const first = await fetch(url, { ...options, signal: controller.signal, headers });

    if (first.status !== 402) {
      return first;
    }

    // Parse x402 payment requirements
    let x402: X402Response;
    try {
      x402 = await first.json() as X402Response;
    } catch {
      throw new Error("Server returned 402 but response body is not valid JSON.");
    }

    if (!x402.accepts?.length) {
      throw new Error("Server returned 402 but no payment requirements (accepts[] is empty).");
    }

    // Select first accepted payment method
    const requirement = x402.accepts[0];

    // Sign the payment
    let paymentHeader: string;
    try {
      paymentHeader = await signPayment(requirement, privateKey, rpcUrl);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("insufficient") || msg.includes("balance")) {
        console.error("\n⚠️  Agent wallet needs USDC on Base to pay for scans.");
        console.error("   Fund the agent wallet, then retry.");
        process.exit(2);
      }
      throw new Error(`Payment signing failed: ${msg}`);
    }

    // Retry with both standard headers (PAYMENT-SIGNATURE per x402 spec + X-PAYMENT for compat)
    const second = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        ...headers,
        "PAYMENT-SIGNATURE": paymentHeader,
        "X-PAYMENT": paymentHeader,
      },
    });

    if (second.status === 402) {
      console.error("\n⚠️  Payment was rejected by the server.");
      console.error("   Check: (1) USDC balance on Base, (2) sufficient amount for tier.");
      process.exit(2);
    }

    return second;
  } finally {
    clearTimeout(timer);
  }
}

// ── scan logic ────────────────────────────────────────────────────────────────

function isValidAddress(addr: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(addr);
}

function formatRisk(score: number): { level: string; emoji: string } {
  if (score >= 75) return { level: "critical", emoji: "🔴" };
  if (score >= 50) return { level: "high",     emoji: "🟠" };
  if (score >= 25) return { level: "medium",   emoji: "🟡" };
  return                  { level: "low",      emoji: "🟢" };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function printResults(result: any, json: boolean): void {
  if (json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  const healthScore = result.summary?.healthScore ?? result.riskScore ?? 0;
  const risk = formatRisk(100 - healthScore);

  console.log("\n🔲  x402janus Security Scan\n");
  console.log("═══════════════════════════════════════");
  console.log(`Address:      ${result.address}`);
  console.log(`Scanned at:   ${result.scannedAt}`);
  console.log(`Coverage:     ${result.coverageLevel}`);
  console.log(`Payer:        ${result.payer}`);
  console.log("───────────────────────────────────────");
  console.log(`Health Score: ${healthScore}/100 ${risk.emoji}`);
  console.log("───────────────────────────────────────");

  if (result.summary) {
    console.log("\n📊 Summary:");
    console.log(`  • Total Approvals:     ${result.summary.totalTokensApproved}`);
    console.log(`  • Unlimited Approvals: ${result.summary.unlimitedApprovals}`);
    console.log(`  • High Risk:           ${result.summary.highRiskApprovals}`);
  }

  if (result.approvals?.length > 0) {
    console.log("\n🔑 Approvals:");
    for (const a of result.approvals) {
      const emoji = a.riskLevel === "high" || a.riskLevel === "critical" ? "🔴" :
                    a.riskLevel === "medium" ? "🟡" : "🟢";
      console.log(`  ${emoji} ${a.token.slice(0, 8)}…${a.token.slice(-4)} → ${a.spender.slice(0, 8)}…${a.spender.slice(-4)}`);
      if (a.isUnlimited) console.log(`     ⚠️  UNLIMITED`);
      if (a.riskReasons?.length) console.log(`     ${a.riskReasons.join(", ")}`);
    }
  }

  if (result.recommendations?.length > 0) {
    console.log("\n💡 Recommendations:");
    for (const rec of result.recommendations) console.log(`  • ${rec}`);
  }

  if (result.revokeTransactions?.length > 0) {
    console.log(`\n🔧 ${result.revokeTransactions.length} revoke transaction(s) available`);
  }

  console.log("\n═══════════════════════════════════════\n");
}

// ── main ─────────────────────────────────────────────────────────────────────

async function main() {
  const { values, positionals } = parseArgs({
    args: process.argv.slice(2),
    options: {
      tier:   { type: "string",  default: "quick" },
      chain:  { type: "string",  default: "base" },
      free:   { type: "boolean", default: false },
      json:   { type: "boolean", default: false },
      help:   { type: "boolean", short: "h", default: false },
    },
    allowPositionals: true,
  });

  if (values.help) {
    console.log(`
x402janus — wallet security scan via x402 micropayment

Usage: npx tsx scripts/scan-wallet.ts <address> [options]

Arguments:
  address                            Wallet address to scan (required, EVM 0x…)

Options:
  --tier <quick|standard|deep>       Scan tier (default: quick)
  --free                             Use free tier (no PRIVATE_KEY needed, 3/day rate limit)
  --chain <base|ethereum>            Chain to scan (default: base)
  --json                             Output as JSON
  --help, -h                         Show this help

Required env:
  JANUS_API_URL    Janus API endpoint (e.g. https://x402janus.com)
  PRIVATE_KEY      Agent wallet key — signs x402 USDC payment (not needed with --free)

Optional env:
  BASE_RPC_URL     RPC for signing transport

Pricing:
  quick    $0.01 USDC   <3s    Deterministic risk score, approval list
  standard $0.05 USDC   <10s   + AI threat analysis, deeper lookback
  deep     $0.25 USDC   <30s   + Full graph analysis, drainer fingerprinting

Exit codes:
  0  — safe (health score ≥ 75)
  1  — medium risk (health score 50–74)
  2  — high risk (health score < 50) or payment insufficient
  3  — critical risk (health score < 25)
`);
    process.exit(0);
  }

  const apiUrl = requireEnv("JANUS_API_URL").replace(/\/$/, "");
  const useFree = values.free ?? false;
  const rpcUrl = optionalEnv("BASE_RPC_URL");

  // PRIVATE_KEY is only required for paid tiers
  const privateKey = useFree ? optionalEnv("PRIVATE_KEY") : requireEnv("PRIVATE_KEY");

  const address = positionals[0];
  if (!address) {
    console.error("Error: wallet address required");
    console.error("Usage: npx tsx scripts/scan-wallet.ts <address>");
    process.exit(1);
  }
  if (!isValidAddress(address)) {
    console.error(`Error: invalid Ethereum address: ${address}`);
    process.exit(1);
  }

  const tier = useFree ? "free" : (values.tier ?? "quick").toLowerCase();
  if (!["free", "quick", "standard", "deep"].includes(tier)) {
    console.error(`Error: invalid tier '${tier}' — use free, quick, standard, or deep`);
    process.exit(1);
  }

  const chain = (values.chain ?? "base").toLowerCase();
  if (!["base", "ethereum"].includes(chain)) {
    console.error(`Error: unsupported chain '${chain}' — use base or ethereum`);
    process.exit(1);
  }

  try {
    const url = `${apiUrl}/api/guardian/scan/${address}?tier=${tier}&chain=${chain}`;
    let response: Response;

    if (useFree || tier === "free") {
      // Free tier — no payment needed, just fetch directly
      response = await fetch(url, {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
      });
    } else {
      // Paid tier — use x402 payment flow
      response = await fetchWithPayment(url, { method: "POST" }, privateKey!, rpcUrl);
    }

    if (!response.ok) {
      const body = await response.text();
      console.error(`Error: scan failed (HTTP ${response.status})`);
      try {
        const err = JSON.parse(body);
        console.error(`  ${err.error || err.message || body.slice(0, 200)}`);
      } catch {
        console.error(`  ${body.slice(0, 200)}`);
      }
      process.exit(1);
    }

    const result = await response.json();
    printResults(result, values.json ?? false);

    const healthScore = result.summary?.healthScore ?? 50;
    if (healthScore < 25) process.exit(3);
    if (healthScore < 50) process.exit(2);
    if (healthScore < 75) process.exit(1);
    process.exit(0);
  } catch (err) {
    console.error("Error:", err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
}

main();
