#!/usr/bin/env node
// Quack Identity — Register an agent on the Quack Network via Agent Card Builder
import { writeFileSync, readFileSync, mkdirSync, existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { argv } from 'process';

const REGISTER_URL = 'https://agent-card-builder.replit.app/api/register';
const CREDS_DIR = join(homedir(), '.openclaw', 'credentials');
const CREDS_FILE = join(CREDS_DIR, 'quack.json');

function parseArgs() {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--agent' && argv[i + 1]) args.agentId = argv[++i];
    else if (argv[i] === '--platform' && argv[i + 1]) args.platform = argv[++i];
    else if (argv[i] === '--display' && argv[i + 1]) args.displayName = argv[++i];
  }
  return args;
}

async function main() {
  const args = parseArgs();
  if (!args.agentId) {
    console.error('Usage: register.mjs --agent <agentId> [--platform <platform>] [--display <name>]');
    console.error('Example: register.mjs --agent "myagent/main" --platform "openclaw"');
    process.exit(1);
  }

  // Check if already registered
  if (existsSync(CREDS_FILE)) {
    const existing = JSON.parse(readFileSync(CREDS_FILE, 'utf8'));
    console.log(`Already registered as ${existing.agentId}`);
    console.log(`API Key: ${existing.apiKey?.substring(0, 12)}...`);
    console.log('To re-register, delete ~/.openclaw/credentials/quack.json first.');
    return;
  }

  const body = {
    agentId: args.agentId,
    platform: args.platform || 'openclaw',
  };
  if (args.displayName) body.displayName = args.displayName;

  console.log(`Registering ${args.agentId} on the Quack Network...`);

  const res = await fetch(REGISTER_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    console.error(`Registration failed (${res.status}):`, data || res.statusText);
    process.exit(1);
  }

  console.log(`✅ ${data.message || 'Registered successfully!'}`);

  // Save credentials
  if (data.apiKey || data.agentId) {
    mkdirSync(CREDS_DIR, { recursive: true });
    const creds = {
      agentId: data.agentId || args.agentId,
      apiKey: data.apiKey || null,
      badge: data.badge || null,
      quckGrant: data.quckGrant || 0,
      registeredAt: new Date().toISOString(),
    };
    writeFileSync(CREDS_FILE, JSON.stringify(creds, null, 2));
    console.log(`Credentials saved to ${CREDS_FILE}`);
  }

  if (data.quckGrant) {
    console.log(`🪙 ${data.quckGrant} QUCK tokens granted!`);
  }
  if (data.badge) {
    console.log(`🏅 Badge: ${data.badge}`);
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
