#!/usr/bin/env node
// Post oracle signals (rebalance or fee recommendation)
// Usage: node post-signal.mjs rebalance <positionId> <tickLower> <tickUpper> <confidence>
//        node post-signal.mjs fee <feeAmount> <confidence>
import { CONTRACTS, ORACLE_ABI, publicClient, walletClient, computePoolId } from "./config.mjs";

const action = process.argv[2];
const poolId = computePoolId();

async function main() {
  if (action === "rebalance") {
    const posId = BigInt(process.argv[3] || "1");
    const tickLower = parseInt(process.argv[4] || "-600");
    const tickUpper = parseInt(process.argv[5] || "600");
    const confidence = parseInt(process.argv[6] || "85");
    const timestamp = BigInt(Math.floor(Date.now() / 1000));

    console.log(`Posting rebalance signal: pos=${posId}, ticks=[${tickLower},${tickUpper}], conf=${confidence}`);
    const txHash = await walletClient.writeContract({
      address: CONTRACTS.oracle, abi: ORACLE_ABI, functionName: "postRebalanceSignal",
      args: [poolId, { positionId: posId, newTickLower: tickLower, newTickUpper: tickUpper, confidence, timestamp }],
    });
    const receipt = await publicClient.waitForTransactionReceipt({ hash: txHash });
    console.log(`TX: ${txHash} (block ${receipt.blockNumber}, status: ${receipt.status})`);
    console.log(`Etherscan: https://sepolia.etherscan.io/tx/${txHash}`);
  } else if (action === "fee") {
    const fee = parseInt(process.argv[3] || "3000");
    const confidence = parseInt(process.argv[4] || "85");
    const timestamp = BigInt(Math.floor(Date.now() / 1000));

    console.log(`Posting fee recommendation: fee=${fee} (${(fee/10000).toFixed(2)}%), conf=${confidence}`);
    const txHash = await walletClient.writeContract({
      address: CONTRACTS.oracle, abi: ORACLE_ABI, functionName: "postFeeRecommendation",
      args: [poolId, { fee, confidence, timestamp }],
    });
    const receipt = await publicClient.waitForTransactionReceipt({ hash: txHash });
    console.log(`TX: ${txHash} (block ${receipt.blockNumber}, status: ${receipt.status})`);
    console.log(`Etherscan: https://sepolia.etherscan.io/tx/${txHash}`);
  } else {
    console.log("Usage:");
    console.log("  node post-signal.mjs rebalance <positionId> <tickLower> <tickUpper> <confidence>");
    console.log("  node post-signal.mjs fee <feeAmount> <confidence>");
  }
}

main().catch(e => { console.error("Error:", e.message); process.exit(1); });
