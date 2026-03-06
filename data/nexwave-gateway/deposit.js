import {
  circleWallet,
  walletAddress,
  ethereum,
  arc,
} from "./setup-gateway.js";

///////////////////////////////////////////////////////////////////////////////
// Deposit USDC into Circle Gateway
// This script deposits USDC into the Gateway Wallet contract on each chain,
// creating a unified crosschain USDC balance.
//
// Uses Circle Programmable Wallets for transaction signing — no raw private keys.
// IMPORTANT: Do NOT use ERC-20 transfer() directly — that will lose funds.
// The correct flow is: approve() → deposit() on the Gateway Wallet contract.

const DEPOSIT_AMOUNT = "10000000"; // 10 USDC (6 decimals, as string for Circle SDK)
const DEPOSIT_DISPLAY = "10";

console.log("═══════════════════════════════════════════════");
console.log("  Nexwave Gateway — Deposit USDC");
console.log("═══════════════════════════════════════════════");
console.log(`Account: ${walletAddress}`);
console.log(`Deposit amount: ${DEPOSIT_DISPLAY} USDC per chain\n`);

for (const chain of [ethereum, arc]) {
  console.log(`\n🔗 ${chain.name} (Domain ${chain.domain})`);
  console.log("─".repeat(40));

  // Check USDC balance (read-only via viem)
  console.log("   Checking USDC balance...");
  const balance = await chain.usdc.read.balanceOf([walletAddress]);
  console.log(`   Balance: ${Number(balance) / 1e6} USDC`);

  if (balance < BigInt(DEPOSIT_AMOUNT)) {
    console.error(`   ❌ Insufficient USDC on ${chain.name}!`);
    console.error("   Please top up at https://faucet.circle.com");
    process.exit(1);
  }

  try {
    // Step 1: Approve Gateway Wallet to spend USDC
    console.log("   Approving Gateway Wallet for USDC...");
    const approveTx = await circleWallet.executeContract(chain.chainName, {
      contractAddress: chain.usdcAddress,
      functionSignature: "approve(address,uint256)",
      params: [chain.gatewayWalletAddress, DEPOSIT_AMOUNT],
    });
    console.log(`   ✅ Approved — tx: ${approveTx.txHash}`);

    // Step 2: Deposit USDC into Gateway Wallet
    console.log("   Depositing USDC into Gateway Wallet...");
    const depositTx = await circleWallet.executeContract(chain.chainName, {
      contractAddress: chain.gatewayWalletAddress,
      functionSignature: "deposit(address,uint256)",
      params: [chain.usdcAddress, DEPOSIT_AMOUNT],
    });
    console.log(`   ✅ Deposited — tx: ${depositTx.txHash}`);
  } catch (error) {
    console.error("   ❌ Error:", error.message || error);
    process.exit(1);
  }
}

console.log("\n═══════════════════════════════════════════════");
console.log("✅ Deposits complete!");
console.log("   Arc: finality is ~0.5 seconds (1 block)");
console.log("   Ethereum: wait ~20 min for finality");
console.log("   Then run: node check-balance.js");
console.log("═══════════════════════════════════════════════");

process.exit(0);
