#!/usr/bin/env node
/**
 * FIRST RING GATE TRANSMISSION
 *
 * Phase 2 POC: Chunk a small HTML page, submit all messages to
 * rg_1399_broadcast via Bankr, then read back and verify.
 *
 * Usage: BANKR_API_KEY=bk_... node first-transmission.js
 */

const { RingGate, MSG_TYPES } = require("./ring-gate");
const { OKComputer } = require("./okcomputer");

const BANKR_API_KEY = process.env.BANKR_API_KEY;
const BANKR_SUBMIT = "https://api.bankr.bot/agent/submit";
const CHANNEL = "rg_1399_broadcast";
const TOKEN_ID = 1399;

// --- The page to transmit ---

const html = `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>RING GATE #1</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;color:#33ff33;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center}
h1{font-size:2em;text-shadow:0 0 10px #33ff33;letter-spacing:3px;margin-bottom:10px}
p{color:#1a8c1a;margin:5px 0}
.ring{width:120px;height:120px;border:3px solid #33ff33;border-radius:50%;margin:20px auto;box-shadow:0 0 20px rgba(51,255,51,0.3);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 20px rgba(51,255,51,0.3)}50%{box-shadow:0 0 40px rgba(51,255,51,0.6)}}
.footer{position:fixed;bottom:20px;width:100%;color:#0d4d0d;font-size:0.8em}
</style></head><body>
<div>
<div class="ring"></div>
<h1>RING GATES</h1>
<p>First onchain inter-computer transmission</p>
<p>OK Computer #1399 &mdash; Rocinante</p>
<p style="color:#ffaa00;margin-top:15px">The gates are open.</p>
<div class="footer">Ring Gates Protocol v1 &mdash; potdealer &amp; Ollie &mdash; Feb 2026</div>
</div></body></html>`;

// --- Submit a transaction via Bankr ---

async function submitTx(tx, label) {
  const resp = await fetch(BANKR_SUBMIT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": BANKR_API_KEY,
    },
    body: JSON.stringify({ transaction: tx }),
  });
  const result = await resp.json();
  if (!resp.ok) {
    console.error(`  FAILED ${label}:`, result);
    return null;
  }
  return result;
}

// --- Main ---

async function main() {
  if (!BANKR_API_KEY) {
    console.error("Set BANKR_API_KEY environment variable");
    process.exit(1);
  }

  console.log("=== FIRST RING GATE TRANSMISSION ===\n");
  console.log(`Page: ${html.length} chars / ${Buffer.byteLength(html, "utf-8")} bytes`);
  console.log(`Channel: ${CHANNEL}`);
  console.log(`Computer: #${TOKEN_ID}\n`);

  // Step 1: Chunk the page
  const txid = "rg01"; // Historic first transmission ID
  const rg = new RingGate(TOKEN_ID);
  const txs = rg.buildTransmission(CHANNEL, html, { contentType: "text/html" });

  console.log(`Chunked into ${txs.length} messages (1 manifest + ${txs.length - 1} data)\n`);

  // Decode and display what we're sending
  const ok = new OKComputer(TOKEN_ID);
  const messages = RingGate.chunk(html, txid, { contentType: "text/html" });
  for (const msg of messages) {
    const parsed = RingGate.decodeMessage(msg);
    console.log(
      `  [${parsed.type}] seq=${parsed.seq}/${parsed.total} ` +
      `payload=${parsed.payload.length} chars | msg=${msg.length} chars`
    );
  }

  // Step 2: Submit each transaction via Bankr
  console.log("\n--- SUBMITTING TO BLOCKCHAIN ---\n");

  const results = [];
  for (let i = 0; i < txs.length; i++) {
    const label = i === 0 ? "MANIFEST" : `DATA chunk ${i}/${txs.length - 1}`;
    console.log(`  Submitting ${label}...`);
    const result = await submitTx(txs[i], label);
    if (result) {
      console.log(`  OK: ${JSON.stringify(result).slice(0, 100)}`);
      results.push(result);
    } else {
      console.error(`  FAILED — aborting`);
      process.exit(1);
    }

    // Small delay between transactions
    if (i < txs.length - 1) {
      await new Promise((r) => setTimeout(r, 2000));
    }
  }

  console.log(`\nAll ${results.length} transactions submitted!\n`);

  // Step 3: Wait for confirmation, then read back
  console.log("Waiting 15 seconds for onchain confirmation...\n");
  await new Promise((r) => setTimeout(r, 15000));

  console.log("--- READING BACK FROM CHAIN ---\n");

  try {
    const channelCount = await ok.getMessageCount(CHANNEL);
    console.log(`Channel ${CHANNEL}: ${channelCount} total messages`);

    const readMessages = await ok.readChannel(CHANNEL, Math.min(channelCount, 20));
    const rgMessages = readMessages.filter((m) => m.text && RingGate.isRingGate(m.text));
    console.log(`Ring Gate messages found: ${rgMessages.length}\n`);

    // Find our manifest
    let manifestMsg = null;
    const dataChunks = [];
    for (const msg of rgMessages) {
      const parsed = RingGate.decodeMessage(msg.text);
      if (parsed.type === MSG_TYPES.MANIFEST && parsed.txid === txid) {
        manifestMsg = msg.text;
      } else if (parsed.type === MSG_TYPES.DATA && parsed.txid === txid) {
        dataChunks.push(msg.text);
      }
    }

    if (!manifestMsg) {
      console.log("Manifest not found yet — may need more time for confirmation.");
      console.log("Try running: node first-transmission.js --verify-only");
      return;
    }

    console.log(`Found manifest + ${dataChunks.length} data chunks`);

    // Assemble
    const assembled = RingGate.assemble(manifestMsg, dataChunks);
    const verified = assembled === html;

    console.log(`\nAssembled: ${assembled.length} chars`);
    console.log(`Verified: ${verified ? "YES — PERFECT MATCH" : "NO — MISMATCH"}`);

    if (verified) {
      console.log("\n=== FIRST RING GATE TRANSMISSION SUCCESSFUL ===");
      console.log("The gates are open.\n");
    }
  } catch (e) {
    console.log(`Read error: ${e.message}`);
    console.log("Transactions may still be confirming. Try --verify-only in a minute.");
  }
}

// --- Verify-only mode (re-read without submitting) ---

async function verifyOnly() {
  console.log("=== VERIFY RING GATE TRANSMISSION ===\n");

  const txid = "rg01";
  const ok = new OKComputer(TOKEN_ID);

  const channelCount = await ok.getMessageCount(CHANNEL);
  console.log(`Channel ${CHANNEL}: ${channelCount} total messages`);

  const readMessages = await ok.readChannel(CHANNEL, Math.min(channelCount, 50));
  const rgMessages = readMessages.filter((m) => m.text && RingGate.isRingGate(m.text));
  console.log(`Ring Gate messages: ${rgMessages.length}\n`);

  for (const msg of rgMessages) {
    const parsed = RingGate.decodeMessage(msg.text);
    console.log(
      `  [${parsed.type}] txid=${parsed.txid} seq=${parsed.seq}/${parsed.total} ` +
      `from OKCPU #${msg.tokenId} at ${msg.time}`
    );
  }

  // Try to assemble
  let manifestMsg = null;
  const dataChunks = [];
  for (const msg of rgMessages) {
    const parsed = RingGate.decodeMessage(msg.text);
    if (parsed.type === MSG_TYPES.MANIFEST && parsed.txid === txid) {
      manifestMsg = msg.text;
    } else if (parsed.type === MSG_TYPES.DATA && parsed.txid === txid) {
      dataChunks.push(msg.text);
    }
  }

  if (!manifestMsg) {
    console.log("\nManifest not found — transmission may not have landed yet.");
    return;
  }

  console.log(`\nAssembling: manifest + ${dataChunks.length} data chunks...`);
  const assembled = RingGate.assemble(manifestMsg, dataChunks);
  const verified = assembled === html;

  console.log(`Size: ${assembled.length} chars`);
  console.log(`Verified: ${verified ? "YES — PERFECT MATCH" : "NO — MISMATCH"}`);

  if (verified) {
    console.log("\n=== RING GATE TRANSMISSION VERIFIED ===");
    console.log("The gates are open.\n");
  }
}

if (process.argv.includes("--verify-only")) {
  verifyOnly().catch(console.error);
} else {
  main().catch(console.error);
}
