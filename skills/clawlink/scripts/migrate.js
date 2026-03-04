#!/usr/bin/env node
/**
 * ClawLink Migration Script
 * 
 * Migrates data from old ~/.clawdbot/clawlink to ~/.openclaw/clawlink
 * Safe to run multiple times - only copies if source exists and dest doesn't
 */

import { existsSync, mkdirSync, copyFileSync, readdirSync, statSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const OLD_DIR = join(homedir(), '.clawdbot', 'clawlink');
const NEW_DIR = join(homedir(), '.openclaw', 'clawlink');

function copyDir(src, dest) {
  mkdirSync(dest, { recursive: true });
  const entries = readdirSync(src);
  
  for (const entry of entries) {
    const srcPath = join(src, entry);
    const destPath = join(dest, entry);
    
    if (statSync(srcPath).isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      if (!existsSync(destPath)) {
        copyFileSync(srcPath, destPath);
        console.log(`  Copied: ${entry}`);
      } else {
        console.log(`  Skipped (exists): ${entry}`);
      }
    }
  }
}

function main() {
  console.log('🔗 ClawLink Migration');
  console.log('='.repeat(50));
  console.log(`Old location: ${OLD_DIR}`);
  console.log(`New location: ${NEW_DIR}`);
  console.log('');
  
  // Check if old directory exists
  if (!existsSync(OLD_DIR)) {
    console.log('✓ No old data found at ~/.clawdbot/clawlink');
    console.log('  Nothing to migrate.');
    return;
  }
  
  // Check if it's actually the same directory (symlink)
  try {
    const oldReal = readdirSync(OLD_DIR);
    if (existsSync(NEW_DIR)) {
      const newReal = readdirSync(NEW_DIR);
      if (JSON.stringify(oldReal.sort()) === JSON.stringify(newReal.sort())) {
        console.log('✓ Old and new directories contain the same files');
        console.log('  (likely ~/.clawdbot is symlinked to ~/.openclaw)');
        console.log('  No migration needed.');
        return;
      }
    }
  } catch (e) {
    // Continue with migration
  }
  
  // Check if new directory already has data
  if (existsSync(NEW_DIR) && existsSync(join(NEW_DIR, 'identity.json'))) {
    console.log('⚠ Data already exists at ~/.openclaw/clawlink');
    console.log('  Will not overwrite. Manual merge may be needed.');
    return;
  }
  
  // Migrate
  console.log('Migrating data...');
  try {
    copyDir(OLD_DIR, NEW_DIR);
    console.log('');
    console.log('✓ Migration complete!');
    console.log('');
    console.log('Your old data is still at ~/.clawdbot/clawlink');
    console.log('You can delete it after verifying everything works.');
  } catch (err) {
    console.error('✖ Migration failed:', err.message);
    process.exit(1);
  }
}

main();
