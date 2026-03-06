#!/usr/bin/env node
// Add liquidity to the GhostBot hook pool
// Usage: node add-liquidity.mjs <amount> [tickLower] [tickUpper] [autoRebalance]
// Example: node add-liquidity.mjs 1000 -600 600 true
import { CONTRACTS, HOOK_ABI, ERC20_ABI, publicClient, walletClient, account, parseEther, formatEther } from "./config.mjs";

const amount = process.argv[2] || "1000";
const tickLower = parseInt(process.argv[3] || "-600");
const tickUpper = parseInt(process.argv[4] || "600");
const autoRebalance = (process.argv[5] || "true") === "true";

async function main() {
  const amountWei = parseEther(amount);
  console.log(`Adding liquidity: ${amount} tokens each, ticks [${tickLower}, ${tickUpper}], autoRebalance=${autoRebalance}`);

  // Check token balances
  const [bal0, bal1] = await Promise.all([
    publicClient.readContract({ address: CONTRACTS.currency0, abi: ERC20_ABI, functionName: "balanceOf", args: [account.address] }),
    publicClient.readContract({ address: CONTRACTS.currency1, abi: ERC20_ABI, functionName: "balanceOf", args: [account.address] }),
  ]);

  if (bal0 < amountWei || bal1 < amountWei) {
    console.log(`Insufficient tokens. Have: ${formatEther(bal0)} / ${formatEther(bal1)}. Need: ${amount} each.`);
    console.log("Minting tokens...");
    const mint0 = await walletClient.writeContract({
      address: CONTRACTS.currency0, abi: ERC20_ABI, functionName: "mint",
      args: [account.address, amountWei],
    });
    const mint1 = await walletClient.writeContract({
      address: CONTRACTS.currency1, abi: ERC20_ABI, functionName: "mint",
      args: [account.address, amountWei],
    });
    await Promise.all([
      publicClient.waitForTransactionReceipt({ hash: mint0 }),
      publicClient.waitForTransactionReceipt({ hash: mint1 }),
    ]);
    console.log("Tokens minted.");
  }

  // Approve hook
  const [allow0, allow1] = await Promise.all([
    publicClient.readContract({ address: CONTRACTS.currency0, abi: ERC20_ABI, functionName: "allowance", args: [account.address, CONTRACTS.hook] }),
    publicClient.readContract({ address: CONTRACTS.currency1, abi: ERC20_ABI, functionName: "allowance", args: [account.address, CONTRACTS.hook] }),
  ]);

  if (allow0 < amountWei) {
    console.log("Approving currency0...");
    const tx = await walletClient.writeContract({
      address: CONTRACTS.currency0, abi: ERC20_ABI, functionName: "approve",
      args: [CONTRACTS.hook, amountWei * 10n],
    });
    await publicClient.waitForTransactionReceipt({ hash: tx });
  }
  if (allow1 < amountWei) {
    console.log("Approving currency1...");
    const tx = await walletClient.writeContract({
      address: CONTRACTS.currency1, abi: ERC20_ABI, functionName: "approve",
      args: [CONTRACTS.hook, amountWei * 10n],
    });
    await publicClient.waitForTransactionReceipt({ hash: tx });
  }

  // Salt: bit 0 = autoRebalance
  const salt = autoRebalance ? "0x0000000000000000000000000000000000000000000000000000000000000001" : "0x0000000000000000000000000000000000000000000000000000000000000000";
  const deadline = BigInt(Math.floor(Date.now() / 1000) + 3600);

  console.log("Sending addLiquidity transaction...");
  const txHash = await walletClient.writeContract({
    address: CONTRACTS.hook,
    abi: HOOK_ABI,
    functionName: "addLiquidity",
    args: [{
      amount0Desired: amountWei,
      amount1Desired: amountWei,
      amount0Min: 0n,
      amount1Min: 0n,
      deadline,
      tickLower,
      tickUpper,
      userInputSalt: salt,
    }],
  });

  console.log(`Transaction sent: ${txHash}`);
  console.log("Waiting for confirmation...");
  const receipt = await publicClient.waitForTransactionReceipt({ hash: txHash });
  console.log(`Confirmed in block ${receipt.blockNumber}, status: ${receipt.status}`);
  console.log(`Gas used: ${receipt.gasUsed}`);
  console.log(`Etherscan: https://sepolia.etherscan.io/tx/${txHash}`);

  // Check new position count
  const posCount = await publicClient.readContract({ address: CONTRACTS.hook, abi: HOOK_ABI, functionName: "positionCounter" });
  console.log(`Total positions on hook: ${posCount}`);
}

main().catch(e => { console.error("Error:", e.message); process.exit(1); });
