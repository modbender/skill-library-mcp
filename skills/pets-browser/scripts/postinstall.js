#!/usr/bin/env node

/**
 * postinstall.js — Clawnet setup
 *
 * Runs automatically on `npm install` / `clawhub install clawnet`:
 * 1. Installs Chromium via Playwright
 * 2. Creates or imports agent credentials (agentId + agentSecret)
 * 3. Saves credentials to ~/.clawnet/agent-credentials.json
 * 4. Registers the agent with Clawnet API (if CN_API_URL is set)
 *
 * Identity model:
 * - agentId is stable for one subscription identity
 * - agentSecret can be rotated if compromised
 * - recoveryCode is optional fallback to rotate when old secret is unavailable
 */

const { execSync } = require('child_process');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');

const CREDENTIALS_DIR = path.join(os.homedir(), '.clawnet');
const CREDENTIALS_FILE = path.join(CREDENTIALS_DIR, 'agent-credentials.json');
const DEFAULT_API_URL = 'https://api.clawpets.io/clawnet/v1';

const AGENT_ID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const AGENT_SECRET_RE = /^[A-Za-z0-9_-]{32,200}$/;
const RECOVERY_CODE_RE = /^[A-Za-z0-9_-]{20,200}$/;

function installChromiumDeps() {
  console.log('[clawnet] Installing Chromium system dependencies...');
  try {
    // Try playwright's built-in deps installer first (needs root/sudo)
    execSync('npx playwright install-deps chromium', {
      stdio: 'inherit',
      timeout: 120_000,
    });
    console.log('[clawnet] System dependencies installed.');
    return;
  } catch (_) {}

  // Fallback: install essential libs directly via apt-get
  const libs = [
    'libnss3', 'libnspr4',
    'libatk1.0-0', 'libatk-bridge2.0-0',
    'libcups2', 'libdrm2',
    'libxkbcommon0', 'libxcomposite1', 'libxdamage1', 'libxfixes3', 'libxrandr2',
    'libgbm1',
    'libpango-1.0-0', 'libpangocairo-1.0-0', 'libcairo2',
    'libasound2',
  ].join(' ');
  try {
    execSync(`apt-get update -qq && apt-get install -y --no-install-recommends ${libs}`, {
      stdio: 'inherit',
      timeout: 120_000,
    });
    console.log('[clawnet] System dependencies installed via apt-get.');
  } catch (_) {
    console.warn('[clawnet] WARNING: Could not install system dependencies.');
    console.warn('  Run manually: apt-get install -y ' + libs);
  }
}

function installChromium() {
  console.log('[clawnet] Installing Chromium...');
  try {
    execSync('npx playwright install chromium', {
      stdio: 'inherit',
      timeout: 300_000,
    });
    console.log('[clawnet] Chromium binary installed.');
  } catch (_) {
    console.error('[clawnet] WARNING: Chromium install failed. You may need to run manually:');
    console.error('  npx playwright install chromium');
  }

  // Install system libraries (libnspr4, libnss3, etc.)
  installChromiumDeps();
}

function generateAgentId() {
  return crypto.randomUUID();
}

function generateAgentSecret() {
  return crypto.randomBytes(32).toString('base64url');
}

function generateRecoveryCode() {
  return crypto.randomBytes(24).toString('base64url');
}

function validateCredentials(credentials) {
  return Boolean(
    credentials &&
      AGENT_ID_RE.test(credentials.agentId || '') &&
      AGENT_SECRET_RE.test(credentials.agentSecret || '') &&
      (!credentials.recoveryCode || RECOVERY_CODE_RE.test(credentials.recoveryCode))
  );
}

function parseCombinedCredentials(raw) {
  const value = String(raw || '').trim();
  if (!value) return null;

  const parts = value.split(':').map(v => v.trim()).filter(Boolean);
  if (parts.length < 2 || parts.length > 3) {
    return null;
  }

  const [agentId, agentSecret, recoveryCode] = parts;
  const candidate = { agentId, agentSecret, recoveryCode };
  return validateCredentials(candidate) ? candidate : null;
}

function readSavedCredentials() {
  try {
    if (!fs.existsSync(CREDENTIALS_FILE)) {
      return null;
    }
    const parsed = JSON.parse(fs.readFileSync(CREDENTIALS_FILE, 'utf-8'));
    if (validateCredentials(parsed)) {
      return parsed;
    }
    return null;
  } catch (_) {
    return null;
  }
}

function saveCredentials(credentials) {
  const now = new Date().toISOString();
  const existing = readSavedCredentials();

  const payload = {
    agentId: credentials.agentId,
    agentSecret: credentials.agentSecret,
    recoveryCode: credentials.recoveryCode || existing?.recoveryCode,
    createdAt: existing?.createdAt || now,
    updatedAt: now,
  };

  fs.mkdirSync(CREDENTIALS_DIR, { recursive: true, mode: 0o700 });
  fs.writeFileSync(CREDENTIALS_FILE, JSON.stringify(payload, null, 2), { mode: 0o600 });

  console.log(`  Saved to: ${CREDENTIALS_FILE}`);
  console.log('');
  console.log('  Agent credentials were written to disk with mode 0600.');
  console.log('  Secrets are not printed to stdout for security.');
  console.log(`  agentId: ${payload.agentId}`);
  console.log('');

  return payload;
}

function readCredentialsFromEnv() {
  const combined = parseCombinedCredentials(process.env.CN_AGENT_CREDENTIALS);
  if (combined) {
    console.log('[clawnet] Using credentials from CN_AGENT_CREDENTIALS.');
    return combined;
  }

  const agentId = process.env.CN_AGENT_ID?.trim();
  const agentSecret = process.env.CN_AGENT_SECRET?.trim();
  const recoveryCode = process.env.CN_AGENT_RECOVERY_CODE?.trim();

  if (!agentId) {
    return null;
  }

  if (agentSecret) {
    const creds = { agentId, agentSecret, recoveryCode };
    if (validateCredentials(creds)) {
      console.log('[clawnet] Using agentId/agentSecret from environment.');
      return creds;
    }
    console.warn('[clawnet] Ignoring invalid CN_AGENT_ID/CN_AGENT_SECRET format.');
    return null;
  }

  if (recoveryCode && AGENT_ID_RE.test(agentId) && RECOVERY_CODE_RE.test(recoveryCode)) {
    console.log('[clawnet] CN_AGENT_ID + CN_AGENT_RECOVERY_CODE detected. Generating a new agentSecret.');
    return {
      agentId,
      agentSecret: generateAgentSecret(),
      recoveryCode,
    };
  }

  return null;
}

async function promptForExistingCredentials() {
  if (!process.stdin.isTTY) {
    return null;
  }

  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

    rl.question(
      '[clawnet] Paste existing credentials (<agentId>:<agentSecret>[:recoveryCode]) or press Enter for new: ',
      (answer) => {
        rl.close();
        const parsed = parseCombinedCredentials(answer);
        if (!answer.trim()) {
          resolve(null);
          return;
        }
        if (!parsed) {
          console.warn('[clawnet] Invalid format. Expected: <agentId>:<agentSecret>[:recoveryCode].');
          resolve(null);
          return;
        }
        resolve(parsed);
      }
    );

    setTimeout(() => {
      rl.close();
      resolve(null);
    }, 30_000);
  });
}

async function rotateSecretWithApi(credentials) {
  const apiUrl = process.env.CN_API_URL || DEFAULT_API_URL;
  if (!apiUrl || !credentials.recoveryCode) {
    return false;
  }

  try {
    const url = `${apiUrl.replace(/\/$/, '')}/agents/rotate-secret`;
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agentId: credentials.agentId,
        newAgentSecret: credentials.agentSecret,
        recoveryCode: credentials.recoveryCode,
      }),
      signal: AbortSignal.timeout(10_000),
    });

    if (resp.ok) {
      console.log('[clawnet] Agent secret rotated using recovery code.');
      return true;
    }

    return false;
  } catch (_) {
    return false;
  }
}

async function registerWithApi(credentials) {
  const apiUrl = process.env.CN_API_URL || DEFAULT_API_URL;

  const url = `${apiUrl.replace(/\/$/, '')}/agents/register`;

  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agentId: credentials.agentId,
        agentSecret: credentials.agentSecret,
        recoveryCode: credentials.recoveryCode,
      }),
      signal: AbortSignal.timeout(10_000),
    });

    if (resp.ok) {
      const data = await resp.json();
      console.log(
        `[clawnet] Agent ${data.created ? 'registered' : 'validated'}. Trial: ${data.trialLimit ?? 1} free session(s).`
      );
      return;
    }

    if (resp.status === 409 && credentials.recoveryCode) {
      const rotated = await rotateSecretWithApi(credentials);
      if (rotated) {
        return;
      }
    }

    const text = await resp.text().catch(() => '');
    console.warn(`[clawnet] API registration returned ${resp.status}: ${text}`);
  } catch (err) {
    console.warn(`[clawnet] Could not reach API: ${err.message}`);
    console.warn('  Agent will work in BYO mode (bring your own proxy/captcha keys).');
  }
}

async function resolveCredentials() {
  const fromEnv = readCredentialsFromEnv();
  if (fromEnv) {
    return fromEnv;
  }

  const fromPrompt = await promptForExistingCredentials();
  if (fromPrompt) {
    return fromPrompt;
  }

  // Security: if the credentials directory already exists, an agent was
  // previously registered. Refuse to silently generate new ones.
  if (fs.existsSync(CREDENTIALS_DIR) || fs.existsSync(CREDENTIALS_FILE)) {
    console.error('[clawnet] Agent account already exists. Cannot generate new credentials.');
    console.error('  Provide existing credentials via:');
    console.error('    CN_AGENT_CREDENTIALS=<agentId>:<agentSecret>');
    console.error('  Or paste them when prompted above.');
    process.exit(1);
  }

  return {
    agentId: generateAgentId(),
    agentSecret: generateAgentSecret(),
    recoveryCode: generateRecoveryCode(),
  };
}

async function main() {
  console.log('');
  console.log('  ┌─────────────────────────────────────────┐');
  console.log('  │  Clawnet - Setup                    │');
  console.log('  │  Stealth Chromium for AI agents          │');
  console.log('  └─────────────────────────────────────────┘');
  console.log('');

  installChromium();

  const saved = readSavedCredentials();
  if (saved) {
    console.log('[clawnet] Agent credentials already configured.');
    console.log(`  agentId: ${saved.agentId}`);
    await registerWithApi(saved);
    console.log('[clawnet] Setup complete.');
    return;
  }

  const credentials = await resolveCredentials();
  const savedCredentials = saveCredentials(credentials);
  await registerWithApi(savedCredentials);

  console.log('[clawnet] Setup complete. Usage:');
  console.log('');
  console.log("  const { launchBrowser } = require('clawnet/scripts/browser');");
  console.log("  const { page } = await launchBrowser({ country: 'us' });");
  console.log('');
}

main().catch(err => {
  console.error('[clawnet] Setup error:', err.message);
  process.exit(0);
});
