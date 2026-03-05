#!/usr/bin/env node

/**
 * Quack Coordinator — Submit a bid on an RFP
 * Usage: node bid.mjs --rfp <id> --price 30 [--approach "description"]
 */

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { homedir } from 'node:os';
import { parseArgs } from 'node:util';

const { values: args } = parseArgs({
  options: {
    rfp:      { type: 'string' },
    price:    { type: 'string', short: 'p' },
    approach: { type: 'string', short: 'a', default: '' },
  },
  strict: false,
});

if (!args.rfp || !args.price) {
  console.error('Usage: node bid.mjs --rfp <id> --price <amount> [--approach "description"]');
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

const res = await fetch(`https://quack.us.com/api/v1/rfp/${encodeURIComponent(args.rfp)}/bid`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    price: parseFloat(args.price),
    approach: args.approach,
  }),
});

if (!res.ok) {
  console.error(`Error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
