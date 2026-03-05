#!/usr/bin/env npx tsx
/**
 * revoke-approval.ts — x402janus revoke transaction builder
 *
 * Builds or executes an ERC20 approve(spender, 0) transaction to revoke a risky approval.
 * Risk data fetch (optional) uses x402 micropayment (USDC on Base).
 * Transaction execution uses PRIVATE_KEY directly via cast.
 * No API keys. x402 IS the auth.
 *
 * Usage:
 *   npx tsx revoke-approval.ts <wallet> <token> <spender> [options]
 *
 * Options:
 *   --chain <base|ethereum>  Chain (default: base)
 *   --allowance <amount>     Set specific allowance in wei instead of 0 (default: 0)
 *   --execute                Execute the transaction with cast
 *   --gas-limit <limit>      Gas limit override
 *   --json                   Output as JSON
 *   --help, -h               Show this help
 *
 * Required env:
 *   JANUS_API_URL   — Janus API base URL (used for gas estimation and risk check)
 *   PRIVATE_KEY     — Agent wallet key; signs x402 payment AND (if --execute) the tx
 *
 * Optional env:
 *   BASE_RPC_URL    — RPC endpoint (recommended: set your own)
 */

import { parseArgs } from "util";
import { spawn } from "child_process";
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
      console.error("  PRIVATE_KEY signs x402 micropayments AND transaction execution.");
      console.error("  No API keys — x402 is the auth mechanism.");
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
  // FIX: narrow the authorization window — 5 min retroactive start, 5 min forward expiry
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

// ── transaction builder ───────────────────────────────────────────────────────

const APPROVE_SELECTOR = "0x095ea7b3";

interface RevokeTransaction {
  from: string;
  to: string;
  data: string;
  value: string;
  gasEstimate: string;
  gasLimit?: string;
  chainId: number;
  description: string;
}

function isValidAddress(addr: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(addr);
}

function encodeApprove(spender: string, amount: bigint): string {
  const spenderPadded = spender.slice(2).toLowerCase().padStart(64, "0");
  const amountHex = amount.toString(16).padStart(64, "0");
  return `${APPROVE_SELECTOR}${spenderPadded}${amountHex}`;
}

function getChainId(chain: string): number {
  return chain === "ethereum" ? 1 : 8453;
}

function getExplorerUrl(chain: string, txHash: string): string {
  return chain === "ethereum"
    ? `https://etherscan.io/tx/${txHash}`
    : `https://basescan.org/tx/${txHash}`;
}

function buildRevokeTx(
  wallet: string,
  token: string,
  spender: string,
  allowance: bigint,
  chain: string
): RevokeTransaction {
  return {
    from: wallet,
    to: token,
    data: encodeApprove(spender, allowance),
    value: "0",
    gasEstimate: "50000",
    chainId: getChainId(chain),
    description: allowance === 0n
      ? `Revoke approval for ${spender} on token ${token}`
      : `Set approval for ${spender} on token ${token} to ${allowance.toString()}`,
  };
}

async function estimateGas(tx: RevokeTransaction): Promise<string> {
  const rpcUrl = process.env.BASE_RPC_URL;
  if (!rpcUrl) return tx.gasEstimate; // BASE_RPC_URL not set — use default
  try {
    const response = await fetch(rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "eth_estimateGas",
        params: [{ from: tx.from, to: tx.to, data: tx.data, value: tx.value }],
        id: 1,
      }),
    });
    const result = await response.json();
    if (result.result) {
      const gas = BigInt(result.result);
      return (gas * 120n / 100n).toString(); // +20% buffer
    }
  } catch { /* use default */ }
  return tx.gasEstimate;
}

async function executeWithCast(
  tx: RevokeTransaction,
  gasLimit: string
): Promise<{ success: boolean; hash?: string; error?: string }> {
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    return { success: false, error: "PRIVATE_KEY not set — cannot execute transaction." };
  }

  const rpcUrl = process.env.BASE_RPC_URL;
  // FIX: validate BASE_RPC_URL before passing to cast — "undefined" string would be passed otherwise
  if (!rpcUrl) {
    return { success: false, error: "BASE_RPC_URL is not set — cannot execute transaction." };
  }

  // Decode spender and amount from calldata
  const spenderRaw = tx.data.slice(10, 74);
  const spender = `0x${spenderRaw.replace(/^0+/, "") || "0"}`;
  const amountHex = tx.data.slice(74);
  const amount = BigInt("0x" + amountHex);

  return new Promise((resolve) => {
    // FIX: pass private key via ETH_PRIVATE_KEY env var instead of --private-key CLI arg
    // to prevent exposure via `ps aux`
    const cast = spawn(
      "cast",
      [
        "send",
        "--rpc-url", rpcUrl,
        "--gas-limit", gasLimit,
        tx.to,
        "approve(address,uint256)(bool)",
        spender,
        amount.toString(),
      ],
      {
        stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env, ETH_PRIVATE_KEY: privateKey },
      }
    );

    let stdout = "";
    let stderr = "";
    cast.stdout?.on("data", (d) => { stdout += d.toString(); });
    cast.stderr?.on("data", (d) => { stderr += d.toString(); });
    cast.on("close", (code) => {
      if (code === 0) {
        const m = stdout.match(/transactionHash\s+(0x[a-fA-F0-9]{64})/)
               ?? stdout.match(/(0x[a-fA-F0-9]{64})/);
        resolve({ success: true, hash: m?.[1] });
      } else {
        resolve({ success: false, error: stderr || stdout || `cast exited with code ${code}` });
      }
    });
  });
}

// ── output ────────────────────────────────────────────────────────────────────

function printTransaction(tx: RevokeTransaction, json: boolean): void {
  if (json) {
    console.log(JSON.stringify({ transaction: tx }, null, 2));
    return;
  }

  console.log("\n🔲  x402janus — Revoke Approval Transaction\n");
  console.log("═══════════════════════════════════════════════════════════════");
  console.log(tx.description);
  console.log("───────────────────────────────────────────────────────────────");
  console.log("Transaction:");
  console.log(`  From:      ${tx.from}`);
  console.log(`  To:        ${tx.to} (token contract)`);
  console.log(`  Value:     ${tx.value} ETH`);
  console.log(`  Gas Est:   ${tx.gasEstimate}`);
  console.log(`  Chain ID:  ${tx.chainId}`);
  console.log("\n📋 Calldata:");
  console.log(`  ${tx.data}`);
  console.log("\n📖 Decoded:");
  console.log(`  Function: approve(address,uint256)`);
  console.log(`  Spender:  0x${tx.data.slice(34, 74).replace(/^0+/, "") || "0"}`);
  console.log(`  Amount:   0x${tx.data.slice(74)} (0 = full revoke)`);
  console.log("───────────────────────────────────────────────────────────────");
  console.log("\n⚠️  To execute:");
  console.log("   1. Set PRIVATE_KEY");
  console.log("   2. Run with --execute, OR use the calldata above with cast/ethers");
  console.log("═══════════════════════════════════════════════════════════════\n");
}

// ── main ─────────────────────────────────────────────────────────────────────

async function main() {
  const { values, positionals } = parseArgs({
    args: process.argv.slice(2),
    options: {
      chain:       { type: "string",  default: "base" },
      allowance:   { type: "string" },
      execute:     { type: "boolean", default: false },
      "gas-limit": { type: "string" },
      json:        { type: "boolean", default: false },
      help:        { type: "boolean", short: "h", default: false },
    },
    allowPositionals: true,
  });

  if (values.help) {
    console.log(`
x402janus — revoke approval transaction builder

Usage: npx tsx revoke-approval.ts <wallet> <token> <spender> [options]

Arguments:
  wallet                   Wallet address revoking approval (required)
  token                    Token contract address (required)
  spender                  Spender to revoke from (required)

Options:
  --chain <base|ethereum>  Chain (default: base)
  --allowance <amount>     Set specific allowance in wei (default: 0 = full revoke)
  --execute                Execute with cast (requires PRIVATE_KEY)
  --gas-limit <limit>      Gas limit override
  --json                   Output as JSON
  --help, -h               Show this help

Required env:
  JANUS_API_URL            Janus API endpoint (used for gas estimation)
  PRIVATE_KEY              Agent wallet key — signs x402 payment + tx execution

Optional env:
  BASE_RPC_URL             RPC endpoint (recommended: set your own)

Examples:
  npx tsx revoke-approval.ts 0xWallet 0xToken 0xSpender
  npx tsx revoke-approval.ts 0xWallet 0xToken 0xSpender --execute
  npx tsx revoke-approval.ts 0xWallet 0xToken 0xSpender --allowance 1000000000000000000
`);
    process.exit(0);
  }

  requireEnv("JANUS_API_URL");
  requireEnv("PRIVATE_KEY");

  const [wallet, token, spender] = positionals;
  if (!wallet || !token || !spender) {
    console.error("Error: wallet, token, and spender are all required");
    console.error("Usage: npx tsx revoke-approval.ts <wallet> <token> <spender>");
    process.exit(1);
  }

  for (const [name, addr] of [["wallet", wallet], ["token", token], ["spender", spender]]) {
    if (!isValidAddress(addr)) {
      console.error(`Error: invalid ${name} address: ${addr}`);
      process.exit(1);
    }
  }

  const chain = (values.chain ?? "base").toLowerCase();
  if (chain !== "base" && chain !== "ethereum") {
    console.error(`Error: unsupported chain '${chain}' — use 'base' or 'ethereum'`);
    process.exit(1);
  }

  let allowance: bigint;
  try {
    allowance = values.allowance ? BigInt(values.allowance) : 0n;
  } catch {
    console.error(`Error: invalid allowance value: ${values.allowance}`);
    process.exit(1);
  }

  try {
    const tx = buildRevokeTx(wallet, token, spender, allowance, chain);
    tx.gasEstimate = await estimateGas(tx);
    if (values["gas-limit"]) tx.gasLimit = values["gas-limit"];

    if (values.execute) {
      console.log("Executing revoke transaction...");
      const gasLimit = tx.gasLimit ?? tx.gasEstimate;
      const result = await executeWithCast(tx, gasLimit);

      if (result.success) {
        if (values.json) {
          console.log(JSON.stringify({ transaction: tx, hash: result.hash }, null, 2));
        } else {
          console.log("\n✅ Transaction submitted!");
          if (result.hash) {
            console.log(`   Hash: ${result.hash}`);
            console.log(`   URL:  ${getExplorerUrl(chain, result.hash)}`);
          }
          console.log();
        }
      } else {
        console.error("Error executing transaction:", result.error);
        process.exit(1);
      }
    } else {
      printTransaction(tx, values.json);
    }
  } catch (err) {
    console.error("Error:", err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
}

main();
