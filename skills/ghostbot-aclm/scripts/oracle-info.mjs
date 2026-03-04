#!/usr/bin/env node
// Check oracle signals and fee recommendations
import { CONTRACTS, ORACLE_ABI, publicClient, computePoolId } from "./config.mjs";

async function main() {
  const poolId = computePoolId();
  console.log("=== Oracle Info ===");
  console.log(`Pool ID: ${poolId}\n`);

  // Dynamic fee
  const [fee, feeConf] = await publicClient.readContract({
    address: CONTRACTS.oracle, abi: ORACLE_ABI, functionName: "getDynamicFee", args: [poolId],
  });
  console.log("--- Fee Recommendation ---");
  if (fee > 0) {
    console.log(`Fee: ${fee} (${(fee / 10000).toFixed(2)}%)`);
    console.log(`Confidence: ${feeConf}/100`);
  } else {
    console.log("No active fee recommendation (expired or not set)");
  }

  // Rebalance signals
  console.log("\n--- Rebalance Signals ---");
  const signals = await publicClient.readContract({
    address: CONTRACTS.oracle, abi: ORACLE_ABI, functionName: "getPositionsNeedingRebalance", args: [poolId],
  });

  if (signals.length === 0) {
    console.log("No active rebalance signals (expired or not set)");
  } else {
    for (const sig of signals) {
      console.log(`Position #${sig.positionId}: ticks [${sig.newTickLower}, ${sig.newTickUpper}], confidence=${sig.confidence}, time=${new Date(Number(sig.timestamp) * 1000).toISOString()}`);
    }
  }

  // Signal TTL
  const ttl = await publicClient.readContract({ address: CONTRACTS.oracle, abi: ORACLE_ABI, functionName: "signalTTL" });
  console.log(`\nSignal TTL: ${ttl} seconds (${Number(ttl) / 60} minutes)`);
}

main().catch(e => { console.error("Error:", e.message); process.exit(1); });
