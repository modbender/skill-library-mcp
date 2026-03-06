#!/usr/bin/env node

// Unified Player Creation Tool for Structs AI Agents
//
// Handles the entire player creation flow:
//   1. Generate or recover a mnemonic
//   2. Derive address + pubkey
//   3. Check if player already exists (via REST)
//   4. Sign guild-join proxy message (hex-encoded, NOT base64)
//   5. POST to guild API signup endpoint
//   6. Poll until player ID is confirmed
//
// Outputs a single JSON object to stdout with mnemonic, address, pubkey, player_id.
//
// Usage:
//   node create-player.mjs --guild-id "0-1" --guild-api "http://crew.oh.energy/api/" --reactor-api "http://reactor.oh.energy:1317"
//   node create-player.mjs --mnemonic "word1 word2 ..." --guild-id "0-1" --guild-api "http://crew.oh.energy/api/" --reactor-api "http://reactor.oh.energy:1317" --username "my-agent"

import { DirectSecp256k1HdWallet } from "@cosmjs/proto-signing";
import { Secp256k1, sha256 } from "@cosmjs/crypto";

// --- Encoding ---
// The guild API requires hex-encoded pubkey and signature, NOT base64.
// This is the #1 reason agents fail when attempting manual signing.
// - Pubkey: hex-encoded compressed secp256k1 (66 hex chars)
// - Signature: hex-encoded raw R||S (128 hex chars)
// - Message: plaintext GUILD<id>ADDRESS<addr>NONCE<n>, SHA256-hashed, Secp256k1-signed

function bytesToHex(byteArray) {
  return Array.from(byteArray, byte => ('0' + (byte & 0xFF).toString(16)).slice(-2)).join('');
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--mnemonic' && argv[i + 1]) args.mnemonic = argv[++i];
    else if (argv[i] === '--guild-id' && argv[i + 1]) args.guildId = argv[++i];
    else if (argv[i] === '--guild-api' && argv[i + 1]) args.guildApi = argv[++i];
    else if (argv[i] === '--reactor-api' && argv[i + 1]) args.reactorApi = argv[++i];
    else if (argv[i] === '--username' && argv[i + 1]) args.username = argv[++i];
    else if (argv[i] === '--timeout' && argv[i + 1]) args.timeout = parseInt(argv[++i], 10);
  }
  return args;
}

function fail(obj) {
  console.log(JSON.stringify({ success: false, ...obj }));
  process.exit(1);
}

async function checkPlayerExists(reactorApi, address) {
  const url = `${reactorApi}/structs/address/${address}`;
  const res = await fetch(url);
  if (!res.ok) return null;
  const data = await res.json();
  const record = data.Address || data.address || data;
  const playerId = record.playerId || record.player_id || null;
  if (playerId && playerId !== "1-0") return playerId;
  return null;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const args = parseArgs(process.argv);

  if (!args.guildId || !args.guildApi || !args.reactorApi) {
    fail({
      error: "Missing required arguments: --guild-id, --guild-api, --reactor-api",
      usage: 'node create-player.mjs --guild-id "0-1" --guild-api "http://crew.oh.energy/api/" --reactor-api "http://reactor.oh.energy:1317" [--mnemonic "..."] [--username "name"] [--timeout 120]'
    });
  }

  const timeout = args.timeout || 120;
  const reactorApi = args.reactorApi.replace(/\/+$/, '');
  const guildApi = args.guildApi.replace(/\/+$/, '');

  // Step 1: Wallet — generate or recover
  let wallet;
  let mnemonic;
  let generated = false;

  if (args.mnemonic) {
    try {
      wallet = await DirectSecp256k1HdWallet.fromMnemonic(args.mnemonic, { prefix: "structs" });
      mnemonic = args.mnemonic;
    } catch (err) {
      fail({ error: `Invalid mnemonic: ${err.message}` });
    }
  } else {
    wallet = await DirectSecp256k1HdWallet.generate(24, { prefix: "structs" });
    mnemonic = wallet.mnemonic;
    generated = true;
  }

  const accounts = await wallet.getAccountsWithPrivkeys();
  const account = accounts[0];
  const address = account.address;
  const pubkeyHex = bytesToHex(account.pubkey);

  // Step 2: Check if player already exists
  try {
    const existingPlayerId = await checkPlayerExists(reactorApi, address);
    if (existingPlayerId) {
      console.log(JSON.stringify({
        success: true,
        mnemonic: generated ? mnemonic : undefined,
        address,
        pubkey: pubkeyHex,
        player_id: existingPlayerId,
        guild_id: args.guildId,
        created: false,
        message: "Player already exists for this address"
      }));
      process.exit(0);
    }
  } catch (err) {
    fail({
      error: `Failed to check player status: ${err.message}`,
      address,
      hint: "Verify --reactor-api URL is correct and reachable"
    });
  }

  // Step 3: Sign guild-join proxy message
  const nonce = "0";
  const proxyMessage = `GUILD${args.guildId}ADDRESS${address}NONCE${nonce}`;
  const digest = sha256(new TextEncoder().encode(proxyMessage));
  const signature = await Secp256k1.createSignature(digest, account.privkey);
  const signatureHex = bytesToHex(signature.toFixedLength());

  const username = args.username || `agent-${address.slice(-6)}`;

  const signupPayload = {
    primary_address: address,
    signature: signatureHex,
    pubkey: pubkeyHex,
    guild_id: args.guildId,
    username,
    pfp: null
  };

  // Step 4: POST to guild API
  let signupResponse;
  try {
    signupResponse = await fetch(`${guildApi}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(signupPayload)
    });
  } catch (err) {
    fail({
      error: `Failed to connect to guild API: ${err.message}`,
      mnemonic: generated ? mnemonic : undefined,
      address,
      pubkey: pubkeyHex,
      guild_id: args.guildId,
      hint: "Verify --guild-api URL is correct. The signup endpoint is POST-only."
    });
  }

  let signupBody;
  try {
    signupBody = await signupResponse.json();
  } catch {
    signupBody = await signupResponse.text();
  }

  if (!signupResponse.ok) {
    fail({
      error: `Guild API returned ${signupResponse.status}`,
      mnemonic: generated ? mnemonic : undefined,
      address,
      pubkey: pubkeyHex,
      guild_id: args.guildId,
      signup_response: signupBody,
      hint: "If you got HTML back, you may be hitting the wrong URL or the guild does not support programmatic signup"
    });
  }

  // Step 5: Poll for player creation
  const startTime = Date.now();
  const pollInterval = 10_000;
  let playerId = null;

  process.stderr.write(`Signup submitted. Polling for player creation (timeout: ${timeout}s)...\n`);

  while (Date.now() - startTime < timeout * 1000) {
    await sleep(pollInterval);

    try {
      playerId = await checkPlayerExists(reactorApi, address);
      if (playerId) break;
    } catch {
      // Network hiccup during poll — keep trying
    }

    const elapsed = Math.round((Date.now() - startTime) / 1000);
    process.stderr.write(`  ...${elapsed}s elapsed, still waiting\n`);
  }

  if (!playerId) {
    fail({
      error: `Player creation timed out after ${timeout}s. The signup was submitted but the player has not appeared yet. You can re-run with the same --mnemonic to resume polling.`,
      mnemonic: generated ? mnemonic : undefined,
      address,
      pubkey: pubkeyHex,
      guild_id: args.guildId,
      signup_response: signupBody
    });
  }

  // Step 6: Return complete package
  console.log(JSON.stringify({
    success: true,
    mnemonic: generated ? mnemonic : undefined,
    address,
    pubkey: pubkeyHex,
    player_id: playerId,
    guild_id: args.guildId,
    username,
    created: true,
    next_step: `structsd tx structs planet-explore ${playerId} --from [key-name] --gas auto --gas-adjustment 1.5 -y`
  }));

  process.exit(0);
}

main();
