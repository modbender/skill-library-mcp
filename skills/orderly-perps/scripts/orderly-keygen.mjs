#!/usr/bin/env node
/**
 * Orderly Network Key Generator
 * Generates ed25519 keypair in correct format (base58)
 */

import crypto from 'crypto';
import bs58 from 'bs58';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CONFIG = {
  ORDERLY_KEYS_FILE: process.env.ORDERLY_KEYS_FILE || path.join(process.env.HOME || '', '.orderly-keys.json')
};

function generateOrderlyKeys() {
  // Generate ed25519 keypair
  const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
  
  // Export raw keys (last 32 bytes of DER)
  const pubKeyDER = publicKey.export({ type: 'spki', format: 'der' });
  const privKeyDER = privateKey.export({ type: 'pkcs8', format: 'der' });
  
  // Extract raw 32-byte keys
  const pubKeyRaw = pubKeyDER.slice(-32);
  const privKeyRaw = privKeyDER.slice(-32);
  
  // Encode in base58
  const pubKeyBase58 = bs58.encode(pubKeyRaw);
  const privKeyBase58 = bs58.encode(privKeyRaw);
  
  return {
    orderly_key: `ed25519:${pubKeyBase58}`,
    orderly_secret: `ed25519:${privKeyBase58}`,
    // Store raw hex for crypto operations
    pub_key_hex: pubKeyRaw.toString('hex'),
    priv_key_hex: privKeyRaw.toString('hex')
  };
}

async function main() {
  console.log(`\n🔑 Orderly Key Generator`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  
  // Load existing keys to preserve account info
  let existingKeys = {};
  if (fs.existsSync(CONFIG.ORDERLY_KEYS_FILE)) {
    existingKeys = JSON.parse(fs.readFileSync(CONFIG.ORDERLY_KEYS_FILE, 'utf8'));
    console.log(`📂 Found existing keys file`);
    console.log(`   Account ID: ${existingKeys.account_id?.slice(0, 20)}...`);
  }
  
  // Generate new keys
  console.log(`\n⏳ Generating new ed25519 keypair...`);
  const newKeys = generateOrderlyKeys();
  
  console.log(`✅ New keys generated:`);
  console.log(`   Public:  ${newKeys.orderly_key}`);
  console.log(`   Secret:  ${newKeys.orderly_secret.slice(0, 30)}...`);
  
  // Merge with existing keys (preserve account info)
  const mergedKeys = {
    ...existingKeys,
    orderly_key: newKeys.orderly_key,
    orderly_secret: newKeys.orderly_secret,
    pub_key_hex: newKeys.pub_key_hex,
    priv_key_hex: newKeys.priv_key_hex,
    keys_regenerated_at: new Date().toISOString()
  };
  
  // Save
  fs.writeFileSync(CONFIG.ORDERLY_KEYS_FILE, JSON.stringify(mergedKeys, null, 2));
  fs.chmodSync(CONFIG.ORDERLY_KEYS_FILE, 0o600);
  
  console.log(`\n💾 Saved to ${CONFIG.ORDERLY_KEYS_FILE}`);
  console.log(`\n⚠️  Now run orderly-add-key.mjs to register this key with your account`);
}

main().catch(console.error);
