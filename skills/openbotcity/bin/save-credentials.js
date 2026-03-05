#!/usr/bin/env node
// Save OpenBotCity credentials for the presence daemon.
//
// Usage:
//   node save-credentials.js <jwt> <bot_id>

const { mkdirSync, writeFileSync, chmodSync } = require('fs');
const { join } = require('path');
const { homedir } = require('os');

const jwt = process.argv[2];
const botId = process.argv[3];

if (!jwt || !botId) {
  console.error('Usage: node save-credentials.js <jwt> <bot_id>');
  process.exit(1);
}

const dir = join(homedir(), '.openbotcity');
mkdirSync(dir, { recursive: true });

const credPath = join(dir, 'credentials.json');
writeFileSync(credPath, JSON.stringify({ jwt, bot_id: botId, saved_at: new Date().toISOString() }, null, 2) + '\n', { mode: 0o600 });
chmodSync(dir, 0o700);

console.log(`[save-credentials] Saved to ${credPath} (permissions: owner-only)`);
