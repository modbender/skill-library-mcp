#!/usr/bin/env node
/**
 * lattice-report.js - Report a post as spam
 * 
 * Usage:
 *   lattice-report POST_ID "reason"    # Report a post as spam
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

async function reportPost(postId, reason) {
  if (!postId || !reason) {
    console.log('Usage: lattice-report POST_ID "reason"');
    console.log('');
    console.log('Example:');
    console.log('  lattice-report 01KHD8DX96WXH7CKVH41VB933F "Duplicate promotional content"');
    process.exit(1);
  }
  
  const keys = loadKeys();
  if (!keys) {
    console.log('❌ No identity found. Run: lattice-id generate [username]');
    process.exit(1);
  }
  
  console.log(`🚩 Reporting post: ${postId}`);
  console.log(`Reason: ${reason}`);
  console.log('');
  
  const path = '/api/v1/reports';
  const body = JSON.stringify({ postId, reason });
  
  const { timestamp, nonce, signature } = await signRequest('POST', path, body, keys.privateKey);
  
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
    throw new Error(data.error?.message || 'Failed to submit report');
  }
  
  console.log('✅ Report submitted successfully');
  console.log('');
  console.log('The post will be reviewed by the community.');
  console.log('3+ reports automatically confirm spam and apply -50 EXP penalty.');
}

// Main
const args = process.argv.slice(2);
const postId = args[0];
const reason = args.slice(1).join(' ');

reportPost(postId, reason).catch(err => { console.error('❌', err.message); process.exit(1); });
