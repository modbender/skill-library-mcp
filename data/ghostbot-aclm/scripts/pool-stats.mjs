#!/usr/bin/env node
// View pool statistics
import { CONTRACTS, HOOK_ABI, publicClient, computePoolId, formatEther } from "./config.mjs";

async function main() {
  const poolId = computePoolId();
  console.log("=== Pool Stats ===");
  console.log(`Pool ID: ${poolId}\n`);

  const stats = await publicClient.readContract({
    address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "getPoolStats", args: [poolId],
  });

  const price = Math.pow(1.0001, stats.lastTick).toFixed(6);

  console.log(`Cumulative Volume: ${formatEther(stats.cumulativeVolume)}`);
  console.log(`Last Volume Update: ${stats.lastVolumeUpdate > 0n ? new Date(Number(stats.lastVolumeUpdate) * 1000).toISOString() : "never"}`);
  console.log(`Volatility: ${stats.volatility}`);
  console.log(`Current Fee: ${stats.currentFee} (${(stats.currentFee / 10000).toFixed(2)}%)`);
  console.log(`Last Tick: ${stats.lastTick} (price: ${price})`);

  // Position and order counts
  const [posCount, orderCount] = await Promise.all([
    publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "positionCounter" }),
    publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "orderCounter" }),
  ]);
  console.log(`\nTotal Positions: ${posCount}`);
  console.log(`Total Limit Orders: ${orderCount}`);
}

main().catch(e => { console.error("Error:", e.message); process.exit(1); });
