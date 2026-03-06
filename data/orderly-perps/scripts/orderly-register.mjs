#!/usr/bin/env node
/**
 * Orderly Network Registration Tool (Node.js)
 * Uses ethers.js for proper EIP-712 typed data signing
 */

import { ethers } from 'ethers';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const CONFIG = {
  WALLET_FILE: '/Users/garysingh/clawd/.eth-wallet.txt',
  ORDERLY_KEYS_FILE: process.env.ORDERLY_KEYS_FILE || path.join(process.env.HOME || '', '.orderly-keys.json'),
  ORDERLY_API: 'https://api-evm.orderly.org',
  BROKER_ID: 'hyper_claw',
  CHAIN_ID: 8453  // Base mainnet
};

// Extract private key from wallet file
function loadPrivateKey() {
  const content = fs.readFileSync(CONFIG.WALLET_FILE, 'utf8');
  const match = content.match(/0x[a-fA-F0-9]{64}/);
  if (!match) throw new Error('Could not extract private key');
  return match[0];
}

// Generate ed25519 keypair for Orderly trading
function generateOrderlyKeys() {
  const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
  
  // Export raw keys
  const pubKeyRaw = publicKey.export({ type: 'spki', format: 'der' }).slice(-32);
  const privKeyRaw = privateKey.export({ type: 'pkcs8', format: 'der' }).slice(-32);
  
  return {
    orderly_key: `ed25519:${pubKeyRaw.toString('hex')}`,
    orderly_secret: `ed25519:${privKeyRaw.toString('hex')}`
  };
}

// Load or generate Orderly keys
function getOrderlyKeys(walletAddress) {
  if (fs.existsSync(CONFIG.ORDERLY_KEYS_FILE)) {
    const existing = JSON.parse(fs.readFileSync(CONFIG.ORDERLY_KEYS_FILE, 'utf8'));
    if (existing.orderly_key) {
      console.log('📂 Using existing Orderly keys');
      return existing;
    }
  }
  
  console.log('🔑 Generating new ed25519 keypair...');
  const keys = generateOrderlyKeys();
  
  const keysData = {
    ...keys,
    wallet_address: walletAddress,
    chain_id: CONFIG.CHAIN_ID,
    broker_id: CONFIG.BROKER_ID,
    created_at: new Date().toISOString()
  };
  
  fs.writeFileSync(CONFIG.ORDERLY_KEYS_FILE, JSON.stringify(keysData, null, 2));
  fs.chmodSync(CONFIG.ORDERLY_KEYS_FILE, 0o600);
  
  console.log(`✅ Keys saved to ${CONFIG.ORDERLY_KEYS_FILE}`);
  return keysData;
}

// Check if already registered
async function checkRegistration(walletAddress) {
  const url = `${CONFIG.ORDERLY_API}/v1/get_account?address=${walletAddress}&broker_id=${CONFIG.BROKER_ID}`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.success && data.data?.account_id) {
      console.log(`✅ Already registered: ${data.data.account_id}`);
      return data.data.account_id;
    }
  } catch (e) {
    console.log('⚠️ Could not check registration status');
  }
  
  return null;
}

// EIP-712 domain for Orderly registration
function getRegistrationDomain() {
  return {
    name: 'Orderly',
    version: '1',
    chainId: CONFIG.CHAIN_ID,
    verifyingContract: '0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC'  // Standard address
  };
}

// EIP-712 types for registration
function getRegistrationTypes() {
  return {
    Registration: [
      { name: 'brokerId', type: 'string' },
      { name: 'chainId', type: 'uint256' },
      { name: 'timestamp', type: 'uint64' },
      { name: 'registrationNonce', type: 'uint256' }
    ]
  };
}

// Get registration nonce from API
async function getRegistrationNonce(walletAddress) {
  const url = `${CONFIG.ORDERLY_API}/v1/registration_nonce?address=${walletAddress}&broker_id=${CONFIG.BROKER_ID}`;
  const response = await fetch(url);
  const data = await response.json();
  
  if (!data.success || !data.data?.registration_nonce) {
    throw new Error(`Failed to get nonce: ${data.message || 'Unknown error'}`);
  }
  
  return data.data.registration_nonce;
}

// Register account with Orderly
async function registerAccount(wallet, orderlyKeys) {
  const timestamp = Date.now();
  
  console.log('🔢 Fetching registration nonce...');
  const nonce = await getRegistrationNonce(wallet.address);
  console.log(`📊 Nonce: ${nonce}`);
  
  const domain = getRegistrationDomain();
  const types = getRegistrationTypes();
  const message = {
    brokerId: CONFIG.BROKER_ID,
    chainId: CONFIG.CHAIN_ID,
    timestamp: timestamp,
    registrationNonce: nonce
  };
  
  console.log('📝 Signing registration message...');
  
  // Sign typed data (EIP-712)
  const signature = await wallet.signTypedData(domain, types, message);
  console.log(`✍️ Signature: ${signature.substring(0, 30)}...`);
  
  // Build request body
  const body = {
    message: {
      brokerId: CONFIG.BROKER_ID,
      chainId: CONFIG.CHAIN_ID,
      timestamp: timestamp,
      registrationNonce: nonce.toString()
    },
    signature: signature,
    userAddress: wallet.address,
    broker_id: CONFIG.BROKER_ID,
    chain_id: CONFIG.CHAIN_ID,
    orderly_key: orderlyKeys.orderly_key
  };
  
  console.log('📤 Calling registration API...');
  
  const response = await fetch(`${CONFIG.ORDERLY_API}/v1/register_account`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });
  
  const data = await response.json();
  console.log('📥 Response:', JSON.stringify(data, null, 2));
  
  if (data.success) {
    console.log(`🎉 Registration successful! Account ID: ${data.data?.account_id}`);
    
    // Update keys file with account ID
    const keysData = JSON.parse(fs.readFileSync(CONFIG.ORDERLY_KEYS_FILE, 'utf8'));
    keysData.account_id = data.data?.account_id;
    keysData.registered_at = new Date().toISOString();
    fs.writeFileSync(CONFIG.ORDERLY_KEYS_FILE, JSON.stringify(keysData, null, 2));
    
    return data.data?.account_id;
  } else {
    console.error(`❌ Registration failed: ${data.message || data.error || 'Unknown error'}`);
    return null;
  }
}

// Main
async function main() {
  console.log('═══════════════════════════════════════════════════════════════');
  console.log('  🔐 Orderly Network Registration (Node.js)');
  console.log('═══════════════════════════════════════════════════════════════');
  console.log();
  
  try {
    // Load wallet
    const privateKey = loadPrivateKey();
    const wallet = new ethers.Wallet(privateKey);
    console.log(`💳 Wallet: ${wallet.address}`);
    
    // Check existing registration
    const existingAccount = await checkRegistration(wallet.address);
    if (existingAccount) {
      console.log('\n✅ Ready to trade on Orderly Network!');
      console.log('💡 Next: Deposit USDC collateral');
      return;
    }
    
    console.log('📭 Not registered yet\n');
    
    // Get/generate Orderly keys
    const orderlyKeys = getOrderlyKeys(wallet.address);
    console.log(`🔑 Orderly key: ${orderlyKeys.orderly_key.substring(0, 30)}...`);
    
    // Register
    console.log('\n🚀 Attempting registration...');
    await registerAccount(wallet, orderlyKeys);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
  
  console.log();
  console.log('═══════════════════════════════════════════════════════════════');
}

main();
