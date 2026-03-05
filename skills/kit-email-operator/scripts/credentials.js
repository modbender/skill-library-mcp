#!/usr/bin/env node

/**
 * Kit Email Operator - Secure Credential Management
 * 
 * Handles encryption, storage, and retrieval of Kit API credentials.
 * Uses AES-256-GCM encryption with a workspace-specific key.
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CREDS_PATH = path.join(os.homedir(), '.openclaw', 'workspace', '.kit-credentials');
const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32; // 256 bits

/**
 * Generate encryption key from workspace path
 * (deterministic but unique per workspace)
 */
function getEncryptionKey() {
  const workspacePath = process.env.OPENCLAW_WORKSPACE || '/data/.openclaw/workspace';
  return crypto.createHash('sha256')
    .update(workspacePath)
    .digest();
}

/**
 * Encrypt credentials
 */
function encrypt(data) {
  const key = getEncryptionKey();
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);
  
  let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  const authTag = cipher.getAuthTag();
  
  return {
    encrypted,
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex')
  };
}

/**
 * Decrypt credentials
 */
function decrypt(encryptedData) {
  const key = getEncryptionKey();
  const { encrypted, iv, authTag } = encryptedData;
  
  const decipher = crypto.createDecipheriv(
    ALGORITHM,
    key,
    Buffer.from(iv, 'hex')
  );
  
  decipher.setAuthTag(Buffer.from(authTag, 'hex'));
  
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return JSON.parse(decrypted);
}

/**
 * Save credentials to file
 */
function saveCredentials(credentials) {
  const encrypted = encrypt(credentials);
  
  // Ensure directory exists
  const dir = path.dirname(CREDS_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  // Write with restricted permissions (owner only)
  fs.writeFileSync(CREDS_PATH, JSON.stringify(encrypted, null, 2), {
    mode: 0o600
  });
  
  console.log('✅ Credentials saved securely');
}

/**
 * Load credentials from file
 */
function loadCredentials() {
  if (!fs.existsSync(CREDS_PATH)) {
    throw new Error('Credentials not found. Run setup first.');
  }
  
  const encryptedData = JSON.parse(fs.readFileSync(CREDS_PATH, 'utf8'));
  return decrypt(encryptedData);
}

/**
 * Check if credentials exist
 */
function credentialsExist() {
  return fs.existsSync(CREDS_PATH);
}

/**
 * Delete credentials
 */
function deleteCredentials() {
  if (fs.existsSync(CREDS_PATH)) {
    fs.unlinkSync(CREDS_PATH);
    console.log('✅ Credentials deleted');
  }
}

/**
 * Validate credentials format
 */
function validateCredentials(creds) {
  const required = ['apiKey', 'apiSecret'];
  const missing = required.filter(field => !creds[field]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required fields: ${missing.join(', ')}`);
  }
  
  // Validate format (Kit API keys have specific patterns)
  if (!creds.apiKey.startsWith('kit_')) {
    throw new Error('Invalid API key format (should start with "kit_")');
  }
  
  if (creds.apiSecret.length < 32) {
    throw new Error('Invalid API secret (too short)');
  }
  
  return true;
}

/**
 * Interactive setup (CLI usage)
 */
async function interactiveSetup() {
  const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  const question = (prompt) => new Promise(resolve => {
    readline.question(prompt, resolve);
  });
  
  console.log('\n🔧 Kit Email Operator - Credential Setup\n');
  console.log('Get your credentials from: https://app.kit.com/account_settings/advanced_settings\n');
  
  const apiKey = await question('Kit API Key (v4, starts with "kit_"): ');
  const apiSecret = await question('Kit API Secret: ');
  
  const credentials = {
    apiKey: apiKey.trim(),
    apiSecret: apiSecret.trim(),
    createdAt: new Date().toISOString()
  };
  
  try {
    validateCredentials(credentials);
    saveCredentials(credentials);
    console.log('\n✅ Setup complete! You can now use the Kit Email Operator.\n');
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}\n`);
    process.exit(1);
  }
  
  readline.close();
}

// CLI usage
if (require.main === module) {
  const command = process.argv[2];
  
  if (!command || command === 'setup') {
    interactiveSetup();
  } else if (command === 'test') {
    try {
      const creds = loadCredentials();
      console.log('✅ Credentials loaded successfully');
      console.log(`API Key: ${creds.apiKey.substring(0, 10)}...`);
      console.log(`Created: ${creds.createdAt}`);
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
      process.exit(1);
    }
  } else if (command === 'delete') {
    deleteCredentials();
  } else {
    console.log('Usage:');
    console.log('  node credentials.js setup   - Interactive setup');
    console.log('  node credentials.js test    - Test credential loading');
    console.log('  node credentials.js delete  - Delete credentials');
  }
}

// Export for use in other scripts
module.exports = {
  saveCredentials,
  loadCredentials,
  credentialsExist,
  deleteCredentials,
  validateCredentials
};
