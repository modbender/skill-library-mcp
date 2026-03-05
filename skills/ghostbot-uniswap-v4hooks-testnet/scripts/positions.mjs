#!/usr/bin/env node
// View user positions on the GhostBot hook
// Usage: node positions.mjs [address]
import { CONTRACTS, HOOK_ABI, publicClient, account } from "./config.mjs";

const userAddress = process.argv[2] || account.address;

async function main() {
  console.log(`=== Positions for ${userAddress} ===`);

  const positionIds = await publicClient.readContract({
    address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "getUserPositions", args: [userAddress],
  });

  if (positionIds.length === 0) {
    console.log("No positions found.");
    return;
  }

  console.log(`Found ${positionIds.length} position(s)\n`);

  for (const id of positionIds) {
    const pos = await publicClient.readContract({
      address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "getPosition", args: [id],
    });
    const price = (tick) => Math.pow(1.0001, tick).toFixed(6);
    console.log(`Position #${id}`);
    console.log(`  Owner: ${pos.owner}`);
    console.log(`  Tick Range: [${pos.tickLower}, ${pos.tickUpper}]`);
    console.log(`  Price Range: [${price(pos.tickLower)}, ${price(pos.tickUpper)}]`);
    console.log(`  Liquidity: ${pos.liquidity}`);
    console.log(`  Auto-Rebalance: ${pos.autoRebalance}`);
    console.log(`  Last Rebalance: ${pos.lastRebalanceTime > 0n ? new Date(Number(pos.lastRebalanceTime) * 1000).toISOString() : "never"}`);
    console.log("");
  }
}

main().catch(e => { console.error("Error:", e.message); process.exit(1); });
