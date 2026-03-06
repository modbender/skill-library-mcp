#!/usr/bin/env node

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { homedir } from 'node:os';
import { parseArgs } from 'node:util';

const { values: args } = parseArgs({
  options: {
    challenge: { type: 'string', short: 'c' },
    proof:     { type: 'string', short: 'p' },
  },
  strict: false,
});

if (!args.challenge || !args.proof) {
  console.error('Usage: node submit.mjs --challenge <id> --proof "description"');
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

const url = `https://quack.us.com/api/v1/challenges/${encodeURIComponent(args.challenge)}/submit`;
const res = await fetch(url, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ proof: args.proof }),
});

if (!res.ok) {
  console.error(`Error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
