#!/usr/bin/env node
/**
 * MindGraph Maintenance Helper
 * Batches common maintenance tasks into a single call.
 * Usage: node scripts/maintenance.js --extract <path> --dream --watchdog
 */

const mg = require('./mindgraph-client.js');
const { execSync } = require('child_process');

async function run() {
  const args = process.argv.slice(2);
  
  if (args.includes('--watchdog')) {
    try { await mg.health(); } 
    catch (e) {
      console.log("🚨 MindGraph server down. Restarting...");
      execSync('bash scripts/start.sh &', { stdio: 'inherit' });
    }
  }

  if (args.includes('--extract')) {
    const path = args[args.indexOf('--extract') + 1];
    console.log(`🧠 Extracting from ${path}...`);
    execSync(`node scripts/extract.js ${path}`, { stdio: 'inherit' });
  }

  if (args.includes('--dream')) {
    console.log("😴 Triggering graph dreaming/optimization...");
    // Future-proofing for server-side dreaming trigger
  }
}

run();
