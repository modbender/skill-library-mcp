#!/usr/bin/env node
// Moltbook — Read feed
import { readFileSync } from 'fs';
import { homedir } from 'os';

const API = 'https://www.moltbook.com/api/v1';

function loadKey() {
  try {
    return JSON.parse(readFileSync(`${homedir()}/.config/moltbook/credentials.json`, 'utf8')).api_key;
  } catch {
    console.error('No Moltbook credentials. Register first (see SKILL.md).');
    process.exit(1);
  }
}

async function main() {
  const key = loadKey();
  const limit = process.argv[2] || 20;
  const res = await fetch(`${API}/feed?limit=${limit}`, { headers: { 'x-api-key': key } });
  const data = await res.json().catch(() => ({ status: res.status, body: res.statusText }));
  console.log(JSON.stringify(data, null, 2));
}

main().catch(e => { console.error(e.message); process.exit(1); });
