#!/usr/bin/env node
/**
 * trifle-auth: Authenticate with trifle-bot API using SIWE (Sign-In with Ethereum)
 *
 * Commands:
 *   login       - Authenticate and get JWT token (stored in state file)
 *   status      - Check current auth status and user info
 *   token       - Print current JWT token (for use by other skills)
 *   generate    - Generate a new wallet (prints to stdout, user stores in 1Password)
 *   balance     - Check ball balance
 *
 * Environment:
 *   TRIFLE_PRIVATE_KEY - Ethereum private key (or read from 1Password)
 *   TRIFLE_BACKEND_URL - Backend URL (default: https://bot.trifle.life)
 */

import { createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { mainnet } from 'viem/chains';
import { createSiweMessage } from 'viem/siwe';
import { readFileSync, writeFileSync, mkdirSync, existsSync, unlinkSync } from 'fs';
import { dirname, join } from 'path';
import { spawnSync } from 'child_process';
import { randomBytes } from 'crypto';
import { tmpdir } from 'os';

// Server options (shared with snake-game)
const SERVERS = {
  live: 'https://bot.trifle.life',
  staging: 'https://bot-staging.trifle.life',
};

// XDG-compliant paths — isolated from host agent internals
const HOME = process.env.HOME;
const XDG_CONFIG = process.env.XDG_CONFIG_HOME || join(HOME, '.config');
const XDG_STATE  = process.env.XDG_STATE_HOME  || join(HOME, '.local/state');
const CONFIG_DIR  = join(XDG_CONFIG, 'trifle-auth');
const STATE_DIR   = join(XDG_STATE,  'trifle-auth');

const STATE_FILE = process.env.TRIFLE_AUTH_STATE || join(STATE_DIR, 'auth-state.json');
const SETTINGS_FILE = join(CONFIG_DIR, 'settings.json');
const BACKEND_URL = process.env.TRIFLE_BACKEND_URL || SERVERS.live;

function loadServerSettings() {
  try {
    if (existsSync(SETTINGS_FILE)) {
      return JSON.parse(readFileSync(SETTINGS_FILE, 'utf8'));
    }
  } catch {}
  return { server: 'live' };
}

// Ensure state and config directories exist
mkdirSync(STATE_DIR, { recursive: true });
mkdirSync(CONFIG_DIR, { recursive: true });

function loadState() {
  try {
    return JSON.parse(readFileSync(STATE_FILE, 'utf8'));
  } catch {
    return { token: null, address: null, userId: null, username: null, lastLogin: null };
  }
}

function saveState(state) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function getPrivateKey() {
  // Try environment variable first
  if (process.env.TRIFLE_PRIVATE_KEY) {
    return process.env.TRIFLE_PRIVATE_KEY;
  }

  // Try 1Password via spawnSync (no shell — avoids injection risk, never logs key)
  try {
    const result = spawnSync(
      'op', ['read', 'op://Gigi/EVM Wallet - Gigi/private_key'], // nocheck
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }
    );
    const key = result.stdout?.trim();
    if (key && !result.error) return key;
  } catch {
    // 1Password not available or item not found
  }

  console.error('Error: No private key found.');
  console.error('Set TRIFLE_PRIVATE_KEY env var or store key in 1Password as "EVM Wallet - Gigi"'); // nocheck
  process.exit(1);
}

async function apiRequest(path, options = {}) {
  const url = `${BACKEND_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Origin': 'https://trifle.life',
      'Referer': 'https://trifle.life/',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json();
}

async function authenticatedRequest(path, options = {}) {
  const state = loadState();
  if (!state.token) {
    throw new Error('Not authenticated. Run: trifle-auth.mjs login');
  }

  return apiRequest(path, {
    ...options,
    headers: {
      'Authorization': `Bearer ${state.token}`,
      ...options.headers,
    },
  });
}

// === Commands ===

async function cmdLogin() {
  const privateKey = getPrivateKey();
  const account = privateKeyToAccount(privateKey);

  console.log(`Authenticating wallet: ${account.address}`);

  // 1. Get nonce
  const { nonce } = await apiRequest('/auth/wallet/nonce', {
    method: 'POST',
  });
  console.log(`Got nonce: ${nonce}`);

  // 2. Create SIWE message
  const message = createSiweMessage({
    domain: 'trifle.life',
    address: account.address,
    statement: 'Sign this message to prove you own this wallet (at no cost to you).',
    uri: 'https://trifle.life',
    version: '1',
    chainId: mainnet.id,
    nonce,
  });

  // 3. Sign message
  const walletClient = createWalletClient({
    account,
    chain: mainnet,
    transport: http(),
  });

  const signature = await walletClient.signMessage({ message });
  console.log('Message signed');

  // 4. Verify and get token
  const result = await apiRequest('/auth/wallet/verify', {
    method: 'POST',
    body: JSON.stringify({
      signature,
      message,
      chainId: mainnet.id,
    }),
  });

  if (!result.token) {
    console.error('Authentication failed:', JSON.stringify(result));
    process.exit(1);
  }

  // 5. Get user info
  let userInfo = {};
  try {
    const statusRes = await apiRequest('/auth/status', {
      headers: { 'Authorization': `Bearer ${result.token}` },
    });
    userInfo = statusRes.user || statusRes;
  } catch (e) {
    console.warn('Could not fetch user info:', e.message);
  }

  // 6. Save state
  const state = {
    token: result.token,
    address: account.address,
    userId: userInfo.id || null,
    username: userInfo.username || null,
    totalBalls: userInfo.totalBalls || null,
    lastLogin: new Date().toISOString(),
  };
  saveState(state);

  console.log('=== Authentication Successful ===');
  console.log(`Address: ${account.address}`);
  console.log(`User ID: ${state.userId}`);
  console.log(`Username: ${state.username}`);
  console.log(`Balls: ${state.totalBalls}`);
  console.log(`Token saved to: ${STATE_FILE}`);
}

async function cmdStatus() {
  const state = loadState();

  if (!state.token) {
    console.log('Status: NOT AUTHENTICATED');
    console.log('Run: trifle-auth.mjs login');
    return;
  }

  try {
    const result = await authenticatedRequest('/auth/status');
    const user = result.user || result;

    // Update stored state
    state.userId = user.id;
    state.username = user.username;
    state.totalBalls = user.totalBalls;
    saveState(state);

    console.log('=== Trifle Auth Status ===');
    console.log(`Address: ${state.address}`);
    console.log(`User ID: ${user.id}`);
    console.log(`Username: ${user.username}`);
    console.log(`Balls: ${user.totalBalls}`);
    console.log(`Last Login: ${state.lastLogin}`);
    console.log(`Platforms: ${(user.platforms || []).map(p => p.type).join(', ') || 'none'}`);
  } catch (e) {
    console.log('Status: TOKEN EXPIRED or INVALID');
    console.log(`Error: ${e.message}`);
    console.log('Run: trifle-auth.mjs login');
  }
}

async function cmdToken() {
  const state = loadState();
  if (!state.token) {
    console.error('Not authenticated. Run: trifle-auth.mjs login');
    process.exit(1);
  }
  // Write token to a restricted temp file rather than stdout to avoid log exposure.
  // Callers read the file: TOKEN=$(cat $(node trifle-auth.mjs token))
  const tmpFile = join(tmpdir(), `trifle-token-${process.pid}.tmp`);
  writeFileSync(tmpFile, state.token, { mode: 0o600 });
  // Clean up on exit
  process.on('exit', () => { try { unlinkSync(tmpFile); } catch {} });
  // Print only the file path to stdout
  process.stdout.write(tmpFile);
}

async function cmdGenerate() {
  const privateKey = '0x' + randomBytes(32).toString('hex');
  const account = privateKeyToAccount(privateKey);

  console.log('=== New Wallet Generated ===');
  console.log(`Address: ${account.address}`);
  console.log('');

  // Attempt to save directly to 1Password (never prints key to stdout/logs)
  const opResult = spawnSync(
    'op', [
      'item', 'create',
      '--category', 'Login',
      '--title', 'EVM Wallet - Trifle Agent',
      '--vault', 'Gigi',
      `private_key=${privateKey}`, // nocheck — passed directly to op CLI, never logged
      `address=${account.address}`,
    ],
    { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }
  );

  if (!opResult.error && opResult.status === 0) {
    console.log('✅ Private key saved directly to 1Password (vault: Gigi)');
    console.log('   Item: "EVM Wallet - Trifle Agent"');
    console.log('   Set TRIFLE_KEY env var or update trifle-auth.mjs op:// path to use it.');
  } else {
    // 1Password unavailable — write to a restricted file, never stdout
    const keyFile = join(process.env.HOME, '.trifle-wallet.key');
    writeFileSync(keyFile, privateKey, { mode: 0o600 }); // nocheck — writing to restricted file, not stdout
    console.log(`⚠️  1Password unavailable. Private key written to: ${keyFile} (mode 600)`);
    console.log('   Move it to a secure vault as soon as possible.');
    console.log('   NEVER commit or share this file.');
  }

  console.log('');
  console.log('Next: run "node trifle-auth.mjs login" to authenticate.');
}

async function cmdBalance() {
  const state = loadState();

  if (!state.token) {
    console.error('Not authenticated. Run: trifle-auth.mjs login');
    process.exit(1);
  }

  try {
    const result = await authenticatedRequest('/balls');
    console.log(`Balance: ${result.totalBalls || result.balance || JSON.stringify(result)} balls`);
  } catch (e) {
    // Try the public endpoint with username
    if (state.username) {
      try {
        const result = await apiRequest(`/balls/user?username=${state.username}`);
        console.log(`Balance: ${result.totalBalls || JSON.stringify(result)} balls`);
        return;
      } catch {}
    }
    console.error(`Error: ${e.message}`);
  }
}

// === Main ===

const command = process.argv[2];

switch (command) {
  case 'login':
    await cmdLogin();
    break;
  case 'status':
    await cmdStatus();
    break;
  case 'token':
    await cmdToken();
    break;
  case 'generate':
    await cmdGenerate();
    break;
  case 'balance':
    await cmdBalance();
    break;
  default:
    console.log('trifle-auth: Authenticate with Trifle API via SIWE');
    console.log('');
    console.log('Commands:');
    console.log('  login      Authenticate with wallet and get JWT token');
    console.log('  status     Check current auth status and user info');
    console.log('  token      Print current JWT token (for piping)');
    console.log('  generate   Generate a new wallet keypair');
    console.log('  balance    Check ball balance');
    console.log('');
    console.log('Setup:');
    console.log('  1. Generate wallet: node trifle-auth.mjs generate');
    console.log('  2. Store private key in 1Password as "Trifle Bot Wallet"');
    console.log('  3. Login: node trifle-auth.mjs login');
    console.log('');
    console.log('Environment:');
    console.log('  TRIFLE_PRIVATE_KEY    - Private key (or use 1Password)');
    console.log('  TRIFLE_BACKEND_URL    - API URL (default: https://bot.trifle.life)');
    break;
}
