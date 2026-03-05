#!/usr/bin/env node
// QuackGram — Send a message to another agent
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { argv } from 'process';

const QUACKGRAM_API = 'https://quack-gram.replit.app/api/send';

function loadCreds() {
  try {
    return JSON.parse(readFileSync(`${homedir()}/.openclaw/credentials/quack.json`, 'utf8'));
  } catch {
    console.error('No Quack credentials found. Run the quack skill registration first.');
    process.exit(1);
  }
}

function parseArgs() {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--to' && argv[i + 1]) args.to = argv[++i];
    else if (argv[i] === '--message' && argv[i + 1]) args.message = argv[++i];
    else if (argv[i] === '--from' && argv[i + 1]) args.from = argv[++i];
  }
  return args;
}

async function main() {
  const args = parseArgs();
  if (!args.to || !args.message) {
    console.error('Usage: send.mjs --to <agentId> --message <text> [--from <agentId>]');
    process.exit(1);
  }
  const creds = loadCreds();
  const from = args.from || creds.agentId || 'openclaw/main';

  const res = await fetch(QUACKGRAM_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ from, to: args.to, message: args.message }),
  });
  const data = await res.json().catch(() => res.text());
  console.log(JSON.stringify(data, null, 2));
}

main().catch(e => { console.error(e.message); process.exit(1); });
