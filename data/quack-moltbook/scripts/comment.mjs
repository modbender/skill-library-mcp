#!/usr/bin/env node
// Moltbook — Comment on a post
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
    if (argv[i] === '--post-id' && argv[i + 1]) args.postId = argv[++i];
    else if (argv[i] === '--content' && argv[i + 1]) args.content = argv[++i];
  }
  return args;
}

async function main() {
  const args = parseArgs();
  if (!args.postId || !args.content) {
    console.error('Usage: comment.mjs --post-id <id> --content <text>');
    process.exit(1);
  }
  const key = loadKey();
  const res = await fetch(`${API}/posts/${args.postId}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': key },
    body: JSON.stringify({ content: args.content }),
  });
  const data = await res.json().catch(() => ({ status: res.status, body: res.statusText }));
  console.log(JSON.stringify(data, null, 2));
}

main().catch(e => { console.error(e.message); process.exit(1); });
