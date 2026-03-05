#!/usr/bin/env node
// Show deployed contract status, wallet balance, and token balances
import { CONTRACTS, HOOK_ABI, ORACLE_ABI, ERC20_ABI, publicClient, account, formatEther, computePoolId } from "./config.mjs";

async function main() {
  const [ethBalance, hookOwner, hookPaused, oracleBot, oracleHook, posCount, orderCount, minConf, poolKey] = await Promise.all([
    publicClient.getBalance({ address: account.address }),
    publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "owner" }),
    publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "paused" }),
    publicClient.readContract({ address: CONTRACTS.oracle, abi: ORACLE_ABI, functionName: "bot" }),
    publicClient.readContract({ address: CONTRACTS.oracle, abi: ORACLE_ABI, functionName: "hook" }),
    publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "positionCounter" }),
    publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "orderCounter" }),
    publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "minConfidence" }),
    publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "poolKey" }),
  ]);

  const [bal0, bal1, sym0, sym1] = await Promise.all([
    publicClient.readContract({ address: CONTRACTS.currency0, abi: ERC20_ABI, functionName: "balanceOf", args: [account.address] }),
    publicClient.readContract({ address: CONTRACTS.currency1, abi: ERC20_ABI, functionName: "balanceOf", args: [account.address] }),
    publicClient.readContract({ address: CONTRACTS.currency0, abi: ERC20_ABI, functionName: "symbol" }),
    publicClient.readContract({ address: CONTRACTS.currency1, abi: ERC20_ABI, functionName: "symbol" }),
  ]);

  const poolId = computePoolId();

  console.log("=== GhostBot Status (Sepolia) ===");
  console.log(`Wallet: ${account.address}`);
  console.log(`ETH Balance: ${formatEther(ethBalance)} ETH`);
  console.log(`${sym0} Balance: ${formatEther(bal0)}`);
  console.log(`${sym1} Balance: ${formatEther(bal1)}`);
  console.log("");
  console.log("--- Contracts ---");
  console.log(`Hook: ${CONTRACTS.hook}`);
  console.log(`Oracle: ${CONTRACTS.oracle}`);
  console.log(`PoolManager: ${CONTRACTS.poolManager}`);
  console.log("");
  console.log("--- Hook State ---");
  console.log(`Owner: ${hookOwner}`);
  console.log(`Paused: ${hookPaused}`);
  console.log(`Min Confidence: ${minConf}`);
  console.log(`Positions: ${posCount}`);
  console.log(`Limit Orders: ${orderCount}`);
  console.log("");
  console.log("--- Pool ---");
  console.log(`Pool ID: ${poolId}`);
  console.log(`Currency0: ${poolKey.currency0} (${sym0})`);
  console.log(`Currency1: ${poolKey.currency1} (${sym1})`);
  console.log(`Fee: DYNAMIC`);
  console.log(`Tick Spacing: ${poolKey.tickSpacing}`);
  console.log("");
  console.log("--- Oracle Link ---");
  console.log(`Oracle -> Hook: ${oracleHook}`);
  console.log(`Oracle -> Bot: ${oracleBot}`);
}

main().catch(e => { console.error("Error:", e.message); process.exit(1); });
