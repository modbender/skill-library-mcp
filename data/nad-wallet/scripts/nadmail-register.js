#!/usr/bin/env node
/**
 * Register for NadMail (nadmail.ai) using wallet signature
 * 
 * Usage:
 *   NAD_PRIVATE_KEY="0x..." node nadmail-register.js --handle myname        # Use env var (recommended)
 *   node nadmail-register.js --wallet my-wallet --handle myname             # Use managed wallet file
 * 
 * ⚠️ SECURITY: Never pass private key as command line argument!
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

const API_BASE = 'https://api.nadmail.ai';

// Audit log
const CONFIG_DIR = path.join(process.env.HOME, '.nad-wallet');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');
const TOKEN_FILE = path.join(CONFIG_DIR, 'nadmail-token.json');

function logAudit(action, details = {}) {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
    }
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      address: details.address ? `${details.address.slice(0, 6)}...${details.address.slice(-4)}` : null,
      handle: details.handle,
      success: details.success ?? true,
    };
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {}
}

function showHelp() {
  console.log('📧 NadMail Registration (SIWE Auth)');
  console.log('═'.repeat(50));
  console.log('');
  console.log('Usage:');
  console.log('  NAD_PRIVATE_KEY="0x..." node nadmail-register.js --handle myname');
  console.log('  node nadmail-register.js --wallet my-wallet --handle myname');
  console.log('');
  console.log('Required Arguments:');
  console.log('  --handle NAME      Your desired NadMail handle');
  console.log('');
  console.log('Optional Arguments:');
  console.log('  --wallet NAME      Use managed wallet file (if not using env var)');
  console.log('');
  console.log('⚠️  SECURITY:');
  console.log('   • Use NAD_PRIVATE_KEY environment variable (recommended)');
  console.log('   • Never pass private key as command line argument');
  console.log('   • Handle must be unique across NadMail');
  console.log('');
  console.log('Examples:');
  console.log('  export NAD_PRIVATE_KEY="0x..."');
  console.log('  node nadmail-register.js --handle littlelobster');
  console.log('');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {};
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--handle' && args[i + 1]) {
      result.handle = args[i + 1];
      i++; // skip next
    } else if (args[i] === '--wallet' && args[i + 1]) {
      result.walletName = args[i + 1];
      i++; // skip next
    } else if (args[i] === '--help' || args[i] === '-h') {
      result.showHelp = true;
    }
  }
  
  return result;
}

function getWallet(walletName) {
  // 1. Check environment variable first (recommended)
  if (process.env.NAD_PRIVATE_KEY) {
    console.log('🔑 Using wallet from NAD_PRIVATE_KEY environment variable');
    return new ethers.Wallet(process.env.NAD_PRIVATE_KEY);
  }
  
  // 2. Load from managed wallet file
  if (!walletName) {
    console.error('❌ No wallet specified and NAD_PRIVATE_KEY not set');
    console.error('');
    console.error('Options:');
    console.error('  1. Set NAD_PRIVATE_KEY environment variable:');
    console.error('     export NAD_PRIVATE_KEY="0x..."');
    console.error('     node nadmail-register.js --handle myname');
    console.error('');
    console.error('  2. Use managed wallet:');
    console.error('     node nadmail-register.js --wallet my-wallet --handle myname');
    process.exit(1);
  }
  
  const walletsDir = process.env.NAD_WALLET_DIR || 
    path.join(process.env.HOME, '.nad-wallet', 'wallets');
  
  const filepath = path.join(walletsDir, `${walletName}.json`);
  
  if (fs.existsSync(filepath)) {
    console.log(`🔑 Using managed wallet: ${filepath}`);
    const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
    return new ethers.Wallet(data.privateKey);
  }
  
  // Not found
  console.error(`❌ Wallet not found: ${filepath}`);
  console.error('');
  console.error('Create wallet first:');
  console.error('  node scripts/create-wallet.js --managed ' + walletName);
  process.exit(1);
}

async function registerNadMail(wallet, handle) {
  console.log('\n🔐 Starting NadMail SIWE registration...');
  
  // Step 1: Start authentication
  console.log('Step 1: Requesting authentication message...');
  const startRes = await fetch(`${API_BASE}/api/auth/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: wallet.address })
  });
  
  if (!startRes.ok) {
    const errorText = await startRes.text();
    throw new Error(`Failed to start auth (${startRes.status}): ${errorText}`);
  }
  
  const startData = await startRes.json();
  
  if (!startData.message) {
    throw new Error('No message in auth start response: ' + JSON.stringify(startData));
  }
  
  console.log('✅ Got authentication message');
  
  // Step 2: Sign the message
  console.log('Step 2: Signing authentication message...');
  const signature = await wallet.signMessage(startData.message);
  console.log('✅ Message signed');
  
  // Step 3: Register with agent endpoint
  console.log('Step 3: Registering with NadMail...');
  const registerRes = await fetch(`${API_BASE}/api/auth/agent-register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      address: wallet.address,
      signature: signature,
      message: startData.message,
      handle: handle
    })
  });
  
  if (!registerRes.ok) {
    const errorText = await registerRes.text();
    throw new Error(`Registration failed (${registerRes.status}): ${errorText}`);
  }
  
  const registerData = await registerRes.json();
  
  if (!registerData.token) {
    throw new Error('No token in registration response: ' + JSON.stringify(registerData));
  }
  
  return registerData;
}

function saveToken(tokenData, handle) {
  const tokenInfo = {
    token: tokenData.token,
    handle: handle,
    address: tokenData.address || 'unknown',
    registeredAt: new Date().toISOString(),
    expiresAt: tokenData.expiresAt || null
  };
  
  fs.writeFileSync(TOKEN_FILE, JSON.stringify(tokenInfo, null, 2), { mode: 0o600 });
  console.log('💾 Token saved to:', TOKEN_FILE);
  
  return tokenInfo;
}

async function main() {
  const args = parseArgs();
  
  // Check for help
  if (args.showHelp) {
    showHelp();
    process.exit(0);
  }
  
  // Check for dangerous private key arguments
  if (process.argv.includes('--private-key') || process.argv.includes('-p')) {
    console.error('');
    console.error('⛔ SECURITY ERROR: Do not pass private key as command line argument!');
    console.error('');
    console.error('Use environment variable instead:');
    console.error('  export NAD_PRIVATE_KEY="0x..."');
    console.error('  node nadmail-register.js --handle myname');
    process.exit(1);
  }
  
  // Validate handle
  if (!args.handle) {
    console.error('❌ Missing required --handle argument');
    console.error('');
    showHelp();
    process.exit(1);
  }
  
  console.log('📧 NadMail Registration');
  console.log('═'.repeat(50));
  console.log('Handle:', args.handle);
  
  try {
    // Get wallet
    const wallet = getWallet(args.walletName);
    console.log('Address:', wallet.address);
    
    // Register with NadMail
    const result = await registerNadMail(wallet, args.handle);
    
    console.log('\n🎉 SUCCESS!');
    console.log('📧 NadMail registration completed!');
    console.log('Handle:', args.handle);
    console.log('Address:', wallet.address);
    
    // Save token
    const tokenInfo = saveToken(result, args.handle);
    
    console.log('\n📋 Registration Details:');
    console.log('  • Token saved for API access');
    console.log('  • Handle:', tokenInfo.handle);
    console.log('  • Registered at:', tokenInfo.registeredAt);
    
    console.log('\n🌐 Next Steps:');
    console.log('  • Access NadMail at: https://nadmail.ai');
    console.log('  • Your handle: ' + args.handle);
    console.log('  • API token stored locally for automation');
    
    logAudit('nadmail_registered', { 
      address: wallet.address, 
      handle: args.handle,
      success: true 
    });
    
    // Update managed wallet file if it exists
    if (args.walletName && !process.env.NAD_PRIVATE_KEY) {
      const walletsDir = process.env.NAD_WALLET_DIR || 
        path.join(process.env.HOME, '.nad-wallet', 'wallets');
      const filepath = path.join(walletsDir, `${args.walletName}.json`);
      
      if (fs.existsSync(filepath)) {
        try {
          const walletData = JSON.parse(fs.readFileSync(filepath, 'utf8'));
          walletData.nadmail = {
            handle: args.handle,
            registeredAt: tokenInfo.registeredAt
          };
          fs.writeFileSync(filepath, JSON.stringify(walletData, null, 2), { mode: 0o600 });
          console.log('\n💾 Wallet file updated with NadMail info');
        } catch (e) {
          // Ignore update errors
          console.log('\n⚠️ Could not update wallet file (non-critical)');
        }
      }
    }
    
  } catch (error) {
    console.error('\n❌ Registration failed:', error.message);
    
    logAudit('nadmail_register_failed', { 
      handle: args.handle,
      success: false 
    });
    
    if (error.message.includes('handle already exists')) {
      console.log('\n💡 Try a different handle:');
      console.log('  node nadmail-register.js --handle ' + args.handle + '2');
    }
    
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});