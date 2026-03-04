#!/usr/bin/env node
/**
 * NadMail Registration Script
 * Registers an AI agent for a @nadmail.ai email address
 *
 * Usage:
 *   node register.js [--handle yourname] [--wallet /path/to/key]
 *
 * Private key sources (in order of priority):
 *   1. NADMAIL_PRIVATE_KEY environment variable (recommended)
 *   2. --wallet argument specifying path to your key file
 *   3. ~/.nadmail/private-key.enc (encrypted, managed by setup.js)
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const readline = require('readline');

const API_BASE = 'https://api.nadmail.ai';
const CONFIG_DIR = path.join(process.env.HOME, '.nadmail');
const TOKEN_FILE = path.join(CONFIG_DIR, 'token.json');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');

// Max wallet file size (1KB — private keys are tiny)
const MAX_WALLET_FILE_SIZE = 1024;

function getArg(name) {
  const args = process.argv.slice(2);
  const idx = args.indexOf(name);
  if (idx !== -1 && args[idx + 1]) {
    return args[idx + 1];
  }
  return null;
}

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function logAudit(action, details = {}) {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
    }
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      wallet: details.wallet ? `${details.wallet.slice(0, 6)}...${details.wallet.slice(-4)}` : null,
      success: details.success ?? true,
      error: details.error,
    };
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {
    // Silently ignore audit errors
  }
}

function decryptPrivateKey(encryptedData, password) {
  const key = crypto.scryptSync(password, Buffer.from(encryptedData.salt, 'hex'), 32);
  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    key,
    Buffer.from(encryptedData.iv, 'hex')
  );
  decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));

  let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

/**
 * Validate a wallet file path for security
 */
function validateWalletPath(walletPath) {
  const resolved = path.resolve(walletPath);

  // Must be under home directory (prevent reading system files)
  const home = process.env.HOME;
  if (!resolved.startsWith(home)) {
    console.error(`Security: Wallet path must be under your home directory (${home})`);
    process.exit(1);
  }

  // Check for suspicious path components
  if (walletPath.includes('..') || walletPath.includes('\0')) {
    console.error('Security: Invalid path — must not contain ".." or null bytes');
    process.exit(1);
  }

  // Check file size
  try {
    const stat = fs.statSync(resolved);
    if (stat.size > MAX_WALLET_FILE_SIZE) {
      console.error(`Security: Wallet file too large (${stat.size} bytes, max ${MAX_WALLET_FILE_SIZE})`);
      process.exit(1);
    }
    if (!stat.isFile()) {
      console.error('Security: Path must point to a regular file');
      process.exit(1);
    }
  } catch (e) {
    // File doesn't exist — let the caller handle it
  }

  return resolved;
}

async function getPrivateKey() {
  // 1. Environment variable (highest priority, most secure)
  if (process.env.NADMAIL_PRIVATE_KEY) {
    console.log('Using NADMAIL_PRIVATE_KEY environment variable');
    const key = process.env.NADMAIL_PRIVATE_KEY.trim();
    if (!/^0x[a-fA-F0-9]{64}$/.test(key)) {
      console.error('Error: NADMAIL_PRIVATE_KEY must be a valid 0x-prefixed hex private key (66 chars)');
      process.exit(1);
    }
    return key;
  }

  // 2. --wallet argument (with path validation)
  const walletArg = getArg('--wallet');
  if (walletArg) {
    const walletPath = validateWalletPath(walletArg.replace(/^~/, process.env.HOME));
    if (fs.existsSync(walletPath)) {
      console.log(`Using wallet file: ${walletPath}`);
      const key = fs.readFileSync(walletPath, 'utf8').trim();
      if (!/^0x[a-fA-F0-9]{64}$/.test(key)) {
        console.error('Error: Wallet file must contain a valid 0x-prefixed hex private key');
        process.exit(1);
      }
      return key;
    } else {
      console.error(`Wallet file not found: ${walletPath}`);
      process.exit(1);
    }
  }

  // 3. ~/.nadmail managed wallet (encrypted only — plaintext no longer supported)
  const encryptedKeyFile = path.join(CONFIG_DIR, 'private-key.enc');
  const legacyPlaintextFile = path.join(CONFIG_DIR, 'private-key');

  // Warn about legacy plaintext file
  if (fs.existsSync(legacyPlaintextFile) && !fs.existsSync(encryptedKeyFile)) {
    console.error('Security: Plaintext private key storage is no longer supported (v1.0.4).');
    console.error('Please re-run setup with encryption: node setup.js --managed');
    console.error('Or use environment variable: export NADMAIL_PRIVATE_KEY="0x..."');
    logAudit('plaintext_key_rejected', { success: false, error: 'plaintext_deprecated' });
    process.exit(1);
  }

  if (fs.existsSync(encryptedKeyFile)) {
    console.log(`Found encrypted wallet: ${encryptedKeyFile}`);
    const encryptedData = JSON.parse(fs.readFileSync(encryptedKeyFile, 'utf8'));

    const password = process.env.NADMAIL_PASSWORD || await prompt('Enter wallet password: ');
    try {
      const privateKey = decryptPrivateKey(encryptedData, password);
      logAudit('decrypt_attempt', { success: true });
      return privateKey;
    } catch (e) {
      logAudit('decrypt_attempt', { success: false, error: 'decryption failed' });
      console.error('Wrong password or decryption failed');
      process.exit(1);
    }
  }

  console.error('No wallet found.\n');
  console.error('Options:');
  console.error('  A. export NADMAIL_PRIVATE_KEY="0xYourPrivateKey"');
  console.error('  B. node register.js --wallet /path/to/key');
  console.error('  C. node setup.js --managed (generate new encrypted wallet)');
  process.exit(1);
}

async function api(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  return res.json();
}

async function main() {
  const handle = getArg('--handle');

  console.log('NadMail Registration');
  console.log('========================\n');

  const privateKey = await getPrivateKey();
  const wallet = new ethers.Wallet(privateKey);
  const address = wallet.address;

  console.log(`\nWallet: ${address}`);
  if (handle) console.log(`Handle: ${handle}`);

  // Step 1: Start auth
  console.log('\n1. Starting authentication...');
  const startData = await api('/api/auth/start', {
    method: 'POST',
    body: JSON.stringify({ address }),
  });

  if (!startData.message) {
    console.error('Auth failed:', startData);
    logAudit('register', { wallet: address, success: false, error: 'auth_start_failed' });
    process.exit(1);
  }
  console.log('   Got SIWE message');

  // Step 2: Sign message
  console.log('\n2. Signing message...');
  const signature = await wallet.signMessage(startData.message);
  console.log('   Message signed');

  // Step 3: Register
  console.log('\n3. Registering agent...');
  const registerData = await api('/api/auth/agent-register', {
    method: 'POST',
    body: JSON.stringify({
      address,
      message: startData.message,
      signature,
      handle: handle || undefined,
    }),
  });

  if (!registerData.token) {
    console.error('Registration failed:', registerData);
    logAudit('register', { wallet: address, success: false, error: 'register_failed' });
    process.exit(1);
  }
  console.log('   Registered!');

  const token = registerData.token;
  const email = registerData.email || `${registerData.handle}@nadmail.ai`;

  // Save token
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
  }

  const tokenData = {
    token,
    email,
    handle: registerData.handle || handle || null,
    wallet: address.toLowerCase(),
    saved_at: new Date().toISOString(),
    expires_hint: '24h',
  };

  fs.writeFileSync(TOKEN_FILE, JSON.stringify(tokenData, null, 2), { mode: 0o600 });
  logAudit('register', { wallet: address, success: true });

  console.log('\n' + '='.repeat(40));
  console.log('Success!');
  console.log('='.repeat(40));
  console.log(`\nEmail: ${email}`);
  console.log(`Token saved to: ${TOKEN_FILE}`);
  if (registerData.token_address) {
    console.log(`Meme coin: $${registerData.token_symbol} (${registerData.token_address})`);
  }

  // Show upgrade guidance if applicable
  if (registerData.guidance) {
    const g = registerData.guidance;
    console.log(`\n${g.message}`);
    if (g.owned_nad_names) {
      console.log(`Your .nad names: ${g.owned_nad_names.map(n => n + '.nad').join(', ')}`);
    }
  }

  console.log('\nNext steps:');
  console.log('  node scripts/send.js someone@nadmail.ai "Hi" "Hello!"');
  console.log('  node scripts/inbox.js');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
