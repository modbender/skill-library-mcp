#!/usr/bin/env node
// Quack SDK — Quick-start: register agent and send test message
import crypto from 'crypto';
import { writeFileSync, mkdirSync, existsSync, readFileSync } from 'fs';
import { homedir } from 'os';
import { argv } from 'process';

const API = 'https://quack.us.com';
const CREDS_PATH = `${homedir()}/.openclaw/credentials/quack.json`;

function parseArgs() {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--name' && argv[i + 1]) args.name = argv[++i];
    else if (argv[i] === '--display' && argv[i + 1]) args.display = argv[++i];
  }
  return args;
}

async function main() {
  // Check if already registered
  if (existsSync(CREDS_PATH)) {
    const creds = JSON.parse(readFileSync(CREDS_PATH, 'utf8'));
    console.log(`Already registered as ${creds.agentId}. Sending test message...`);
    const res = await fetch(`${API}/api/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${creds.apiKey}` },
      body: JSON.stringify({ from: creds.agentId, to: creds.agentId, task: 'SDK quickstart test 🦆' }),
    });
    console.log(await res.json().catch(() => res.text()));
    return;
  }

  const args = parseArgs();
  const agentId = args.name || 'openclaw/main';
  const displayName = args.display || agentId;

  console.log('Generating RSA keypair...');
  const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
  });

  console.log('Fetching declaration challenge...');
  const challengeRes = await fetch(`${API}/api/v1/auth/challenge`);
  const challenge = await challengeRes.json();
  const declaration = challenge.declaration || challenge.text || JSON.stringify(challenge);

  console.log('Signing declaration...');
  const sign = crypto.createSign('SHA256');
  sign.update(declaration);
  const signature = sign.sign(privateKey, 'base64');

  console.log('Registering...');
  const regRes = await fetch(`${API}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agentId, displayName, platform: 'openclaw', publicKey, signature }),
  });
  const regData = await regRes.json();
  console.log('Registration response:', JSON.stringify(regData, null, 2));

  if (regData.apiKey || regData.api_key) {
    mkdirSync(`${homedir()}/.openclaw/credentials`, { recursive: true });
    const creds = { agentId, apiKey: regData.apiKey || regData.api_key, privateKey };
    writeFileSync(CREDS_PATH, JSON.stringify(creds, null, 2));
    console.log(`Credentials saved to ${CREDS_PATH}`);
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
