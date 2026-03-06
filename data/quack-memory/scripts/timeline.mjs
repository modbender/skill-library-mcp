#!/usr/bin/env node
// Quack Memory — View memory timeline via FlightBox
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { argv } from 'process';

const FLIGHTBOX_BASE = 'https://flightbox.replit.app/api/v1/timeline';

function loadCreds() {
  try {
    return JSON.parse(readFileSync(join(homedir(), '.openclaw', 'credentials', 'quack.json'), 'utf8'));
  } catch {
    console.error('No Quack credentials found. Run quack-identity registration first.');
    process.exit(1);
  }
}

async function main() {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--type' && argv[i + 1]) args.type = argv[++i];
    else if (argv[i] === '--limit' && argv[i + 1]) args.limit = argv[++i];
  }

  const creds = loadCreds();
  const params = new URLSearchParams({ agentId: creds.agentId });
  if (args.type) params.set('type', args.type);
  if (args.limit) params.set('limit', args.limit);

  const res = await fetch(`${FLIGHTBOX_BASE}?${params}`, {
    headers: { 'Authorization': `Bearer ${creds.apiKey}` },
  });

  const data = await res.json().catch(() => res.text());
  if (!res.ok) {
    console.error(`Failed (${res.status}):`, data);
    process.exit(1);
  }

  const entries = data.entries || data.results || data;
  if (Array.isArray(entries)) {
    for (const e of entries) {
      const time = e.createdAt ? new Date(e.createdAt).toLocaleString() : '?';
      console.log(`${time} [${e.type}] ${e.content}`);
    }
  } else {
    console.log(JSON.stringify(data, null, 2));
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
