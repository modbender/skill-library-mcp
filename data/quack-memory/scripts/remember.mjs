#!/usr/bin/env node
// Quack Memory — Store a memory via FlightBox
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { argv } from 'process';

const FLIGHTBOX_URL = 'https://flightbox.replit.app/api/v1/remember';

function loadCreds() {
  try {
    return JSON.parse(readFileSync(join(homedir(), '.openclaw', 'credentials', 'quack.json'), 'utf8'));
  } catch {
    console.error('No Quack credentials found. Run quack-identity registration first.');
    process.exit(1);
  }
}

function parseArgs() {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--type' && argv[i + 1]) args.type = argv[++i];
    else if (argv[i] === '--content' && argv[i + 1]) args.content = argv[++i];
    else if (argv[i] === '--tags' && argv[i + 1]) args.tags = argv[++i].split(',');
    else if (argv[i] === '--importance' && argv[i + 1]) args.importance = parseFloat(argv[++i]);
  }
  return args;
}

async function main() {
  const args = parseArgs();
  if (!args.content) {
    console.error('Usage: remember.mjs --content "memory text" [--type lesson|fact|decision|todo|context] [--tags "a,b"] [--importance 0.8]');
    process.exit(1);
  }

  const creds = loadCreds();
  const body = {
    agentId: creds.agentId,
    type: args.type || 'context',
    content: args.content,
    metadata: {},
  };
  if (args.tags) body.metadata.tags = args.tags;
  if (args.importance != null) body.metadata.importance = args.importance;

  const res = await fetch(FLIGHTBOX_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${creds.apiKey}`,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => res.text());
  if (!res.ok) {
    console.error(`Failed (${res.status}):`, data);
    process.exit(1);
  }

  console.log(`✅ Memory stored: ${data.id || 'ok'}`);
  console.log(JSON.stringify(data, null, 2));
}

main().catch(e => { console.error(e.message); process.exit(1); });
