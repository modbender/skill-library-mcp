#!/usr/bin/env node
/**
 * Orderly Network - Add Orderly Key
 * Registers the ed25519 trading key with the account
 */

import { ethers } from 'ethers';
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

// EIP-712 domain for off-chain signing
const EIP712_DOMAIN = {
  name: 'Orderly',
  version: '1',
  chainId: CONFIG.CHAIN_ID,
  verifyingContract: '0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC'
};

const ADD_KEY_TYPES = {
  AddOrderlyKey: [
    { name: 'brokerId', type: 'string' },
    { name: 'chainId', type: 'uint256' },
    { name: 'orderlyKey', type: 'string' },
    { name: 'scope', type: 'string' },
    { name: 'timestamp', type: 'uint64' },
    { name: 'expiration', type: 'uint64' }
  ]
};

function loadPrivateKey() {
  const content = fs.readFileSync(CONFIG.WALLET_FILE, 'utf8');
  const match = content.match(/0x[a-fA-F0-9]{64}/);
  if (!match) throw new Error('Could not extract private key');
  return match[0];
}

function loadOrderlyKeys() {
  if (!fs.existsSync(CONFIG.ORDERLY_KEYS_FILE)) {
    throw new Error('Orderly keys not found. Run orderly-register.mjs first.');
  }
  return JSON.parse(fs.readFileSync(CONFIG.ORDERLY_KEYS_FILE, 'utf8'));
}

async function addOrderlyKey() {
  console.log(`\n🔑 Orderly - Add Trading Key`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  
  const privateKey = loadPrivateKey();
  const keys = loadOrderlyKeys();
  
  // Create wallet for signing
  const wallet = new ethers.Wallet(privateKey);
  console.log(`📍 Wallet: ${wallet.address}`);
  console.log(`🔑 Orderly Key: ${keys.orderly_key.slice(0, 30)}...`);
  
  // Prepare message data
  const timestamp = Date.now();
  const expiration = timestamp + (365 * 24 * 60 * 60 * 1000); // 1 year from now
  
  const message = {
    brokerId: CONFIG.BROKER_ID,
    chainId: CONFIG.CHAIN_ID,
    orderlyKey: keys.orderly_key,
    scope: 'read,trading',
    timestamp: timestamp,
    expiration: expiration
  };
  
  console.log(`\n📝 Message to sign:`);
  console.log(`   brokerId: ${message.brokerId}`);
  console.log(`   chainId: ${message.chainId}`);
  console.log(`   scope: ${message.scope}`);
  console.log(`   timestamp: ${message.timestamp}`);
  console.log(`   expiration: ${new Date(message.expiration).toISOString()}`);
  
  // Sign with EIP-712
  console.log(`\n⏳ Signing with EIP-712...`);
  const signature = await wallet.signTypedData(EIP712_DOMAIN, ADD_KEY_TYPES, message);
  console.log(`✅ Signature: ${signature.slice(0, 40)}...`);
  
  // Send to Orderly API
  console.log(`\n⏳ Adding key to Orderly...`);
  const response = await fetch(`${CONFIG.ORDERLY_API}/v1/orderly_key`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: message,
      signature: signature,
      userAddress: wallet.address
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log(`\n✅ ORDERLY KEY ADDED SUCCESSFULLY!`);
    console.log(`   Response:`, JSON.stringify(data, null, 2));
    
    // Update keys file
    keys.key_added = true;
    keys.key_expiration = new Date(expiration).toISOString();
    keys.key_scope = 'read,trading';
    fs.writeFileSync(CONFIG.ORDERLY_KEYS_FILE, JSON.stringify(keys, null, 2));
    console.log(`\n💾 Updated keys file with key status`);
  } else {
    console.log(`\n❌ Failed to add key:`);
    console.log(JSON.stringify(data, null, 2));
  }
  
  return data;
}

addOrderlyKey().catch(console.error);
