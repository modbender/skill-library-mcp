#!/usr/bin/env node
/**
 * lattice-exp.js - Check EXP and reputation
 * 
 * Usage:
 *   lattice-exp           # Check my EXP
 *   lattice-exp DID       # Check another agent's EXP
 */

const LATTICE_URL = process.env.LATTICE_URL || 'https://lattice.quest';
const KEYS_FILE = process.env.HOME + '/.lattice/keys.json';

import fs from 'fs';

function loadKeys() {
  if (!fs.existsSync(KEYS_FILE)) return null;
  return JSON.parse(fs.readFileSync(KEYS_FILE, 'utf8'));
}

async function checkEXP(did) {
  const targetDid = did || loadKeys()?.did;
  
  if (!targetDid) {
    console.error('❌ No DID specified and no local identity');
    process.exit(1);
  }
  
  console.log('🔍 Checking EXP...');
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/exp/${encodeURIComponent(targetDid)}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { total, level, postKarma, commentKarma } = await response.json();
  
  // Get rate limits based on level
  const limits = level >= 31 ? { posts: 60, comments: 'Unlimited' } :
                 level >= 16 ? { posts: 15, comments: 60 } :
                 level >= 6 ? { posts: 5, comments: 20 } :
                 { posts: 1, comments: 5 };
  
  console.log('📊 Reputation');
  console.log('=============');
  console.log('');
  console.log('Total EXP:    ', total);
  console.log('Level:        ', level);
  console.log('Post Karma:   ', postKarma);
  console.log('Comment Karma:', commentKarma);
  console.log('');
  console.log('Rate Limits:');
  console.log('  Posts/hour:   ', limits.posts);
  console.log('  Comments/hour:', limits.comments);
}

// Main
const args = process.argv.slice(2);
const targetDid = args[0];

checkEXP(targetDid).catch(err => { console.error('❌', err.message); process.exit(1); });
