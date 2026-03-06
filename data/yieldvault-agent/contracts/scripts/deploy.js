const hre = require("hardhat");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

// Vault configurations from mockdata.json
const VAULT_CONFIGS = {
  vault_bnb_lp_001: {
    name: "BNB-BUSD LP Yield",
    token: "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312", // USDC testnet
  },
  vault_eth_staking_001: {
    name: "ETH Staking Vault",
    token: "0x8ba1f109551bD432803012645Ac136ddd64DBA72", // WETH testnet
  },
  vault_cake_farm_001: {
    name: "CAKE Farming",
    token: "0x8301F2213c0eeD49a7E28Ae4c3e91722919B8c63", // CAKE testnet
  },
  vault_usdc_stable_001: {
    name: "USDC Stable Yield",
    token: "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312", // USDC testnet
  },
  vault_btc_hodl_001: {
    name: "BTC Yield Wrapper",
    token: "0x7afd064DaE57eaFa1dD3E3f9B9c1B98d1a7C9E1F", // Mock WBTC
  },
  vault_high_risk_001: {
    name: "Exotic Yield (HIGH RISK)",
    token: "0x1111111254fb6c44bac0bed2854e76f90643097d", // Mock
  },
  vault_bnb_native_001: {
    name: "Native BNB Staking",
    token: "0x0000000000000000000000000000000000000000", // BNB native
  },
  vault_link_oracle_001: {
    name: "LINK Oracle Rewards",
    token: "0x84b9B910527Ad5C03A9Ca831909E21e236EA7b06", // LINK testnet
  },
};

async function deployVault(vaultId, config) {
  console.log(`\n📝 Deploying ${vaultId}...`);
  console.log(`   Name: ${config.name}`);
  console.log(`   Token: ${config.token}`);

  try {
    const YieldVault = await hre.ethers.getContractFactory("YieldVault");
    const vault = await YieldVault.deploy(vaultId, config.token);

    await vault.waitForDeployment();
    const address = await vault.getAddress();

    console.log(`   ✅ Deployed to: ${address}`);

    return {
      vaultId,
      name: config.name,
      address,
      token: config.token,
      network: "BNB Testnet",
      chainId: 97,
      deploymentTx: vault.deploymentTransaction()?.hash,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    console.error(`   ❌ Deployment failed:`, error.message);
    return null;
  }
}

async function main() {
  console.log("🚀 YieldVault Multi-Vault Deployment");
  console.log("====================================");
  console.log(`Network: BNB Testnet (chainId: 97)`);
  console.log(
    `RPC: ${process.env.RPC_URL || "https://data-seed-prebsc-1-b7a35f9.binance.org:8545"}`
  );

  const deployer = (await hre.ethers.getSigners())[0];
  console.log(`Deployer: ${deployer.address}\n`);

  // Check balance
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log(`💰 Deployer Balance: ${hre.ethers.formatEther(balance)} BNB\n`);

  if (balance === 0n) {
    console.error("❌ Insufficient balance! Get BNB from testnet faucet:");
    console.error("   https://testnet.binance.org/faucet-smart-chain");
    process.exit(1);
  }

  // Deploy contracts
  const deployments = [];

  for (const [vaultId, config] of Object.entries(VAULT_CONFIGS)) {
    const result = await deployVault(vaultId, config);
    if (result) {
      deployments.push(result);
    }
  }

  // Save deployment results
  const deploymentsFile = path.join(__dirname, "../deployments.json");
  fs.writeFileSync(deploymentsFile, JSON.stringify(deployments, null, 2));

  console.log("\n📊 Deployment Summary");
  console.log("====================");
  console.log(`Total Contracts Deployed: ${deployments.length}`);
  console.log(
    `Results saved to: ${deploymentsFile}\n`
  );

  console.log("📋 Deployed Contracts:");
  deployments.forEach((d) => {
    console.log(`   • ${d.vaultId}`);
    console.log(`     Address: ${d.address}`);
  });

  console.log("\n✨ Next Steps:");
  console.log("1. Verify contracts on BscScan:");
  console.log('   npm run verify <ADDRESS>');
  console.log("2. Test contract interactions:");
  console.log("   npm run test");
  console.log("3. Update agent configuration with contract addresses");

  return deployments;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
