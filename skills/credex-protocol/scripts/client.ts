#!/usr/bin/env node
/**
 * Credex Client CLI
 *
 * Borrower-side commands for interacting with the Credex Protocol.
 * All commands return JSON for machine readability.
 *
 * Usage:
 *   npx ts-node scripts/client.ts <command> [args]
 *
 * Commands:
 *   status [address]             Check credit status
 *   borrow <amount>              Borrow USDC from pool
 *   repay <amount|all>           Repay debt
 *   bridge <amount> <from> <to>  Bridge USDC between chains
 *   balance                      Check wallet balance on both chains
 *
 * Environment:
 *   WALLET_PRIVATE_KEY  (required) Your wallet private key
 *   RPC_URL             (optional) Arc Network RPC
 *   CREDEX_POOL_ADDRESS (optional) Pool contract address
 *   CREDEX_AGENT_URL    (optional) URL of Credex agent server
 */

import "dotenv/config";
import { ethers, Wallet, Contract, JsonRpcProvider, getAddress } from "ethers";
import { BridgeKit } from "@circle-fin/bridge-kit";
import { createViemAdapterFromPrivateKey } from "@circle-fin/adapter-viem-v2";

// ═══════════════════════════════════════════════════════════════════════════
//                              CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

const CONFIG = {
  RPC_URL: process.env.RPC_URL || "https://rpc.testnet.arc.network",
  BASE_RPC_URL: "https://sepolia.base.org",
  // Use env var if set, otherwise use a valid checksummed address
  POOL_ADDRESS: getAddress(
    process.env.CREDEX_POOL_ADDRESS ||
      "0x32239e52534c0b7e525fb37ed7b8d1912f263ad3",
  ),
  USDC_ARC: "0x3600000000000000000000000000000000000000",
  USDC_BASE: getAddress("0x036CbD53842c5426634e7929541eC2318f3dCF7e"),
  AGENT_URL: process.env.CREDEX_AGENT_URL || "http://localhost:10003",
};

const ERC20_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function approve(address, uint256) returns (bool)",
];

const POOL_ABI = [
  "function getAgentState(address) view returns (uint256, uint256, uint256, uint256, uint256, bool, bool)",
  "function availableCredit(address) view returns (uint256)",
];

// ═══════════════════════════════════════════════════════════════════════════
//                                HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function output(data: object): void {
  console.log(JSON.stringify(data, null, 2));
}

function error(message: string, details?: object): void {
  console.log(
    JSON.stringify({ success: false, error: message, ...details }, null, 2),
  );
  process.exit(1);
}

function getWallet(): Wallet {
  const pk = process.env.WALLET_PRIVATE_KEY;
  if (!pk) {
    error("WALLET_PRIVATE_KEY required", {
      hint: "Set WALLET_PRIVATE_KEY environment variable before running commands",
    });
  }
  const provider = new JsonRpcProvider(CONFIG.RPC_URL);
  return new Wallet(pk!, provider);
}

function formatUsdc(amount: bigint): string {
  return ethers.formatUnits(amount, 6);
}

function parseUsdc(amount: string): bigint {
  return ethers.parseUnits(amount, 6);
}

async function callAgent(endpoint: string, body?: object): Promise<any> {
  const response = await fetch(`${CONFIG.AGENT_URL}${endpoint}`, {
    method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  return response.json();
}

// ═══════════════════════════════════════════════════════════════════════════
//                               COMMANDS
// ═══════════════════════════════════════════════════════════════════════════

async function checkStatus(address: string): Promise<void> {
  const wallet = getWallet();
  const pool = new Contract(CONFIG.POOL_ADDRESS, POOL_ABI, wallet);

  try {
    const [
      debtRaw,
      principalRaw,
      creditLimitRaw,
      ,
      lastRepayment,
      frozen,
      active,
    ] = await pool.getAgentState(address);
    const availableRaw = await pool.availableCredit(address);

    // Explicit bigint casting for TypeScript
    const debt = BigInt(debtRaw);
    const principal = BigInt(principalRaw);
    const creditLimit = BigInt(creditLimitRaw);
    const available = BigInt(availableRaw);
    const interest = debt - principal;

    output({
      creditLimit: formatUsdc(creditLimit),
      principal: formatUsdc(principal),
      interest: formatUsdc(interest),
      debt: formatUsdc(debt),
      availableCredit: formatUsdc(available),
      active,
      frozen,
    });
  } catch (e) {
    error("Failed to fetch status", { address, cause: String(e) });
  }
}

async function borrowFunds(amount: string): Promise<void> {
  const wallet = getWallet();

  try {
    const result = await callAgent("/borrow", {
      agentAddress: wallet.address,
      amount,
    });

    if (result.success) {
      output({
        success: true,
        txHash: result.txHash || null,
        borrowed: amount,
        newDebt: result.data?.debt || null,
        availableCredit: result.data?.available || null,
      });
    } else {
      error("Borrow failed", { message: result.message });
    }
  } catch (e) {
    error("Borrow request failed", { cause: String(e) });
  }
}

async function repayDebt(amount: string): Promise<void> {
  const wallet = getWallet();
  const usdc = new Contract(CONFIG.USDC_ARC, ERC20_ABI, wallet);

  let repayAmount = amount;

  // Handle "all" repayment
  if (amount.toLowerCase() === "all" || amount.toLowerCase() === "full") {
    try {
      const statusRes = await callAgent(`/status/${wallet.address}`);
      if (!statusRes.success) {
        error("Failed to fetch debt for full repayment", {
          message: statusRes.message,
        });
      }
      const debt = parseFloat(statusRes.data.debt);
      repayAmount = (debt * 1.01).toFixed(6); // 1% buffer
    } catch (e) {
      error("Failed to calculate full repayment", { cause: String(e) });
    }
  }

  try {
    // Approve USDC
    const approveTx = await usdc.approve(
      CONFIG.POOL_ADDRESS,
      parseUsdc(repayAmount),
    );
    await approveTx.wait();

    // Repay via agent
    const result = await callAgent("/repay", {
      agentAddress: wallet.address,
      amount: repayAmount,
    });

    if (result.success) {
      output({
        success: true,
        txHash: result.txHash || null,
        repaid: repayAmount,
        remainingDebt: result.data?.debt || "0.000000",
        newCreditLimit: result.data?.creditLimit || null,
      });
    } else {
      error("Repay failed", { message: result.message });
    }
  } catch (e) {
    error("Repay request failed", { cause: String(e) });
  }
}

async function bridgeUsdc(
  amount: string,
  from: string,
  to: string,
): Promise<void> {
  const pk = process.env.WALLET_PRIVATE_KEY;
  if (!pk) error("WALLET_PRIVATE_KEY required");

  const fromChain = from.toLowerCase().includes("base")
    ? "Base_Sepolia"
    : "Arc_Testnet";
  const toChain = to.toLowerCase().includes("base")
    ? "Base_Sepolia"
    : "Arc_Testnet";

  if (fromChain === toChain) {
    error("Same chain error", {
      message: "Source and destination must be different",
      from: fromChain,
      to: toChain,
    });
  }

  try {
    const kit = new BridgeKit();
    const adapter = createViemAdapterFromPrivateKey({
      privateKey: pk as `0x${string}`,
    });

    await kit.bridge({
      from: { adapter, chain: fromChain },
      to: { adapter, chain: toChain },
      amount,
    });

    output({
      success: true,
      amount,
      from: fromChain,
      to: toChain,
      estimatedArrival: "5-10 minutes",
    });
  } catch (e) {
    error("Bridge failed", { cause: String(e) });
  }
}

async function checkBalance(): Promise<void> {
  const wallet = getWallet();

  try {
    // Arc balance
    const arcUsdc = new Contract(CONFIG.USDC_ARC, ERC20_ABI, wallet);
    const arcBalanceRaw = await arcUsdc.balanceOf(wallet.address);
    const arcBalance = BigInt(arcBalanceRaw);

    // Base balance
    const baseProvider = new JsonRpcProvider(CONFIG.BASE_RPC_URL);
    const baseUsdc = new Contract(CONFIG.USDC_BASE, ERC20_ABI, baseProvider);
    const baseBalanceRaw = await baseUsdc.balanceOf(wallet.address);
    const baseBalance = BigInt(baseBalanceRaw);

    const arc = parseFloat(formatUsdc(arcBalance));
    const base = parseFloat(formatUsdc(baseBalance));

    output({
      arc: formatUsdc(arcBalance),
      base: formatUsdc(baseBalance),
      total: (arc + base).toFixed(6),
    });
  } catch (e) {
    error("Failed to fetch balances", { cause: String(e) });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
//                                  CLI
// ═══════════════════════════════════════════════════════════════════════════

async function main(): Promise<void> {
  const [, , command, ...args] = process.argv;

  switch (command) {
    case "status":
      await checkStatus(args[0] || getWallet().address);
      break;
    case "borrow":
      if (!args[0]) error("Amount required", { usage: "borrow <amount>" });
      await borrowFunds(args[0]);
      break;
    case "repay":
      if (!args[0]) error("Amount required", { usage: "repay <amount|all>" });
      await repayDebt(args[0]);
      break;
    case "bridge":
      if (args.length < 3)
        error("Invalid arguments", { usage: "bridge <amount> <from> <to>" });
      await bridgeUsdc(args[0], args[1], args[2]);
      break;
    case "balance":
      await checkBalance();
      break;
    default:
      output({
        name: "Credex Client CLI",
        commands: {
          "status [address]": "Check credit status",
          "borrow <amount>": "Borrow USDC from pool",
          "repay <amount|all>": "Repay debt",
          "bridge <amount> <from> <to>": "Bridge USDC (arc/base)",
          balance: "Check wallet balances",
        },
        examples: [
          "npx ts-node scripts/client.ts status",
          "npx ts-node scripts/client.ts borrow 5",
          "npx ts-node scripts/client.ts repay all",
          "npx ts-node scripts/client.ts bridge 10 arc base",
        ],
      });
  }
}

main();
