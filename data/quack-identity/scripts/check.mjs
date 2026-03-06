#!/usr/bin/env node
// Quack Identity — Check registration status
import { readFileSync, existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const CREDS_FILE = join(homedir(), '.openclaw', 'credentials', 'quack.json');

function main() {
  if (!existsSync(CREDS_FILE)) {
    console.log('❌ Not registered on the Quack Network.');
    console.log('Run: register.mjs --agent "youragent/main" --platform "openclaw"');
    return;
  }

  const creds = JSON.parse(readFileSync(CREDS_FILE, 'utf8'));
  console.log('✅ Registered on the Quack Network');
  console.log(`   Agent ID:    ${creds.agentId}`);
  console.log(`   Badge:       ${creds.badge || 'unknown'}`);
  console.log(`   QUCK Grant:  ${creds.quckGrant || 0}`);
  console.log(`   Registered:  ${creds.registeredAt || 'unknown'}`);
  if (creds.apiKey) {
    console.log(`   API Key:     ${creds.apiKey.substring(0, 12)}...`);
  }
}

main();
