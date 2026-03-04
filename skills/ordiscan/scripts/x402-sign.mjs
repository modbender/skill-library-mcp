#!/usr/bin/env node

/**
 * x402 v2 ERC-3009 signing script for Ordiscan API payments.
 *
 * Usage:
 *   node x402-sign.mjs sign <base64-payment-required-header>
 *   node x402-sign.mjs balance
 *
 * Env vars:
 *   X402_PRIVATE_KEY  - Ethereum private key (with USDC on Base)
 *   BASE_RPC_URL      - (optional) Base RPC endpoint, defaults to https://mainnet.base.org
 */

import {
  createPublicClient,
  createWalletClient,
  http,
  keccak256,
  encodePacked,
  concat,
  pad,
  toHex,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { base } from "viem/chains";

// ── Constants ──────────────────────────────────────────────────────────────────

const USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const USDC_DECIMALS = 6;

const USDC_DOMAIN = {
  name: "USD Coin",
  version: "2",
  chainId: 8453n,
  verifyingContract: USDC_ADDRESS,
};

const TRANSFER_WITH_AUTHORIZATION_TYPES = {
  TransferWithAuthorization: [
    { name: "from", type: "address" },
    { name: "to", type: "address" },
    { name: "value", type: "uint256" },
    { name: "validAfter", type: "uint256" },
    { name: "validBefore", type: "uint256" },
    { name: "nonce", type: "bytes32" },
  ],
};

const BALANCE_OF_ABI = [
  {
    name: "balanceOf",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "account", type: "address" }],
    outputs: [{ name: "", type: "uint256" }],
  },
];

// ── Helpers ────────────────────────────────────────────────────────────────────

function log(msg) {
  process.stderr.write(msg + "\n");
}

function getPrivateKey() {
  const raw = process.env.X402_PRIVATE_KEY;
  if (!raw) {
    log("Error: X402_PRIVATE_KEY environment variable is not set.");
    process.exit(1);
  }
  return raw.startsWith("0x") ? raw : `0x${raw}`;
}

function getRpcUrl() {
  return process.env.BASE_RPC_URL ?? "https://mainnet.base.org";
}

// ── Commands ───────────────────────────────────────────────────────────────────

async function cmdSign(base64Header) {
  const privateKey = getPrivateKey();
  const account = privateKeyToAccount(privateKey);
  const rpcUrl = getRpcUrl();

  // Decode the Payment-Required header (x402 v2)
  const headerJson = Buffer.from(base64Header, "base64").toString("utf-8");
  const paymentRequired = JSON.parse(headerJson);

  const accept = paymentRequired.accepts?.[0];
  if (!accept) {
    log("Error: No payment options in Payment-Required header.");
    process.exit(1);
  }

  const amount = BigInt(accept.amount);
  const amountUsdc = Number(amount) / 10 ** USDC_DECIMALS;

  log(`Signing payment of $${amountUsdc.toFixed(2)} USDC`);
  log(`  From: ${account.address}`);
  log(`  To:   ${accept.payTo}`);

  // Check balance
  const publicClient = createPublicClient({
    chain: base,
    transport: http(rpcUrl),
  });

  const balance = await publicClient.readContract({
    address: USDC_ADDRESS,
    abi: BALANCE_OF_ABI,
    functionName: "balanceOf",
    args: [account.address],
  });

  if (balance < amount) {
    const balanceUsdc = Number(balance) / 10 ** USDC_DECIMALS;
    log(
      `Error: Insufficient USDC balance. Have $${balanceUsdc.toFixed(2)}, need $${amountUsdc.toFixed(2)}`
    );
    process.exit(1);
  }

  // Generate nonce and validity window
  const nonce = keccak256(
    concat([
      pad(toHex(Date.now())),
      encodePacked(["address"], [account.address]),
    ])
  );
  const validAfter = 0n;
  const validBefore = BigInt(Math.floor(Date.now() / 1000) + 3600);

  // Sign EIP-3009 TransferWithAuthorization
  const walletClient = createWalletClient({
    account,
    chain: base,
    transport: http(rpcUrl),
  });

  const signature = await walletClient.signTypedData({
    domain: USDC_DOMAIN,
    types: TRANSFER_WITH_AUTHORIZATION_TYPES,
    primaryType: "TransferWithAuthorization",
    message: {
      from: account.address,
      to: accept.payTo,
      value: amount,
      validAfter,
      validBefore,
      nonce,
    },
  });

  // Build Payment-Signature header payload (x402 v2)
  const paymentPayload = {
    x402Version: 2,
    resource: paymentRequired.resource,
    accepted: accept,
    payload: {
      signature,
      authorization: {
        from: account.address,
        to: accept.payTo,
        value: String(amount),
        validAfter: String(validAfter),
        validBefore: String(validBefore),
        nonce,
      },
    },
  };

  const paymentHeader = Buffer.from(JSON.stringify(paymentPayload)).toString(
    "base64"
  );

  log("Payment signed successfully.");

  // Output ONLY the base64 header to stdout (for piping)
  process.stdout.write(paymentHeader);
}

async function cmdBalance() {
  const privateKey = getPrivateKey();
  const account = privateKeyToAccount(privateKey);
  const rpcUrl = getRpcUrl();

  const publicClient = createPublicClient({
    chain: base,
    transport: http(rpcUrl),
  });

  const balance = await publicClient.readContract({
    address: USDC_ADDRESS,
    abi: BALANCE_OF_ABI,
    functionName: "balanceOf",
    args: [account.address],
  });

  const balanceUsdc = Number(balance) / 10 ** USDC_DECIMALS;

  log(`Wallet:  ${account.address}`);
  log(`Balance: $${balanceUsdc.toFixed(2)} USDC (${balance} units)`);
}

// ── Main ───────────────────────────────────────────────────────────────────────

const [command, ...args] = process.argv.slice(2);

if (command === "sign") {
  const base64Header = args[0];
  if (!base64Header) {
    log("Usage: node x402-sign.mjs sign <base64-payment-required-header>");
    process.exit(1);
  }
  await cmdSign(base64Header);
} else if (command === "balance") {
  await cmdBalance();
} else {
  log("Usage:");
  log("  node x402-sign.mjs sign <base64-payment-required-header>");
  log("  node x402-sign.mjs balance");
  process.exit(1);
}
