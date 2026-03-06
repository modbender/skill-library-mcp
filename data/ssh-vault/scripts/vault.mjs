#!/usr/bin/env node
/**
 * SSH Vault CLI — sign requests with agent Ed25519 key and interact with vault API.
 * Usage: node vault.mjs <command> [args...]
 * 
 * Commands:
 *   status                  - Check vault lock status
 *   unlock                  - Request vault unlock (prints URL for user)
 *   session                 - Show cached session info
 *   register                - Register agent with vault
 *   hosts                   - List available hosts
 *   exec <host> <cmd> [timeout] - Execute SSH command on host
 */

import _sodium from 'libsodium-wrappers';
import { readFileSync, writeFileSync, existsSync } from 'fs';

await _sodium.ready;
const sodium = _sodium;

const VAULT_URL = process.env.SSH_VAULT_URL;
if (!VAULT_URL) {
  console.error('Error: SSH_VAULT_URL env var required');
  process.exit(1);
}
const SESSION_FILE = '/tmp/ssh-vault-session.json';

// Agent keys — read from environment variables
const PRIVATE_KEY_B64 = process.env.SSH_VAULT_AGENT_PRIVATE_KEY;
const PUBLIC_KEY_B64 = process.env.SSH_VAULT_AGENT_PUBLIC_KEY;
// Derive fingerprint from public key
import crypto from 'crypto';
const FINGERPRINT = 'SHA256:' + crypto.createHash('sha256').update(Buffer.from(PUBLIC_KEY_B64, 'base64')).digest('base64').replace(/=+$/, '');

if (!PRIVATE_KEY_B64 || !PUBLIC_KEY_B64) {
  console.error('Error: SSH_VAULT_AGENT_PRIVATE_KEY and SSH_VAULT_AGENT_PUBLIC_KEY env vars required');
  process.exit(1);
}

const PRIVATE_KEY = Buffer.from(PRIVATE_KEY_B64, 'base64');

function sign(payloadObj) {
  const payload = JSON.stringify(payloadObj);
  const timestamp = Date.now();
  const nonce = Buffer.from(sodium.randombytes_buf(16)).toString('hex');
  const message = `${payload}:${timestamp}:${nonce}`;
  const signature = Buffer.from(
    sodium.crypto_sign_detached(Buffer.from(message), PRIVATE_KEY)
  ).toString('base64');
  return { signature, publicKey: PUBLIC_KEY_B64, timestamp, nonce };
}

function loadSession() {
  try {
    if (existsSync(SESSION_FILE)) {
      const data = JSON.parse(readFileSync(SESSION_FILE, 'utf-8'));
      if (data.expiresAt && data.expiresAt > Date.now()) return data;
    }
  } catch {}
  return null;
}

function saveSession(session) {
  writeFileSync(SESSION_FILE, JSON.stringify(session, null, 2));
}

async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${VAULT_URL}${path}`, opts);
  const text = await res.text();
  try { return JSON.parse(text); } catch { return { raw: text, status: res.status }; }
}

// Commands
const cmd = process.argv[2];

if (cmd === 'status') {
  const r = await api('GET', '/api/vault/status');
  console.log(JSON.stringify(r, null, 2));

} else if (cmd === 'unlock') {
  const r = await api('POST', '/api/vault/unlock', { agentFingerprint: FINGERPRINT });
  if (r.challengeId) {
    console.log(JSON.stringify({
      status: 'pending',
      unlockUrl: r.unlockUrl,
      challengeId: r.challengeId,
      expiresAt: new Date(r.expiresAt).toISOString(),
    }, null, 2));
  } else {
    console.log(JSON.stringify(r, null, 2));
  }

} else if (cmd === 'check-unlock') {
  const challengeId = process.argv[3];
  if (!challengeId) { console.error('Usage: vault.mjs check-unlock <challengeId>'); process.exit(1); }
  const r = await api('GET', `/api/challenge/${challengeId}/status`);
  // If approved with unlockCode, submit it
  if (r.status === 'approved' && r.unlockCode) {
    const submit = await api('POST', '/api/vault/submit-unlock', {
      unlockCode: r.unlockCode,
      agentFingerprint: FINGERPRINT,
    });
    if (submit.success) {
      saveSession({ sessionId: submit.sessionId, expiresAt: submit.expiresAt });
      console.log(JSON.stringify({ status: 'unlocked', sessionId: submit.sessionId, expiresAt: new Date(submit.expiresAt).toISOString() }, null, 2));
    } else {
      console.log(JSON.stringify(submit, null, 2));
    }
  } else {
    console.log(JSON.stringify(r, null, 2));
  }

} else if (cmd === 'session') {
  const s = loadSession();
  if (s) {
    console.log(JSON.stringify({ ...s, expiresAtHuman: new Date(s.expiresAt).toISOString(), valid: true }, null, 2));
  } else {
    console.log(JSON.stringify({ valid: false, message: 'No active session' }, null, 2));
  }

} else if (cmd === 'register') {
  const r = await api('POST', '/api/agent/request-access', {
    name: 'openclaw',
    publicKey: PUBLIC_KEY_B64,
    requestedHosts: ['*'],
  });
  console.log(JSON.stringify(r, null, 2));

} else if (cmd === 'hosts') {
  const session = loadSession();
  if (!session) { console.error('No active session. Run: vault.mjs unlock'); process.exit(1); }
  const payload = {};
  const sig = sign(payload);
  const r = await api('GET', `/api/agent/hosts?sessionId=${session.sessionId}&publicKey=${encodeURIComponent(PUBLIC_KEY_B64)}&signature=${encodeURIComponent(sig.signature)}&timestamp=${sig.timestamp}&nonce=${sig.nonce}`);
  console.log(JSON.stringify(r, null, 2));

} else if (cmd === 'exec') {
  const host = process.argv[3];
  const command = process.argv[4];
  const timeout = process.argv[5] ? parseInt(process.argv[5]) : 30;
  if (!host || !command) { console.error('Usage: vault.mjs exec <host> <command> [timeout]'); process.exit(1); }

  const session = loadSession();
  const payload = { host, command };
  const sig = sign(payload);
  const body = { ...payload, timeout, ...sig };
  if (session) body.sessionId = session.sessionId;

  const r = await api('POST', '/api/vault/execute', body);
  
  // Handle auto-approval response — listen on SSE for result
  if (r.needsApproval) {
    console.log(JSON.stringify({
      needsApproval: true,
      approvalUrl: r.approvalUrl,
      execRequestId: r.execRequestId,
      listenUrl: r.listenUrl,
      message: r.message,
    }, null, 2));
  } else if (r.output !== undefined) {
    process.stdout.write(r.output);
    if (r.exitCode !== undefined && r.exitCode !== 0) {
      process.stderr.write(`\n[exit code: ${r.exitCode}]`);
    }
  } else {
    console.log(JSON.stringify(r, null, 2));
  }

} else {
  console.log(`SSH Vault CLI
Usage: node vault.mjs <command> [args...]

Commands:
  status                     Check vault lock status
  unlock                     Request vault unlock
  check-unlock <challengeId> Check unlock status & submit code
  session                    Show cached session
  register                   Register agent with vault
  hosts                      List available hosts
  exec <host> <cmd> [timeout] Execute command on host`);
}
