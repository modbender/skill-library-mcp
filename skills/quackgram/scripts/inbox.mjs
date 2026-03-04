#!/usr/bin/env node
// QuackGram — Check agent inbox
import { readFileSync } from 'fs';
import { homedir } from 'os';

const QUACKGRAM_API = 'https://quack-gram.replit.app/api/inbox';

function loadCreds() {
  try {
    return JSON.parse(readFileSync(`${homedir()}/.openclaw/credentials/quack.json`, 'utf8'));
  } catch {
    console.error('No Quack credentials found. Run the quack skill registration first.');
    process.exit(1);
  }
}

async function main() {
  const creds = loadCreds();
  const agentId = process.argv[2] || creds.agentId || 'openclaw/main';

  const res = await fetch(`${QUACKGRAM_API}/${encodeURIComponent(agentId)}`);
  const data = await res.json().catch(() => res.text());
  console.log(JSON.stringify(data, null, 2));
}

main().catch(e => { console.error(e.message); process.exit(1); });
