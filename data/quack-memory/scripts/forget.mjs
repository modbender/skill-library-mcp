#!/usr/bin/env node
// Quack Memory — Delete a memory via FlightBox
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { argv } from 'process';

const FLIGHTBOX_BASE = 'https://flightbox.replit.app/api/v1/forget';

function loadCreds() {
  try {
    return JSON.parse(readFileSync(join(homedir(), '.openclaw', 'credentials', 'quack.json'), 'utf8'));
  } catch {
    console.error('No Quack credentials found. Run quack-identity registration first.');
    process.exit(1);
  }
}

async function main() {
  let memoryId;
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--id' && argv[i + 1]) memoryId = argv[++i];
  }
  if (!memoryId) {
    console.error('Usage: forget.mjs --id <memoryId>');
    process.exit(1);
  }

  const creds = loadCreds();
  const params = new URLSearchParams({ agentId: creds.agentId, id: memoryId });

  const res = await fetch(`${FLIGHTBOX_BASE}?${params}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${creds.apiKey}` },
  });

  if (res.ok) {
    console.log(`✅ Memory ${memoryId} deleted.`);
  } else {
    const data = await res.json().catch(() => res.text());
    console.error(`Failed (${res.status}):`, data);
    process.exit(1);
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
