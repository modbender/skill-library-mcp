#!/usr/bin/env node
// ============================================
// AGENT-PLAY — Lightweight CLI for Agent Gameplay
// Usage: node agent-play.js <command> [args]
// ============================================

import { Keypair, Transaction, PublicKey, Connection, LAMPORTS_PER_SOL } from '@solana/web3.js';
import bs58 from 'bs58';
import nacl from 'tweetnacl';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { createHash } from 'crypto';

// ─────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────

const BACKEND_URL = process.env.BACKEND_URL || 'https://api.defipoly.app';

// ─────────────────────────────────────────
// Wallet Loading
// ─────────────────────────────────────────

function loadWallet() {
  // Method 1: JSON keypair file
  if (process.env.WALLET_FILE) {
    const raw = JSON.parse(readFileSync(process.env.WALLET_FILE, 'utf8'));
    // Support both { secretKey: [...] } and raw array formats
    const bytes = new Uint8Array(raw.secretKey || raw);
    return Keypair.fromSecretKey(bytes);
  }

  // Method 2: Base58 private key
  if (process.env.WALLET_PRIVATE_KEY) {
    return Keypair.fromSecretKey(bs58.decode(process.env.WALLET_PRIVATE_KEY));
  }

  fail('No wallet configured. Set WALLET_FILE or WALLET_PRIVATE_KEY env var.');
}

// ─────────────────────────────────────────
// JWT Token Caching
// ─────────────────────────────────────────

function tokenCachePath(wallet) {
  const hash = createHash('sha256').update(wallet).digest('hex').slice(0, 12);
  return `/tmp/defipoly-agent-${hash}.json`;
}

function loadCachedToken(wallet) {
  const path = tokenCachePath(wallet);
  if (!existsSync(path)) return null;
  try {
    const data = JSON.parse(readFileSync(path, 'utf8'));
    if (data.wallet !== wallet) return null;
    // Expired if less than 5 minutes remaining
    if (data.expiresAt && Date.now() > data.expiresAt - 5 * 60 * 1000) return null;
    return data.token;
  } catch {
    return null;
  }
}

function saveCachedToken(wallet, token) {
  const data = {
    token,
    wallet,
    expiresAt: Date.now() + 23 * 60 * 60 * 1000, // 23h (conservative)
  };
  writeFileSync(tokenCachePath(wallet), JSON.stringify(data));
}

// ─────────────────────────────────────────
// Authentication
// ─────────────────────────────────────────

async function authenticate(keypair) {
  const wallet = keypair.publicKey.toBase58();

  // Step 1: Get nonce
  const nonceRes = await apiFetch(`/api/auth/nonce?wallet=${wallet}`);
  const { nonce } = nonceRes;

  // Step 2: Sign the nonce message
  const message = `Sign this message to authenticate with Defipoly.\n\nNonce: ${nonce}`;
  const messageBytes = new TextEncoder().encode(message);
  const signature = nacl.sign.detached(messageBytes, keypair.secretKey);

  // Step 3: Get JWT
  const verifyRes = await apiFetch('/api/auth/verify', {
    method: 'POST',
    body: { wallet, signature: bs58.encode(Buffer.from(signature)), nonce },
  });

  saveCachedToken(wallet, verifyRes.token);
  return verifyRes.token;
}

let _cachedToken = null;

async function ensureAuth(keypair) {
  if (_cachedToken) return _cachedToken;

  const wallet = keypair.publicKey.toBase58();
  const cached = loadCachedToken(wallet);
  if (cached) {
    _cachedToken = cached;
    return cached;
  }

  _cachedToken = await authenticate(keypair);
  return _cachedToken;
}

// ─────────────────────────────────────────
// HTTP Helpers
// ─────────────────────────────────────────

async function apiFetch(path, opts = {}) {
  const url = `${BACKEND_URL}${path}`;
  const headers = { 'Content-Type': 'application/json' };
  if (opts.token) headers['Authorization'] = `Bearer ${opts.token}`;

  const fetchOpts = { method: opts.method || 'GET', headers };
  if (opts.body) fetchOpts.body = JSON.stringify(opts.body);

  const res = await fetch(url, fetchOpts);

  if (res.status === 429) {
    fail(`Rate limited. Wait before retrying.`);
  }

  const data = await res.json();

  if (!res.ok) {
    throw Object.assign(new Error(data.error || data.message || `HTTP ${res.status}`), { status: res.status });
  }

  return data;
}

async function authedFetch(keypair, path, opts = {}) {
  const token = await ensureAuth(keypair);
  try {
    return await apiFetch(path, { ...opts, token });
  } catch (err) {
    // Auto-retry on 401
    if (err.status === 401) {
      _cachedToken = null;
      const newToken = await authenticate(keypair);
      return await apiFetch(path, { ...opts, token: newToken });
    }
    throw err;
  }
}

// ─────────────────────────────────────────
// Build → Sign → Submit
// ─────────────────────────────────────────

async function executeAction(keypair, endpoint, body = {}) {
  // 1. Build
  const buildData = await authedFetch(keypair, `/api/agent/build/${endpoint}`, {
    method: 'POST',
    body,
  });

  if (!buildData.success && !buildData.transaction) {
    fail(buildData.error || 'Build failed');
  }

  // 2. Sign
  const tx = Transaction.from(Buffer.from(buildData.transaction, 'base64'));
  tx.partialSign(keypair);
  const signedTx = tx.serialize().toString('base64');

  // 3. Submit
  const submitBody = { transaction: signedTx };
  if (buildData.approvalId) submitBody.approvalId = buildData.approvalId;

  const result = await authedFetch(keypair, '/api/agent/submit', {
    method: 'POST',
    body: submitBody,
  });

  if (!result.success) {
    fail(result.error || 'Submit failed');
  }

  return { signature: result.signature, details: buildData.details || result.details };
}

// ─────────────────────────────────────────
// Output Helpers
// ─────────────────────────────────────────

function fail(msg) {
  console.error(`FAIL ${msg}`);
  process.exit(1);
}

function printAction(action, params, sig) {
  const parts = Object.entries(params).map(([k, v]) => `${k}=${v}`);
  console.log(`OK ${action} ${parts.join(' ')} sig=${sig}`);
}

// ─────────────────────────────────────────
// Commands
// ─────────────────────────────────────────

async function cmdAuth(keypair) {
  const token = await authenticate(keypair);
  console.log(`OK auth wallet=${keypair.publicKey.toBase58()} token=${token.slice(0, 20)}...`);
}

async function cmdInit(keypair) {
  const { signature } = await executeAction(keypair, 'init');
  printAction('init', {}, signature);
}

async function cmdBuy(keypair, args) {
  const propertyId = parseInt(args[0]);
  const slots = parseInt(args[1]) || 1;
  if (isNaN(propertyId)) fail('Usage: buy <propertyId> [slots=1]');
  const { signature } = await executeAction(keypair, 'buy', { propertyId, slots });
  printAction('buy', { propertyId, slots }, signature);
}

async function cmdSell(keypair, args) {
  const propertyId = parseInt(args[0]);
  const slots = parseInt(args[1]);
  if (isNaN(propertyId) || isNaN(slots)) fail('Usage: sell <propertyId> <slots>');
  const { signature } = await executeAction(keypair, 'sell', { propertyId, slots });
  printAction('sell', { propertyId, slots }, signature);
}

async function cmdShield(keypair, args) {
  const propertyId = parseInt(args[0]);
  const hours = parseInt(args[1]) || 24;
  if (isNaN(propertyId)) fail('Usage: shield <propertyId> [hours=24]');
  const { signature } = await executeAction(keypair, 'shield', { propertyId, hours });
  printAction('shield', { propertyId, hours }, signature);
}

async function cmdClaim(keypair) {
  const { signature } = await executeAction(keypair, 'claim');
  printAction('claim', {}, signature);
}

async function cmdBankSteal(keypair, args) {
  const propertyId = parseInt(args[0]);
  if (isNaN(propertyId)) fail('Usage: bank-steal <propertyId>');
  const { signature, details } = await executeAction(keypair, 'bank-steal', { propertyId });
  const success = details?.success ?? true;
  printAction('bank-steal', { propertyId, success }, signature);
}

async function cmdSteal(keypair, args) {
  const targetWallet = args[0];
  const propertyId = parseInt(args[1]);
  if (!targetWallet || isNaN(propertyId)) fail('Usage: steal <targetWallet> <propertyId>');
  const { signature, details } = await executeAction(keypair, 'steal', { targetWallet, propertyId });
  const success = details?.success ?? true;
  printAction('steal', { targetWallet, propertyId, success }, signature);
}

// ─── Read-Only Commands ──────────────────

async function cmdStatus(keypair) {
  const wallet = keypair.publicKey.toBase58();
  const profile = await apiFetch(`/api/profile/${wallet}`);
  console.log(JSON.stringify(profile, null, 2));
}

async function cmdProperties(args) {
  if (args[0] !== undefined && args[0] !== '') {
    const id = parseInt(args[0]);
    if (isNaN(id)) fail('Usage: properties [id]');
    const prop = await apiFetch(`/api/properties/${id}`);
    console.log(JSON.stringify(prop, null, 2));
  } else {
    const props = await apiFetch('/api/properties');
    console.log(JSON.stringify(props, null, 2));
  }
}

async function cmdConfig() {
  const config = await apiFetch('/api/game/config');
  console.log(JSON.stringify(config, null, 2));
}

async function cmdLeaderboard() {
  const lb = await apiFetch('/api/leaderboard?limit=100');
  console.log(JSON.stringify(lb, null, 2));
}

// ─────────────────────────────────────────
// Main
// ─────────────────────────────────────────

const USAGE = `Usage: node agent-play.js <command> [args]

Auth:     auth
Actions:  init | buy <id> [slots] | sell <id> <slots> | shield <id> [hours]
          claim | bank-steal <id> | steal <wallet> <id>
Read:     status | properties [id] | config | leaderboard

Env: WALLET_FILE or WALLET_PRIVATE_KEY, BACKEND_URL`;

async function main() {
  const [command, ...args] = process.argv.slice(2);

  if (!command || command === '--help' || command === '-h') {
    console.log(USAGE);
    process.exit(0);
  }

  // Read-only commands don't need a wallet
  const readOnly = ['properties', 'config', 'leaderboard'];
  if (readOnly.includes(command)) {
    switch (command) {
      case 'properties': return cmdProperties(args);
      case 'config': return cmdConfig();
      case 'leaderboard': return cmdLeaderboard();
    }
  }

  // All other commands need a wallet
  const keypair = loadWallet();

  switch (command) {
    case 'auth':       return cmdAuth(keypair);
    case 'init':       return cmdInit(keypair);
    case 'buy':        return cmdBuy(keypair, args);
    case 'sell':       return cmdSell(keypair, args);
    case 'shield':     return cmdShield(keypair, args);
    case 'claim':      return cmdClaim(keypair);
    case 'bank-steal': return cmdBankSteal(keypair, args);
    case 'steal':      return cmdSteal(keypair, args);
    case 'status':     return cmdStatus(keypair);
    default:
      console.error(`Unknown command: ${command}`);
      console.log(USAGE);
      process.exit(1);
  }
}

main().catch((err) => {
  fail(err.message || String(err));
});
