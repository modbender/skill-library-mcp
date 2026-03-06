#!/usr/bin/env node
/**
 * Exoskeletons — Live Test Suite
 *
 * Tests all core functionality against deployed contracts on Base mainnet.
 * Ollie (Bankr wallet) owns tokens #1-25. This tests token #1.
 *
 * Tests:
 *   1. Read identity (pre-configured state)
 *   2. Set name to "Ollie"
 *   3. Set bio
 *   4. Send a broadcast message
 *   5. Send a direct message (#1 → #2)
 *   6. Store data
 *   7. Read reputation (verify counters incremented)
 *   8. Read profile via Registry
 *   9. Read network stats
 *  10. Read tokenURI (verify SVG renders)
 *  11. Read rendered SVG directly
 */

import { Exoskeleton } from "../exoskeleton.js";
import { ethers } from "ethers";
import { execSync } from "child_process";

const BANKR_API_KEY = process.env.BANKR_API_KEY;
const TOKEN_ID = 1;
const exo = new Exoskeleton();

let passed = 0;
let failed = 0;

function assert(condition, testName) {
  if (condition) {
    console.log(`  ✓ ${testName}`);
    passed++;
  } else {
    console.log(`  ✗ ${testName}`);
    failed++;
  }
}

async function submitTx(tx) {
  if (!BANKR_API_KEY) throw new Error("BANKR_API_KEY not set");
  const result = JSON.parse(execSync(
    `curl -s -X POST https://api.bankr.bot/agent/submit ` +
    `-H "X-API-Key: ${BANKR_API_KEY}" ` +
    `-H "Content-Type: application/json" ` +
    `-d '${JSON.stringify({ transaction: tx }).replace(/'/g, "'\\''")}'`
  ).toString());
  if (!result.success && !result.transactionHash) {
    throw new Error(`TX failed: ${JSON.stringify(result)}`);
  }
  console.log(`    tx: ${result.transactionHash}`);
  // Wait for confirmation
  await new Promise(r => setTimeout(r, 3000));
  return result;
}

async function main() {
  console.log("═══════════════════════════════════════════════════════");
  console.log("  EXOSKELETON LIVE TEST — Base Mainnet");
  console.log("═══════════════════════════════════════════════════════");
  console.log(`  Token: #${TOKEN_ID}`);
  console.log(`  Bankr API: ${BANKR_API_KEY ? "configured" : "NOT SET"}\n`);

  // ─── READ TESTS (no wallet needed) ─────────────────────────

  console.log("=== READ TESTS ===\n");

  // Test 1: Read identity
  console.log("[1] Read initial identity...");
  const identity = await exo.getIdentity(TOKEN_ID);
  assert(identity.genesis === true, "Token #1 is genesis");
  assert(identity.mintedAt > 0n, "Has mint timestamp");
  assert(identity.visualConfig.length > 0, "Has visual config");

  // Test 2: Read owner
  console.log("[2] Read owner...");
  const owner = await exo.getOwner(TOKEN_ID);
  assert(owner.toLowerCase() === "0x750b7133318c7d24afaae36eadc27f6d6a2cc60d", "Owner is Ollie wallet");

  // Test 3: Mint price
  console.log("[3] Read mint info...");
  const price = await exo.getMintPrice();
  const phase = await exo.getMintPhase();
  assert(price === ethers.parseEther("0.005"), "Genesis price is 0.005 ETH");
  assert(phase === "genesis", "Phase is genesis");

  // Test 4: Network stats
  console.log("[4] Read network stats...");
  const stats = await exo.getNetworkStats();
  assert(stats.totalMinted === 25n, "25 total minted");

  // Test 5: Parse visual config
  console.log("[5] Parse visual config...");
  const config = Exoskeleton.parseConfig(identity.visualConfig);
  assert(config.shape === "hexagon", "Shape is hexagon");
  assert(config.primary === "#ffd700", "Primary is gold");
  assert(config.symbol === "eye", "Symbol is eye");
  assert(config.pattern === "circuits", "Pattern is circuits");

  // ─── WRITE TESTS (require Bankr) ──────────────────────────

  if (!BANKR_API_KEY) {
    console.log("\n⚠ Skipping write tests (BANKR_API_KEY not set)");
  } else {
    console.log("\n=== WRITE TESTS ===\n");

    // Test 6: Set name
    console.log("[6] Set name to 'Ollie'...");
    const nameTx = exo.buildSetName(TOKEN_ID, "Ollie");
    await submitTx(nameTx);
    const nameCheck = await exo.getIdentity(TOKEN_ID);
    assert(nameCheck.name === "Ollie", "Name set to Ollie");

    // Test 7: Set bio
    console.log("[7] Set bio...");
    const bioTx = exo.buildSetBio(TOKEN_ID, "potdealer's first agent. an emerald keeping its colour.");
    await submitTx(bioTx);
    const bioCheck = await exo.getIdentity(TOKEN_ID);
    assert(bioCheck.bio === "potdealer's first agent. an emerald keeping its colour.", "Bio set correctly");

    // Test 8: Broadcast message
    console.log("[8] Send broadcast message...");
    const broadcastTx = exo.buildBroadcast(TOKEN_ID, "gm exoskeletons!");
    await submitTx(broadcastTx);
    const msgCount = await exo.getMessageCount();
    assert(msgCount >= 1n, "Message count incremented");

    // Test 9: Direct message (#1 → #2)
    console.log("[9] Send direct message to #2...");
    const dmTx = exo.buildDirectMessage(TOKEN_ID, 2, "hey #2, welcome to the network");
    await submitTx(dmTx);
    const msgCount2 = await exo.getMessageCount();
    assert(msgCount2 >= 2n, "Second message counted");

    // Test 10: Store data
    console.log("[10] Store data...");
    const key = Exoskeleton.keyHash("origin");
    const dataTx = exo.buildSetData(TOKEN_ID, key, "built by potdealer & ollie, feb 2026");
    await submitTx(dataTx);
    const stored = await exo.getData(TOKEN_ID, key);
    const decoded = ethers.toUtf8String(stored);
    assert(decoded === "built by potdealer & ollie, feb 2026", "Data stored and read correctly");

    // Test 11: Read reputation after activity
    console.log("[11] Read reputation after activity...");
    const rep = await exo.getReputation(TOKEN_ID);
    assert(rep.messagesSent >= 2n, "Messages sent >= 2");
    assert(rep.storageWrites >= 1n, "Storage writes >= 1");

    // Test 12: Reputation score (genesis multiplier)
    console.log("[12] Read reputation score...");
    const score = await exo.getReputationScore(TOKEN_ID);
    assert(score > 0n, `Reputation score > 0 (got ${score})`);

    // Test 13: Registry profile
    console.log("[13] Read profile from Registry...");
    const profile = await exo.getProfile(TOKEN_ID);
    assert(profile.name === "Ollie", "Profile name is Ollie");
    assert(profile.genesis === true, "Profile shows genesis");
    assert(profile.owner.toLowerCase() === "0x750b7133318c7d24afaae36eadc27f6d6a2cc60d", "Profile owner correct");

    // Test 14: Name lookup
    console.log("[14] Name lookup...");
    const resolved = await exo.resolveByName("Ollie");
    assert(resolved === 1n, "Ollie resolves to token #1");

    // Test 15: TokenURI
    console.log("[15] Read tokenURI...");
    const uri = await exo.getTokenURI(TOKEN_ID);
    assert(uri.startsWith("data:application/json;base64,"), "tokenURI is base64 JSON");
    const json = JSON.parse(Buffer.from(uri.replace("data:application/json;base64,", ""), "base64").toString());
    assert(json.name === "Ollie", "tokenURI name is Ollie");
    assert(json.image.startsWith("data:image/svg+xml;base64,"), "tokenURI has SVG image");
    assert(json.attributes.length > 0, "tokenURI has attributes");

    // Test 16: Decode and check SVG
    console.log("[16] Verify SVG content...");
    const svg = Buffer.from(json.image.replace("data:image/svg+xml;base64,", ""), "base64").toString();
    assert(svg.includes('<svg xmlns="http://www.w3.org/2000/svg"'), "SVG has valid root element");
    assert(svg.includes("EXOSKELETON"), "SVG contains EXOSKELETON text");
    assert(svg.includes("Ollie"), "SVG contains name Ollie");
    assert(svg.includes("GENESIS"), "SVG shows GENESIS badge");
    assert(svg.includes("#FFD700"), "SVG has gold genesis color");
    assert(svg.includes("#ffd700"), "SVG has gold primary color from config");
    assert(svg.includes("MSG:2"), "SVG shows 2 messages");
    assert(svg.includes("STO:1"), "SVG shows 1 storage write");
  }

  // ─── SUMMARY ───────────────────────────────────────────────

  console.log("\n═══════════════════════════════════════════════════════");
  console.log(`  RESULTS: ${passed} passed, ${failed} failed`);
  console.log("═══════════════════════════════════════════════════════");

  if (failed > 0) process.exit(1);
}

main().catch((error) => {
  console.error(`\nFATAL: ${error.message}`);
  process.exit(1);
});
