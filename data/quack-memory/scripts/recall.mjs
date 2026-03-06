#!/usr/bin/env node
// Quack Memory — Recall memories via FlightBox semantic search
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { argv } from 'process';

const FLIGHTBOX_BASE = 'https://flightbox.replit.app/api/v1/recall';

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
    if (argv[i] === '--query' && argv[i + 1]) args.query = argv[++i];
    else if (argv[i] === '--type' && argv[i + 1]) args.type = argv[++i];
    else if (argv[i] === '--limit' && argv[i + 1]) args.limit = argv[++i];
  }
  return args;
}

async function main() {
  const args = parseArgs();
  if (!args.query) {
    console.error('Usage: recall.mjs --query "what to search for" [--type fact] [--limit 5]');
    process.exit(1);
  }

  const creds = loadCreds();
  const params = new URLSearchParams({
    agentId: creds.agentId,
    query: args.query,
  });
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

  const memories = data.results || data;
  if (Array.isArray(memories) && memories.length === 0) {
    console.log('No memories found matching your query.');
    return;
  }

  console.log(`Found ${Array.isArray(memories) ? memories.length : '?'} memories:\n`);
  if (Array.isArray(memories)) {
    for (const m of memories) {
      console.log(`[${m.type || '?'}] ${m.content}`);
      if (m.metadata?.tags) console.log(`  Tags: ${m.metadata.tags.join(', ')}`);
      console.log(`  ID: ${m.id} | Created: ${m.createdAt || '?'}\n`);
    }
  } else {
    console.log(JSON.stringify(data, null, 2));
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
