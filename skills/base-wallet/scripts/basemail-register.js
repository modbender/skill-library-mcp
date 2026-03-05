#!/usr/bin/env node
/**
 * Register for BaseMail.ai email using wallet signature
 * 
 * Usage:
 *   PRIVATE_KEY="0x..." node basemail-register.js          # Use env var (recommended)
 *   node basemail-register.js [wallet-name]                # Use managed wallet file
 * 
 * ⚠️ SECURITY: Never pass private key as command line argument!
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

const API_BASE = 'https://api.basemail.ai';

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
      email: details.email,
      success: details.success ?? true,
    };
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {}
}

function getWallet(walletName) {
  // 1. Check environment variable first (recommended)
  if (process.env.PRIVATE_KEY) {
    console.log('🔑 Using wallet from PRIVATE_KEY environment variable');
    return new ethers.Wallet(process.env.PRIVATE_KEY);
  }
  
  // 2. Load from managed wallet file
  const walletsDir = process.env.WALLET_DIR || 
    path.join(process.env.HOME, '.openclaw', 'wallets');
  
  const filepath = path.join(walletsDir, `${walletName}.json`);
  
  if (fs.existsSync(filepath)) {
    console.log(`🔑 Using managed wallet: ${filepath}`);
    const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
    return new ethers.Wallet(data.privateKey);
  }
  
  // Not found
  console.error('❌ No wallet found');
  console.error('');
  console.error('Options:');
  console.error('  1. Set PRIVATE_KEY environment variable:');
  console.error('     export PRIVATE_KEY="0x..."');
  console.error('     node basemail-register.js');
  console.error('');
  console.error('  2. Create a managed wallet first:');
  console.error('     node create-wallet.js --managed');
  console.error('     node basemail-register.js');
  process.exit(1);
}

async function getAuthToken(wallet) {
  // Start auth
  const startRes = await fetch(`${API_BASE}/api/auth/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: wallet.address })
  });
  const startData = await startRes.json();
  
  if (!startData.message) {
    throw new Error('Failed to start auth: ' + JSON.stringify(startData));
  }

  // Sign message
  const signature = await wallet.signMessage(startData.message);
  
  // Verify
  const verifyRes = await fetch(`${API_BASE}/api/auth/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      message: startData.message, 
      signature, 
      address: wallet.address 
    })
  });
  
  return await verifyRes.json();
}

async function main() {
  const walletName = process.argv[2] || 'default';
  
  // Check for dangerous --private-key argument
  if (process.argv.includes('--private-key') || process.argv.includes('-p')) {
    console.error('');
    console.error('⛔ SECURITY ERROR: Do not pass private key as command line argument!');
    console.error('');
    console.error('Use environment variable instead:');
    console.error('  export PRIVATE_KEY="0x..."');
    console.error('  node basemail-register.js');
    process.exit(1);
  }
  
  console.log('📧 BaseMail Registration');
  console.log('═'.repeat(50));
  
  // Get wallet
  const wallet = getWallet(walletName);
  console.log('Address:', wallet.address);
  
  // Authenticate
  console.log('\n🔐 Authenticating with SIWE signature...');
  const authData = await getAuthToken(wallet);
  
  if (!authData.token) {
    console.error('❌ Authentication failed:', authData);
    logAudit('basemail_auth_failed', { address: wallet.address, success: false });
    process.exit(1);
  }
  
  console.log('✅ Authenticated!');
  
  if (authData.registered) {
    console.log('\n✅ Already registered!');
    console.log('📧 Your email:', authData.suggested_email || authData.email);
    logAudit('basemail_exists', { address: wallet.address, email: authData.suggested_email });
    return;
  }
  
  // Register
  console.log('\n📝 Registering email...');
  const regRes = await fetch(`${API_BASE}/api/register`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authData.token}`
    },
    body: JSON.stringify({})
  });
  
  const regData = await regRes.json();
  
  if (regData.success || regData.email) {
    const email = regData.email || regData.suggested_email;
    console.log('\n🎉 SUCCESS!');
    console.log('📧 Your BaseMail:', email);
    console.log('Handle:', regData.handle);
    
    logAudit('basemail_registered', { address: wallet.address, email });
    
    // Update managed wallet file if it exists
    if (!process.env.PRIVATE_KEY) {
      const walletsDir = process.env.WALLET_DIR || 
        path.join(process.env.HOME, '.openclaw', 'wallets');
      const filepath = path.join(walletsDir, `${walletName}.json`);
      
      if (fs.existsSync(filepath)) {
        try {
          const walletData = JSON.parse(fs.readFileSync(filepath, 'utf8'));
          walletData.basemail = email;
          walletData.basemailRegisteredAt = new Date().toISOString();
          fs.writeFileSync(filepath, JSON.stringify(walletData, null, 2), { mode: 0o600 });
          console.log('\n💾 Wallet file updated with BaseMail info');
        } catch (e) {
          // Ignore update errors
        }
      }
    }
  } else {
    console.error('❌ Registration failed:', regData);
    logAudit('basemail_register_failed', { address: wallet.address, success: false });
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
