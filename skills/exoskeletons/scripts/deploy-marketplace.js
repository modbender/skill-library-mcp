#!/usr/bin/env node
/**
 * Exoskeletons Module Marketplace — Base Mainnet Deploy Script
 *
 * Deploys ModuleMarketplace contract, wired to existing ExoskeletonCore.
 *
 * Usage:
 *   source .env && BASE_RPC_URL="$BASE_RPC_URL" PRIVATE_KEY="$PRIVATE_KEY" npx hardhat run scripts/deploy-marketplace.js --network base
 */

import { network } from "hardhat";

const { ethers } = await network.connect();

// ─── Addresses ───────────────────────────────────────────────

const CORE_ADDRESS = "0x8241BDD5009ed3F6C99737D2415994B58296Da0d";
const TREASURY = "0x750b7133318c7d24afaae36eadc27f6d6a2cc60d"; // Bankr wallet

// ─── Deploy ──────────────────────────────────────────────────

async function main() {
  const [deployer] = await ethers.getSigners();
  const deployerAddr = await deployer.getAddress();
  const balance = await ethers.provider.getBalance(deployerAddr);

  console.log("═══════════════════════════════════════════════════════");
  console.log("  MODULE MARKETPLACE DEPLOYMENT — Base Mainnet");
  console.log("═══════════════════════════════════════════════════════");
  console.log(`  Deployer:  ${deployerAddr}`);
  console.log(`  Balance:   ${ethers.formatEther(balance)} ETH`);
  console.log(`  Core:      ${CORE_ADDRESS}`);
  console.log(`  Treasury:  ${TREASURY}`);
  console.log("═══════════════════════════════════════════════════════\n");

  console.log("Deploying ModuleMarketplace...");
  const marketplace = await ethers.deployContract("ModuleMarketplace", [
    CORE_ADDRESS,
    TREASURY,
  ]);
  await marketplace.waitForDeployment();
  const marketplaceAddr = await marketplace.getAddress();

  console.log("\n═══════════════════════════════════════════════════════");
  console.log("  DEPLOYMENT COMPLETE");
  console.log("═══════════════════════════════════════════════════════");
  console.log(`  ModuleMarketplace: ${marketplaceAddr}`);
  console.log(`  Core (ref):        ${CORE_ADDRESS}`);
  console.log(`  Treasury:          ${TREASURY}`);
  console.log(`  Platform Fee:      4.20% (420 bps)`);
  console.log(`  Listing Fee:       0.001 ETH`);
  console.log("═══════════════════════════════════════════════════════");

  console.log("\n--- UPDATE THESE IN exoskeleton.js & SKILL.md ---");
  console.log(`  marketplace: "${marketplaceAddr}",`);

  const finalBalance = await ethers.provider.getBalance(deployerAddr);
  console.log(`\nDeployer balance remaining: ${ethers.formatEther(finalBalance)} ETH`);
  console.log(`Gas used: ${ethers.formatEther(balance - finalBalance)} ETH`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
