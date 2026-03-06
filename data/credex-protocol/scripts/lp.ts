#!/usr/bin/env node
/**
 * Credex LP CLI
 *
 * Liquidity Provider commands for interacting with the Credex Protocol.
 * All commands return JSON for machine readability.
 *
 * Usage:
 *   npx ts-node scripts/lp.ts <command> [args]
 *
 * Commands:
 *   pool-status             Check overall pool metrics
 *   deposit <amount>        Deposit USDC to receive shares
 *   withdraw <shares|all>   Burn shares to withdraw USDC
 *   lp-balance [address]    Check LP position
 *   balance                 Check wallet balance on both chains
 *   bridge <amount> <from> <to>  Bridge USDC between chains
 *
 * Environment:
 *   WALLET_PRIVATE_KEY  (required) Your wallet private key
 *   RPC_URL             (optional) Arc Network RPC
 *   CREDEX_POOL_ADDRESS (optional) Pool contract address
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
};

const ERC20_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function approve(address, uint256) returns (bool)",
];

const POOL_ABI = [
  "function totalLiquidity() view returns (uint256)",
  "function totalAssets() view returns (uint256)",
  "function totalShares() view returns (uint256)",
  "function lpShares(address) view returns (uint256)",
  "function deposit(uint256) returns (uint256)",
  "function withdraw(uint256) returns (uint256)",
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

// ═══════════════════════════════════════════════════════════════════════════
//                               COMMANDS
// ═══════════════════════════════════════════════════════════════════════════

async function poolStatus(): Promise<void> {
  const wallet = getWallet();
  const pool = new Contract(CONFIG.POOL_ADDRESS, POOL_ABI, wallet);

  try {
    const [liquidityRaw, assetsRaw, sharesRaw] = await Promise.all([
      pool.totalLiquidity(),
      pool.totalAssets(),
      pool.totalShares(),
    ]);

    // Explicit bigint casting for TypeScript
    const liquidity = BigInt(liquidityRaw);
    const assets = BigInt(assetsRaw);
    const shares = BigInt(sharesRaw);

    const debt = assets - liquidity;
    const sharePrice = shares > 0n ? Number(assets) / Number(shares) : 1;
    const utilizationPct = assets > 0n ? Number((debt * 100n) / assets) : 0;

    output({
      totalAssets: formatUsdc(assets),
      totalLiquidity: formatUsdc(liquidity),
      totalDebt: formatUsdc(debt),
      totalShares: formatUsdc(shares),
      sharePrice: sharePrice.toFixed(6),
      utilizationPercent: utilizationPct,
    });
  } catch (e) {
    error("Failed to fetch pool status", { cause: String(e) });
  }
}

async function depositUsdc(amount: string): Promise<void> {
  const wallet = getWallet();
  const usdc = new Contract(CONFIG.USDC_ARC, ERC20_ABI, wallet);
  const pool = new Contract(CONFIG.POOL_ADDRESS, POOL_ABI, wallet);

  const amountWei = parseUsdc(amount);

  try {
    // Check balance
    const balanceRaw = await usdc.balanceOf(wallet.address);
    const balance = BigInt(balanceRaw);
    if (balance < amountWei) {
      error("Insufficient balance", {
        required: amount,
        available: formatUsdc(balance),
      });
    }

    // Approve
    const approveTx = await usdc.approve(CONFIG.POOL_ADDRESS, amountWei);
    await approveTx.wait();

    // Deposit
    const depositTx = await pool.deposit(amountWei);
    const receipt = await depositTx.wait();

    // Get new shares
    const newSharesRaw = await pool.lpShares(wallet.address);
    const newShares = BigInt(newSharesRaw);

    output({
      success: true,
      txHash: receipt.hash,
      deposited: amount,
      sharesReceived: formatUsdc(newShares),
      totalShares: formatUsdc(newShares),
    });
  } catch (e) {
    error("Deposit failed", { cause: String(e) });
  }
}

async function withdrawShares(input: string): Promise<void> {
  const wallet = getWallet();
  const pool = new Contract(CONFIG.POOL_ADDRESS, POOL_ABI, wallet);

  try {
    const currentSharesRaw = await pool.lpShares(wallet.address);
    const currentShares = BigInt(currentSharesRaw);
    let sharesToWithdraw: bigint;

    // Handle "all"
    if (input.toLowerCase() === "all" || input.toLowerCase() === "max") {
      const [liquidityRaw, assetsRaw, totalSharesRaw] = await Promise.all([
        pool.totalLiquidity(),
        pool.totalAssets(),
        pool.totalShares(),
      ]);

      const liquidity = BigInt(liquidityRaw);
      const assets = BigInt(assetsRaw);
      const totalShares = BigInt(totalSharesRaw);

      // Max shares based on available liquidity
      const maxShares = (liquidity * totalShares) / assets;
      sharesToWithdraw = currentShares < maxShares ? currentShares : maxShares;
    } else {
      sharesToWithdraw = parseUsdc(input);
    }

    if (sharesToWithdraw === 0n) {
      error("No shares to withdraw");
    }

    if (currentShares < sharesToWithdraw) {
      error("Insufficient shares", {
        requested: formatUsdc(sharesToWithdraw),
        available: formatUsdc(currentShares),
      });
    }

    const withdrawTx = await pool.withdraw(sharesToWithdraw);
    const receipt = await withdrawTx.wait();

    // Get updated balance
    const remainingSharesRaw = await pool.lpShares(wallet.address);
    const remainingShares = BigInt(remainingSharesRaw);

    output({
      success: true,
      txHash: receipt.hash,
      sharesBurned: formatUsdc(sharesToWithdraw),
      usdcReceived: formatUsdc(sharesToWithdraw),
      remainingShares: formatUsdc(remainingShares),
    });
  } catch (e) {
    error("Withdrawal failed", { cause: String(e) });
  }
}

async function lpBalance(address?: string): Promise<void> {
  const wallet = getWallet();
  const pool = new Contract(CONFIG.POOL_ADDRESS, POOL_ABI, wallet);
  const target = address || wallet.address;

  try {
    const [sharesRaw, assetsRaw, totalSharesRaw] = await Promise.all([
      pool.lpShares(target),
      pool.totalAssets(),
      pool.totalShares(),
    ]);

    // Explicit bigint casting for TypeScript
    const shares = BigInt(sharesRaw);
    const assets = BigInt(assetsRaw);
    const totalShares = BigInt(totalSharesRaw);

    const value: bigint =
      totalShares > 0n ? (shares * assets) / totalShares : 0n;

    output({
      shares: formatUsdc(shares),
      value: formatUsdc(value),
    });
  } catch (e) {
    error("Failed to fetch LP balance", { cause: String(e) });
  }
}

async function checkBalance(): Promise<void> {
  const wallet = getWallet();

  try {
    // Arc balance
    const arcUsdc = new Contract(CONFIG.USDC_ARC, ERC20_ABI, wallet);
    const arcBalance = await arcUsdc.balanceOf(wallet.address);

    // Base balance
    const baseProvider = new JsonRpcProvider(CONFIG.BASE_RPC_URL);
    const baseUsdc = new Contract(CONFIG.USDC_BASE, ERC20_ABI, baseProvider);
    const baseBalance = await baseUsdc.balanceOf(wallet.address);

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

// ═══════════════════════════════════════════════════════════════════════════
//                                  CLI
// ═══════════════════════════════════════════════════════════════════════════

async function main(): Promise<void> {
  const [, , command, ...args] = process.argv;

  switch (command) {
    case "pool-status":
      await poolStatus();
      break;
    case "deposit":
      if (!args[0]) error("Amount required", { usage: "deposit <amount>" });
      await depositUsdc(args[0]);
      break;
    case "withdraw":
      if (!args[0])
        error("Shares required", { usage: "withdraw <shares|all>" });
      await withdrawShares(args[0]);
      break;
    case "lp-balance":
      await lpBalance(args[0]);
      break;
    case "balance":
      await checkBalance();
      break;
    case "bridge":
      if (args.length < 3)
        error("Invalid arguments", { usage: "bridge <amount> <from> <to>" });
      await bridgeUsdc(args[0], args[1], args[2]);
      break;
    default:
      output({
        name: "Credex LP CLI",
        commands: {
          "pool-status": "Check pool metrics",
          "deposit <amount>": "Deposit USDC to receive shares",
          "withdraw <shares|all>": "Burn shares to withdraw USDC",
          "lp-balance [address]": "Check LP position",
          balance: "Check wallet balances",
          "bridge <amount> <from> <to>": "Bridge USDC (arc/base)",
        },
        examples: [
          "npx ts-node scripts/lp.ts pool-status",
          "npx ts-node scripts/lp.ts deposit 100",
          "npx ts-node scripts/lp.ts withdraw all",
          "npx ts-node scripts/lp.ts bridge 50 base arc",
        ],
      });
  }
}

main();
