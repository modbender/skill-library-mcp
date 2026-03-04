#!/usr/bin/env node

/**
 * Quack Wallet — Check agent balance
 * Usage: node balance.mjs [--agent <agentId>]
 */

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { homedir } from 'node:os';
import { parseArgs } from 'node:util';

const { values: args } = parseArgs({
  options: {
    agent: { type: 'string' },
  },
  strict: false,
});

const credsPath = resolve(homedir(), '.openclaw/credentials/quack.json');
let apiKey;
try {
  const creds = JSON.parse(await readFile(credsPath, 'utf8'));
  apiKey = creds.apiKey;
} catch {
  console.error('Missing ~/.openclaw/credentials/quack.json with {"apiKey": "..."}');
  process.exit(1);
}

const agentId = args.agent || apiKey.split('_').slice(1).join('_') || 'me';
const url = `https://quack.us.com/api/v1/agent/${encodeURIComponent(agentId)}/balance`;

const res = await fetch(url, {
  headers: { 'Authorization': `Bearer ${apiKey}` },
});

if (!res.ok) {
  console.error(`Error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
