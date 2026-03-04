#!/usr/bin/env node
/**
 * NadMail Setup Script
 * Creates a new wallet for AI agents who don't have one
 *
 * Usage:
 *   node setup.js              # Show help
 *   node setup.js --managed    # Generate wallet (always encrypted)
 *
 * Security: Private keys are ALWAYS encrypted with AES-256-GCM.
 * Plaintext storage is not supported.
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const crypto = require('crypto');

const CONFIG_DIR = path.join(process.env.HOME, '.nadmail');
const KEY_FILE_ENCRYPTED = path.join(CONFIG_DIR, 'private-key.enc');
const WALLET_FILE = path.join(CONFIG_DIR, 'wallet.json');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');

// Legacy files to clean up
const LEGACY_PLAINTEXT_KEY = path.join(CONFIG_DIR, 'private-key');
const LEGACY_MNEMONIC_FILE = path.join(CONFIG_DIR, 'mnemonic.backup');

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
    if (!fs.existsSync(CONFIG_DIR)) return;
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      wallet: details.wallet ? `${details.wallet.slice(0, 6)}...${details.wallet.slice(-4)}` : null,
      success: details.success ?? true,
    };
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {
    // Silently ignore audit errors
  }
}

function encryptPrivateKey(privateKey, password) {
  const salt = crypto.randomBytes(16);
  const key = crypto.scryptSync(password, salt, 32);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);

  let encrypted = cipher.update(privateKey, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag();

  return {
    encrypted,
    salt: salt.toString('hex'),
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex'),
    algorithm: 'aes-256-gcm',
    version: 2,
  };
}

/**
 * Validate password strength
 */
function validatePassword(password) {
  const errors = [];
  if (!password || password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }
  if (password && password.length > 128) {
    errors.push('Password must not exceed 128 characters');
  }
  if (password && !/[a-zA-Z]/.test(password)) {
    errors.push('Password must contain at least one letter');
  }
  if (password && !/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  return { valid: errors.length === 0, errors };
}

function showHelp() {
  console.log('NadMail Wallet Setup');
  console.log('========================\n');

  console.log('Recommended: Use an environment variable (no setup script needed)\n');
  console.log('   export NADMAIL_PRIVATE_KEY="0xYourPrivateKey"');
  console.log('   node scripts/register.js\n');

  console.log('Or specify an existing wallet path:\n');
  console.log('   node scripts/register.js --wallet /path/to/your/private-key\n');

  console.log('-'.repeat(50));
  console.log('\nIf you don\'t have a wallet, let this skill generate one:\n');
  console.log('   node setup.js --managed\n');
  console.log('   Private key is ALWAYS encrypted with AES-256-GCM.');
  console.log('   Stored at ~/.nadmail/private-key.enc\n');
}

/**
 * Clean up legacy insecure files if they exist
 */
function cleanupLegacyFiles() {
  let cleaned = false;

  if (fs.existsSync(LEGACY_PLAINTEXT_KEY)) {
    // Overwrite with random data before deleting (best effort secure delete)
    try {
      const size = fs.statSync(LEGACY_PLAINTEXT_KEY).size;
      fs.writeFileSync(LEGACY_PLAINTEXT_KEY, crypto.randomBytes(size));
      fs.unlinkSync(LEGACY_PLAINTEXT_KEY);
      console.log('   Removed legacy plaintext key file (security upgrade)');
      cleaned = true;
    } catch (e) {
      console.error('   Warning: Could not remove legacy plaintext key:', LEGACY_PLAINTEXT_KEY);
    }
  }

  if (fs.existsSync(LEGACY_MNEMONIC_FILE)) {
    try {
      const size = fs.statSync(LEGACY_MNEMONIC_FILE).size;
      fs.writeFileSync(LEGACY_MNEMONIC_FILE, crypto.randomBytes(size));
      fs.unlinkSync(LEGACY_MNEMONIC_FILE);
      console.log('   Removed legacy mnemonic backup file (security upgrade)');
      cleaned = true;
    } catch (e) {
      console.error('   Warning: Could not remove legacy mnemonic file:', LEGACY_MNEMONIC_FILE);
    }
  }

  return cleaned;
}

async function main() {
  const args = process.argv.slice(2);
  const isManaged = args.includes('--managed');

  if (args.includes('--no-encrypt')) {
    console.error('Error: --no-encrypt has been removed in v1.0.4 for security reasons.');
    console.error('Private keys are always encrypted. Run: node setup.js --managed');
    process.exit(1);
  }

  if (!isManaged) {
    showHelp();
    process.exit(0);
  }

  console.log('NadMail Wallet Setup (Managed Mode)');
  console.log('=======================================\n');

  console.log('About to generate a new wallet.');
  console.log('   Private key will be encrypted with AES-256-GCM');
  console.log('   Stored at ~/.nadmail/private-key.enc\n');

  // Clean up any legacy insecure files
  cleanupLegacyFiles();

  // Check if wallet already exists
  if (fs.existsSync(KEY_FILE_ENCRYPTED)) {
    console.log('Encrypted wallet already exists!');
    console.log(`   ${KEY_FILE_ENCRYPTED}`);

    const answer = await prompt('\nOverwrite existing wallet? This will permanently delete the old one! (yes/no): ');
    if (answer.toLowerCase() !== 'yes') {
      console.log('Cancelled.');
      process.exit(0);
    }
  }

  const confirm = await prompt('Continue? (yes/no): ');
  if (confirm.toLowerCase() !== 'yes') {
    console.log('Cancelled.');
    process.exit(0);
  }

  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
    console.log(`\nCreated directory ${CONFIG_DIR}`);
  }

  // Password setup with validation
  let password;
  while (true) {
    password = await prompt('\nSet encryption password (min 8 chars, must include letter + number): ');
    const validation = validatePassword(password);
    if (validation.valid) break;
    console.error('Invalid password:');
    validation.errors.forEach(e => console.error(`   - ${e}`));
  }

  const confirmPwd = await prompt('Confirm password: ');
  if (password !== confirmPwd) {
    console.error('Passwords do not match. Cancelled.');
    process.exit(1);
  }

  console.log('\nGenerating new wallet...\n');
  const wallet = ethers.Wallet.createRandom();

  const encryptedData = encryptPrivateKey(wallet.privateKey, password);
  fs.writeFileSync(KEY_FILE_ENCRYPTED, JSON.stringify(encryptedData, null, 2), { mode: 0o600 });

  console.log('='.repeat(50));
  console.log('New wallet created');
  console.log('='.repeat(50));
  console.log(`\nAddress: ${wallet.address}`);
  console.log(`Encrypted key saved to: ${KEY_FILE_ENCRYPTED}`);

  // Display mnemonic ONCE — never save to file
  console.log('\n' + '='.repeat(50));
  console.log('BACKUP YOUR MNEMONIC PHRASE NOW!');
  console.log('='.repeat(50));
  console.log('\n' + wallet.mnemonic.phrase + '\n');
  console.log('='.repeat(50));
  console.log('This is shown ONLY ONCE and is NOT saved anywhere.');
  console.log('Write it down on paper or store in a password manager.');
  console.log('Losing your mnemonic = losing your wallet permanently.');
  console.log('='.repeat(50));

  const walletInfo = {
    address: wallet.address,
    created_at: new Date().toISOString(),
    encrypted: true,
    skill_version: '1.0.4',
    note: 'Private key stored separately (encrypted)',
  };
  fs.writeFileSync(WALLET_FILE, JSON.stringify(walletInfo, null, 2), { mode: 0o600 });
  logAudit('wallet_created', { wallet: wallet.address, success: true });

  console.log('\nSecurity reminders:');
  console.log('   1. Back up your mnemonic to a safe location (paper/password manager)');
  console.log('   2. Remember your encryption password — it cannot be recovered');
  console.log('   3. Never share your private key or mnemonic');
  console.log('   4. Never commit ~/.nadmail/ to git');

  console.log('\nNext steps:');
  console.log('   node scripts/register.js');
  console.log('   (Optional) Get a .nad domain for a prettier email address');

  console.log('\nSetup complete!');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
