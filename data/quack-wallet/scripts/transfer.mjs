#!/usr/bin/env node

/**
 * Quack Wallet — Transfer tokens
 * Usage: node transfer.mjs --to "recipient/main" --amount 10 --memo "Payment"
 */

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { homedir } from 'node:os';
import { parseArgs } from 'node:util';

const { values: args } = parseArgs({
  options: {
    to:     { type: 'string' },
    amount: { type: 'string' },
    memo:   { type: 'string', default: '' },
    agent:  { type: 'string' },
  },
  strict: false,
});

if (!args.to || !args.amount) {
  console.error('Usage: node transfer.mjs --to <recipient> --amount <number> [--memo "reason"]');
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

const agentId = args.agent || apiKey.split('_').slice(1).join('_') || 'me';
const url = `https://quack.us.com/api/v1/agent/${encodeURIComponent(agentId)}/transfer`;

const res = await fetch(url, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    to: args.to,
    amount: parseFloat(args.amount),
    memo: args.memo,
  }),
});

if (!res.ok) {
  console.error(`Error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
