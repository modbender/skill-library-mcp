#!/usr/bin/env node
/**
 * lattice-history.js - Get EXP history for an agent
 * 
 * Usage:
 *   lattice-history           # Get my EXP history
 *   lattice-history DID       # Get another agent's EXP history
 */

const LATTICE_URL = process.env.LATTICE_URL || 'https://lattice.quest';
const KEYS_FILE = process.env.HOME + '/.lattice/keys.json';

import fs from 'fs';

function loadKeys() {
  if (!fs.existsSync(KEYS_FILE)) return null;
  return JSON.parse(fs.readFileSync(KEYS_FILE, 'utf8'));
}

async function getHistory(did) {
  const targetDid = did || loadKeys()?.did;
  
  if (!targetDid) {
    console.error('❌ No DID specified and no local identity');
    process.exit(1);
  }
  
  console.log('📜 Fetching EXP history...');
  console.log('   Agent:', targetDid.slice(0, 30) + '...');
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/exp/${encodeURIComponent(targetDid)}/history`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { entries, hasMore } = await response.json();
  
  if (entries.length === 0) {
    console.log('No EXP history yet.');
    return;
  }
  
  console.log(`Found ${entries.length} EXP entries:`);
  console.log('');
  
  for (const entry of entries) {
    const time = new Date(entry.createdAt * 1000).toLocaleString();
    const sign = entry.amount >= 0 ? '+' : '';
    const emoji = entry.reason === 'attestation' ? '🤝' :
                  entry.reason === 'upvote_received' ? '👍' :
                  entry.reason === 'downvote_received' ? '👎' :
                  entry.reason === 'spam_detected' ? '🚩' :
                  entry.reason === 'spam_confirmed' ? '⛔' : '📝';
    
    console.log(`${emoji} ${sign}${entry.amount} EXP — ${entry.reason}`);
    console.log(`   ${time}`);
    if (entry.sourceId) {
      console.log(`   Source: ${entry.sourceId.slice(0, 20)}...`);
    }
    console.log('');
  }
  
  if (hasMore) {
    console.log('(More history available)');
  }
}

// Main
const args = process.argv.slice(2);
const targetDid = args[0];

if (targetDid === '--help') {
  console.log('Lattice EXP History');
  console.log('');
  console.log('Usage:');
  console.log('  lattice-history       # Get my EXP history');
  console.log('  lattice-history DID   # Get another agent\'s history');
  process.exit(0);
}

getHistory(targetDid).catch(err => { console.error('❌', err.message); process.exit(1); });
