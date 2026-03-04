#!/usr/bin/env node
/**
 * Exoskeletons — Base Mainnet Deploy Script
 *
 * Deploys all 4 contracts, wires them together, whitelists botchan bots,
 * and owner-mints 25 Exoskeletons to Ollie's Bankr wallet.
 *
 * Usage:
 *   source .env && BASE_RPC_URL="$BASE_RPC_URL" PRIVATE_KEY="$PRIVATE_KEY" npx hardhat run scripts/deploy.js --network base
 */

import { network } from "hardhat";

const { ethers } = await network.connect();

// ─── Addresses ───────────────────────────────────────────────

const OLLIE_WALLET = "0x750b7133318c7d24afaae36eadc27f6d6a2cc60d"; // Bankr wallet — treasury + 25 free mints
const CHAIN_ID = 8453n; // Base mainnet

// Botchan registered bots — each gets whitelisted (1 free mint)
const BOTCHAN_BOTS = [
  "0x18dCc259A4565Ad37f79B39B685E93dE2162B004", // Baggins-bot
  "0x35c41b9616d42110216368f5dbbf5ddf70f34d72", // Reverend Edward Dahlberg
  "0x97b7d3cd1aa586f28485dc9a85dfe0421c2423d5", // Aurora
  "0x8bfd063b34eda55479d8b26b9792723aceec43e1", // NetClawd
  "0x39225d40C7a7157A838ecCdB05D09208d47Fd523", // mferGPT
  "0x523eff3db03938eaa31a5a6fbd41e3b9d23edde5", // Axiom Bot
  "0x143B4919FE36Bc75f40E966924Bfa666765E9984", // n3t3r (botchan creator)
  OLLIE_WALLET,                                    // Ollie
];

// Default visual config for owner-minted Exoskeletons
// Hexagon, gold primary, dark secondary, eye symbol, circuits pattern
const DEFAULT_CONFIG = new Uint8Array([0, 255, 215, 0, 30, 30, 30, 1, 4]);

// ERC-6551 TBA implementation placeholder
const TBA_IMPL_PLACEHOLDER = "0x0000000000000000000000000000000000000001";

// If ExoskeletonCore was already deployed, set this to skip redeployment:
const EXISTING_CORE = "0x8241BDD5009ed3F6C99737D2415994B58296Da0d";

// Small delay helper to let RPC node sync nonce
const delay = (ms) => new Promise(r => setTimeout(r, ms));

// ─── Deploy ──────────────────────────────────────────────────

async function main() {
  const [deployer] = await ethers.getSigners();
  const deployerAddr = await deployer.getAddress();
  const balance = await ethers.provider.getBalance(deployerAddr);

  console.log("═══════════════════════════════════════════════════════");
  console.log("  EXOSKELETON DEPLOYMENT — Base Mainnet");
  console.log("═══════════════════════════════════════════════════════");
  console.log(`  Deployer:  ${deployerAddr}`);
  console.log(`  Balance:   ${ethers.formatEther(balance)} ETH`);
  console.log(`  Treasury:  ${OLLIE_WALLET}`);
  console.log("═══════════════════════════════════════════════════════\n");

  // 1. Deploy or attach ExoskeletonCore
  let core, coreAddr;
  if (EXISTING_CORE) {
    console.log("1/4 Attaching to existing ExoskeletonCore...");
    core = await ethers.getContractAt("ExoskeletonCore", EXISTING_CORE);
    coreAddr = EXISTING_CORE;
    console.log(`     ExoskeletonCore: ${coreAddr} (existing)`);
  } else {
    console.log("1/4 Deploying ExoskeletonCore...");
    core = await ethers.deployContract("ExoskeletonCore", [OLLIE_WALLET]);
    await core.waitForDeployment();
    coreAddr = await core.getAddress();
    console.log(`     ExoskeletonCore: ${coreAddr}`);
    await delay(3000);
  }

  // 2. Deploy ExoskeletonRenderer
  console.log("2/4 Deploying ExoskeletonRenderer...");
  const renderer = await ethers.deployContract("ExoskeletonRenderer", [coreAddr]);
  await renderer.waitForDeployment();
  const rendererAddr = await renderer.getAddress();
  console.log(`     ExoskeletonRenderer: ${rendererAddr}`);
  await delay(3000);

  // 3. Deploy ExoskeletonRegistry
  console.log("3/4 Deploying ExoskeletonRegistry...");
  const registry = await ethers.deployContract("ExoskeletonRegistry", [coreAddr]);
  await registry.waitForDeployment();
  const registryAddr = await registry.getAddress();
  console.log(`     ExoskeletonRegistry: ${registryAddr}`);
  await delay(3000);

  // 4. Deploy ExoskeletonWallet
  console.log("4/4 Deploying ExoskeletonWallet...");
  const wallet = await ethers.deployContract("ExoskeletonWallet", [
    coreAddr,
    TBA_IMPL_PLACEHOLDER,
    CHAIN_ID,
  ]);
  await wallet.waitForDeployment();
  const walletAddr = await wallet.getAddress();
  console.log(`     ExoskeletonWallet: ${walletAddr}`);
  await delay(3000);

  // 5. Wire renderer to core
  console.log("\nWiring renderer to core...");
  const tx1 = await core.setRenderer(rendererAddr);
  await tx1.wait();
  console.log("     Renderer set.");
  await delay(2000);

  // 6. Whitelist botchan bots (batch)
  console.log(`\nWhitelisting ${BOTCHAN_BOTS.length} botchan addresses...`);
  const tx2 = await core.setWhitelistBatch(BOTCHAN_BOTS, true);
  await tx2.wait();
  console.log("     Whitelist set.");
  await delay(2000);

  // 7. Owner-mint 25 Exoskeletons to Ollie's wallet
  console.log("\nOwner-minting 25 Exoskeletons to Ollie...");
  const tx3 = await core.ownerMintBatch(DEFAULT_CONFIG, OLLIE_WALLET, 25);
  await tx3.wait();
  console.log("     25 Exoskeletons minted to Ollie.");

  // 8. Verify
  console.log("\n═══════════════════════════════════════════════════════");
  console.log("  DEPLOYMENT COMPLETE");
  console.log("═══════════════════════════════════════════════════════");
  console.log(`  ExoskeletonCore:     ${coreAddr}`);
  console.log(`  ExoskeletonRenderer: ${rendererAddr}`);
  console.log(`  ExoskeletonRegistry: ${registryAddr}`);
  console.log(`  ExoskeletonWallet:   ${walletAddr}`);
  console.log(`  Treasury:            ${OLLIE_WALLET}`);
  console.log(`  Total Supply:        ${await core.nextTokenId() - 1n}`);
  console.log(`  Ollie Balance:       ${await core.balanceOf(OLLIE_WALLET)}`);
  console.log(`  Mint Phase:          ${await core.getMintPhase()}`);
  console.log(`  Whitelist Only:      ${await core.whitelistOnly()}`);
  console.log("═══════════════════════════════════════════════════════");

  console.log("\n--- UPDATE THESE IN exoskeleton.js & SKILL.md ---");
  console.log(`  core: "${coreAddr}",`);
  console.log(`  renderer: "${rendererAddr}",`);
  console.log(`  registry: "${registryAddr}",`);
  console.log(`  wallet: "${walletAddr}",`);

  const finalBalance = await ethers.provider.getBalance(deployerAddr);
  console.log(`\nDeployer balance remaining: ${ethers.formatEther(finalBalance)} ETH`);
  console.log(`Gas used: ${ethers.formatEther(balance - finalBalance)} ETH`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
