#!/usr/bin/env node
'use strict';

/*
  LaunchPulse project generator (hosted API)
  - No dependencies (Node 18+; uses global fetch)
  - Logs to stderr; prints final JSON result to stdout
*/

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const VERSION = '1.1.1';
const DEFAULT_API_BASE_URL = 'https://api.launchpulse.ai/api';

function usage(exitCode) {
  const text = `
Usage:
  launchpulse.cjs login
  launchpulse.cjs logout
  launchpulse.cjs status
  launchpulse.cjs upgrade [--tier <STARTER|BUILDER>] [--tokens <0-3>]
  launchpulse.cjs projects
  launchpulse.cjs project-status <projectId>
  launchpulse.cjs deploy <projectId> [--target <cloud-run|fly>] [--wait]
  launchpulse.cjs deploy-status <projectId> <deploymentId>
  launchpulse.cjs store-publish <projectId> --payload-file <json> [--wait]
  launchpulse.cjs store-status <projectId> [--publish-id <id>]
  launchpulse.cjs store-2fa <projectId> <publishId> <code>
  launchpulse.cjs domains <action> [...]
  launchpulse.cjs db <action> [...]
  launchpulse.cjs storage <action> [...]
  launchpulse.cjs payments <action> [...]
  launchpulse.cjs env-files <action> [...]
  launchpulse.cjs web    "<description>" [options]
  launchpulse.cjs mobile "<description>" [options]
  launchpulse.cjs iterate <projectId> "<change request>" [options]

Options:
  --api-base <url>        (default: env LAUNCHPULSE_API_BASE_URL or hosted LaunchPulse API)
  --pat <token>           (default: env LAUNCHPULSE_PAT; or stored device-login token)
  --api-key <token>       alias for --pat (for API-key style workflows)
  --access-token <jwt>    (default: env LAUNCHPULSE_ACCESS_TOKEN; Supabase access token)
  --user-id <uuid>        legacy fallback for older LaunchPulse backends that require userId
  --no-login              fail instead of starting device-login flow when unauthenticated
  --name <project-slug>   preferred project id/slug
  --concurrency <n>       1-10 (default: 1)
  --no-plan               skip AI feature planner and use a single MVP feature fallback
  --poll-ms <ms>          polling interval (default: 8000)
  --timeout-min <min>     polling timeout (default: 45)
  --chat-id <id>          (iterate) optional project chat id
  --provider <id>         (iterate) optional AI provider override
  --model <id>            (iterate) optional model override
  --tier <STARTER|BUILDER> (upgrade) subscription tier
  --tokens <0-3>          (upgrade) token addon pack index
  --billing-period <m|a>  (upgrade) monthly or annual (default: monthly)
  --target <id>           (deploy) cloud-run (default) or fly
  --region <id>           (deploy/domains) region override
  --wait                  wait for terminal status when supported
  --payload-file <path>   JSON request payload file for complex commands
  --publish-id <id>       publish job id for store-status/store-2fa
  --project-type <id>     (payments) vitereact or expo
  --api-url <url>         (payments) override injected API URL
  --record-type <type>    (domains dns) CNAME/TXT/A/AAAA
  --app-name <name>       (domains) app/service name for cert checks
  --service-name <name>   (domains map) explicit service name
  --fly-token <token>     Fly API token override
  --github-username <id>  GitHub username override for deploy target=fly
  --github-token <token>  GitHub token override for deploy target=fly
  --file-path <path>      target env file path for env-files save
  --vars-file <path>      JSON vars file for env-files save
  --contact-file <path>   JSON contact info file for domains register
  --stripe-publishable-key <key>    (payments setup) Stripe publishable key
  --stripe-secret-key <key>         (payments setup) Stripe secret key
  --revenuecat-ios-key <key>        (payments setup) RevenueCat iOS public key
  --revenuecat-android-key <key>    (payments setup) RevenueCat Android public key
  --revenuecat-secret-key <key>     (payments setup) RevenueCat secret key
  --revenuecat-entitlement-id <id>  (payments setup) RevenueCat entitlement id
  -v, --version           show version
  -h, --help              show help

Env:
  LAUNCHPULSE_API_BASE_URL optional; override API base (e.g. http://localhost:667/api)
  LAUNCHPULSE_PAT         optional; LaunchPulse personal access token (PAT)
  LAUNCHPULSE_API_KEY     optional; alias of LAUNCHPULSE_PAT
  LAUNCHPULSE_ACCESS_TOKEN optional; Supabase access token JWT (alternative to PAT)
  LAUNCHPULSE_USER_ID     optional; legacy user id fallback for non-device-auth backends
`;
  process.stderr.write(text.trimStart());
  process.stderr.write('\n');
  process.exit(exitCode);
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function slugify(text) {
  return String(text || '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '');
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function nowIso() {
  return new Date().toISOString();
}

function pick(obj, keys) {
  const out = {};
  for (const k of keys) {
    if (obj[k] !== undefined) out[k] = obj[k];
  }
  return out;
}

function normalizeApiBaseUrl(value) {
  const fallback = DEFAULT_API_BASE_URL;
  const raw = value && String(value).trim().length ? String(value).trim() : fallback;
  return raw.replace(/\/+$/, '');
}

function withUserId(url, userId) {
  if (!userId) return url;
  const sep = url.includes('?') ? '&' : '?';
  return `${url}${sep}userId=${encodeURIComponent(userId)}`;
}

function decodeBase64Url(value) {
  if (!value || typeof value !== 'string') return null;
  try {
    let input = value.replace(/-/g, '+').replace(/_/g, '/');
    while (input.length % 4 !== 0) input += '=';
    return Buffer.from(input, 'base64').toString('utf8');
  } catch {
    return null;
  }
}

function deriveUserIdFromJwt(jwt) {
  if (!jwt || typeof jwt !== 'string') return null;
  const parts = jwt.split('.');
  if (parts.length < 2) return null;
  const payloadText = decodeBase64Url(parts[1]);
  if (!payloadText) return null;
  try {
    const payload = JSON.parse(payloadText);
    return payload && typeof payload.sub === 'string' && payload.sub ? payload.sub : null;
  } catch {
    return null;
  }
}

function getOpenClawStateDir() {
  const stateDir = process.env.OPENCLAW_STATE_DIR;
  if (stateDir && String(stateDir).trim()) return String(stateDir).trim();
  return path.join(os.homedir(), '.openclaw');
}

function getAuthFilePath() {
  return path.join(getOpenClawStateDir(), 'launchpulse', 'auth.json');
}

function loadStoredAuth() {
  try {
    const authPath = getAuthFilePath();
    if (!fs.existsSync(authPath)) return { pat: null, userId: null };
    const raw = fs.readFileSync(authPath, 'utf8');
    const parsed = JSON.parse(raw);
    const pat = parsed && typeof parsed.pat === 'string' ? parsed.pat : null;
    const userId = parsed && typeof parsed.userId === 'string' ? parsed.userId : null;
    return {
      pat: pat && pat.trim().length ? pat.trim() : null,
      userId: userId && userId.trim().length ? userId.trim() : null,
    };
  } catch {
    return { pat: null, userId: null };
  }
}

function saveStoredAuth(pat, userId) {
  const authPath = getAuthFilePath();
  ensureDir(path.dirname(authPath));
  fs.writeFileSync(
    authPath,
    JSON.stringify(
      {
        pat,
        userId: userId || null,
        savedAt: nowIso(),
      },
      null,
      2,
    ),
    'utf8',
  );
}

function clearStoredPat() {
  try {
    const authPath = getAuthFilePath();
    if (fs.existsSync(authPath)) fs.unlinkSync(authPath);
    return true;
  } catch {
    return false;
  }
}

async function fetchWithTimeout(url, options, timeoutMs) {
  const controller = new AbortController();
  const id = setTimeout(
    () => controller.abort(new Error(`Timeout after ${timeoutMs}ms`)),
    timeoutMs,
  );
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}

async function fetchJson(url, options) {
  const method = (options && options.method) || 'GET';
  const body = options && options.body !== undefined ? options.body : undefined;
  const timeoutMs = (options && options.timeoutMs) || 60_000;

  const headers = {
    ...(options && options.headers ? options.headers : {}),
  };

  let payload;
  if (body !== undefined) {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    payload = typeof body === 'string' ? body : JSON.stringify(body);
  }

  const res = await fetchWithTimeout(
    url,
    {
      method,
      headers,
      body: payload,
    },
    timeoutMs,
  );

  const contentType = String(res.headers.get('content-type') || '').toLowerCase();
  const isJson = contentType.includes('application/json');

  const text = await res.text().catch(() => '');
  let json = null;
  if (isJson && text) {
    try {
      json = JSON.parse(text);
    } catch {
      json = null;
    }
  }

  if (!res.ok) {
    const err = new Error(`HTTP ${res.status} ${res.statusText}: ${text.slice(0, 500)}`);
    err.status = res.status;
    err.responseText = text;
    err.responseJson = json;
    err.isBillingError = res.status === 402 || (json && json.code === 'TOKEN_LIMIT_EXCEEDED');
    err.billing = (json && json.billing) || null;
    throw err;
  }

  return json !== null ? json : text;
}

function parseArgs(argv) {
  const args = Array.isArray(argv) ? [...argv] : [];
  if (args.length === 0) usage(1);

  const cmd = args.shift();
  if (!cmd || cmd === '-h' || cmd === '--help') usage(0);
  if (cmd === '-v' || cmd === '--version') {
    process.stdout.write(`launchpulse ${VERSION}\n`);
    process.exit(0);
  }

  const VALID_CMDS = [
    'login',
    'logout',
    'status',
    'upgrade',
    'projects',
    'project-status',
    'deploy',
    'deploy-status',
    'store-publish',
    'store-status',
    'store-2fa',
    'domains',
    'db',
    'storage',
    'payments',
    'env-files',
    'web',
    'mobile',
    'iterate',
  ];
  if (!VALID_CMDS.includes(cmd)) {
    process.stderr.write(`Unknown command: ${cmd}\n`);
    usage(1);
  }

  let apiBase = process.env.LAUNCHPULSE_API_BASE_URL || DEFAULT_API_BASE_URL;
  let pat = process.env.LAUNCHPULSE_PAT || process.env.LAUNCHPULSE_API_KEY || null;
  let accessToken = process.env.LAUNCHPULSE_ACCESS_TOKEN || null;
  let userId = process.env.LAUNCHPULSE_USER_ID || null;
  let noLogin = false;
  let name = null;
  let concurrency = 1;
  let noPlan = false;
  let pollMs = 8000;
  let timeoutMin = 45;
  let chatId = null;
  let provider = null;
  let model = null;
  let tier = null;
  let tokens = null;
  let billingPeriod = 'monthly';
  let target = 'cloud-run';
  let region = null;
  let wait = false;
  let payloadFile = null;
  let publishId = null;
  let deploymentId = null;
  let projectType = null;
  let apiUrl = null;
  let recordType = 'CNAME';
  let appName = null;
  let serviceName = null;
  let flyToken = process.env.FLY_API_TOKEN || null;
  let githubUsername = process.env.GITHUB_USERNAME || null;
  let githubToken = process.env.GITHUB_TOKEN || null;
  let filePath = null;
  let varsFile = null;
  let contactFile = null;
  let stripePublishableKey = null;
  let stripeSecretKey = null;
  let revenuecatIosKey = null;
  let revenuecatAndroidKey = null;
  let revenuecatSecretKey = null;
  let revenuecatEntitlementId = null;

  const positionalParts = [];

  for (let i = 0; i < args.length; i++) {
    const a = args[i];

    if (a === '-h' || a === '--help') usage(0);

    if (a === '--api-base') {
      apiBase = args[i + 1] || apiBase;
      i += 1;
      continue;
    }

    if (a === '--pat') {
      pat = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--api-key') {
      pat = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--access-token') {
      accessToken = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--user-id') {
      userId = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--no-login') {
      noLogin = true;
      continue;
    }

    if (a === '--name') {
      name = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--concurrency') {
      concurrency = Number(args[i + 1] || '1');
      i += 1;
      continue;
    }

    if (a === '--no-plan' || a === '--skip-plan') {
      noPlan = true;
      continue;
    }

    if (a === '--poll-ms') {
      pollMs = Number(args[i + 1] || String(pollMs));
      i += 1;
      continue;
    }

    if (a === '--timeout-min') {
      timeoutMin = Number(args[i + 1] || String(timeoutMin));
      i += 1;
      continue;
    }

    if (a === '--chat-id') {
      chatId = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--provider') {
      provider = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--model') {
      model = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--tier') {
      tier = (args[i + 1] || '').toUpperCase();
      i += 1;
      continue;
    }

    if (a === '--tokens') {
      tokens = Number(args[i + 1]);
      i += 1;
      continue;
    }

    if (a === '--billing-period') {
      const val = (args[i + 1] || '').toLowerCase();
      billingPeriod = val === 'annual' || val === 'a' ? 'annual' : 'monthly';
      i += 1;
      continue;
    }

    if (a === '--target') {
      target = String(args[i + 1] || target).toLowerCase();
      i += 1;
      continue;
    }

    if (a === '--region') {
      region = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--wait') {
      wait = true;
      continue;
    }

    if (a === '--payload-file') {
      payloadFile = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--publish-id') {
      publishId = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--project-type') {
      projectType = String(args[i + 1] || '').toLowerCase();
      i += 1;
      continue;
    }

    if (a === '--api-url') {
      apiUrl = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--record-type') {
      recordType = String(args[i + 1] || recordType).toUpperCase();
      i += 1;
      continue;
    }

    if (a === '--app-name') {
      appName = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--service-name') {
      serviceName = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--fly-token') {
      flyToken = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--github-username') {
      githubUsername = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--github-token') {
      githubToken = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--file-path') {
      filePath = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--vars-file') {
      varsFile = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--contact-file') {
      contactFile = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--stripe-publishable-key') {
      stripePublishableKey = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--stripe-secret-key') {
      stripeSecretKey = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--revenuecat-ios-key') {
      revenuecatIosKey = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--revenuecat-android-key') {
      revenuecatAndroidKey = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--revenuecat-secret-key') {
      revenuecatSecretKey = args[i + 1] || null;
      i += 1;
      continue;
    }

    if (a === '--revenuecat-entitlement-id') {
      revenuecatEntitlementId = args[i + 1] || null;
      i += 1;
      continue;
    }

    positionalParts.push(a);
  }

  let projectId = null;
  let description = null;
  let message = null;
  let twoFactorCode = null;
  let subcommand = null;
  let subcommandArgs = [];

  if (cmd === 'login' || cmd === 'logout' || cmd === 'status' || cmd === 'upgrade' || cmd === 'projects') {
    // no positional args required
  } else if (cmd === 'iterate') {
    projectId = positionalParts.shift() || null;
    message = positionalParts.join(' ').trim();
    if (!projectId) {
      throw new Error('Missing projectId. Usage: launchpulse.cjs iterate <projectId> "<change request>"');
    }
    if (!message) {
      throw new Error('Missing change request message. Provide a quoted message string.');
    }
  } else if (cmd === 'web' || cmd === 'mobile') {
    description = positionalParts.join(' ').trim();
    if (!description) {
      throw new Error('Missing description. Provide a quoted description string.');
    }
  } else if (cmd === 'project-status') {
    projectId = positionalParts.shift() || null;
    if (!projectId) throw new Error('Missing projectId. Usage: launchpulse.cjs project-status <projectId>');
  } else if (cmd === 'deploy') {
    projectId = positionalParts.shift() || null;
    if (!projectId) throw new Error('Missing projectId. Usage: launchpulse.cjs deploy <projectId> [options]');
  } else if (cmd === 'deploy-status') {
    projectId = positionalParts.shift() || null;
    deploymentId = positionalParts.shift() || deploymentId;
    if (!projectId || !deploymentId) {
      throw new Error('Usage: launchpulse.cjs deploy-status <projectId> <deploymentId>');
    }
  } else if (cmd === 'store-publish') {
    projectId = positionalParts.shift() || null;
    if (!projectId) throw new Error('Missing projectId. Usage: launchpulse.cjs store-publish <projectId> --payload-file <json>');
    if (!payloadFile) throw new Error('store-publish requires --payload-file <json>');
  } else if (cmd === 'store-status') {
    projectId = positionalParts.shift() || null;
    if (!projectId) throw new Error('Missing projectId. Usage: launchpulse.cjs store-status <projectId> [--publish-id <id>]');
  } else if (cmd === 'store-2fa') {
    projectId = positionalParts.shift() || null;
    publishId = positionalParts.shift() || publishId;
    twoFactorCode = positionalParts.shift() || null;
    if (!projectId || !publishId || !twoFactorCode) {
      throw new Error('Usage: launchpulse.cjs store-2fa <projectId> <publishId> <code>');
    }
  } else {
    subcommand = positionalParts.shift() || null;
    subcommandArgs = positionalParts;
    if (!subcommand) {
      throw new Error(`Missing action. Usage: launchpulse.cjs ${cmd} <action> [...]`);
    }
  }

  const resolvedConcurrency = Number.isFinite(concurrency)
    ? Math.min(Math.max(1, Math.floor(concurrency)), 10)
    : 1;
  const resolvedPollMs = Number.isFinite(pollMs)
    ? Math.min(Math.max(1000, Math.floor(pollMs)), 60_000)
    : 8000;
  const resolvedTimeoutMin = Number.isFinite(timeoutMin)
    ? Math.min(Math.max(1, Math.floor(timeoutMin)), 240)
    : 45;

  return {
    cmd,
    apiBase: normalizeApiBaseUrl(apiBase),
    pat: pat || null,
    accessToken: accessToken || null,
    userId: userId ? String(userId).trim() : null,
    noLogin,
    name,
    concurrency: resolvedConcurrency,
    noPlan,
    pollMs: resolvedPollMs,
    timeoutMin: resolvedTimeoutMin,
    description,
    projectId,
    message,
    chatId,
    provider,
    model,
    tier,
    tokens,
    billingPeriod,
    target,
    region: region || null,
    wait,
    payloadFile,
    publishId,
    deploymentId,
    projectType,
    apiUrl,
    recordType,
    appName,
    serviceName,
    flyToken,
    githubUsername,
    githubToken,
    filePath,
    varsFile,
    contactFile,
    stripePublishableKey,
    stripeSecretKey,
    revenuecatIosKey,
    revenuecatAndroidKey,
    revenuecatSecretKey,
    revenuecatEntitlementId,
    twoFactorCode,
    subcommand,
    subcommandArgs,
  };
}

function buildAuthHeaders(bearerToken) {
  return bearerToken ? { Authorization: `Bearer ${bearerToken}` } : {};
}

function withUserHeaders(headers, userId) {
  if (!userId) return { ...(headers || {}) };
  return {
    ...(headers || {}),
    'x-user-id': userId,
  };
}

function readJsonFile(filePath, label) {
  if (!filePath) throw new Error(`Missing ${label} file path`);
  const absPath = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
  const raw = fs.readFileSync(absPath, 'utf8');
  try {
    return JSON.parse(raw);
  } catch (err) {
    throw new Error(`Invalid JSON in ${label} file (${absPath}): ${err?.message || String(err)}`);
  }
}

function normalizeProjectType(value) {
  const raw = String(value || '').trim().toLowerCase();
  if (!raw) return null;
  if (raw === 'mobile' || raw === 'mobile-app' || raw === 'expo') return 'expo';
  return 'vitereact';
}

async function runDeviceLoginFlow(apiBase) {
  process.stderr.write('[launchpulse] Starting device login...\n');

  const started = await fetchJson(`${apiBase}/auth/device/start`, {
    method: 'POST',
    body: {},
    timeoutMs: 30_000,
  });

  const deviceCode = started?.device_code || null;
  const userCode = started?.user_code || null;
  const verificationUrl = started?.verification_uri_complete || started?.verification_uri || null;
  const expiresIn = Number(started?.expires_in || 0) || 0;
  const intervalSec = Number(started?.interval || 0) || 5;

  if (!deviceCode || !verificationUrl) {
    throw new Error(`Device login start failed: ${JSON.stringify(started).slice(0, 500)}`);
  }

  process.stderr.write(`[launchpulse] User code: ${userCode || '(unknown)'}\n`);
  process.stderr.write(`[launchpulse] Open this link to sign in: ${verificationUrl}\n`);

  const deadline = Date.now() + Math.max(60, Math.min(expiresIn || 900, 1800)) * 1000;
  const pollMs = Math.min(Math.max(1000, Math.floor(intervalSec * 1000)), 10_000);

  while (Date.now() < deadline) {
    const status = await fetchJson(
      `${apiBase}/auth/device/status?device_code=${encodeURIComponent(deviceCode)}`,
      { method: 'GET', timeoutMs: 15_000 },
    ).catch(() => null);

    const state = status?.status || null;
    if (state === 'authorized') break;
    if (state === 'expired') throw new Error('Device login expired. Re-run `launchpulse.cjs login`.');

    process.stderr.write(`[launchpulse] Waiting for login... (${state || 'pending'})\n`);
    await sleep(pollMs);
  }

  process.stderr.write('[launchpulse] Exchanging device code for token...\n');
  const exchanged = await fetchJson(`${apiBase}/auth/device/exchange`, {
    method: 'POST',
    body: { device_code: deviceCode },
    timeoutMs: 30_000,
  });

  const pat = exchanged?.access_token || null;
  if (!pat || typeof pat !== 'string') {
    throw new Error(`Device token exchange failed: ${JSON.stringify(exchanged).slice(0, 500)}`);
  }

  const userId = typeof exchanged?.user_id === 'string' && exchanged.user_id.trim().length
    ? exchanged.user_id.trim()
    : (deriveUserIdFromJwt(pat) || null);

  saveStoredAuth(pat, userId);
  process.stderr.write(`[launchpulse] Saved token to ${getAuthFilePath()}\n`);
  return { pat, userId };
}

function isDeviceAuthUnsupported(err) {
  return Number(err?.status) === 404;
}

function isProjectNotReady(err) {
  const status = Number(err?.status);
  const text = String(err?.responseText || '').toLowerCase();
  return (status === 404 || status === 409) && text.includes('project not found');
}

function isAutoModeAlreadyRunning(err) {
  const status = Number(err?.status);
  const text = String(err?.responseText || '').toLowerCase();
  return status === 409 && text.includes('already running');
}

function handleBillingError(err) {
  if (!err.isBillingError && !err.billing) return false;

  const billing = err.billing || err.responseJson?.billing || {};
  const tier = billing.tier || 'unknown';
  const upgradeUrl = billing.upgradeUrl || 'https://launchpulse.ai/billing';
  const buyTokensUrl = billing.buyTokensUrl || 'https://launchpulse.ai/billing#tokens';

  process.stderr.write('\n');
  process.stderr.write('[launchpulse] ========================================\n');
  process.stderr.write('[launchpulse] TOKEN LIMIT REACHED\n');
  process.stderr.write('[launchpulse] ========================================\n');
  process.stderr.write(`[launchpulse] Your ${tier} plan tokens are used up.\n`);
  if (billing.used !== undefined && billing.limit !== undefined) {
    process.stderr.write(`[launchpulse] Used: ${billing.used} / ${billing.limit}\n`);
  }
  process.stderr.write('[launchpulse]\n');
  process.stderr.write(`[launchpulse] Upgrade your plan: ${upgradeUrl}\n`);
  process.stderr.write(`[launchpulse] Buy token packs:   ${buyTokensUrl}\n`);
  process.stderr.write('[launchpulse] ========================================\n');
  process.stderr.write('\n');

  const result = {
    ok: false,
    status: 'token_limit_exceeded',
    billing: { tier, upgradeUrl, buyTokensUrl, used: billing.used ?? null, limit: billing.limit ?? null },
    message: `Token limit reached. Upgrade at ${upgradeUrl}`,
  };
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  return true;
}

async function fetchUsageBalance(apiBase, authHeaders) {
  return fetchJson(`${apiBase}/usage/balance`, {
    method: 'GET',
    headers: authHeaders,
    timeoutMs: 15_000,
  });
}

async function preflightBalanceCheck(apiBase, authHeaders) {
  try {
    const balance = await fetchUsageBalance(apiBase, authHeaders);
    if (balance.isExhausted) {
      process.stderr.write('\n');
      process.stderr.write('[launchpulse] ========================================\n');
      process.stderr.write('[launchpulse] TOKEN LIMIT REACHED\n');
      process.stderr.write('[launchpulse] ========================================\n');
      process.stderr.write(`[launchpulse] Your ${balance.tier} plan tokens are used up.\n`);
      process.stderr.write(`[launchpulse] Used: ${balance.used} / ${balance.limit}\n`);
      process.stderr.write('[launchpulse]\n');
      process.stderr.write(`[launchpulse] Upgrade your plan: ${balance.upgradeUrl}\n`);
      process.stderr.write(`[launchpulse] Buy token packs:   ${balance.buyTokensUrl}\n`);
      process.stderr.write('[launchpulse] ========================================\n');
      process.stderr.write('\n');
      const result = {
        ok: false,
        status: 'token_limit_exceeded',
        billing: {
          tier: balance.tier,
          upgradeUrl: balance.upgradeUrl,
          buyTokensUrl: balance.buyTokensUrl,
          used: balance.used,
          limit: balance.limit,
        },
        message: `Token limit reached. Upgrade at ${balance.upgradeUrl}`,
      };
      process.stdout.write(JSON.stringify(result, null, 2) + '\n');
      process.exit(5);
    }
    if (balance.usagePercent >= 80) {
      process.stderr.write(`[launchpulse] Warning: Token balance low (${balance.usagePercent}% used). Upgrade: ${balance.upgradeUrl}\n`);
    }
  } catch (err) {
    // Non-fatal: proceed if the balance endpoint is unavailable
    process.stderr.write(`[launchpulse] Could not check token balance: ${err?.message || String(err)}\n`);
  }
}

async function startAutoModeWithRetry(apiBase, projectId, authHeaders, userId, concurrency, options = {}) {
  const maxAttempts = 5;
  const url = withUserId(`${apiBase}/project/${encodeURIComponent(projectId)}/auto-mode/start`, userId);
  const quickStart = options && options.quickStart === true;
  const body = {
    ...(userId ? { userId } : {}),
    maxConcurrency: concurrency,
    ...(quickStart ? { quickStart: true } : {}),
  };

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fetchJson(url, {
        method: 'POST',
        headers: authHeaders,
        body,
        timeoutMs: 60_000,
      });
    } catch (err) {
      if (attempt < maxAttempts && isProjectNotReady(err)) {
        process.stderr.write(
          `[launchpulse] Project not ready for ${quickStart ? 'quick start' : 'auto-build'} yet (attempt ${attempt}/${maxAttempts}); retrying...\n`,
        );
        await sleep(2000 * attempt);
        continue;
      }
      if (isAutoModeAlreadyRunning(err)) {
        process.stderr.write(`[launchpulse] ${quickStart ? 'Quick start' : 'Auto-build'} is already running for this project; attaching to existing session.\n`);
        return { sessionId: null, alreadyRunning: true, quickStart };
      }
      throw err;
    }
  }

  throw new Error(`Failed to start ${quickStart ? 'quick start' : 'auto-build'}`);
}

async function continueAutoMode(apiBase, projectId, authHeaders, userId) {
  return fetchJson(withUserId(`${apiBase}/project/${encodeURIComponent(projectId)}/auto-mode/continue`, userId), {
    method: 'POST',
    headers: authHeaders,
    body: {
      ...(userId ? { userId } : {}),
    },
    timeoutMs: 60_000,
  });
}

async function fetchUnifiedBuildStatus(apiBase, projectId, authHeaders, userId) {
  return fetchJson(withUserId(`${apiBase}/project/${encodeURIComponent(projectId)}/build-status`, userId), {
    method: 'GET',
    headers: authHeaders,
    timeoutMs: 30_000,
  });
}

async function ackUnifiedBuildCompletion(apiBase, projectId, authHeaders, userId, completionAt) {
  return fetchJson(withUserId(`${apiBase}/project/${encodeURIComponent(projectId)}/build-status/ack-completion`, userId), {
    method: 'POST',
    headers: authHeaders,
    body: {
      ...(userId ? { userId } : {}),
      ...(completionAt ? { completionAt } : {}),
    },
    timeoutMs: 20_000,
  });
}

async function ensureAuthContext(cfg) {
  // Priority order: explicit PAT/API key -> stored PAT -> Supabase access token -> userId fallback -> device login
  const directPat = cfg.pat && String(cfg.pat).trim().length ? String(cfg.pat).trim() : null;
  const storedAuth = loadStoredAuth();
  const storedPat = storedAuth.pat;
  const storedUserId = storedAuth.userId;
  const accessToken = cfg.accessToken && String(cfg.accessToken).trim().length ? String(cfg.accessToken).trim() : null;
  const fallbackUserId = cfg.userId && String(cfg.userId).trim().length ? String(cfg.userId).trim() : null;
  const derivedUserIdFromPat = directPat ? deriveUserIdFromJwt(directPat) : null;
  const derivedUserIdFromStoredPat = storedPat ? deriveUserIdFromJwt(storedPat) : null;
  const derivedUserIdFromJwt = accessToken ? deriveUserIdFromJwt(accessToken) : null;
  const preferredUserId =
    fallbackUserId ||
    derivedUserIdFromJwt ||
    derivedUserIdFromPat ||
    storedUserId ||
    derivedUserIdFromStoredPat ||
    null;

  if (directPat) return { bearerToken: directPat, userId: preferredUserId };
  if (storedPat) return { bearerToken: storedPat, userId: preferredUserId };
  if (accessToken) return { bearerToken: accessToken, userId: preferredUserId };
  if (preferredUserId) {
    process.stderr.write('[launchpulse] Using legacy userId mode (no bearer token).\n');
    return { bearerToken: null, userId: preferredUserId };
  }

  if (cfg.noLogin) {
    throw new Error('Not authenticated. Run `launchpulse.cjs login`, or provide --pat/--api-key (LAUNCHPULSE_PAT/LAUNCHPULSE_API_KEY), or pass --user-id for legacy mode.');
  }

  try {
    const login = await runDeviceLoginFlow(cfg.apiBase);
    return { bearerToken: login.pat, userId: login.userId || null };
  } catch (err) {
    if (isDeviceAuthUnsupported(err)) {
      throw new Error(
        `Device auth endpoints are not available on ${cfg.apiBase}. Use --api-base to point to your updated/local backend, or pass --user-id for legacy mode.`,
      );
    }
    throw err;
  }
}

function summarizeFeatures(featuresPayload) {
  if (
    featuresPayload &&
    typeof featuresPayload === 'object' &&
    Number.isFinite(Number(featuresPayload.selectedCount)) &&
    Number.isFinite(Number(featuresPayload.completedCount))
  ) {
    const totalMaybe = Number.isFinite(Number(featuresPayload.totalCount))
      ? Number(featuresPayload.totalCount)
      : Number(featuresPayload.selectedCount);
    return {
      total: totalMaybe,
      selected: Number(featuresPayload.selectedCount),
      completed: Number(featuresPayload.completedCount),
    };
  }

  const features = Array.isArray(featuresPayload?.features)
    ? featuresPayload.features
    : (Array.isArray(featuresPayload) ? featuresPayload : null);
  if (!features) return { total: null, selected: null, completed: null };

  const selected = features.filter((f) => f && f.selected !== false);
  const completed = selected.filter(
    (f) => f && (f.passes === true || f.status === 'completed' || f.status === 'skipped'),
  );

  return {
    total: features.length,
    selected: selected.length,
    completed: completed.length,
  };
}

function normalizeFeatureSteps(rawSteps) {
  if (!Array.isArray(rawSteps)) return ['Implement and verify this feature end-to-end'];
  const cleaned = rawSteps
    .map((s) => (typeof s === 'string' ? s.trim() : ''))
    .filter((s) => s.length > 0)
    .slice(0, 6);
  return cleaned.length > 0 ? cleaned : ['Implement and verify this feature end-to-end'];
}

function normalizePlannedFeatures(rawFeatures) {
  if (!Array.isArray(rawFeatures)) return [];

  const normalized = rawFeatures
    .map((feature, index) => {
      const priorityRaw = Number(feature?.priority);
      const priority = Number.isFinite(priorityRaw)
        ? Math.min(Math.max(1, Math.floor(priorityRaw)), 5)
        : Math.min(index + 1, 5);

      const idCandidate = typeof feature?.id === 'string' && feature.id.trim().length
        ? feature.id
        : `${feature?.category || 'feature'}-${index + 1}`;
      const id = slugify(idCandidate) || `feature-${index + 1}`;

      const category = typeof feature?.category === 'string' && feature.category.trim().length
        ? feature.category.trim()
        : 'functional';

      const description = typeof feature?.description === 'string' && feature.description.trim().length
        ? feature.description.trim()
        : `Implement ${id.replace(/-/g, ' ')}`;

      const orderRaw = Number(feature?.order);
      const order = Number.isFinite(orderRaw) ? Math.max(1, Math.floor(orderRaw)) : index + 1;
      const selected = feature?.selected === false ? false : priority <= 3;

      return {
        ...feature,
        id,
        category,
        description,
        steps: normalizeFeatureSteps(feature?.steps),
        priority,
        order,
        selected,
        status: 'pending',
        passes: false,
      };
    })
    .filter((feature) => typeof feature.id === 'string' && typeof feature.description === 'string');

  if (normalized.length > 0 && normalized.every((feature) => feature.selected === false)) {
    normalized[0].selected = true;
  }

  return normalized;
}

function buildFallbackFeatures(description, mode) {
  const appType = mode === 'mobile-app' ? 'Expo React Native mobile app' : 'web app';
  return [
    {
      id: mode === 'mobile-app' ? 'mvp-mobile-foundation' : 'mvp-web-foundation',
      category: 'functional',
      description: `Build a complete production-ready ${appType} MVP based on this request: ${description}`,
      steps: [
        'Implement the primary user flow described in the request',
        'Create polished UI screens/components for all core flows',
        'Connect real data/state management and backend interactions',
        'Run lint/type/build checks and resolve errors',
        'Verify all core flows in preview and mark this feature as passed',
      ],
      priority: 1,
      order: 1,
      selected: true,
      status: 'pending',
      passes: false,
    },
  ];
}

async function planFeaturesWithRetry(cfg, authHeaders, legacyUserId) {
  const maxAttempts = 3;
  let lastError = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    process.stderr.write(`[launchpulse] Planning features (attempt ${attempt}/${maxAttempts})...\n`);
    try {
      const planned = await fetchJson(`${cfg.apiBase}/projects/plan-features`, {
        method: 'POST',
        headers: authHeaders,
        body: {
          description: cfg.description,
          ...(legacyUserId ? { userId: legacyUserId } : {}),
          streaming: false,
        },
        timeoutMs: 120_000,
      });

      const raw = Array.isArray(planned?.features)
        ? planned.features
        : (Array.isArray(planned) ? planned : null);
      const normalized = normalizePlannedFeatures(raw);

      if (normalized.length > 0) {
        return normalized;
      }

      lastError = new Error('Planner returned no features.');
    } catch (err) {
      lastError = err;
    }

    if (attempt < maxAttempts) {
      await sleep(2000 * attempt);
    }
  }

  throw lastError || new Error('Feature planning failed.');
}

async function saveApprovedFeatures(cfg, projectId, authHeaders, legacyUserId, features) {
  await fetchJson(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/features`, legacyUserId), {
    method: 'PUT',
    headers: authHeaders,
    body: {
      ...(legacyUserId ? { userId: legacyUserId } : {}),
      features,
    },
    timeoutMs: 120_000,
  });

  // Keep parity with UI flow: clear planning gate once features are approved.
  try {
    await fetchJson(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/metadata`, legacyUserId), {
      method: 'PATCH',
      headers: authHeaders,
      body: {
        ...(legacyUserId ? { userId: legacyUserId } : {}),
        updates: { needsFeaturePlanning: false },
      },
      timeoutMs: 60_000,
    });
  } catch (err) {
    const msg = err?.message || String(err);
    process.stderr.write(`[launchpulse] Warning: could not clear metadata planning flag: ${msg}\n`);
  }
}

function summarizeIterationPayload(iteratePayload) {
  if (!iteratePayload || typeof iteratePayload !== 'object') return iteratePayload;
  const response = iteratePayload.response || null;
  const validation = iteratePayload.validation || null;

  return {
    success: iteratePayload.success ?? null,
    aborted: iteratePayload.aborted ?? null,
    response: response
      ? pick(response, [
          'response',
          'changedFiles',
          'commitHash',
          'snapshotId',
          'databaseLSN',
          'sessionId',
        ])
      : null,
    validation: validation
      ? pick(validation, ['success', 'message', 'criticalIssues', 'usedGitHub'])
      : null,
  };
}

async function main() {
  const startedAt = Date.now();
  const startedAtIso = nowIso();

  let cfg;
  try {
    cfg = parseArgs(process.argv.slice(2));
  } catch (e) {
    process.stderr.write(`${e.message || String(e)}\n`);
    usage(1);
    return;
  }

  process.stderr.write(`[launchpulse] API: ${cfg.apiBase}\n`);

  if (cfg.cmd === 'logout') {
    const ok = clearStoredPat();
    const result = {
      ok,
      status: ok ? 'logged_out' : 'not_logged_in',
      authFile: getAuthFilePath(),
    };
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    return;
  }

  if (cfg.cmd === 'login') {
    const login = await runDeviceLoginFlow(cfg.apiBase);
    const result = {
      ok: true,
      status: 'logged_in',
      tokenPrefix: String(login.pat).slice(0, 12),
      userId: login.userId || null,
      authFile: getAuthFilePath(),
    };
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    return;
  }

  const auth = await ensureAuthContext(cfg);
  const authHeaders = buildAuthHeaders(auth.bearerToken);
  const legacyUserId = auth.userId;

  // ─── status command ────────────────────────────────────────────────
  if (cfg.cmd === 'status') {
    try {
      const balance = await fetchUsageBalance(cfg.apiBase, authHeaders);
      const pct = Math.round(balance.usagePercent || 0);
      const statusLabel = balance.isExhausted ? 'EXHAUSTED' : pct >= 80 ? 'LOW' : 'OK';

      process.stderr.write(`[launchpulse] Plan:      ${balance.tier}\n`);
      process.stderr.write(`[launchpulse] Used:      ${balance.used} / ${balance.limit}\n`);
      process.stderr.write(`[launchpulse] Available: ${balance.available}\n`);
      process.stderr.write(`[launchpulse] Usage:     ${pct}%\n`);
      process.stderr.write(`[launchpulse] Status:    ${statusLabel}\n`);
      if (balance.isExhausted || pct >= 80) {
        process.stderr.write(`[launchpulse] Upgrade:   ${balance.upgradeUrl}\n`);
      }

      process.stdout.write(JSON.stringify({ ok: true, ...balance, statusLabel }, null, 2) + '\n');
    } catch (err) {
      if (handleBillingError(err)) { process.exit(5); return; }
      throw err;
    }
    return;
  }

  // ─── upgrade command ───────────────────────────────────────────────
  if (cfg.cmd === 'upgrade') {
    const TOKEN_PACKS = [
      { index: 0, tokens: '50K', price: '$5' },
      { index: 1, tokens: '100K', price: '$9' },
      { index: 2, tokens: '500K', price: '$39' },
      { index: 3, tokens: '1M', price: '$69' },
    ];

    // Determine what type of upgrade
    const wantAddon = cfg.tokens !== null && Number.isFinite(cfg.tokens);
    const wantSubscription = cfg.tier && ['STARTER', 'BUILDER'].includes(cfg.tier);

    if (!wantAddon && !wantSubscription) {
      // Show available options
      process.stderr.write('[launchpulse] Upgrade options:\n');
      process.stderr.write('[launchpulse]\n');
      process.stderr.write('[launchpulse] Subscriptions:\n');
      process.stderr.write('[launchpulse]   --tier STARTER   $19/mo  200K tokens\n');
      process.stderr.write('[launchpulse]   --tier BUILDER   $49/mo  500K tokens\n');
      process.stderr.write('[launchpulse]   Add --billing-period annual for ~20% off\n');
      process.stderr.write('[launchpulse]\n');
      process.stderr.write('[launchpulse] Token addon packs (one-time, never expire):\n');
      for (const p of TOKEN_PACKS) {
        process.stderr.write(`[launchpulse]   --tokens ${p.index}  ${p.tokens} tokens  ${p.price}\n`);
      }
      process.stderr.write('[launchpulse]\n');
      process.stderr.write('[launchpulse] Or visit: https://launchpulse.ai/billing\n');
      process.stdout.write(JSON.stringify({
        ok: true,
        status: 'upgrade_options_shown',
        upgradeUrl: 'https://launchpulse.ai/billing',
        subscriptions: [
          { tier: 'STARTER', price: '$19/mo', tokens: '200K' },
          { tier: 'BUILDER', price: '$49/mo', tokens: '500K' },
        ],
        tokenPacks: TOKEN_PACKS,
      }, null, 2) + '\n');
      return;
    }

    // Generate checkout link
    const body = wantAddon
      ? { type: 'addon', packIndex: cfg.tokens }
      : { type: 'subscription', tier: cfg.tier, billingPeriod: cfg.billingPeriod };

    try {
      const checkout = await fetchJson(`${cfg.apiBase}/billing/checkout-link`, {
        method: 'POST',
        headers: authHeaders,
        body,
        timeoutMs: 30_000,
      });

      if (checkout && checkout.url) {
        process.stderr.write(`[launchpulse] Checkout link generated!\n`);
        process.stderr.write(`[launchpulse] Open this link to complete your purchase:\n`);
        process.stderr.write(`[launchpulse] ${checkout.url}\n`);
        process.stdout.write(JSON.stringify({ ok: true, status: 'checkout_link', url: checkout.url }, null, 2) + '\n');
      } else {
        throw new Error('No checkout URL returned');
      }
    } catch (err) {
      // Fallback: direct to billing page
      const billingUrl = 'https://launchpulse.ai/billing';
      process.stderr.write(`[launchpulse] Could not generate checkout link: ${err?.message || String(err)}\n`);
      process.stderr.write(`[launchpulse] Visit ${billingUrl} to upgrade.\n`);
      process.stdout.write(JSON.stringify({ ok: false, status: 'checkout_fallback', upgradeUrl: billingUrl, error: err?.message }, null, 2) + '\n');
      process.exit(4);
    }
    return;
  }

  if (cfg.cmd === 'projects') {
    const headers = withUserHeaders(authHeaders, legacyUserId);
    const payload = await fetchJson(`${cfg.apiBase}/projects/list`, {
      method: 'GET',
      headers,
      timeoutMs: 30_000,
    });

    const projects = Array.isArray(payload?.projects) ? payload.projects : (Array.isArray(payload) ? payload : []);
    process.stderr.write(`[launchpulse] Found ${projects.length} project(s)\n`);
    process.stdout.write(JSON.stringify({
      ok: true,
      status: 'projects',
      count: projects.length,
      projects,
    }, null, 2) + '\n');
    return;
  }

  if (cfg.cmd === 'project-status') {
    const projectId = cfg.projectId;
    const headers = withUserHeaders(authHeaders, legacyUserId);

    const requests = [
      fetchJson(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/build-status`, legacyUserId), { method: 'GET', headers, timeoutMs: 30_000 }),
      fetchJson(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/preview-status`, legacyUserId), { method: 'GET', headers, timeoutMs: 30_000 }),
      fetchJson(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/deployment/info`, legacyUserId), { method: 'GET', headers, timeoutMs: 30_000 }),
      fetchJson(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/store/publish/status`, legacyUserId), { method: 'GET', headers, timeoutMs: 30_000 }),
      fetchJson(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/features`, legacyUserId), { method: 'GET', headers, timeoutMs: 30_000 }),
    ];

    const [buildRes, previewRes, deployRes, storeRes, featuresRes] = await Promise.allSettled(requests);
    const unwrap = (settled) => settled.status === 'fulfilled'
      ? { ok: true, data: settled.value }
      : { ok: false, error: settled.reason?.message || String(settled.reason || 'Unknown error') };

    const build = unwrap(buildRes);
    const preview = unwrap(previewRes);
    const deploy = unwrap(deployRes);
    const store = unwrap(storeRes);
    const features = unwrap(featuresRes);

    const featureSummary = summarizeFeatures(features.ok ? features.data : null);
    process.stdout.write(JSON.stringify({
      ok: build.ok || preview.ok || deploy.ok || store.ok || features.ok,
      status: 'project_status',
      projectId,
      buildStatus: build,
      previewStatus: preview,
      deploymentInfo: deploy,
      storePublish: store,
      features: features,
      featureSummary,
      checkedAt: nowIso(),
    }, null, 2) + '\n');
    return;
  }

  if (cfg.cmd === 'deploy-status') {
    const projectId = cfg.projectId;
    const deploymentId = cfg.deploymentId;
    const headers = withUserHeaders(authHeaders, legacyUserId);
    const status = await fetchJson(
      withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/deployment/${encodeURIComponent(deploymentId)}/status`, legacyUserId),
      { method: 'GET', headers, timeoutMs: 30_000 },
    );

    process.stdout.write(JSON.stringify({
      ok: true,
      status: 'deploy_status',
      projectId,
      deploymentId,
      deployment: status?.deployment || status,
      raw: status,
    }, null, 2) + '\n');
    return;
  }

  if (cfg.cmd === 'deploy') {
    const projectId = cfg.projectId;
    const headers = withUserHeaders(authHeaders, legacyUserId);
    let startResult = null;

    if (cfg.target === 'cloud-run') {
      startResult = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/deploy/cloud-run`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            ...(legacyUserId ? { userId: legacyUserId } : {}),
            ...(cfg.region ? { gcpRegion: cfg.region } : {}),
          },
          timeoutMs: 60_000,
        },
      );
    } else if (cfg.target === 'fly') {
      const githubUsername = cfg.githubUsername || process.env.GITHUB_USERNAME || null;
      const githubToken = cfg.githubToken || process.env.GITHUB_TOKEN || null;
      const flyApiToken = cfg.flyToken || process.env.FLY_API_TOKEN || null;
      if (!githubUsername || !githubToken || !flyApiToken) {
        throw new Error('deploy --target fly requires --github-username, --github-token, and --fly-token (or env vars)');
      }

      startResult = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/deploy`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            ...(legacyUserId ? { userId: legacyUserId } : {}),
            githubUsername,
            githubToken,
            flyApiToken,
          },
          timeoutMs: 60_000,
        },
      );
    } else {
      throw new Error(`Unsupported deploy target "${cfg.target}". Use --target cloud-run or --target fly.`);
    }

    const deploymentId = startResult?.deploymentId || null;
    if (!cfg.wait || !deploymentId) {
      process.stdout.write(JSON.stringify({
        ok: true,
        status: 'deploy_started',
        projectId,
        target: cfg.target,
        deploymentId,
        result: startResult,
      }, null, 2) + '\n');
      return;
    }

    process.stderr.write(`[launchpulse] Waiting for deployment ${deploymentId}...\n`);
    const deadline = Date.now() + cfg.timeoutMin * 60_000;
    let deployment = null;
    let timedOut = false;

    while (Date.now() < deadline) {
      const status = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/deployment/${encodeURIComponent(deploymentId)}/status`, legacyUserId),
        { method: 'GET', headers, timeoutMs: 30_000 },
      );

      deployment = status?.deployment || null;
      const state = String(deployment?.status || '').toLowerCase();
      process.stderr.write(`[launchpulse] Deploy status: ${state || 'unknown'}\n`);

      if (state === 'completed') {
        process.stdout.write(JSON.stringify({
          ok: true,
          status: 'deploy_completed',
          projectId,
          target: cfg.target,
          deploymentId,
          deployment,
        }, null, 2) + '\n');
        return;
      }

      if (state === 'failed') {
        process.stdout.write(JSON.stringify({
          ok: false,
          status: 'deploy_failed',
          projectId,
          target: cfg.target,
          deploymentId,
          deployment,
        }, null, 2) + '\n');
        process.exit(4);
        return;
      }

      await sleep(cfg.pollMs);
    }

    timedOut = true;
    process.stdout.write(JSON.stringify({
      ok: false,
      status: timedOut ? 'timeout' : 'deploy_unknown',
      projectId,
      target: cfg.target,
      deploymentId,
      deployment,
    }, null, 2) + '\n');
    process.exit(3);
    return;
  }

  if (cfg.cmd === 'store-status') {
    const projectId = cfg.projectId;
    const headers = withUserHeaders(authHeaders, legacyUserId);
    const url = new URL(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/store/publish/status`, legacyUserId));
    if (cfg.publishId) url.searchParams.set('publishId', cfg.publishId);
    const status = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });

    process.stdout.write(JSON.stringify({
      ok: true,
      status: 'store_status',
      projectId,
      publishId: cfg.publishId || status?.publishId || null,
      store: status,
    }, null, 2) + '\n');
    return;
  }

  if (cfg.cmd === 'store-2fa') {
    const projectId = cfg.projectId;
    const headers = withUserHeaders(authHeaders, legacyUserId);
    const result = await fetchJson(
      withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/store/publish/2fa`, legacyUserId),
      {
        method: 'POST',
        headers,
        body: {
          ...(legacyUserId ? { userId: legacyUserId } : {}),
          publishId: cfg.publishId,
          code: cfg.twoFactorCode,
        },
        timeoutMs: 30_000,
      },
    );

    process.stdout.write(JSON.stringify({
      ok: true,
      status: 'store_2fa_submitted',
      projectId,
      publishId: cfg.publishId,
      result,
    }, null, 2) + '\n');
    return;
  }

  if (cfg.cmd === 'store-publish') {
    const projectId = cfg.projectId;
    const headers = withUserHeaders(authHeaders, legacyUserId);
    const payload = readJsonFile(cfg.payloadFile, 'store publish payload');
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
      throw new Error('store-publish payload must be a JSON object');
    }
    if (legacyUserId && !payload.userId) payload.userId = legacyUserId;

    const start = await fetchJson(
      withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/store/publish`, legacyUserId),
      {
        method: 'POST',
        headers,
        body: payload,
        timeoutMs: 60_000,
      },
    );

    const publishId = start?.publishId || payload.publishId || null;
    if (!cfg.wait) {
      process.stdout.write(JSON.stringify({
        ok: true,
        status: 'store_publish_started',
        projectId,
        publishId,
        result: start,
      }, null, 2) + '\n');
      return;
    }

    process.stderr.write('[launchpulse] Waiting for store publish status...\n');
    const deadline = Date.now() + cfg.timeoutMin * 60_000;
    let finalStatus = null;
    let latest = null;

    while (Date.now() < deadline) {
      const url = new URL(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/store/publish/status`, legacyUserId));
      if (publishId) url.searchParams.set('publishId', publishId);
      latest = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });
      finalStatus = String(latest?.status || '').toLowerCase() || 'unknown';
      process.stderr.write(`[launchpulse] Store publish status: ${finalStatus}\n`);

      if (finalStatus === 'completed') {
        process.stdout.write(JSON.stringify({
          ok: true,
          status: 'store_publish_completed',
          projectId,
          publishId: publishId || latest?.publishId || null,
          store: latest,
        }, null, 2) + '\n');
        return;
      }

      if (finalStatus === 'awaiting_2fa') {
        process.stdout.write(JSON.stringify({
          ok: false,
          status: 'store_publish_awaiting_2fa',
          projectId,
          publishId: publishId || latest?.publishId || null,
          store: latest,
        }, null, 2) + '\n');
        process.exit(2);
        return;
      }

      if (finalStatus === 'failed') {
        process.stdout.write(JSON.stringify({
          ok: false,
          status: 'store_publish_failed',
          projectId,
          publishId: publishId || latest?.publishId || null,
          store: latest,
        }, null, 2) + '\n');
        process.exit(4);
        return;
      }

      await sleep(cfg.pollMs);
    }

    process.stdout.write(JSON.stringify({
      ok: false,
      status: 'timeout',
      projectId,
      publishId: publishId || latest?.publishId || null,
      store: latest,
    }, null, 2) + '\n');
    process.exit(3);
    return;
  }

  if (cfg.cmd === 'domains') {
    const action = String(cfg.subcommand || '').toLowerCase();
    const args = cfg.subcommandArgs || [];
    const headers = withUserHeaders(authHeaders, legacyUserId);

    if (action === 'search') {
      const query = args.join(' ').trim();
      if (!query) throw new Error('Usage: launchpulse.cjs domains search <query>');
      const url = new URL(withUserId(`${cfg.apiBase}/domains/search`, legacyUserId));
      url.searchParams.set('query', query);
      const result = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_search', query, result }, null, 2) + '\n');
      return;
    }

    if (action === 'check') {
      const domain = args[0];
      if (!domain) throw new Error('Usage: launchpulse.cjs domains check <domain>');
      const url = new URL(withUserId(`${cfg.apiBase}/domains/check`, legacyUserId));
      url.searchParams.set('domain', domain);
      const result = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_check', domain, result }, null, 2) + '\n');
      return;
    }

    if (action === 'my' || action === 'mine') {
      const url = new URL(withUserId(`${cfg.apiBase}/domains/my-domains`, legacyUserId));
      if (args[0]) url.searchParams.set('projectId', args[0]);
      const result = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_my', result }, null, 2) + '\n');
      return;
    }

    if (action === 'project-list') {
      const projectId = args[0];
      if (!projectId) throw new Error('Usage: launchpulse.cjs domains project-list <projectId>');
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/domains`, legacyUserId),
        { method: 'GET', headers, timeoutMs: 30_000 },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_project_list', projectId, result }, null, 2) + '\n');
      return;
    }

    if (action === 'add' || action === 'primary') {
      const projectId = args[0];
      const domain = args[1];
      if (!projectId || !domain) {
        throw new Error(`Usage: launchpulse.cjs domains ${action} <projectId> <domain>`);
      }
      const pathSuffix = action === 'add' ? 'domains/add' : 'domains/primary';
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/${pathSuffix}`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            ...(legacyUserId ? { userId: legacyUserId } : {}),
            domain,
          },
          timeoutMs: 30_000,
        },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: `domains_${action}`, projectId, domain, result }, null, 2) + '\n');
      return;
    }

    if (action === 'provision') {
      const projectId = args[0];
      const domain = args[1];
      const appName = args[2] || cfg.appName;
      if (!projectId || !domain || !appName) {
        throw new Error('Usage: launchpulse.cjs domains provision <projectId> <domain> <appName>');
      }
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/domains/provision`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            ...(legacyUserId ? { userId: legacyUserId } : {}),
            domain,
            appName,
            ...(cfg.flyToken ? { flyApiToken: cfg.flyToken } : {}),
          },
          timeoutMs: 60_000,
        },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_provision', projectId, domain, appName, result }, null, 2) + '\n');
      return;
    }

    if (action === 'status') {
      const projectId = args[0];
      const domain = args[1];
      const appName = args[2] || cfg.appName;
      if (!projectId || !domain || !appName) {
        throw new Error('Usage: launchpulse.cjs domains status <projectId> <domain> <appName>');
      }
      const url = new URL(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/domains/status`, legacyUserId));
      url.searchParams.set('domain', domain);
      url.searchParams.set('appName', appName);
      if (cfg.flyToken) url.searchParams.set('flyApiToken', cfg.flyToken);
      if (cfg.region) url.searchParams.set('region', cfg.region);
      const result = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_status', projectId, domain, appName, result }, null, 2) + '\n');
      return;
    }

    if (action === 'dns') {
      const projectId = args[0];
      const fqdn = args[1];
      const type = String(args[2] || cfg.recordType || 'CNAME').toUpperCase();
      if (!projectId || !fqdn) {
        throw new Error('Usage: launchpulse.cjs domains dns <projectId> <fqdn> [recordType]');
      }
      const url = new URL(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/domains/dns-lookup`, legacyUserId));
      url.searchParams.set('fqdn', fqdn);
      url.searchParams.set('type', type);
      const result = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_dns', projectId, fqdn, type, result }, null, 2) + '\n');
      return;
    }

    if (action === 'map') {
      const projectId = args[0];
      const domain = args[1];
      const serviceName = args[2] || cfg.serviceName || null;
      const region = args[3] || cfg.region || null;
      if (!projectId || !domain) {
        throw new Error('Usage: launchpulse.cjs domains map <projectId> <domain> [serviceName] [region]');
      }
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/domain/map`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            ...(legacyUserId ? { userId: legacyUserId } : {}),
            domain,
            ...(serviceName ? { serviceName } : {}),
            ...(region ? { region } : {}),
          },
          timeoutMs: 60_000,
        },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_map', projectId, domain, serviceName, region, result }, null, 2) + '\n');
      return;
    }

    if (action === 'mapping-status') {
      const projectId = args[0];
      const domain = args[1] || null;
      const region = args[2] || cfg.region || null;
      if (!projectId) throw new Error('Usage: launchpulse.cjs domains mapping-status <projectId> [domain] [region]');
      const url = new URL(withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/domain/status`, legacyUserId));
      if (domain) url.searchParams.set('domain', domain);
      if (region) url.searchParams.set('region', region);
      const result = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_mapping_status', projectId, domain, region, result }, null, 2) + '\n');
      return;
    }

    if (action === 'checkout') {
      const domain = args[0];
      const domainPrice = args[1];
      const projectId = args[2];
      if (!domain || !domainPrice || !projectId) {
        throw new Error('Usage: launchpulse.cjs domains checkout <domain> <domainPrice> <projectId>');
      }
      const result = await fetchJson(`${cfg.apiBase}/domains/create-checkout`, {
        method: 'POST',
        headers,
        body: {
          ...(legacyUserId ? { userId: legacyUserId } : {}),
          domain,
          domainPrice,
          projectId,
        },
        timeoutMs: 30_000,
      });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_checkout', domain, domainPrice, projectId, result }, null, 2) + '\n');
      return;
    }

    if (action === 'register') {
      const domain = args[0];
      const projectId = args[1] || null;
      if (!domain) throw new Error('Usage: launchpulse.cjs domains register <domain> [projectId] [--contact-file <json>]');
      const contactInfo = cfg.contactFile ? readJsonFile(cfg.contactFile, 'domain contact') : null;
      const result = await fetchJson(`${cfg.apiBase}/domains/register`, {
        method: 'POST',
        headers,
        body: {
          ...(legacyUserId ? { userId: legacyUserId } : {}),
          domain,
          ...(projectId ? { projectId } : {}),
          ...(contactInfo ? { contactInfo } : {}),
        },
        timeoutMs: 60_000,
      });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_register', domain, projectId, result }, null, 2) + '\n');
      return;
    }

    if (action === 'verification-start' || action === 'verification-verify') {
      const domain = args[0];
      if (!domain) throw new Error(`Usage: launchpulse.cjs domains ${action} <domain>`);
      const endpoint = action === 'verification-start' ? 'start' : 'verify';
      const result = await fetchJson(`${cfg.apiBase}/domains/verification/${endpoint}`, {
        method: 'POST',
        headers,
        body: {
          ...(legacyUserId ? { userId: legacyUserId } : {}),
          domain,
        },
        timeoutMs: 30_000,
      });
      process.stdout.write(JSON.stringify({ ok: true, status: `domains_${action.replace(/-/g, '_')}`, domain, result }, null, 2) + '\n');
      return;
    }

    if (action === 'verification-status') {
      const domain = args[0];
      if (!domain) throw new Error('Usage: launchpulse.cjs domains verification-status <domain>');
      const url = new URL(withUserId(`${cfg.apiBase}/domains/verification/status`, legacyUserId));
      url.searchParams.set('domain', domain);
      const result = await fetchJson(url.toString(), { method: 'GET', headers, timeoutMs: 30_000 });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_verification_status', domain, result }, null, 2) + '\n');
      return;
    }

    if (action === 'verification-list') {
      const result = await fetchJson(withUserId(`${cfg.apiBase}/domains/verification/list`, legacyUserId), {
        method: 'GET',
        headers,
        timeoutMs: 30_000,
      });
      process.stdout.write(JSON.stringify({ ok: true, status: 'domains_verification_list', result }, null, 2) + '\n');
      return;
    }

    throw new Error(
      'Unknown domains action. Use: search | check | my | project-list | add | primary | map | mapping-status | provision | status | dns | checkout | register | verification-start | verification-verify | verification-status | verification-list',
    );
  }

  if (cfg.cmd === 'db') {
    const action = String(cfg.subcommand || '').toLowerCase();
    const args = cfg.subcommandArgs || [];
    const headers = withUserHeaders(authHeaders, legacyUserId);

    if (action === 'info') {
      const projectId = args[0];
      if (!projectId) throw new Error('Usage: launchpulse.cjs db info <projectId>');
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/database`, legacyUserId),
        { method: 'GET', headers, timeoutMs: 45_000 },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'db_info', projectId, result }, null, 2) + '\n');
      return;
    }

    if (action === 'table') {
      const projectId = args[0];
      const tableName = args[1];
      if (!projectId || !tableName) throw new Error('Usage: launchpulse.cjs db table <projectId> <tableName>');
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/database/${encodeURIComponent(tableName)}/data`, legacyUserId),
        { method: 'GET', headers, timeoutMs: 45_000 },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'db_table', projectId, tableName, result }, null, 2) + '\n');
      return;
    }

    if (action === 'query') {
      const projectId = args[0];
      const sql = args.slice(1).join(' ').trim();
      if (!projectId || !sql) throw new Error('Usage: launchpulse.cjs db query <projectId> "<sql>"');
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/database/query`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            ...(legacyUserId ? { userId: legacyUserId } : {}),
            query: sql,
          },
          timeoutMs: 60_000,
        },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'db_query', projectId, sql, result }, null, 2) + '\n');
      return;
    }

    throw new Error('Unknown db action. Use: info | table | query');
  }

  if (cfg.cmd === 'storage') {
    const action = String(cfg.subcommand || '').toLowerCase();
    const args = cfg.subcommandArgs || [];
    const headers = withUserHeaders(authHeaders, legacyUserId);

    if (action === 'init') {
      const result = await fetchJson(`${cfg.apiBase}/storage/init-uploads-bucket`, {
        method: 'POST',
        headers,
        body: {},
        timeoutMs: 30_000,
      });
      process.stdout.write(JSON.stringify({ ok: true, status: 'storage_init', result }, null, 2) + '\n');
      return;
    }

    if (action === 'upload') {
      const projectId = args[0];
      if (!projectId || !cfg.payloadFile) {
        throw new Error('Usage: launchpulse.cjs storage upload <projectId> --payload-file <json>');
      }
      const payload = readJsonFile(cfg.payloadFile, 'storage upload payload');
      if (legacyUserId && !payload.userId) payload.userId = legacyUserId;
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/assets/upload-base64`, legacyUserId),
        { method: 'POST', headers, body: payload, timeoutMs: 60_000 },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'storage_upload', projectId, result }, null, 2) + '\n');
      return;
    }

    if (action === 'save-assets') {
      const projectId = args[0];
      if (!projectId || !cfg.payloadFile) {
        throw new Error('Usage: launchpulse.cjs storage save-assets <projectId> --payload-file <json>');
      }
      const payloadIn = readJsonFile(cfg.payloadFile, 'storage save-assets payload');
      const payload = Array.isArray(payloadIn)
        ? { assets: payloadIn }
        : { ...(payloadIn || {}) };
      if (legacyUserId && !payload.userId) payload.userId = legacyUserId;
      if (!Array.isArray(payload.assets)) {
        throw new Error('storage save-assets payload must contain an assets array');
      }
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/assets/save`, legacyUserId),
        { method: 'POST', headers, body: payload, timeoutMs: 60_000 },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'storage_save_assets', projectId, result }, null, 2) + '\n');
      return;
    }

    throw new Error('Unknown storage action. Use: init | upload | save-assets');
  }

  if (cfg.cmd === 'env-files') {
    const action = String(cfg.subcommand || '').toLowerCase();
    const args = cfg.subcommandArgs || [];
    const headers = withUserHeaders(authHeaders, legacyUserId);

    if (action === 'list') {
      const projectId = args[0];
      if (!projectId) throw new Error('Usage: launchpulse.cjs env-files list <projectId>');
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/env-files`, legacyUserId),
        { method: 'GET', headers, timeoutMs: 60_000 },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'env_files_list', projectId, result }, null, 2) + '\n');
      return;
    }

    if (action === 'save') {
      const projectId = args[0];
      const filePath = cfg.filePath || args[1] || null;
      const varsInput = cfg.varsFile ? readJsonFile(cfg.varsFile, 'env vars') : null;
      if (!projectId || !filePath || !varsInput) {
        throw new Error('Usage: launchpulse.cjs env-files save <projectId> --file-path <path> --vars-file <json>');
      }

      const vars = Array.isArray(varsInput)
        ? varsInput
        : Object.entries(varsInput).map(([key, value]) => ({ key, value: String(value), isSecret: /secret|key|token|password/i.test(key) }));

      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/env-files/save`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            filePath,
            variables: vars,
          },
          timeoutMs: 120_000,
        },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'env_files_save', projectId, filePath, result }, null, 2) + '\n');
      return;
    }

    throw new Error('Unknown env-files action. Use: list | save');
  }

  if (cfg.cmd === 'payments') {
    const action = String(cfg.subcommand || '').toLowerCase();
    const args = cfg.subcommandArgs || [];
    const headers = withUserHeaders(authHeaders, legacyUserId);

    if (action === 'inject-env') {
      const projectId = args[0];
      if (!projectId) throw new Error('Usage: launchpulse.cjs payments inject-env <projectId> [--project-type <vitereact|expo>]');
      const projectType = normalizeProjectType(cfg.projectType || args[1]) || 'vitereact';
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/inject-payment-env`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            projectType,
            ...(cfg.apiUrl ? { apiUrl: cfg.apiUrl } : {}),
          },
          timeoutMs: 120_000,
        },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'payments_inject_env', projectId, projectType, result }, null, 2) + '\n');
      return;
    }

    if (action === 'setup') {
      const projectId = args[0];
      if (!projectId) {
        throw new Error('Usage: launchpulse.cjs payments setup <projectId> [--project-type <vitereact|expo>] [keys...] [--vars-file <json>]');
      }
      const projectType = normalizeProjectType(cfg.projectType || args[1]) || 'vitereact';
      const envPath = cfg.filePath || (projectType === 'expo' ? 'expo/.env' : 'vitereact/.env');

      const generatedVars = [];
      if (cfg.stripePublishableKey) {
        generatedVars.push({
          key: projectType === 'expo' ? 'EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY' : 'VITE_STRIPE_PUBLISHABLE_KEY',
          value: cfg.stripePublishableKey,
          isSecret: false,
        });
      }
      if (cfg.stripeSecretKey) generatedVars.push({ key: 'STRIPE_SECRET_KEY', value: cfg.stripeSecretKey, isSecret: true });
      if (cfg.revenuecatIosKey) {
        generatedVars.push({
          key: projectType === 'expo' ? 'EXPO_PUBLIC_REVENUECAT_IOS_PUBLIC_KEY' : 'REVENUECAT_IOS_PUBLIC_KEY',
          value: cfg.revenuecatIosKey,
          isSecret: false,
        });
      }
      if (cfg.revenuecatAndroidKey) {
        generatedVars.push({
          key: projectType === 'expo' ? 'EXPO_PUBLIC_REVENUECAT_ANDROID_PUBLIC_KEY' : 'REVENUECAT_ANDROID_PUBLIC_KEY',
          value: cfg.revenuecatAndroidKey,
          isSecret: false,
        });
      }
      if (cfg.revenuecatSecretKey) generatedVars.push({ key: 'REVENUECAT_SECRET_KEY', value: cfg.revenuecatSecretKey, isSecret: true });
      if (cfg.revenuecatEntitlementId) generatedVars.push({ key: 'REVENUECAT_ENTITLEMENT_ID', value: cfg.revenuecatEntitlementId, isSecret: false });

      if (cfg.varsFile) {
        const varsInput = readJsonFile(cfg.varsFile, 'payments vars');
        const extraVars = Array.isArray(varsInput)
          ? varsInput
          : Object.entries(varsInput).map(([key, value]) => ({ key, value: String(value), isSecret: /secret|key|token|password/i.test(key) }));
        generatedVars.push(...extraVars);
      }

      if (generatedVars.length === 0) {
        throw new Error('payments setup requires at least one key flag or --vars-file');
      }

      // First inject LaunchPulse payment routing variables
      const injectResult = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/inject-payment-env`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            projectType,
            ...(cfg.apiUrl ? { apiUrl: cfg.apiUrl } : {}),
          },
          timeoutMs: 120_000,
        },
      );

      // Then save provider keys to env file and push to GitHub
      const saveResult = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/env-files/save`, legacyUserId),
        {
          method: 'POST',
          headers,
          body: {
            filePath: envPath,
            variables: generatedVars,
          },
          timeoutMs: 120_000,
        },
      );

      process.stdout.write(JSON.stringify({
        ok: true,
        status: 'payments_setup',
        projectId,
        projectType,
        filePath: envPath,
        injectedKeys: generatedVars.map((v) => v.key),
        injectResult,
        saveResult,
      }, null, 2) + '\n');
      return;
    }

    if (action === 'env-list') {
      const projectId = args[0];
      if (!projectId) throw new Error('Usage: launchpulse.cjs payments env-list <projectId>');
      const result = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/env-files`, legacyUserId),
        { method: 'GET', headers, timeoutMs: 60_000 },
      );
      process.stdout.write(JSON.stringify({ ok: true, status: 'payments_env_list', projectId, result }, null, 2) + '\n');
      return;
    }

    throw new Error('Unknown payments action. Use: inject-env | setup | env-list');
  }

  if (cfg.cmd === 'iterate') {
    const projectId = cfg.projectId;
    const mode = 'iterate';

    process.stderr.write(`[launchpulse] Mode: ${mode}\n`);
    process.stderr.write(`[launchpulse] Project: ${projectId}\n`);

    // Pre-flight billing check
    await preflightBalanceCheck(cfg.apiBase, authHeaders);

    process.stderr.write(`[launchpulse] Iterating...\n`);

    const iterateBody = {
      message: cfg.message,
      ...(legacyUserId ? { userId: legacyUserId } : {}),
      ...(cfg.chatId ? { chatId: cfg.chatId } : {}),
      ...(cfg.provider ? { provider: cfg.provider } : {}),
      ...(cfg.model ? { model: cfg.model } : {}),
    };

    const iterateTimeoutMs = Math.min(Math.max(1, cfg.timeoutMin), 240) * 60_000;
    let iteratePayload;
    try {
      iteratePayload = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/agent/iterate`, legacyUserId),
        { method: 'POST', headers: authHeaders, body: iterateBody, timeoutMs: iterateTimeoutMs },
      );
    } catch (err) {
      if (handleBillingError(err)) { process.exit(5); return; }
      throw err;
    }

    // Fetch preview status (best-effort)
    let previewRaw = null;
    try {
      previewRaw = await fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/preview-status`, legacyUserId),
        { method: 'GET', headers: authHeaders, timeoutMs: 30_000 },
      );
    } catch {
      previewRaw = null;
    }

    const preview = pick(previewRaw || {}, [
      'frontendUrl',
      'backendUrl',
      'expoGoUrl',
      'earlyPreviewHealthy',
      'message',
    ]);

    const iteration = summarizeIterationPayload(iteratePayload);
    const ok = iteration?.success !== false;

    const result = {
      ok,
      status: ok ? 'success' : 'iteration_failed',
      startedAt: startedAtIso,
      finishedAt: nowIso(),
      projectId,
      mode,
      preview,
      iteration,
    };

    process.stdout.write(JSON.stringify(result, null, 2) + '\n');

    if (!ok) process.exit(4);
    return;
  }

  // Create flow (web/mobile)
  const mode = cfg.cmd === 'web' ? 'single-agent' : 'mobile-app';
  const projectName = cfg.name ? slugify(cfg.name) : null;

  process.stderr.write(`[launchpulse] Mode: ${mode}\n`);

  // Pre-flight billing check
  await preflightBalanceCheck(cfg.apiBase, authHeaders);

  // 1) Create project
  process.stderr.write(`[launchpulse] Creating project...\n`);
  const createPayload = {
    ...(projectName ? { project: projectName } : {}),
    description: cfg.description,
    aesthetics: '',
    mode,
    ...(legacyUserId ? { userId: legacyUserId } : {}),
    needsFeaturePlanning: true,
    features: [],
  };

  const created = await fetchJson(`${cfg.apiBase}/projects/new`, {
    method: 'POST',
    headers: authHeaders,
    body: createPayload,
    timeoutMs: 120_000,
  });

  const projectId = created && (created.project || created.projectId || created.id);
  if (!projectId) {
    throw new Error(
      `Create project succeeded but response did not include project id. Response: ${JSON.stringify(created).slice(0, 500)}`,
    );
  }

  process.stderr.write(`[launchpulse] Project: ${projectId}\n`);

  // 2) Build non-interactive "approved features" set (UI parity without manual confirmation)
  let approvedFeatures = null;
  if (!cfg.noPlan) {
    try {
      approvedFeatures = await planFeaturesWithRetry(cfg, authHeaders, legacyUserId);
      process.stderr.write(`[launchpulse] Planned features: ${approvedFeatures.length}\n`);
    } catch (planErr) {
      const planMsg = planErr?.message || String(planErr);
      process.stderr.write(`[launchpulse] Planner unavailable (${planMsg}). Using MVP fallback feature.\n`);
      approvedFeatures = buildFallbackFeatures(cfg.description, mode);
    }
  } else {
    process.stderr.write('[launchpulse] Skipping planner (--no-plan); using MVP fallback feature.\n');
    approvedFeatures = buildFallbackFeatures(cfg.description, mode);
  }

  // 3) Save approved features and clear planning gate
  process.stderr.write(`[launchpulse] Saving ${approvedFeatures.length} approved feature(s)...\n`);
  await saveApprovedFeatures(cfg, projectId, authHeaders, legacyUserId, approvedFeatures);
  await sleep(500);

  // 4) Quick Start only: kick off initial build and return immediately.
  process.stderr.write('[launchpulse] Starting Quick Start build...\n');
  let quickStartStart;
  try {
    quickStartStart = await startAutoModeWithRetry(
      cfg.apiBase,
      projectId,
      authHeaders,
      legacyUserId,
      1,
      { quickStart: true },
    );
  } catch (err) {
    if (handleBillingError(err)) { process.exit(5); return; }
    throw err;
  }

  const sessionId = quickStartStart && (quickStartStart.sessionId || null);
  if (sessionId) {
    process.stderr.write(`[launchpulse] Quick Start session: ${sessionId}\n`);
  }

  // Best-effort snapshot for immediate user feedback.
  let buildStatus = null;
  let previewRaw = null;
  let featuresRaw = null;

  try {
    [buildStatus, previewRaw, featuresRaw] = await Promise.all([
      fetchUnifiedBuildStatus(cfg.apiBase, projectId, authHeaders, legacyUserId).catch(() => null),
      fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/preview-status`, legacyUserId),
        { method: 'GET', headers: authHeaders, timeoutMs: 20_000 },
      ).catch(() => null),
      fetchJson(
        withUserId(`${cfg.apiBase}/project/${encodeURIComponent(projectId)}/features`, legacyUserId),
        { method: 'GET', headers: authHeaders, timeoutMs: 20_000 },
      ).catch(() => null),
    ]);
  } catch {
    // Snapshot is optional.
  }

  const preview = pick((previewRaw || buildStatus?.preview || {}), [
    'frontendUrl',
    'backendUrl',
    'expoGoUrl',
    'earlyPreviewHealthy',
    'message',
  ]);
  const featureSummary = summarizeFeatures(
    (buildStatus?.features && typeof buildStatus.features === 'object')
      ? buildStatus.features
      : featuresRaw,
  );

  if (featureSummary.total === null) featureSummary.total = approvedFeatures.length;
  if (featureSummary.selected === null) featureSummary.selected = approvedFeatures.length;
  if (featureSummary.completed === null) featureSummary.completed = 0;

  const result = {
    ok: true,
    status: 'quick_start_started',
    startedAt: startedAtIso,
    finishedAt: nowIso(),
    projectId,
    mode,
    sessionId,
    quickStart: true,
    preview,
    features: featureSummary,
    buildState: typeof buildStatus?.state === 'string' ? buildStatus.state : null,
    message: 'Quick Start started. Build is running in the background. Use project-status to monitor progress.',
  };

  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  return;
}

main().catch((err) => {
  const message = err && err.message ? err.message : String(err);
  process.stderr.write(`[launchpulse] ERROR: ${message}\n`);
  process.exit(1);
});
