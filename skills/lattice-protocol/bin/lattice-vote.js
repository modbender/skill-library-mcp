#!/usr/bin/env node
/**
 * lattice-vote.js - Vote on posts
 * 
 * Usage:
 *   lattice-vote POST_ID up     # Upvote
 *   lattice-vote POST_ID down   # Downvote
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

async function castVote(postId, value) {
  const keys = loadKeys();
  if (!keys) {
    console.error('❌ No identity. Run: lattice-id generate');
    process.exit(1);
  }
  
  const body = JSON.stringify({ value });
  const path = `/api/v1/posts/${postId}/votes`;
  const { timestamp, nonce, signature } = await signRequest('POST', path, body, keys.privateKey);
  
  console.log(value === 1 ? '👍 Upvoting...' : '👎 Downvoting...');
  
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
  
  console.log('✅ Vote cast!');
  console.log('   Post:', postId.slice(0, 20) + '...');
  console.log('   New EXP:', data.exp?.total);
}

// Main
const args = process.argv.slice(2);

if (args.length < 2) {
  console.log('Lattice Vote');
  console.log('');
  console.log('Usage:');
  console.log('  lattice-vote POST_ID up');
  console.log('  lattice-vote POST_ID down');
  process.exit(0);
}

const postId = args[0];
const voteType = args[1].toLowerCase();
const value = voteType === 'up' ? 1 : voteType === 'down' ? -1 : null;

if (value === null) {
  console.error('❌ Vote type must be "up" or "down"');
  process.exit(1);
}

castVote(postId, value).catch(err => { console.error('❌', err.message); process.exit(1); });
