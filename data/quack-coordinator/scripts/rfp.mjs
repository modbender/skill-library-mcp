#!/usr/bin/env node

/**
 * Quack Coordinator — Post a Request for Proposals
 * Usage: node rfp.mjs --task "Review this code" --budget 50
 */

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { homedir } from 'node:os';
import { parseArgs } from 'node:util';

const { values: args } = parseArgs({
  options: {
    task:   { type: 'string', short: 't' },
    budget: { type: 'string', short: 'b' },
  },
  strict: false,
});

if (!args.task || !args.budget) {
  console.error('Usage: node rfp.mjs --task "description" --budget <amount>');
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

const res = await fetch('https://quack.us.com/api/v1/rfp', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    task: args.task,
    budget: parseFloat(args.budget),
  }),
});

if (!res.ok) {
  console.error(`Error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
