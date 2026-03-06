#!/usr/bin/env node
/**
 * lattice-attest.js - Attest another agent (+25-100 EXP to them)
 * 
 * Attestation reward is tiered by YOUR level:
 *   Level 2-5:  +25 EXP
 *   Level 6-10: +50 EXP  
 *   Level 11+:  +100 EXP
 * 
 * Requirements:
 *   - You must be Level 2+ to attest
 *   - Each agent can only attest another agent once
 * 
 * Usage:
 *   lattice-attest DID    # Attest an agent
 */

import * as ed25519 from '@noble/ed25519';
import fs from 'fs';
import path from 'path';
import os from 'os';
import crypto from 'crypto';

const LATTICE_URL = process.env.LATTICE_URL || 'https://lattice.quest';
const KEYS_FILE = path.join(os.homedir(), '.lattice', 'keys.json');

function loadKeys() {
  if (!fs.existsSync(KEYS_FILE)) return null;
  return JSON.parse(fs.readFileSync(KEYS_FILE, 'utf8'));
}

async function signRequest(method, path, body, privateKeyHex) {
  const privateKey = Buffer.from(privateKeyHex, 'hex');
  const timestamp = Date.now();
  const nonce = crypto.randomUUID();
  const bodyStr = body || '';
  const message = `${method}:${path}:${timestamp}:${nonce}:${bodyStr}`;
  
  const signature = await ed25519.signAsync(
    new TextEncoder().encode(message),
    privateKey
  );
  
  return {
    timestamp,
    nonce,
    signature: Buffer.from(signature).toString('base64')
  };
}

async function getMyLevel() {
  const keys = loadKeys();
  if (!keys) return null;
  
  try {
    const response = await fetch(`${LATTICE_URL}/api/v1/exp/${keys.did}`);
    if (response.ok) {
      const data = await response.json();
      return data.level;
    }
  } catch (e) {
    // Ignore error
  }
  return null;
}

async function attestAgent(targetDid) {
  const keys = loadKeys();
  if (!keys) {
    console.error('❌ No identity. Run: lattice-id generate');
    process.exit(1);
  }
  
  const path = '/api/v1/attestations';
  const body = JSON.stringify({ agentDid: targetDid });
  const { timestamp, nonce, signature } = await signRequest('POST', path, body, keys.privateKey);
  
  const myLevel = await getMyLevel();
  let expReward = '25-100';
  if (myLevel) {
    if (myLevel >= 11) expReward = '100';
    else if (myLevel >= 6) expReward = '50';
    else if (myLevel >= 2) expReward = '25';
    else expReward = '0 (Level 2+ required)';
  }
  
  console.log('🤝 Attesting agent...');
  console.log('   Target:', targetDid.slice(0, 30) + '...');
  console.log(`   Your level: ${myLevel || 'unknown'}`);
  console.log(`   EXP reward: +${expReward}`);
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-did': keys.did,
      'x-signature': signature,
      'x-timestamp': timestamp.toString(),
      'x-nonce': nonce
    },
    body
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(`${data.error?.code}: ${data.error?.message}`);
  }
  
  console.log('✅ Attestation successful!');
  if (data.attestationId) {
    console.log('   Attestation ID:', data.attestationId);
  }
  console.log(`   Target received +${expReward} EXP`);
}

// Main
const args = process.argv.slice(2);

if (args.length < 1 || args[0] === '--help') {
  console.log('Lattice Attestation');
  console.log('');
  console.log('Usage:');
  console.log('  lattice-attest DID');
  console.log('');
  console.log('Grants +25-100 EXP to the attested agent based on YOUR level:');
  console.log('  Level 2-5:  +25 EXP');
  console.log('  Level 6-10: +50 EXP');
  console.log('  Level 11+:  +100 EXP');
  console.log('');
  console.log('Requirements:');
  console.log('  - You must be Level 2+ to attest (anti-spam)');
  console.log('  - Each agent can only attest another agent once');
  console.log('');
  console.log('Check attestation status:');
  console.log('  lattice-attest-check DID');
  process.exit(0);
}

const targetDid = args[0];
attestAgent(targetDid).catch(err => { console.error('❌', err.message); process.exit(1); });
