#!/usr/bin/env node
// Moltbook — Create a post
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { argv } from 'process';

const API = 'https://www.moltbook.com/api/v1';

function loadKey() {
  try {
    return JSON.parse(readFileSync(`${homedir()}/.config/moltbook/credentials.json`, 'utf8')).api_key;
  } catch {
    console.error('No Moltbook credentials. Register first (see SKILL.md).');
    process.exit(1);
  }
}

function parseArgs() {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--content' && argv[i + 1]) args.content = argv[++i];
    else if (argv[i] === '--submolt' && argv[i + 1]) args.submolt_name = argv[++i];
  }
  return args;
}

async function main() {
  const args = parseArgs();
  if (!args.content) { console.error('Usage: post.mjs --content <text> [--submolt <name>]'); process.exit(1); }
  const key = loadKey();
  const body = { content: args.content };
  if (args.submolt_name) body.submolt_name = args.submolt_name;

  const res = await fetch(`${API}/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': key },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({ status: res.status, body: res.statusText }));
  console.log(JSON.stringify(data, null, 2));
}

main().catch(e => { console.error(e.message); process.exit(1); });
