#!/usr/bin/env node
/**
 * ClawLink Uninstall Script
 * 
 * Removes ClawLink heartbeat polling from user's HEARTBEAT.md
 * Run: node scripts/uninstall.js
 */

import { existsSync, readFileSync, writeFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const CLAWD_DIR = join(homedir(), 'clawd');
const HEARTBEAT_FILE = join(CLAWD_DIR, 'HEARTBEAT.md');

function main() {
  console.log('🔗 ClawLink Uninstall');
  console.log('='.repeat(50));
  
  // Check if HEARTBEAT.md exists
  if (!existsSync(HEARTBEAT_FILE)) {
    console.log('⚠ HEARTBEAT.md not found at', HEARTBEAT_FILE);
    console.log('  Nothing to uninstall.');
    return;
  }
  
  const content = readFileSync(HEARTBEAT_FILE, 'utf8');
  
  // Check if ClawLink is installed
  if (!content.includes('ClawLink') && !content.includes('clawlink')) {
    console.log('✓ ClawLink not found in HEARTBEAT.md');
    console.log('  Nothing to uninstall.');
    return;
  }
  
  // Remove ClawLink section
  // Pattern: ## ClawLink followed by content until next ## or end of file
  const clawlinkPattern = /\n*## ClawLink[\s\S]*?(?=\n## |\n# |$)/gi;
  
  // Also handle inline references
  const inlinePattern = /^.*clawlink.*\n?/gim;
  
  let newContent = content.replace(clawlinkPattern, '');
  
  // Clean up any double newlines left behind
  newContent = newContent.replace(/\n{3,}/g, '\n\n');
  
  // Trim trailing whitespace
  newContent = newContent.trimEnd() + '\n';
  
  writeFileSync(HEARTBEAT_FILE, newContent);
  
  console.log('✓ Removed ClawLink from HEARTBEAT.md');
  console.log('');
  console.log('ClawLink heartbeat polling disabled.');
  console.log('');
  console.log('Note: Your identity and friends are still in ~/.openclaw/clawlink/');
  console.log('      Delete that directory to fully remove ClawLink data.');
}

main();
