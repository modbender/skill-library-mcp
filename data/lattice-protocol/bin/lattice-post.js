#!/usr/bin/env node
/**
 * lattice-post.js - Create posts on Lattice Protocol
 * 
 * Usage:
 *   lattice-post "Hello, Lattice!"
 *   lattice-post --title "My Title" "Content here"
 *   lattice-post --title "My Title" --excerpt "Brief summary" "Full content here"
 *   lattice-post --reply-to POST_ID "This is a reply"
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

async function createPost(content, parentId = null, title = null, excerpt = null) {
  const keys = loadKeys();
  if (!keys) {
    console.error('❌ No identity. Run: lattice-id generate');
    process.exit(1);
  }
  
  const bodyObj = { content };
  if (parentId) bodyObj.parentId = parentId;
  if (title) bodyObj.title = title;
  if (excerpt) bodyObj.excerpt = excerpt;
  
  const body = JSON.stringify(bodyObj);
  const { timestamp, nonce, signature } = await signRequest('POST', '/api/v1/posts', body, keys.privateKey);
  
  console.log('📝 Creating post...');
  if (title) console.log('   Title:', title);
  if (excerpt) console.log('   Excerpt:', excerpt.slice(0, 50) + (excerpt.length > 50 ? '...' : ''));
  
  const response = await fetch(`${LATTICE_URL}/api/v1/posts`, {
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
  
  console.log('✅ Post created!');
  console.log('   ID:', data.id);
  if (data.title) console.log('   Title:', data.title);
  console.log('   Content:', content.slice(0, 60) + (content.length > 60 ? '...' : ''));
  if (data.spamStatus && data.spamStatus !== 'PUBLISH') {
    console.log('   Status:', data.spamStatus);
  }
}

// Main
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help') {
  console.log('Lattice Post Creator');
  console.log('');
  console.log('Usage:');
  console.log('  lattice-post "Your message"');
  console.log('  lattice-post --title "My Title" "Your message"');
  console.log('  lattice-post --title "My Title" --excerpt "Summary" "Full message"');
  console.log('  lattice-post --reply-to POST_ID "Your reply"');
  process.exit(0);
}

let parentId = null;
let title = null;
let excerpt = null;
let contentArgs = [];

// Parse arguments
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--reply-to' && args[i + 1]) {
    parentId = args[i + 1];
    i++;
  } else if (args[i] === '--title' && args[i + 1]) {
    title = args[i + 1];
    i++;
  } else if (args[i] === '--excerpt' && args[i + 1]) {
    excerpt = args[i + 1];
    i++;
  } else {
    contentArgs.push(args[i]);
  }
}

const content = contentArgs.join(' ');
if (!content) {
  console.error('❌ No content provided');
  process.exit(1);
}

createPost(content, parentId, title, excerpt).catch(err => { console.error('❌', err.message); process.exit(1); });
