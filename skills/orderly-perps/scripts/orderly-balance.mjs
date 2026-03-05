#!/usr/bin/env node
/**
 * Orderly Network Balance Checker
 * Checks account balance using ed25519 authentication
 */

import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const CONFIG = {
  ORDERLY_KEYS_FILE: process.env.ORDERLY_KEYS_FILE || path.join(process.env.HOME || '', '.orderly-keys.json'),
  ORDERLY_API: 'https://api-evm.orderly.org'
};

function loadOrderlyKeys() {
  if (!fs.existsSync(CONFIG.ORDERLY_KEYS_FILE)) {
    throw new Error('Orderly keys not found. Run orderly-register.mjs first.');
  }
  return JSON.parse(fs.readFileSync(CONFIG.ORDERLY_KEYS_FILE, 'utf8'));
}

function signMessage(message, keys) {
  // Use raw hex key for signing
  const secretKeyHex = keys.priv_key_hex;
  const secretKeyBytes = Buffer.from(secretKeyHex, 'hex');
  
  // Create keypair from secret
  const privateKey = crypto.createPrivateKey({
    key: Buffer.concat([
      Buffer.from('302e020100300506032b657004220420', 'hex'),
      secretKeyBytes
    ]),
    format: 'der',
    type: 'pkcs8'
  });
  
  const signature = crypto.sign(null, Buffer.from(message), privateKey);
  return signature.toString('base64');
}

async function getBalance() {
  const keys = loadOrderlyKeys();
  const timestamp = Date.now();
  
  // Build message to sign (for GET requests: timestamp + method + path)
  const method = 'GET';
  const path = '/v1/client/holding';
  const message = `${timestamp}${method}${path}`;
  
  const signature = signMessage(message, keys);
  
  const url = `${CONFIG.ORDERLY_API}${path}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'orderly-account-id': keys.account_id,
      'orderly-key': keys.orderly_key,
      'orderly-signature': signature,
      'orderly-timestamp': timestamp.toString()
    }
  });
  
  const data = await response.json();
  return data;
}

async function getAccountInfo() {
  const keys = loadOrderlyKeys();
  const timestamp = Date.now();
  
  const method = 'GET';
  const path = '/v1/client/info';
  const message = `${timestamp}${method}${path}`;
  
  const signature = signMessage(message, keys);
  
  const url = `${CONFIG.ORDERLY_API}${path}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'orderly-account-id': keys.account_id,
      'orderly-key': keys.orderly_key,
      'orderly-signature': signature,
      'orderly-timestamp': timestamp.toString()
    }
  });
  
  const data = await response.json();
  return data;
}

async function main() {
  const keys = loadOrderlyKeys();
  
  console.log(`\n💰 Orderly Account Balance`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`📍 Account: ${keys.account_id.slice(0, 20)}...`);
  console.log(`📍 Wallet: ${keys.wallet_address}`);
  
  try {
    console.log(`\n📊 Fetching account info...`);
    const info = await getAccountInfo();
    console.log(`Account info:`, JSON.stringify(info, null, 2));
    
    console.log(`\n📊 Fetching holdings...`);
    const holdings = await getBalance();
    console.log(`Holdings:`, JSON.stringify(holdings, null, 2));
    
  } catch (error) {
    console.error(`❌ Error:`, error.message);
  }
}

main().catch(console.error);
