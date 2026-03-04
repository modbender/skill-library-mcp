const hre = require("hardhat");
require("dotenv").config();

async function main() {
  const DEPLOYER_ADDRESS = process.env.DEPLOYER_ADDRESS;

  if (!DEPLOYER_ADDRESS) {
    console.error("❌ DEPLOYER_ADDRESS not set in .env");
    process.exit(1);
  }

  console.log("🔍 Checking BNB Balance");
  console.log("========================");
  console.log(`Address: ${DEPLOYER_ADDRESS}`);
  console.log(`Network: BNB Testnet (chainId: 97)\n`);

  try {
    const balance = await hre.ethers.provider.getBalance(DEPLOYER_ADDRESS);
    const balanceInBNB = hre.ethers.formatEther(balance);

    console.log(`💰 Balance: ${balanceInBNB} BNB`);
    console.log(`   (${balance.toString()} wei)`);

    if (balance === 0n) {
      console.log("\n⚠️  Balance is 0. Request BNB from faucet:");
      console.log("   https://testnet.binance.org/faucet-smart-chain");
    } else if (balance < hre.ethers.parseEther("0.1")) {
      console.log("\n⚠️  Low balance. You may need more BNB for gas fees.");
    } else {
      console.log("\n✅ Sufficient balance for deployment!");
    }

    // Get gas price
    const gasPrice = await hre.ethers.provider.getGasPrice();
    const gasPriceInGwei = hre.ethers.formatUnits(gasPrice, "gwei");

    console.log(`\n⛽ Current Gas Price: ${gasPriceInGwei} Gwei`);

    // Estimate deployment cost (rough)
    const estimatedGas = 3000000n; // Typical for YieldVault
    const estimatedCost = (gasPrice * estimatedGas) / BigInt(10) ** 18n;
    const estimatedCostInBNB = hre.ethers.formatEther(estimatedCost);

    console.log(`📊 Estimated Deployment Cost: ~${estimatedCostInBNB} BNB`);

  } catch (error) {
    console.error("❌ Error:", error.message);
    process.exit(1);
  }
}

main();
