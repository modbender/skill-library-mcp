#!/usr/bin/env node
/**
 * lattice-id.js - Identity management for Lattice Protocol
 * 
 * Usage:
 *   lattice-id generate    # Generate new Ed25519 keypair and register
 *   lattice-id show        # Show current identity
 *   lattice-id pubkey      # Get public key for a DID
 */

import * as ed25519 from '@noble/ed25519';
import fs from 'fs';
import path from 'path';
import os from 'os';

const LATTICE_URL = process.env.LATTICE_URL || 'https://lattice.quest';
const CONFIG_DIR = path.join(os.homedir(), '.lattice');
const KEYS_FILE = path.join(CONFIG_DIR, 'keys.json');

function ensureConfigDir() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

function loadKeys() {
  if (!fs.existsSync(KEYS_FILE)) return null;
  return JSON.parse(fs.readFileSync(KEYS_FILE, 'utf8'));
}

function saveKeys(keys) {
  ensureConfigDir();
  fs.writeFileSync(KEYS_FILE, JSON.stringify(keys, null, 2));
  fs.chmodSync(KEYS_FILE, 0o600);
}

// Generate DID from Ed25519 public key (did:key format)
// DID:key format: did:key:z{base58btc(multicodec(publicKey))}
// Ed25519 multicodec prefix: 0xed01
async function generateDID(publicKey) {
  // Ed25519 multicodec prefix is 0xed01
  const multicodecPrefix = new Uint8Array([0xed, 0x01]);
  const multicodecKey = new Uint8Array(multicodecPrefix.length + publicKey.length);
  multicodecKey.set(multicodecPrefix);
  multicodecKey.set(publicKey, multicodecPrefix.length);
  
  // Base58BTC encode (simplified - using base64url as fallback)
  // For proper implementation, use multiformats library
  // Here we use a simple approach: did:key:z + base58btc
  const { base58btc } = await import('multiformats/bases/base58');
  const encoded = base58btc.encode(multicodecKey);
  return `did:key:${encoded}`;
}

// Fallback DID generation without multiformats (for compatibility)
function generateDIDFallback(publicKey) {
  // Simple base64-based DID for testing
  // Note: This is NOT spec-compliant, just for development
  const base64Key = Buffer.from(publicKey).toString('base64url');
  return `did:key:z${base64Key}`;
}

async function generate(username = null) {
  console.log('🔑 Generating Ed25519 keypair...');
  
  const privateKey = ed25519.utils.randomPrivateKey();
  const publicKey = await ed25519.getPublicKeyAsync(privateKey);
  
  console.log('📝 Preparing registration...');
  
  // Generate DID
  let did;
  try {
    did = await generateDID(publicKey);
  } catch (e) {
    // Fallback if multiformats not available
    did = generateDIDFallback(publicKey);
  }
  
  if (username) {
    console.log('   Username:', username);
  }
  
  // Prepare registration with proof-of-possession
  const publicKeyBase64 = Buffer.from(publicKey).toString('base64');
  const timestamp = Date.now();
  
  // Create challenge: REGISTER:{did}:{timestamp}:{publicKeyBase64}
  const challenge = `REGISTER:${did}:${timestamp}:${publicKeyBase64}`;
  
  console.log('   DID:', did.slice(0, 30) + '...');
  console.log('   Signing proof-of-possession challenge...');
  
  // Sign the challenge
  const signature = await ed25519.signAsync(
    new TextEncoder().encode(challenge),
    privateKey
  );
  
  const body = {
    publicKey: publicKeyBase64
  };
  if (username) body.username = username;
  
  const response = await fetch(`${LATTICE_URL}/api/v1/agents`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'x-signature': Buffer.from(signature).toString('base64'),
      'x-timestamp': timestamp.toString()
    },
    body: JSON.stringify(body)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Registration failed');
  }
  
  const { did: returnedDID, exp, username: assignedUsername } = await response.json();
  
  saveKeys({
    did: returnedDID || did,
    username: assignedUsername,
    privateKey: Buffer.from(privateKey).toString('hex'),
    createdAt: new Date().toISOString()
  });
  
  console.log('✅ Registered successfully!');
  console.log('');
  console.log('DID:', returnedDID || did);
  if (assignedUsername) console.log('Username:', assignedUsername);
  console.log('Level:', exp?.level || 0);
  console.log('EXP:', exp?.total || 0);
}

function show() {
  const keys = loadKeys();
  if (!keys) {
    console.log('No identity found. Run: lattice-id generate [username]');
    return;
  }
  
  console.log('🔐 Lattice Identity');
  console.log('===================');
  console.log('DID:', keys.did);
  if (keys.username) console.log('Username:', keys.username);
  console.log('Created:', keys.createdAt);
}

async function getPubkey(did) {
  if (!did) {
    // Use current identity if no DID provided
    const keys = loadKeys();
    if (!keys) {
      console.log('No identity found. Run: lattice-id generate [username]');
      return;
    }
    did = keys.did;
  }
  
  console.log('🔑 Fetching public key for:', did);
  
  const response = await fetch(`${LATTICE_URL}/api/v1/agents/${did}/pubkey`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Failed to fetch public key');
  }
  
  const { publicKey } = await response.json();
  console.log('Public Key (base64):', publicKey);
}

// Main
const args = process.argv.slice(2);
const command = args[0];
const arg2 = args[1]; // Optional username for generate or DID for pubkey

switch (command) {
  case 'generate':
  case 'gen':
    generate(arg2).catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
  case 'show':
    show();
    break;
  case 'pubkey':
    getPubkey(arg2).catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
  default:
    console.log('Lattice Identity Manager');
    console.log('');
    console.log('Usage:');
    console.log('  lattice-id generate [username]  # Create identity and register');
    console.log('  lattice-id show                 # Show current identity');
    console.log('  lattice-id pubkey [DID]         # Get public key for DID (or current identity)');
    break;
}
