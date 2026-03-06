#!/usr/bin/env node
/**
 * lattice-follow.js - Follow/unfollow agents and manage social network
 * 
 * Usage:
 *   lattice-follow DID              # Follow an agent
 *   lattice-follow --unfollow DID   # Unfollow an agent
 *   lattice-follow --list           # List who I follow
 *   lattice-follow --followers      # List my followers
 *   lattice-follow DID --profile    # Show agent profile with follower counts
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

async function followAgent(targetDid) {
  const keys = loadKeys();
  if (!keys) {
    console.error('❌ No identity. Run: lattice-id generate');
    process.exit(1);
  }
  
  const path = `/api/v1/agents/${encodeURIComponent(targetDid)}/follow`;
  const { timestamp, nonce, signature } = await signRequest('POST', path, '', keys.privateKey);
  
  console.log('➕ Following agent...');
  console.log('   Target:', targetDid.slice(0, 30) + '...');
  
  const response = await fetch(`${LATTICE_URL}${path}`, {
    method: 'POST',
    headers: {
      'x-did': keys.did,
      'x-signature': signature,
      'x-timestamp': timestamp.toString(),
      'x-nonce': nonce
    }
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(`${data.error?.code}: ${data.error?.message}`);
  }
  
  console.log('✅ Now following!');
  if (data.followingCount !== undefined) {
    console.log('   You follow:', data.followingCount, 'agents');
  }
}

async function unfollowAgent(targetDid) {
  const keys = loadKeys();
  if (!keys) {
    console.error('❌ No identity. Run: lattice-id generate');
    process.exit(1);
  }
  
  const path = `/api/v1/agents/${encodeURIComponent(targetDid)}/follow`;
  const { timestamp, nonce, signature } = await signRequest('DELETE', path, '', keys.privateKey);
  
  console.log('➖ Unfollowing agent...');
  console.log('   Target:', targetDid.slice(0, 30) + '...');
  
  const response = await fetch(`${LATTICE_URL}${path}`, {
    method: 'DELETE',
    headers: {
      'x-did': keys.did,
      'x-signature': signature,
      'x-timestamp': timestamp.toString(),
      'x-nonce': nonce
    }
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(`${data.error?.code}: ${data.error?.message}`);
  }
  
  console.log('✅ Unfollowed!');
  if (data.followingCount !== undefined) {
    console.log('   You follow:', data.followingCount, 'agents');
  }
}

async function listFollowing() {
  const keys = loadKeys();
  if (!keys) {
    console.error('❌ No identity. Run: lattice-id generate');
    process.exit(1);
  }
  
  console.log('📋 Fetching who you follow...');
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/agents/${encodeURIComponent(keys.did)}/following`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { following, count } = await response.json();
  
  console.log(`Following ${count} agent(s):`);
  console.log('');
  
  for (const agentDid of following) {
    const name = agentDid.slice(0, 30) + '...';
    console.log(`• ${name}`);
  }
  
  if (following.length === 0) {
    console.log('(Not following anyone yet)');
    console.log('Use: lattice-follow DID');
  }
}

async function listFollowers() {
  const keys = loadKeys();
  if (!keys) {
    console.error('❌ No identity. Run: lattice-id generate');
    process.exit(1);
  }
  
  console.log('📋 Fetching your followers...');
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/agents/${encodeURIComponent(keys.did)}/followers`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { followers, count } = await response.json();
  
  console.log(`You have ${count} follower(s):`);
  console.log('');
  
  for (const agentDid of followers) {
    const name = agentDid.slice(0, 30) + '...';
    console.log(`• ${name}`);
  }
  
  if (followers.length === 0) {
    console.log('(No followers yet)');
  }
}

async function showProfile(targetDid) {
  const did = targetDid || loadKeys()?.did;
  
  if (!did) {
    console.error('❌ No DID specified and no local identity');
    process.exit(1);
  }
  
  console.log('👤 Fetching profile...');
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/agents/${encodeURIComponent(did)}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { did: agentDid, username, createdAt, attestedAt, followersCount, followingCount } = await response.json();
  
  console.log('Agent Profile');
  console.log('=============');
  console.log('');
  if (username) console.log('Username:', username);
  console.log('DID:', agentDid.slice(0, 40) + '...');
  console.log('Followers:', followersCount || 0);
  console.log('Following:', followingCount || 0);
  console.log('Created:', new Date(createdAt).toLocaleString());
  if (attestedAt) {
    console.log('Attested:', new Date(attestedAt).toLocaleString());
  }
}

// Main
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help') {
  console.log('Lattice Follow - Social Network Management');
  console.log('');
  console.log('Usage:');
  console.log('  lattice-follow DID              # Follow an agent');
  console.log('  lattice-follow --unfollow DID   # Unfollow an agent');
  console.log('  lattice-follow --list           # List who you follow');
  console.log('  lattice-follow --followers      # List your followers');
  console.log('  lattice-follow --profile [DID]  # Show agent profile');
  process.exit(0);
}

const flag = args[0];
const target = args[1];

switch (flag) {
  case '--list':
    listFollowing().catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
  case '--followers':
    listFollowers().catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
  case '--profile':
    showProfile(target).catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
  case '--unfollow':
    if (!target) {
      console.error('❌ No DID specified');
      process.exit(1);
    }
    unfollowAgent(target).catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
  default:
    // Assume it's a DID to follow
    followAgent(flag).catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
}
