#!/usr/bin/env node
/**
 * Create a new Base/Ethereum wallet
 * 
 * Usage:
 *   node create-wallet.js                    # Show help
 *   node create-wallet.js --env              # Output as env var (recommended)
 *   node create-wallet.js --managed [name]   # Save to file (opt-in)
 * 
 * ⚠️ SECURITY: By default, private key is only shown once and NOT saved to file.
 *    Use --managed only if you understand the risks.
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Audit log
const CONFIG_DIR = path.join(process.env.HOME, '.base-wallet');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');

function logAudit(action, details = {}) {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
    }
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      address: details.address ? `${details.address.slice(0, 6)}...${details.address.slice(-4)}` : null,
      mode: details.mode,
      success: details.success ?? true,
    };
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {}
}

function showHelp() {
  console.log('🔐 Base Wallet Creator');
  console.log('═'.repeat(50));
  console.log('');
  console.log('Usage: node create-wallet.js [options]');
  console.log('');
  console.log('Options:');
  console.log('  --env              Output private key as env var format (recommended)');
  console.log('  --managed [name]   Save wallet to file (opt-in, less secure)');
  console.log('  --json             Output as JSON (for piping)');
  console.log('');
  console.log('Recommended usage:');
  console.log('  node create-wallet.js --env');
  console.log('  # Then set the output as environment variable');
  console.log('');
  console.log('⚠️  SECURITY:');
  console.log('   • Private keys are shown ONCE and not stored');
  console.log('   • Copy the key immediately and store securely');
  console.log('   • --managed stores keys in files (use with caution)');
  console.log('');
}

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim().toLowerCase());
    });
  });
}

async function main() {
  const args = process.argv.slice(2);
  
  const isEnv = args.includes('--env');
  const isJson = args.includes('--json');
  const isManaged = args.includes('--managed');
  
  // Get wallet name for managed mode
  let walletName = 'default';
  const managedIdx = args.indexOf('--managed');
  if (managedIdx !== -1 && args[managedIdx + 1] && !args[managedIdx + 1].startsWith('-')) {
    walletName = args[managedIdx + 1];
  }
  
  // No args: show help
  if (!isEnv && !isJson && !isManaged) {
    showHelp();
    process.exit(0);
  }
  
  // Create wallet
  const wallet = ethers.Wallet.createRandom();
  
  // Mode: --env (recommended)
  if (isEnv) {
    console.log('# 🔐 New Wallet Created');
    console.log('# Copy these lines to your shell or .env file:');
    console.log('');
    console.log(`export WALLET_ADDRESS="${wallet.address}"`);
    console.log(`export PRIVATE_KEY="${wallet.privateKey}"`);
    console.log('');
    console.log('# Mnemonic (backup phrase) - store offline securely:');
    console.log(`# ${wallet.mnemonic.phrase}`);
    console.log('');
    console.log('# ⚠️ This is shown ONCE. Copy now!');
    
    logAudit('wallet_created', { address: wallet.address, mode: 'env' });
    return;
  }
  
  // Mode: --json (for piping)
  if (isJson) {
    console.log(JSON.stringify({
      address: wallet.address,
      privateKey: wallet.privateKey,
      mnemonic: wallet.mnemonic.phrase,
      createdAt: new Date().toISOString(),
    }, null, 2));
    
    console.error('# ⚠️ Private key shown above. Store securely!');
    
    logAudit('wallet_created', { address: wallet.address, mode: 'json' });
    return;
  }
  
  // Mode: --managed (stores to file)
  if (isManaged) {
    console.log('🔐 Base Wallet Creator (Managed Mode)');
    console.log('═'.repeat(50));
    console.log('');
    console.log('⚠️ WARNING: This will save private key to a file.');
    console.log('   File location: ~/.openclaw/wallets/' + walletName + '.json');
    console.log('   Permissions: 600 (owner read/write only)');
    console.log('');
    console.log('   This is convenient but less secure than using environment variables.');
    console.log('');
    
    const confirm = await prompt('Continue? (yes/no): ');
    if (confirm !== 'yes' && confirm !== 'y') {
      console.log('Cancelled.');
      process.exit(0);
    }
    
    console.log('');
    console.log('Address:', wallet.address);
    
    // Prepare wallet data
    const walletData = {
      address: wallet.address,
      privateKey: wallet.privateKey,
      mnemonic: wallet.mnemonic.phrase,
      createdAt: new Date().toISOString(),
      network: 'base-mainnet',
      chainId: 8453
    };
    
    // Determine storage path
    const walletsDir = process.env.WALLET_DIR || 
      path.join(process.env.HOME, '.openclaw', 'wallets');
    
    fs.mkdirSync(walletsDir, { recursive: true, mode: 0o700 });
    
    const filepath = path.join(walletsDir, `${walletName}.json`);
    
    // Check if exists
    if (fs.existsSync(filepath)) {
      const overwrite = await prompt(`\n⚠️ Wallet "${walletName}" already exists. Overwrite? (yes/no): `);
      if (overwrite !== 'yes') {
        console.log('Cancelled.');
        process.exit(0);
      }
    }
    
    // Save with restricted permissions
    fs.writeFileSync(filepath, JSON.stringify(walletData, null, 2), { mode: 0o600 });
    
    console.log('\n💾 Wallet saved to:', filepath);
    console.log('🔒 File permissions: 600');
    
    // Also save mnemonic separately (read-only backup)
    const mnemonicPath = filepath.replace('.json', '.mnemonic');
    fs.writeFileSync(mnemonicPath, wallet.mnemonic.phrase, { mode: 0o400 });
    console.log('📝 Mnemonic backup:', mnemonicPath, '(read-only)');
    
    console.log('\n⚠️ SECURITY REMINDERS:');
    console.log('   • Back up the mnemonic file offline and delete it');
    console.log('   • Never share your private key or mnemonic');
    console.log('   • Add wallet files to .gitignore');
    
    console.log('\n📧 To get a BaseMail email, run:');
    console.log(`   node basemail-register.js ${walletName}`);
    
    logAudit('wallet_created', { address: wallet.address, mode: 'managed' });
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
