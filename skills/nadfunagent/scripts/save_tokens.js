#!/usr/bin/env node
/**
 * Append found tokens to found_tokens.json. Reads token addresses (0x...) one per line from stdin.
 * Data dir: NADFUNAGENT_DATA_DIR env or $HOME/nadfunagent. Keeps last 100 scans.
 * Usage: echo -e "0x...\n0x..." | node save_tokens.js
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const DATA_DIR = process.env.NADFUNAGENT_DATA_DIR || path.join(os.homedir(), 'nadfunagent');
const FILE_PATH = path.join(DATA_DIR, 'found_tokens.json');

async function main() {
  let data = [];
  if (fs.existsSync(FILE_PATH)) {
    try {
      const raw = fs.readFileSync(FILE_PATH, 'utf-8').trim();
      if (raw) data = JSON.parse(raw);
    } catch {}
  }
  if (!Array.isArray(data)) data = [];

  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const input = Buffer.concat(chunks).toString('utf-8');
  const tokens = input.split(/\r?\n/).map(s => s.trim()).filter(s => s && s.startsWith('0x'));

  if (tokens.length === 0) {
    console.error('No tokens provided');
    process.exit(1);
  }

  const logEntry = {
    timestamp: new Date().toISOString().replace(/\.\d{3}Z$/, '.000Z'),
    totalFound: tokens.length,
    tokens: tokens.slice(0, 50).map(t => ({ address: t, foundInMethods: 1 }))
  };
  data.push(logEntry);
  data = data.slice(-100);

  const dir = path.dirname(FILE_PATH);
  if (dir) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(FILE_PATH, JSON.stringify(data, null, 2), 'utf-8');

  console.log(`Saved ${tokens.length} tokens to ${FILE_PATH}`);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
