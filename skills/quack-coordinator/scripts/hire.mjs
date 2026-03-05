#!/usr/bin/env node

/**
 * Quack Coordinator — Hire an agent from a bid
 * Usage: node hire.mjs --bid <id>
 */

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { homedir } from 'node:os';
import { parseArgs } from 'node:util';

const { values: args } = parseArgs({
  options: {
    bid: { type: 'string', short: 'b' },
  },
  strict: false,
});

if (!args.bid) {
  console.error('Usage: node hire.mjs --bid <id>');
  process.exit(1);
}

const credsPath = resolve(homedir(), '.openclaw/credentials/quack.json');
let apiKey;
try {
  const creds = JSON.parse(await readFile(credsPath, 'utf8'));
  apiKey = creds.apiKey;
} catch {
  console.error('Missing ~/.openclaw/credentials/quack.json');
  process.exit(1);
}

const res = await fetch(`https://quack.us.com/api/v1/bids/${encodeURIComponent(args.bid)}/hire`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  },
});

if (!res.ok) {
  console.error(`Error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
