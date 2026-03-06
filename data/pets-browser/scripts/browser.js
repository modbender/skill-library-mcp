/**
 * browser.js — Clawnet for AI Agents v1.0.0
 *
 * Stealth browser with residential proxies from 10+ countries.
 * Appears as iPhone 15 Pro or Desktop Chrome to every website.
 * Bypasses Cloudflare, DataDome, PerimeterX out of the box.
 *
 * Service: https://clawpets.io
 *
 * Usage:
 *   const { launchBrowser, solveCaptcha } = require('./browser');
 *   const { browser, page } = await launchBrowser({ country: 'us' });
 *
 * Zero-config: launchBrowser() auto-registers a new agent on first call.
 * No env vars required. Credentials are saved to ~/.clawnet/agent-credentials.json.
 *
 * Proxy config via env vars (optional — BYO mode):
 *   CN_PROXY_PROVIDER  — decodo | brightdata | iproyal | nodemaven (default: decodo)
 *   CN_PROXY_USER      — proxy username
 *   CN_PROXY_PASS      — proxy password
 *   CN_PROXY_SERVER    — full override: http://host:port
 *   CN_PROXY_COUNTRY   — country code: ro, us, de, gb, fr, nl, sg... (default: us)
 *   CN_PROXY_SESSION   — Decodo sticky port 10001-49999 (unique IP per user)
 *   CN_NO_PROXY        — set to "1" to disable proxy entirely
 *
 * Service credentials (optional — auto-generated if not set):
 *   CN_API_URL         — Clawnet API base URL (default: https://api.clawpets.io/clawnet/v1)
 *   CN_AGENT_TOKEN     — Full auth token: CN1.<agentId>.<agentSecret>
 *   CN_AGENT_ID        — Agent UUID (alternative to token)
 *   CN_AGENT_SECRET    — Agent secret (alternative to token)
 *
 * CAPTCHA:
 *   TWOCAPTCHA_KEY     — 2captcha.com API key (BYO)
 */

// ─── PLAYWRIGHT RESOLVER ──────────────────────────────────────────────────────

function _requirePlaywright() {
  const tries = [
    () => require('playwright'),
    () => require(`${__dirname}/../node_modules/playwright`),
    () => require(`${__dirname}/../../node_modules/playwright`),
    () => require(`${process.env.HOME || '/root'}/.openclaw/workspace/node_modules/playwright`),
    () => require('./node_modules/playwright'),
  ];
  for (const fn of tries) {
    try { return fn(); } catch (_) {}
  }
  throw new Error(
    '[clawnet] playwright not found.\n' +
    'Run: npm install playwright && npx playwright install chromium'
  );
}

const { chromium } = _requirePlaywright();

// ─── COUNTRY CONFIGS ──────────────────────────────────────────────────────────

const COUNTRY_META = {
  ro: { locale: 'ro-RO', tz: 'Europe/Bucharest',  lat: 44.4268,  lon: 26.1025,   lang: 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7' },
  us: { locale: 'en-US', tz: 'America/New_York',   lat: 40.7128,  lon: -74.006,   lang: 'en-US,en;q=0.9' },
  uk: { locale: 'en-GB', tz: 'Europe/London',      lat: 51.5074,  lon: -0.1278,   lang: 'en-GB,en;q=0.9' },
  gb: { locale: 'en-GB', tz: 'Europe/London',      lat: 51.5074,  lon: -0.1278,   lang: 'en-GB,en;q=0.9' },
  de: { locale: 'de-DE', tz: 'Europe/Berlin',      lat: 52.5200,  lon: 13.4050,   lang: 'de-DE,de;q=0.9,en;q=0.8' },
  nl: { locale: 'nl-NL', tz: 'Europe/Amsterdam',   lat: 52.3676,  lon: 4.9041,    lang: 'nl-NL,nl;q=0.9,en;q=0.8' },
  jp: { locale: 'ja-JP', tz: 'Asia/Tokyo',         lat: 35.6762,  lon: 139.6503,  lang: 'ja-JP,ja;q=0.9,en;q=0.8' },
  fr: { locale: 'fr-FR', tz: 'Europe/Paris',       lat: 48.8566,  lon: 2.3522,    lang: 'fr-FR,fr;q=0.9,en;q=0.8' },
  ca: { locale: 'en-CA', tz: 'America/Toronto',    lat: 43.6532,  lon: -79.3832,  lang: 'en-CA,en;q=0.9' },
  au: { locale: 'en-AU', tz: 'Australia/Sydney',   lat: -33.8688, lon: 151.2093,  lang: 'en-AU,en;q=0.9' },
  sg: { locale: 'en-SG', tz: 'Asia/Singapore',     lat: 1.3521,   lon: 103.8198,  lang: 'en-SG,en;q=0.9' },
  br: { locale: 'pt-BR', tz: 'America/Sao_Paulo',  lat: -23.5505, lon: -46.6333,  lang: 'pt-BR,pt;q=0.9,en;q=0.8' },
  in: { locale: 'en-IN', tz: 'Asia/Kolkata',       lat: 28.6139,  lon: 77.2090,   lang: 'en-IN,en;q=0.9,hi;q=0.8' },
};

// ─── DEVICE PROFILES ─────────────────────────────────────────────────────────

function buildDevice(mobile, country = 'us') {
  const meta = COUNTRY_META[country.toLowerCase()] || COUNTRY_META.us;

  if (mobile) {
    return {
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Mobile/15E148 Safari/604.1',
      viewport: { width: 393, height: 852 },
      deviceScaleFactor: 3,
      isMobile: true,
      hasTouch: true,
      locale: meta.locale,
      timezoneId: meta.tz,
      geolocation: { latitude: meta.lat, longitude: meta.lon, accuracy: 50 },
      colorScheme: 'light',
      extraHTTPHeaders: {
        'Accept-Language': meta.lang,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
      },
    };
  }

  return {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    viewport: { width: 1440, height: 900 },
    locale: meta.locale,
    timezoneId: meta.tz,
    geolocation: { latitude: meta.lat, longitude: meta.lon, accuracy: 50 },
    colorScheme: 'light',
    extraHTTPHeaders: {
      'Accept-Language': meta.lang,
      'sec-ch-ua': '"Google Chrome";v="134", "Chromium";v="134", "Not_A Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"',
    },
  };
}

// ─── PROXY PRESETS ────────────────────────────────────────────────────────────

const PROXY_PRESETS = {
  decodo: {
    serverTemplate: (country, port) => `http://${country}.decodo.com:${port}`,
    usernameTemplate: (user) => user,
    defaultCountry: 'us',
    stickyPortMin: 10001,
    stickyPortMax: 49999,
  },
  brightdata: {
    server: 'http://brd.superproxy.io:33335',
    usernameTemplate: (user, country, session) =>
      `${user}-country-${country}-session-${session}`,
    defaultCountry: 'us',
  },
  iproyal: {
    server: 'http://geo.iproyal.com:12321',
    usernameTemplate: (user) => user,
    passwordTemplate: (pass, country, session) =>
      `${pass}_country-${country}_session-${session}_lifetime-30m`,
    defaultCountry: 'us',
  },
  nodemaven: {
    server: 'http://rp.nodemavenio.com:10001',
    usernameTemplate: (user, country, session) =>
      `${user}-country-${country}-session-${session}`,
    defaultCountry: 'us',
  },
};

function makeProxy(sessionId = null, country = null) {
  if (process.env.CN_NO_PROXY === '1') return null;

  const cty = (country || process.env.CN_PROXY_COUNTRY || 'us').toLowerCase();

  // 1. Full manual BYO override — explicit env vars take priority
  if (process.env.CN_PROXY_SERVER && process.env.CN_PROXY_USER) {
    return {
      server:   process.env.CN_PROXY_SERVER,
      username: process.env.CN_PROXY_USER,
      password: process.env.CN_PROXY_PASS || '',
    };
  }

  // 2. BYO provider (decodo / brightdata / iproyal / nodemaven via CN_PROXY_PROVIDER)
  //    Only activates when BOTH provider AND credentials are set.
  //    Without CN_PROXY_USER/CN_PROXY_PASS, falls through to managed mode.
  const providerName = process.env.CN_PROXY_PROVIDER;
  const providerUser = process.env.CN_PROXY_USER?.trim();
  const providerPass = process.env.CN_PROXY_PASS?.trim();
  if (providerName && PROXY_PRESETS[providerName] && providerUser && providerPass) {
    const preset = PROXY_PRESETS[providerName];
    const user = providerUser;
    const pass = providerPass;
    // Decodo: port-based sticky sessions
    if (preset.serverTemplate) {
      const portMin = preset.stickyPortMin || 10001;
      const portMax = preset.stickyPortMax || 49999;
      const randomPort = () => Math.floor(Math.random() * (portMax - portMin + 1)) + portMin;
      const parsePort = (v) => { const n = parseInt(v, 10); return (Number.isFinite(n) && n >= portMin && n <= portMax) ? n : null; };
      const port = parsePort(sessionId) ?? parsePort(process.env.CN_PROXY_SESSION) ?? randomPort();
      const server = preset.serverTemplate(cty, port);
      const username = preset.usernameTemplate(user, cty, port);
      const password = preset.passwordTemplate ? preset.passwordTemplate(pass, cty, port) : pass;
      return { server, username, password };
    }
    // Other providers: session-string based
    const sid = sessionId || process.env.CN_PROXY_SESSION || Math.random().toString(36).slice(2, 10);
    const server = preset.server;
    const username = preset.usernameTemplate(user, cty, sid);
    const password = preset.passwordTemplate ? preset.passwordTemplate(pass, cty, sid) : pass;
    return { server, username, password };
  }

  // 3. Managed mode — stable agentId:agentSecret against our forward proxy.
  //    Credentials never change so Chromium context never needs restarting for proxy reasons.
  //    Country is encoded in username as "agentId|country" and parsed server-side.
  //    Access is gated on _proxyAllowed, which is set by getCredentials() from the server's
  //    sessionGranted flag. If trial is exceeded, we return null so the browser runs without
  //    the managed proxy (will get CAPTCHAs) rather than receiving 407 from the forward proxy.
  const apiUrl = process.env.CN_API_URL || DEFAULT_API_URL;

  if (!_proxyAllowed) {
    // Trial expired or getCredentials() hasn't been called yet / returned sessionGranted=false
    return null;
  }

  const creds = resolveAgentCredentials();
  if (!creds) {
    console.warn('[clawnet] No agent credentials found. Set CN_AGENT_TOKEN or run: npm install clawnet');
    return null;
  }

  try {
    const proxyHost = new URL(apiUrl).hostname;
    const proxyPort = process.env.CN_PROXY_PORT || '8080';
    return {
      server:   `http://${proxyHost}:${proxyPort}`,
      username: `${creds.agentId}|${cty}`,  // forward proxy splits on '|' to get country
      password: creds.agentSecret,
    };
  } catch (_) {
    console.warn('[clawnet] Could not parse CN_API_URL for managed proxy host.');
    return null;
  }
}

// ─── AGENT CREDENTIALS ───────────────────────────────────────────────────────

const _path   = require('path');
const _fs     = require('fs');
const _os     = require('os');
const _crypto = require('crypto');

const DEFAULT_API_URL = 'https://api.clawpets.io/clawnet/v1';

const CREDENTIALS_FILE = _path.join(_os.homedir(), '.clawnet', 'agent-credentials.json');
const PROFILES_DIR = _path.join(_os.homedir(), '.clawnet', 'profiles');
const LOGS_DIR    = _path.join(_os.homedir(), '.clawnet', 'logs');
const DEFAULT_PROFILE_NAME = (process.env.CN_PROFILE || 'default').trim() || 'default';
const LOG_LEVELS  = ['off', 'actions', 'verbose'];
const MAX_LOG_SESSIONS = 50;

// ─── ACTION LOGGER ───────────────────────────────────────────────────────────

class ActionLogger {
  /**
   * @param {string} sessionId  — unique session identifier
   * @param {string} level      — 'off' | 'actions' | 'verbose'
   */
  constructor(sessionId, level = 'actions') {
    this.sessionId = sessionId;
    this.level = LOG_LEVELS.includes(level) ? level : 'actions';
    this.startedAt = new Date().toISOString();
    if (this.level === 'off') {
      this.logFile = null;
      return;
    }
    _fs.mkdirSync(LOGS_DIR, { recursive: true });
    this.logFile = _path.join(LOGS_DIR, `${sessionId}.jsonl`);
    this._rotate();
  }

  /** Append a structured log entry. */
  log(action, detail = {}) {
    if (!this.logFile) return;
    const record = { ts: new Date().toISOString(), action, ...detail };
    try { _fs.appendFileSync(this.logFile, JSON.stringify(record) + '\n'); } catch (_) {}
  }

  /** Agent reasoning — only recorded at verbose level. */
  note(message) {
    if (this.level !== 'verbose') return;
    this.log('note', { message });
  }

  /** Return all log entries as an array. */
  getLog() {
    if (!this.logFile || !_fs.existsSync(this.logFile)) return [];
    try {
      return _fs.readFileSync(this.logFile, 'utf-8')
        .trim().split('\n').filter(Boolean).map(l => JSON.parse(l));
    } catch (_) { return []; }
  }

  /** Keep only the newest MAX_LOG_SESSIONS log files. */
  _rotate() {
    try {
      if (!_fs.existsSync(LOGS_DIR)) return;
      const files = _fs.readdirSync(LOGS_DIR)
        .filter(f => f.endsWith('.jsonl'))
        .map(f => ({ name: f, mtime: _fs.statSync(_path.join(LOGS_DIR, f)).mtimeMs }))
        .sort((a, b) => b.mtime - a.mtime);
      for (const f of files.slice(MAX_LOG_SESSIONS)) {
        _fs.unlinkSync(_path.join(LOGS_DIR, f));
      }
    } catch (_) {}
  }
}

// ─── LOG HELPERS ─────────────────────────────────────────────────────────────

/** Get the page URL without throwing. */
function _safeUrl(page) {
  try { return page.url(); } catch (_) { return ''; }
}

/** Strip non-serializable args (page object) and mask passwords. */
function _sanitizeArgs(actionName, args) {
  const clean = [];
  for (const a of args) {
    if (a && typeof a === 'object' && typeof a.goto === 'function') continue; // skip page
    if (typeof a === 'string' && a.length > 500) { clean.push(a.slice(0, 500) + '…'); continue; }
    clean.push(a);
  }
  // mask text in humanType if selector hints at password
  if (actionName === 'humanType' && clean.length >= 3) {
    const sel = String(clean[1] || '').toLowerCase();
    if (sel.includes('pass') || sel.includes('secret') || sel.includes('token')) {
      clean[2] = '***';
    }
  }
  return clean;
}

/** Truncate a value for logging. */
function _truncate(val, max = 500) {
  if (val == null) return val;
  const s = typeof val === 'string' ? val : JSON.stringify(val);
  return s.length > max ? s.slice(0, max) + '…' : s;
}

// Active browser instances keyed by profile name (for reuse mode)
// Value: { browser, ctx, proxyEnabled }
const _activeBrowsers = new Map();
const AGENT_ID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const AGENT_SECRET_RE = /^[A-Za-z0-9_-]{32,200}$/;
let _cachedDockerRuntime = null;
let _sandboxModeLogged = false;

// Whether the managed forward proxy is allowed for the current process.
// Set by getCredentials() from the server's sessionGranted flag.
// makeProxy() returns null in managed mode when false, so expired-trial agents
// launch without the managed proxy (no stealth) rather than getting 407 errors.
let _proxyAllowed = false;

function isDockerRuntime() {
  if (_cachedDockerRuntime !== null) {
    return _cachedDockerRuntime;
  }

  const forced = process.env.CN_RUNTIME_DOCKER?.trim().toLowerCase();
  if (forced === '1' || forced === 'true' || forced === 'yes') {
    _cachedDockerRuntime = true;
    return true;
  }
  if (forced === '0' || forced === 'false' || forced === 'no') {
    _cachedDockerRuntime = false;
    return false;
  }

  if (process.platform !== 'linux') {
    _cachedDockerRuntime = false;
    return false;
  }

  try {
    if (_fs.existsSync('/.dockerenv')) {
      _cachedDockerRuntime = true;
      return true;
    }
  } catch (_) {}

  const markers = /(docker|containerd|kubepods|podman|lxc)/i;
  try {
    const cgroup = _fs.readFileSync('/proc/1/cgroup', 'utf-8');
    if (markers.test(cgroup)) {
      _cachedDockerRuntime = true;
      return true;
    }
  } catch (_) {}

  try {
    const cgroupSelf = _fs.readFileSync('/proc/self/cgroup', 'utf-8');
    if (markers.test(cgroupSelf)) {
      _cachedDockerRuntime = true;
      return true;
    }
  } catch (_) {}

  _cachedDockerRuntime = false;
  return false;
}

function shouldDisableSandbox() {
  const forced = process.env.CN_CHROMIUM_NO_SANDBOX?.trim().toLowerCase();
  if (forced === '1' || forced === 'true' || forced === 'yes') return true;
  if (forced === '0' || forced === 'false' || forced === 'no') return false;
  return isDockerRuntime();
}

function logSandboxMode(disableSandbox) {
  if (_sandboxModeLogged) return;
  _sandboxModeLogged = true;
  if (disableSandbox) {
    console.log('[clawnet] Chromium sandbox disabled (container runtime detected).');
  } else {
    console.log('[clawnet] Chromium sandbox enabled (host runtime detected).');
  }
}

/**
 * Load agent credentials saved during install.
 * Returns { agentId, agentSecret } or null if not found/invalid.
 */
function loadAgentCredentials() {
  try {
    if (!_fs.existsSync(CREDENTIALS_FILE)) return null;
    const data = JSON.parse(_fs.readFileSync(CREDENTIALS_FILE, 'utf-8'));
    if (AGENT_ID_RE.test(data.agentId || '') && AGENT_SECRET_RE.test(data.agentSecret || '')) {
      return {
        agentId: data.agentId,
        agentSecret: data.agentSecret,
        recoveryCode: data.recoveryCode || undefined,
        rotatedAt: data.rotatedAt || undefined,
      };
    }
    return null;
  } catch (_) {
    return null;
  }
}

function buildAgentToken(agentId, agentSecret) {
  return `CN1.${agentId}.${agentSecret}`;
}

/**
 * Resolve agent credentials from any supported source.
 * Priority: rotated file > CN_AGENT_TOKEN > CN_AGENT_ID+CN_AGENT_SECRET > non-rotated file.
 *
 * Rotated credentials (saved after server-side secret rotation) take top priority
 * because env vars may contain a stale original secret. After rotation, the file
 * has the latest valid secret.
 *
 * Returns { agentId, agentSecret } or null.
 */
function resolveAgentCredentials() {
  // 0. Rotated file credentials take top priority (server rotated the secret)
  const fileCreds = loadAgentCredentials();
  if (fileCreds?.rotatedAt) {
    return { agentId: fileCreds.agentId, agentSecret: fileCreds.agentSecret };
  }

  // 1. CN_AGENT_TOKEN=CN1.<agentId>.<agentSecret>
  const directToken = process.env.CN_AGENT_TOKEN?.trim();
  if (directToken && directToken.startsWith('CN1.')) {
    const parts = directToken.split('.');
    if (parts.length === 3 && AGENT_ID_RE.test(parts[1]) && AGENT_SECRET_RE.test(parts[2])) {
      return { agentId: parts[1], agentSecret: parts[2] };
    }
  }

  // 2. CN_AGENT_ID + CN_AGENT_SECRET
  const envAgentId = process.env.CN_AGENT_ID?.trim();
  const envAgentSecret = process.env.CN_AGENT_SECRET?.trim();
  if (AGENT_ID_RE.test(envAgentId || '') && AGENT_SECRET_RE.test(envAgentSecret || '')) {
    return { agentId: envAgentId, agentSecret: envAgentSecret };
  }

  // 3. Non-rotated file (~/.clawnet/agent-credentials.json)
  return fileCreds;
}

function resolveAgentToken() {
  const creds = resolveAgentCredentials();
  return creds ? buildAgentToken(creds.agentId, creds.agentSecret) : null;
}

/**
 * Auto-register a new agent with the Clawnet API.
 * Generates credentials, registers with the server, and saves to disk.
 * Called automatically by launchBrowser() when no credentials are found.
 *
 * @param {string} apiUrl — API base URL
 * @returns {{ agentId, agentSecret, recoveryCode } | null}
 */
async function autoRegisterAgent(apiUrl) {
  // Security: if credentials file or directory already exists, an agent was
  // previously registered. Refuse to generate new ones — the user must either
  // provide existing credentials via importCredentials() / env vars, or
  // re-run postinstall interactively.
  const credentialsDir = _path.dirname(CREDENTIALS_FILE);
  if (_fs.existsSync(CREDENTIALS_FILE) || _fs.existsSync(credentialsDir)) {
    console.error('[clawnet] Agent account already exists.');
    console.error('  Cannot generate new credentials — use importCredentials() to');
    console.error('  provide your existing agentId and agentSecret instead.');
    return null;
  }

  const agentId = _crypto.randomUUID();
  const agentSecret = _crypto.randomBytes(32).toString('base64url');
  const recoveryCode = _crypto.randomBytes(24).toString('base64url');

  console.log('[clawnet] First run — registering new agent...');

  try {
    const resp = await fetch(`${apiUrl.replace(/\/$/, '')}/agents/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agentId, agentSecret, recoveryCode }),
      signal: AbortSignal.timeout(10_000),
    });

    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      console.warn(`[clawnet] Auto-registration failed (HTTP ${resp.status}): ${text}`);
      return null;
    }

    const data = await resp.json();
    console.log(`[clawnet] Agent registered. Trial: ${data.trialLimit ?? 1} free session(s).`);
  } catch (err) {
    console.warn(`[clawnet] Auto-registration failed: ${err.message}`);
    return null;
  }

  // Save credentials to disk
  const creds = {
    agentId,
    agentSecret,
    recoveryCode,
    createdAt: new Date().toISOString(),
  };

  try {
    _fs.mkdirSync(_path.dirname(CREDENTIALS_FILE), { recursive: true, mode: 0o700 });
    _fs.writeFileSync(CREDENTIALS_FILE, JSON.stringify(creds, null, 2), { mode: 0o600 });
    console.log(`[clawnet] Credentials saved to ${CREDENTIALS_FILE}`);
  } catch (err) {
    console.warn(`[clawnet] Could not save credentials to disk: ${err.message}`);
  }

  // Set env vars for current process so resolveAgentCredentials() picks them up
  process.env.CN_AGENT_ID = agentId;
  process.env.CN_AGENT_SECRET = agentSecret;

  return creds;
}

/**
 * Import existing agent credentials provided by the user.
 * ONLY saves credentials that the user explicitly provides — NEVER generates new ones.
 * Use this when the user says "here are my credentials" or "use this agentId/secret".
 *
 * @param {string} agentId — existing agent UUID
 * @param {string} agentSecret — existing agent secret
 * @returns {{ ok: boolean, agentId: string } | { ok: false, error: string }}
 */
function importCredentials(agentId, agentSecret) {
  if (!agentId || !agentSecret) {
    return { ok: false, error: 'agentId and agentSecret are required' };
  }
  if (!AGENT_ID_RE.test(agentId)) {
    return { ok: false, error: 'Invalid agentId format (expected UUID)' };
  }
  if (!AGENT_SECRET_RE.test(agentSecret)) {
    return { ok: false, error: 'Invalid agentSecret format (expected 32-200 char base64url string)' };
  }

  const creds = {
    agentId,
    agentSecret,
    createdAt: new Date().toISOString(),
    importedAt: new Date().toISOString(),
  };

  try {
    _fs.mkdirSync(_path.dirname(CREDENTIALS_FILE), { recursive: true, mode: 0o700 });
    _fs.writeFileSync(CREDENTIALS_FILE, JSON.stringify(creds, null, 2), { mode: 0o600 });
  } catch (err) {
    return { ok: false, error: `Could not save credentials: ${err.message}` };
  }

  // Update env vars for current process
  process.env.CN_AGENT_ID = agentId;
  process.env.CN_AGENT_SECRET = agentSecret;

  console.log(`[clawnet] Credentials imported and saved for agentId: ${agentId}`);
  return { ok: true, agentId };
}

// ─── SERVICE CREDENTIALS ──────────────────────────────────────────────────────

/**
 * Fetch managed credentials from Clawnet API (proxy + captcha keys).
 *
 * Authentication: uses CN1.<agentId>.<agentSecret> token from:
 * 1) CN_AGENT_TOKEN
 * 2) CN_AGENT_ID + CN_AGENT_SECRET
 * 3) ~/.clawnet/agent-credentials.json
 *
 * If agent has a subscription or trial remaining, returns managed
 * Decodo proxy + 2captcha credentials.
 * Falls back gracefully — agent can still use BYO credentials via env vars.
 *
 * @returns {{ ok: boolean, proxy?, captcha?, trialRemaining? }}
 */
async function getCredentials() {
  const apiUrl = process.env.CN_API_URL || DEFAULT_API_URL;

  // Resolve agent auth token
  const agentToken = resolveAgentToken();

  if (!apiUrl || !agentToken) {
    console.warn('[clawnet] No API config. Using BYO credentials from env vars.');
    return { ok: false, reason: 'no_api_config' };
  }

  try {
    const resp = await fetch(`${apiUrl.replace(/\/$/, '')}/credentials`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${agentToken}`,
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(10_000),
    });

    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      console.warn(`[clawnet] Credentials API returned ${resp.status}: ${text}`);
      return { ok: false, reason: 'api_error', status: resp.status };
    }

    const data = await resp.json();

    // Handle secret rotation: server rotates the secret on every /credentials call.
    // Save the new secret to disk and update process env so that makeProxy() uses it.
    if (data.newAgentSecret && data.newAgentToken) {
      const existingFile = loadAgentCredentials();
      const rotatedCreds = {
        agentId: resolveAgentCredentials()?.agentId,
        agentSecret: data.newAgentSecret,
        rotatedAt: new Date().toISOString(),
      };
      // Preserve recoveryCode if it exists in the file
      if (existingFile?.recoveryCode) {
        rotatedCreds.recoveryCode = existingFile.recoveryCode;
      }

      try {
        _fs.mkdirSync(_path.dirname(CREDENTIALS_FILE), { recursive: true, mode: 0o700 });
        _fs.writeFileSync(CREDENTIALS_FILE, JSON.stringify(rotatedCreds, null, 2), { mode: 0o600 });
      } catch (_) {
        // Best effort — if save fails, the previous secret still works for one more rotation
      }

      // Update process env so makeProxy() picks up the new secret
      process.env.CN_AGENT_TOKEN = data.newAgentToken;
      if (rotatedCreds.agentId) {
        process.env.CN_AGENT_ID = rotatedCreds.agentId;
      }
      process.env.CN_AGENT_SECRET = data.newAgentSecret;
    }

    // Update managed proxy access permission.
    // sessionGranted=true  → server granted a managed proxy session (trial or subscription).
    // sessionGranted=false → trial exceeded; makeProxy() will return null so the browser
    //                        launches without proxy rather than hammering the forward proxy.
    if (typeof data.sessionGranted === 'boolean') {
      _proxyAllowed = data.sessionGranted;
    }

    // Apply proxy credentials — BYO mode only.
    // Managed proxy now uses stable agentId:agentSecret via makeProxy() directly,
    // so no env vars needed and no TTL to track.
    if (data.proxy && data.proxy.source === 'byo') {
      if (data.proxy.server)   process.env.CN_PROXY_SERVER   = data.proxy.server;
      if (data.proxy.username) process.env.CN_PROXY_USER     = data.proxy.username;
      if (data.proxy.password) process.env.CN_PROXY_PASS     = data.proxy.password;
      if (data.proxy.provider) process.env.CN_PROXY_PROVIDER = data.proxy.provider;
      if (data.proxy.country)  process.env.CN_PROXY_COUNTRY  = data.proxy.country;
    } else if (!data.proxy) {
      // Server revoked BYO keys — clear any cached BYO credentials
      delete process.env.CN_PROXY_SERVER;
      delete process.env.CN_PROXY_USER;
      delete process.env.CN_PROXY_PASS;
    }

    // Apply or revoke captcha key
    if (data.captcha && data.captcha.apiKey) {
      process.env.TWOCAPTCHA_KEY = data.captcha.apiKey;
    } else {
      delete process.env.TWOCAPTCHA_KEY;
    }

    // Show trial status and upgrade link
    if (typeof data.trialRemainingMs === 'number' && !data.subscriptionActive) {
      if (data.trialRemainingMs <= 0) {
        if (data.upgradeUrl) {
          console.log(`[clawnet] Trial expired. Subscribe to continue: ${data.upgradeUrl}`);
        } else {
          console.log('[clawnet] Trial expired. Subscribe at https://petsbrowser.dev or use BYO keys.');
        }
      } else {
        const mins = Math.ceil(data.trialRemainingMs / 60_000);
        const display = mins >= 60
          ? `${Math.floor(mins / 60)}h ${mins % 60}m`
          : `${mins}m`;
        console.log(`[clawnet] Trial: ${display} remaining.`);
      }
    }

    return { ok: true, ...data };
  } catch (err) {
    console.warn('[clawnet] Failed to fetch credentials:', err.message);
    return { ok: false, reason: 'network_error', error: err.message };
  }
}

// ─── HUMAN BEHAVIOR ──────────────────────────────────────────────────────────

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const rand  = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

async function humanMouseMove(page, toX, toY, fromX = null, fromY = null) {
  const startX = fromX ?? rand(100, 300);
  const startY = fromY ?? rand(200, 600);
  const cp1x = startX + rand(-80, 80), cp1y = startY + rand(-60, 60);
  const cp2x = toX   + rand(-50, 50), cp2y = toY   + rand(-40, 40);
  const steps = rand(12, 25);
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = Math.round(Math.pow(1-t,3)*startX + 3*Math.pow(1-t,2)*t*cp1x + 3*(1-t)*t*t*cp2x + t*t*t*toX);
    const y = Math.round(Math.pow(1-t,3)*startY + 3*Math.pow(1-t,2)*t*cp1y + 3*(1-t)*t*t*cp2y + t*t*t*toY);
    await page.mouse.move(x, y);
    await sleep(t < 0.2 || t > 0.8 ? rand(8, 20) : rand(2, 8));
  }
}

async function humanClick(page, x, y) {
  await humanMouseMove(page, x, y);
  await sleep(rand(50, 180));
  await page.mouse.down();
  await sleep(rand(40, 100));
  await page.mouse.up();
  await sleep(rand(100, 300));
}

async function humanType(page, selector, text) {
  const el = await page.$(selector);
  if (!el) throw new Error(`Element not found: ${selector}`);
  const box = await el.boundingBox();
  if (box) await humanClick(page, box.x + box.width / 2, box.y + box.height / 2);
  await sleep(rand(200, 500));
  for (const char of text) {
    await page.keyboard.type(char);
    await sleep(rand(60, 220));
    if (Math.random() < 0.08) await sleep(rand(400, 900));
  }
  await sleep(rand(200, 400));
}

async function humanScroll(page, direction = 'down', amount = null) {
  const scrollAmount = amount || rand(200, 600);
  const delta = direction === 'down' ? scrollAmount : -scrollAmount;
  const vp = page.viewportSize();
  await humanMouseMove(page, rand(100, vp.width - 100), rand(200, vp.height - 200));
  const steps = rand(4, 10);
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, delta / steps + rand(-5, 5));
    await sleep(rand(30, 80));
  }
  await sleep(rand(200, 800));
}

async function humanRead(page, minMs = 1500, maxMs = 4000) {
  await sleep(rand(minMs, maxMs));
  if (Math.random() < 0.3) await humanScroll(page, 'down', rand(50, 150));
}

// ─── BATCH ACTIONS ──────────────────────────────────────────────────────────
// Inspired by PinchTab's /actions endpoint (internal/handlers/actions.go).
// Execute multiple actions sequentially with shared error handling, reducing
// LLM round-trips for multi-step flows (form filling, login, checkout).

/**
 * Execute multiple actions sequentially in a single call.
 *
 * Each action descriptor: { action, selector, text, value, key, ms, options }
 *   action: 'click' | 'fill' | 'type' | 'press' | 'hover' | 'scroll' | 'select' |
 *           'focus' | 'humanClick' | 'humanType' | 'wait' | 'waitForSelector' | 'snapshot'
 *
 * @param {import('playwright').Page} page
 * @param {Array<Object>} actions - Array of action descriptors
 * @param {Object} [opts]
 * @param {boolean} [opts.stopOnError=false] - Halt on first failure or continue
 * @param {number} [opts.delayBetween=50] - ms delay between actions for realism
 * @returns {Promise<{results: Array<{index: number, success: boolean, result?: any, error?: string}>, total: number, successful: number, failed: number}>}
 */
async function batchActions(page, actions, opts = {}) {
  const { stopOnError = false, delayBetween = 50 } = opts;
  const results = [];
  let successful = 0;
  let failed = 0;

  for (let i = 0; i < actions.length; i++) {
    const act = actions[i];
    try {
      let result;
      switch (act.action) {
        case 'click':
          await page.click(act.selector, act.options);
          result = { clicked: act.selector };
          break;
        case 'fill':
          await page.fill(act.selector, act.text || act.value || '');
          result = { filled: act.selector };
          break;
        case 'type':
          await page.type(act.selector, act.text || '', act.options);
          result = { typed: act.selector };
          break;
        case 'press':
          await page.press(act.selector || 'body', act.key);
          result = { pressed: act.key };
          break;
        case 'hover':
          await page.hover(act.selector, act.options);
          result = { hovered: act.selector };
          break;
        case 'select':
          await page.selectOption(act.selector, act.value);
          result = { selected: act.value };
          break;
        case 'scroll':
          await page.evaluate(({ x, y }) => window.scrollBy(x || 0, y || 300), act.options || {});
          result = { scrolled: true };
          break;
        case 'focus':
          await page.focus(act.selector);
          result = { focused: act.selector };
          break;
        case 'wait':
          await page.waitForTimeout(act.ms || 1000);
          result = { waited: act.ms || 1000 };
          break;
        case 'waitForSelector':
          await page.waitForSelector(act.selector, act.options);
          result = { found: act.selector };
          break;
        case 'humanClick': {
          const el = await page.$(act.selector);
          if (!el) throw new Error('Element not found: ' + act.selector);
          const box = await el.boundingBox();
          if (!box) throw new Error('Element not visible: ' + act.selector);
          await humanClick(page, box.x + box.width / 2, box.y + box.height / 2);
          result = { humanClicked: act.selector };
          break;
        }
        case 'humanType':
          await humanType(page, act.selector, act.text || '');
          result = { humanTyped: act.selector };
          break;
        case 'snapshot':
          result = { snapshot: await snapshot(page, act.options || {}) };
          break;
        case 'snapshotAI':
          result = await snapshotAI(page, act.options || act);
          break;
        case 'clickRef':
          await clickRef(page, act.ref, act);
          result = { clicked: act.ref };
          break;
        case 'fillRef':
          await fillRef(page, act.ref, act.value, act);
          result = { filled: act.ref };
          break;
        case 'typeRef':
          await typeRef(page, act.ref, act.text, act);
          result = { typed: act.ref };
          break;
        case 'selectRef':
          await selectRef(page, act.ref, act.value, act);
          result = { selected: act.ref };
          break;
        case 'hoverRef':
          await hoverRef(page, act.ref, act);
          result = { hovered: act.ref };
          break;
        default:
          throw new Error('Unknown action: ' + act.action);
      }
      results.push({ index: i, success: true, result });
      successful++;
    } catch (err) {
      results.push({ index: i, success: false, error: err.message });
      failed++;
      if (stopOnError) break;
    }

    // Delay between actions for realism (skip after last action)
    if (i < actions.length - 1 && delayBetween > 0) {
      await sleep(delayBetween);
    }
  }

  return { results, total: actions.length, successful, failed };
}

// ─── 2CAPTCHA SOLVER ──────────────────────────────────────────────────────────

async function solveCaptcha(page, opts = {}) {
  const {
    apiKey   = process.env.TWOCAPTCHA_KEY,
    action   = 'verify',
    minScore = 0.7,
    timeout  = 120000,
    verbose  = false,
  } = opts;

  const log = verbose ? (...a) => console.log('[captcha]', ...a) : () => {};
  const pageUrl = page.url();

  // Auto-detect captcha type
  const detected = await page.evaluate(() => {
    const rc = document.querySelector('.g-recaptcha, [data-sitekey]');
    if (rc) {
      const sitekey = rc.getAttribute('data-sitekey') || rc.getAttribute('data-key');
      const version = rc.getAttribute('data-version') || (typeof window.grecaptcha !== 'undefined' && 'v2');
      return { type: 'recaptcha', sitekey, version: version === 'v3' ? 'v3' : 'v2' };
    }
    const hc = document.querySelector('.h-captcha, [data-hcaptcha-sitekey]');
    if (hc) return { type: 'hcaptcha', sitekey: hc.getAttribute('data-sitekey') || hc.getAttribute('data-hcaptcha-sitekey') };
    const ts = document.querySelector('.cf-turnstile, [data-cf-turnstile-sitekey]');
    if (ts) return { type: 'turnstile', sitekey: ts.getAttribute('data-sitekey') || ts.getAttribute('data-cf-turnstile-sitekey') };
    const scripts = [...document.scripts].map(s => s.src + s.textContent).join(' ');
    const rcMatch = scripts.match(/(?:sitekey|data-sitekey)['":\s]+([A-Za-z0-9_-]{40,})/);
    if (rcMatch) return { type: 'recaptcha', sitekey: rcMatch[1], version: 'v2' };
    return null;
  });

  if (!detected || !detected.sitekey) throw new Error('[captcha] No captcha detected on page.');
  log(`Detected ${detected.type} v${detected.version || ''}`, detected.sitekey.slice(0, 20) + '...');

  // Map client captcha types to server types
  const typeMap = {
    'recaptcha': detected.version === 'v3' ? 'recaptcha-v3' : 'recaptcha-v2',
    'hcaptcha': 'hcaptcha',
    'turnstile': 'turnstile',
  };
  const serverType = typeMap[detected.type] || 'recaptcha-v2';

  let token = null;

  // Try server-side solving first (managed mode — no API key needed)
  const apiUrl = process.env.CN_API_URL || DEFAULT_API_URL;
  const agentToken = resolveAgentToken();

  if (apiUrl && agentToken) {
    log('Using server-side captcha solving...');
    try {
      const resp = await fetch(`${apiUrl.replace(/\/$/, '')}/captcha/solve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${agentToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          challenge: {
            type: serverType,
            siteKey: detected.sitekey,
            pageUrl,
          },
        }),
        signal: AbortSignal.timeout(timeout),
      });

      if (resp.ok) {
        const data = await resp.json();
        if (data.solved && data.token) {
          token = data.token;
          log('Server solved captcha');
        } else {
          log(`Server returned no solution: ${JSON.stringify(data)}`);
        }
      } else {
        log(`Server captcha solve failed (HTTP ${resp.status})`);
      }
    } catch (err) {
      log(`Server captcha error: ${err.message}`);
    }
  }

  // Fallback: direct 2captcha call (BYO mode)
  if (!token) {
    if (!apiKey) {
      throw new Error('[captcha] No API key and server-side solving failed. Set TWOCAPTCHA_KEY env or use managed mode.');
    }
    log('Falling back to direct 2captcha...');

    let submitUrl = `https://2captcha.com/in.php?key=${apiKey}&json=1&pageurl=${encodeURIComponent(pageUrl)}&googlekey=${encodeURIComponent(detected.sitekey)}`;
    if (detected.type === 'recaptcha') {
      submitUrl += `&method=userrecaptcha`;
      if (detected.version === 'v3') submitUrl += `&version=v3&action=${action}&min_score=${minScore}`;
    } else if (detected.type === 'hcaptcha') {
      submitUrl += `&method=hcaptcha&sitekey=${encodeURIComponent(detected.sitekey)}`;
    } else if (detected.type === 'turnstile') {
      submitUrl += `&method=turnstile&sitekey=${encodeURIComponent(detected.sitekey)}`;
    }

    const submitResp = await fetch(submitUrl);
    const submitData = await submitResp.json();
    if (!submitData.status || submitData.status !== 1) throw new Error(`[captcha] Submit failed: ${JSON.stringify(submitData)}`);
    const taskId = submitData.request;
    log(`Task submitted: ${taskId}`);

    const maxAttempts = Math.floor(timeout / 5000);
    for (let i = 0; i < maxAttempts; i++) {
      await sleep(i === 0 ? 15000 : 5000);
      const pollResp = await fetch(`https://2captcha.com/res.php?key=${apiKey}&action=get&id=${taskId}&json=1`);
      const pollData = await pollResp.json();
      if (pollData.status === 1) { token = pollData.request; log('Solved!'); break; }
      if (pollData.request !== 'CAPCHA_NOT_READY') throw new Error(`[captcha] Poll error: ${JSON.stringify(pollData)}`);
      log(`Waiting... ${i + 1}/${maxAttempts}`);
    }
    if (!token) throw new Error('[captcha] Timeout waiting for captcha solution');
  }

  // Inject token into page
  await page.evaluate(({ type, token }) => {
    if (type === 'recaptcha' || type === 'turnstile') {
      const ta = document.querySelector('#g-recaptcha-response, [name="g-recaptcha-response"]');
      if (ta) { ta.style.display = 'block'; ta.value = token; ta.dispatchEvent(new Event('change', { bubbles: true })); }
      try {
        const clients = window.___grecaptcha_cfg && window.___grecaptcha_cfg.clients;
        if (clients) Object.values(clients).forEach(c => Object.values(c).forEach(w => { if (w && typeof w.callback === 'function') w.callback(token); }));
      } catch (_) {}
    }
    if (type === 'hcaptcha') {
      const ta = document.querySelector('[name="h-captcha-response"], #h-captcha-response');
      if (ta) { ta.style.display = 'block'; ta.value = token; ta.dispatchEvent(new Event('change', { bubbles: true })); }
    }
    if (type === 'turnstile') {
      const inp = document.querySelector('[name="cf-turnstile-response"]');
      if (inp) { inp.value = token; inp.dispatchEvent(new Event('change', { bubbles: true })); }
    }
  }, { type: detected.type, token });

  log('Token injected');
  return { token, type: detected.type, sitekey: detected.sitekey };
}

// ─── LAUNCH ───────────────────────────────────────────────────────────────────

/**
 * Apply stealth anti-detection scripts to a browser context.
 */
async function applyStealthScripts(ctx, mobile, locale) {
  await ctx.addInitScript((m) => {
    Object.defineProperty(navigator, 'webdriver',           { get: () => false });
    Object.defineProperty(navigator, 'maxTouchPoints',      { get: () => m.mobile ? 5 : 0 });
    Object.defineProperty(navigator, 'platform',            { get: () => m.mobile ? 'iPhone' : 'Win32' });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => m.mobile ? 6 : 8 });
    Object.defineProperty(navigator, 'language',            { get: () => m.locale });
    Object.defineProperty(navigator, 'languages',           { get: () => [m.locale, 'en'] });
    if (m.mobile) {
      Object.defineProperty(screen, 'width',       { get: () => 393 });
      Object.defineProperty(screen, 'height',      { get: () => 852 });
      Object.defineProperty(screen, 'availWidth',  { get: () => 393 });
      Object.defineProperty(screen, 'availHeight', { get: () => 852 });
    }
    // WebRTC leak protection
    if (window.RTCPeerConnection) {
      const OrigRTC = window.RTCPeerConnection;
      window.RTCPeerConnection = function(...args) {
        if (args[0] && args[0].iceServers) args[0].iceServers = [];
        return new OrigRTC(...args);
      };
      window.RTCPeerConnection.prototype = OrigRTC.prototype;
    }
    // Navigator connection
    if (navigator.connection) {
      try {
        Object.defineProperty(navigator.connection, 'effectiveType', { get: () => '4g' });
        Object.defineProperty(navigator.connection, 'rtt',           { get: () => 50 });
        Object.defineProperty(navigator.connection, 'downlink',      { get: () => 10 });
      } catch (_) {}
    }
    // Chrome runtime stub
    if (!window.chrome) window.chrome = {};
    if (!window.chrome.runtime) window.chrome.runtime = { connect: () => {}, sendMessage: () => {} };
  }, { mobile, locale });
}

/**
 * Build a result object returned by launchBrowser().
 */
/**
 * Take a screenshot and return it as a base64-encoded PNG string.
 * Use this to attach visual proof to every message sent to the user.
 *
 * @param {import('playwright').Page} pg — Playwright page
 * @param {Object} [opts]
 * @param {boolean} [opts.fullPage=false] — Capture the full scrollable page
 * @returns {Promise<string>} base64-encoded PNG screenshot
 */
async function takeScreenshot(pg, opts = {}) {
  const buf = await pg.screenshot({ type: 'png', fullPage: Boolean(opts.fullPage) });
  return buf.toString('base64');
}

/**
 * Take a screenshot and pair it with a message for the user.
 * Returns an object ready to be attached to an LLM response.
 *
 * @param {import('playwright').Page} pg — Playwright page
 * @param {string} message — Human-readable message describing what happened
 * @param {Object} [opts]
 * @param {boolean} [opts.fullPage=false] — Capture the full scrollable page
 * @returns {Promise<{ message: string, screenshot: string, mimeType: string }>}
 */
async function screenshotAndReport(pg, message, opts = {}) {
  const screenshot = await takeScreenshot(pg, opts);
  return { message, screenshot, mimeType: 'image/png' };
}

// ── PAGE PROXY ──────────────────────────────────────────────────────────────
// Intercepts ALL page & locator method calls for comprehensive logging.
// The agent uses Playwright chains like page.getByRole('button').click() —
// without a Proxy these calls are invisible to our logger.

/**
 * Methods whose calls we log at "actions" level (user-visible actions).
 * Everything else is logged only at "verbose" level.
 */
const ACTION_METHODS = new Set([
  // navigation
  'goto', 'goBack', 'goForward', 'reload',
  // interaction
  'click', 'dblclick', 'fill', 'type', 'press', 'check', 'uncheck', 'selectOption',
  'setInputFiles', 'tap', 'hover', 'focus', 'dragTo', 'scrollIntoViewIfNeeded',
  // waiting
  'waitForSelector', 'waitForNavigation', 'waitForURL', 'waitForLoadState', 'waitForTimeout',
  // locator creation (we log the chain, e.g. getByRole → click)
  'getByRole', 'getByText', 'getByLabel', 'getByPlaceholder', 'getByAltText',
  'getByTitle', 'getByTestId', 'locator', 'first', 'last', 'nth',
]);

/**
 * Methods that return a new Locator and need to be wrapped recursively
 * so the whole chain is captured: page.getByRole('button', { name: 'Submit' }).click()
 */
const LOCATOR_RETURNING = new Set([
  'getByRole', 'getByText', 'getByLabel', 'getByPlaceholder', 'getByAltText',
  'getByTitle', 'getByTestId', 'locator', 'first', 'last', 'nth',
  'filter', 'and', 'or',
]);

/**
 * Properties / methods that should NOT be proxied (internal Playwright, symbols, etc.)
 */
const PROXY_SKIP = new Set([
  'then', 'catch', 'finally', // thenable checks
  'toJSON', 'toString', 'valueOf', 'inspect',
  'constructor', 'prototype',
]);

/**
 * Serialize a locator call argument for logging.
 * Handles role names, { name: ... } options, regex, etc.
 */
function _serializeLocatorArg(arg) {
  if (arg == null) return arg;
  if (arg instanceof RegExp) return arg.toString();
  if (typeof arg === 'string') return arg.length > 200 ? arg.slice(0, 200) + '…' : arg;
  if (typeof arg === 'number' || typeof arg === 'boolean') return arg;
  if (typeof arg === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(arg)) {
      if (typeof v === 'function') continue; // skip callbacks
      out[k] = _serializeLocatorArg(v);
    }
    return out;
  }
  return String(arg).slice(0, 100);
}

/**
 * Create a logging Proxy around a Playwright Page or Locator.
 *
 * @param {object} target   — Playwright Page or Locator instance
 * @param {ActionLogger} logger
 * @param {Page} rawPage    — the unwrapped page (for _safeUrl)
 * @param {string[]} chain  — accumulated method chain, e.g. ['getByRole("button")', 'first()']
 */
function _createLoggingProxy(target, logger, rawPage, chain = []) {
  if (!target || typeof target !== 'object') return target;

  return new Proxy(target, {
    get(obj, prop, receiver) {
      // Symbols, internal props — pass through
      if (typeof prop === 'symbol') return Reflect.get(obj, prop, receiver);
      if (PROXY_SKIP.has(prop)) return Reflect.get(obj, prop, receiver);

      const value = Reflect.get(obj, prop, receiver);
      if (typeof value !== 'function') return value;

      // Determine if this method is worth logging
      const isAction = ACTION_METHODS.has(prop);
      const isLocatorReturning = LOCATOR_RETURNING.has(prop);
      const shouldLog = logger.level === 'verbose' || isAction;

      if (!shouldLog && !isLocatorReturning) {
        // Not interesting — return bound original
        return value.bind(obj);
      }

      // Return a wrapper function
      return function proxyWrapper(...args) {
        const prettyArgs = args.map(_serializeLocatorArg);
        const callLabel = `${prop}(${prettyArgs.map(a => JSON.stringify(a)).join(', ')})`;
        const fullChain = [...chain, callLabel];

        // If this method returns a Locator, wrap the result recursively
        if (isLocatorReturning) {
          const result = value.apply(obj, args);
          if (shouldLog) {
            logger.log('locator', { chain: fullChain.join(' → '), url: _safeUrl(rawPage) });
          }
          // Wrap the returned locator so subsequent .click() / .fill() are also logged
          return _createLoggingProxy(result, logger, rawPage, fullChain);
        }

        // Action method — log before and after
        const url = _safeUrl(rawPage);
        const entry = { method: prop, args: prettyArgs, chain: fullChain.join(' → '), url };

        // If the result is a promise (async method), handle it
        let result;
        try {
          result = value.apply(obj, args);
        } catch (err) {
          logger.log(prop + '_error', { ...entry, error: err.message });
          throw err;
        }

        // Handle both sync and async returns
        if (result && typeof result.then === 'function') {
          return result.then(
            (res) => {
              const detail = { ...entry, ok: true };
              // For some methods, capture return value
              if (prop === 'textContent' || prop === 'innerText' || prop === 'innerHTML' ||
                  prop === 'inputValue' || prop === 'getAttribute' || prop === 'count' ||
                  prop === 'isVisible' || prop === 'isEnabled' || prop === 'isChecked') {
                detail.result = _truncate(res);
              }
              if (prop === 'goto' && res) {
                detail.status = typeof res.status === 'function' ? res.status() : undefined;
              }
              logger.log(prop, detail);
              return res;
            },
            (err) => {
              logger.log(prop + '_error', { ...entry, error: err.message });
              throw err;
            }
          );
        }

        // Sync result
        if (shouldLog) {
          logger.log(prop, { ...entry, ok: true });
        }
        return result;
      };
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────

function buildResult(browser, ctx, page, logger) {
  // ── Create logging proxy for the page object ──
  const rawPage = page;  // keep unwrapped reference for internal use
  const proxiedPage = logger.level !== 'off'
    ? _createLoggingProxy(page, logger, rawPage)
    : page;

  // ── Subscribe to page events for passive logging ──
  if (logger.level !== 'off') {
    rawPage.on('framenavigated', (frame) => {
      if (frame === rawPage.mainFrame()) {
        logger.log('navigated', { url: frame.url() });
      }
    });
    rawPage.on('popup', (popup) => {
      logger.log('popup', { url: _safeUrl(popup) });
    });
    rawPage.on('dialog', (dialog) => {
      logger.log('dialog', { type: dialog.type(), message: _truncate(dialog.message(), 300) });
    });
    rawPage.on('download', (download) => {
      logger.log('download', { filename: download.suggestedFilename(), url: download.url() });
    });
    rawPage.on('pageerror', (err) => {
      logger.log('page_error', { error: err.message });
    });
  }
  if (logger.level === 'verbose') {
    rawPage.on('console', (msg) => {
      if (msg.type() === 'error' || msg.type() === 'warning') {
        logger.log('console', { type: msg.type(), text: _truncate(msg.text(), 300) });
      }
    });
    rawPage.on('response', (resp) => {
      const status = resp.status();
      if (status >= 400) {
        logger.log('http_error', { url: resp.url(), status });
      }
    });
  }

  // ── Wrap human* functions ──
  const wrap = (name, fn) => {
    if (logger.level === 'off') return fn;
    return async (...args) => {
      const url = _safeUrl(rawPage);
      try {
        const result = await fn(...args);
        logger.log(name, { args: _sanitizeArgs(name, args), url, ok: true });
        return result;
      } catch (err) {
        logger.log(name, { args: _sanitizeArgs(name, args), url, error: err.message });
        throw err;
      }
    };
  };

  // ── Wrap observation functions ──
  const wrappedSnapshot = async (opts) => {
    const result = await snapshot(rawPage, opts);
    if (logger.level !== 'off') {
      logger.log('snapshot', { selector: opts?.selector || 'body', interactiveOnly: opts?.interactiveOnly || false, length: result.length, url: _safeUrl(rawPage) });
    }
    return result;
  };

  const wrappedDumpInteractive = async (opts) => {
    const result = await dumpInteractiveElements(rawPage, opts);
    if (logger.level !== 'off') {
      logger.log('dumpInteractiveElements', { count: result.length, url: _safeUrl(rawPage) });
    }
    return result;
  };

  const wrappedScreenshot = async (opts) => {
    const result = await takeScreenshot(rawPage, opts);
    if (logger.level !== 'off') {
      logger.log('screenshot', { url: _safeUrl(rawPage) });
    }
    return result;
  };

  const wrappedScreenshotAndReport = async (message, opts) => {
    const result = await screenshotAndReport(rawPage, message, opts);
    if (logger.level !== 'off') {
      logger.log('screenshotAndReport', { message: _truncate(message, 200), url: _safeUrl(rawPage) });
    }
    return result;
  };

  return {
    browser, ctx,
    page: proxiedPage,
    logger,
    humanClick:     wrap('humanClick', humanClick),
    humanMouseMove: wrap('humanMouseMove', humanMouseMove),
    humanType:      wrap('humanType', humanType),
    humanScroll:    wrap('humanScroll', humanScroll),
    humanRead:      wrap('humanRead', humanRead),
    solveCaptcha:   wrap('solveCaptcha', (captchaOpts) => solveCaptcha(rawPage, captchaOpts)),
    takeScreenshot: wrappedScreenshot,
    screenshotAndReport: wrappedScreenshotAndReport,

    // Observation layer — use these instead of page.textContent()
    snapshot:               wrappedSnapshot,
    snapshotAI:             wrap('snapshotAI', (opts) => snapshotAI(rawPage, opts)),
    dumpInteractiveElements: wrappedDumpInteractive,

    // Ref-based interactions — use refs from snapshotAI() output
    clickRef:       wrap('clickRef', (ref, opts) => clickRef(rawPage, ref, opts)),
    fillRef:        wrap('fillRef', (ref, value, opts) => fillRef(rawPage, ref, value, opts)),
    typeRef:        wrap('typeRef', (ref, text, opts) => typeRef(rawPage, ref, text, opts)),
    selectRef:      wrap('selectRef', (ref, value, opts) => selectRef(rawPage, ref, value, opts)),
    hoverRef:       wrap('hoverRef', (ref, opts) => hoverRef(rawPage, ref, opts)),

    // Text extraction — clean readable text from pages
    extractText:    wrap('extractText', (opts) => extractText(rawPage, opts)),

    // Cookie management — get/set/clear cookies
    getCookies:     wrap('getCookies', (urls) => getCookies(ctx, urls)),
    setCookies:     wrap('setCookies', (cookies) => setCookies(ctx, cookies)),
    clearCookies:   wrap('clearCookies', () => clearCookies(ctx)),

    // Batch actions — execute multiple actions in one call
    batchActions:   wrap('batchActions', (actions, opts) => batchActions(rawPage, actions, opts)),

    sleep, rand,
    getSessionLog:  () => logger.getLog(),
  };
}

/**
 * Launch a stealth browser with residential proxy and device fingerprint.
 *
 * @param {Object}  opts
 * @param {string}  opts.country   — 'us'|'ro'|'gb'|'de'|'nl'|'jp'|'fr'|'ca'|'au'|'sg' (default: 'us')
 * @param {boolean} opts.mobile    — iPhone 15 Pro (true) or Desktop Chrome (false). Default: true
 * @param {boolean} opts.useProxy  — Enable residential proxy. Default: true
 * @param {boolean} opts.headless  — Headless mode. Default: true
 * @param {string}  opts.session   — Sticky session ID / Decodo port (unique IP per value)
 * @param {string}  opts.profile   — Persistent profile name. Saves cookies/localStorage between launches.
 *                                   Default: "default". Pass null for ephemeral.
 * @param {boolean} opts.reuse     — Reuse running browser for this profile. Proxy mode must match
 *                                   the existing live context. Default: true
 * @param {string}  opts.logLevel  — 'off' | 'actions' | 'verbose'. Default: 'actions' (env CN_LOG_LEVEL)
 * @param {string}  opts.task      — User's task / prompt to record in the session log. Optional.
 *
 * @returns {{ browser, ctx, page, logger, humanClick, humanMouseMove, humanType, humanScroll, humanRead, solveCaptcha, takeScreenshot, screenshotAndReport, snapshot, dumpInteractiveElements, sleep, rand, getSessionLog }}
 */
async function launchBrowser(opts = {}) {
  const {
    country  = null,
    mobile   = true,
    useProxy = true,
    headless = true,
    session  = null,
    profile  = DEFAULT_PROFILE_NAME,
    reuse    = true,
    logLevel = null,
    task     = null,
  } = opts;
  const normalizedProfile = typeof profile === 'string' ? profile.trim() : profile;
  const profileName = normalizedProfile === '' ? DEFAULT_PROFILE_NAME : normalizedProfile;

  const cty   = country || process.env.CN_PROXY_COUNTRY || 'us';
  const level = logLevel || process.env.CN_LOG_LEVEL || 'actions';
  const logger = new ActionLogger(_crypto.randomUUID(), level);
  logger.log('launch', { country: cty, mobile, profile: profileName, useProxy, headless, logLevel: level });
  if (task) logger.log('task', { prompt: typeof task === 'string' ? task : JSON.stringify(task) });

  // ── Reuse: return existing browser if alive ──
  // Reuse is only safe when requested proxy mode matches the live context.
  // Playwright cannot swap proxy config on an already running context.
  if (reuse && profileName) {
    const active = _activeBrowsers.get(profileName);
    if (active) {
      const requestedProxyEnabled = Boolean(useProxy) && process.env.CN_NO_PROXY !== '1';
      const activeProxyEnabled = Boolean(active.proxyEnabled);
      if (requestedProxyEnabled !== activeProxyEnabled) {
        throw new Error(
          `[clawnet] Reuse refused for profile "${profileName}": ` +
          `existing context proxy=${activeProxyEnabled ? 'on' : 'off'}, requested proxy=${requestedProxyEnabled ? 'on' : 'off'}. ` +
          'Close this profile (closeBrowser) or launch with reuse:false/new profile to change proxy mode.'
        );
      }

      try {
        active.ctx.pages(); // throws if context is dead
        const page = await active.ctx.newPage();
        console.log(`[clawnet] Reusing browser for profile "${profileName}"`);
        logger.log('reuse', { profile: profileName });
        return buildResult(active.browser, active.ctx, page, logger);
      } catch (_) {
        // Context died — remove and fall through to fresh launch
        _activeBrowsers.delete(profileName);
      }
    }
  }

  // ── Fresh launch: ensure credentials exist and fetch managed config ──
  if (!resolveAgentCredentials()) {
    await autoRegisterAgent(process.env.CN_API_URL || DEFAULT_API_URL);
  }
  try {
    await getCredentials();
  } catch (e) {
    console.warn('[clawnet] Could not fetch managed credentials:', e.message);
  }

  const device = buildDevice(mobile, cty);
  const meta   = COUNTRY_META[cty.toLowerCase()] || COUNTRY_META.us;
  const proxy  = useProxy ? makeProxy(session, cty) : null;

  // Fail-closed: refuse to launch without proxy unless explicitly opted out.
  // A silent fallback to no-proxy would expose the agent's real datacenter IP,
  // defeating the entire purpose of a stealth browser.
  // Users who intentionally want no proxy must set useProxy:false or CN_NO_PROXY=1.
  if (useProxy && !proxy && process.env.CN_NO_PROXY !== '1') {
    throw new Error(
      '[clawnet] Proxy unavailable — auto-registration failed or trial/subscription expired. ' +
      'Set CN_NO_PROXY=1 to launch without proxy, or provide BYO credentials via CN_PROXY_SERVER/CN_PROXY_USER.'
    );
  }

  const disableSandbox = shouldDisableSandbox();
  logSandboxMode(disableSandbox);

  const launchArgs = [
    '--ignore-certificate-errors',
    '--disable-blink-features=AutomationControlled',
    '--disable-features=IsolateOrigins,site-per-process',
  ];
  if (disableSandbox) {
    launchArgs.unshift('--disable-setuid-sandbox');
    launchArgs.unshift('--no-sandbox');
  }
  if (process.env.CN_DISABLE_WEB_SECURITY === '1') {
    launchArgs.push('--disable-web-security');
  }

  const ctxOpts = {
    ...device,
    ignoreHTTPSErrors: true,
    permissions: ['geolocation', 'notifications'],
  };
  if (proxy) ctxOpts.proxy = proxy;

  // ── Persistent profile: launchPersistentContext ──
  if (profileName) {
    const safeName = encodeURIComponent(profileName);
    const profileDir = _path.join(PROFILES_DIR, safeName);
    _fs.mkdirSync(profileDir, { recursive: true });

    const ctx = await chromium.launchPersistentContext(profileDir, {
      headless,
      args: launchArgs,
      ...ctxOpts,
    });

    await applyStealthScripts(ctx, mobile, meta.locale);
    const page = ctx.pages()[0] || await ctx.newPage();
    const browser = ctx.browser();
    const result = buildResult(browser, ctx, page, logger);

    if (reuse) {
      _activeBrowsers.set(profileName, { browser, ctx, proxyEnabled: Boolean(proxy) });
    }

    console.log(`[clawnet] Launched with persistent profile "${profileName}"`);
    return result;
  }

  // ── Ephemeral: standard launch (only when profile === null) ──
  const browser = await chromium.launch({
    headless,
    args: launchArgs,
  });

  const ctx = await browser.newContext(ctxOpts);
  await applyStealthScripts(ctx, mobile, meta.locale);
  const page = await ctx.newPage();

  return buildResult(browser, ctx, page, logger);
}

/**
 * Close a reused browser by profile name.
 * No-op if the profile has no active browser.
 *
 * @param {string} profile — Profile name to close (default: 'default')
 */
async function closeBrowser(profile = 'default') {
  const active = _activeBrowsers.get(profile);
  if (!active) return;
  _activeBrowsers.delete(profile);
  try {
    await active.ctx.close();
  } catch (_) {}
}

// ─── SHADOW DOM UTILITIES ─────────────────────────────────────────────────────

async function shadowQuery(page, selector) {
  return page.evaluateHandle((sel) => {
    function q(root, s) {
      const el = root.querySelector(s); if (el) return el;
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) { const f = q(n.shadowRoot, s); if (f) return f; }
    }
    return q(document, sel) || null;
  }, selector);
}

async function shadowFill(page, selector, value) {
  await page.evaluate(({ sel, val }) => {
    function q(root, s) {
      const el = root.querySelector(s); if (el) return el;
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) { const f = q(n.shadowRoot, s); if (f) return f; }
    }
    const el = q(document, sel);
    if (!el) throw new Error('shadowFill: not found: ' + sel);
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(el, val);
    el.dispatchEvent(new Event('input',  { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, { sel: selector, val: value });
}

async function shadowClickButton(page, buttonText) {
  await page.evaluate((text) => {
    function find(root) {
      for (const b of root.querySelectorAll('button')) if (b.textContent.trim() === text) return b;
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) { const f = find(n.shadowRoot); if (f) return f; }
    }
    const btn = find(document);
    if (!btn) throw new Error('shadowClickButton: not found: ' + text);
    btn.click();
  }, buttonText);
}

/**
 * List all interactive elements on the page using the accessibility tree.
 * Returns a compact YAML string with only buttons, inputs, links, etc.
 * Falls back to DOM querySelectorAll if ariaSnapshot is unavailable.
 *
 * @param {import('playwright').Page} page
 * @param {Object} [opts]
 * @param {string} [opts.selector='body'] — Scope to a region
 * @returns {Promise<string>} YAML accessibility tree of interactive elements
 */
async function dumpInteractiveElements(page, opts = {}) {
  try {
    return await snapshot(page, {
      selector: opts.selector || 'body',
      interactiveOnly: true,
    });
  } catch (_) {
    // Fallback: original DOM-based approach for older Playwright versions
    return JSON.stringify(await _dumpInteractiveElementsDOM(page), null, 2);
  }
}

/**
 * Legacy DOM-based interactive element dump. Used as fallback when
 * ariaSnapshot is unavailable (Playwright < 1.49).
 * @private
 */
async function _dumpInteractiveElementsDOM(page) {
  return page.evaluate(() => {
    const res = [];
    function collect(root) {
      for (const el of root.querySelectorAll('input,textarea,button,select,[contenteditable]')) {
        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0)
          res.push({ tag: el.tagName, name: el.name || '', id: el.id || '', type: el.type || '', text: el.textContent?.trim().slice(0, 25) || '', placeholder: el.placeholder?.slice(0, 25) || '' });
      }
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) collect(n.shadowRoot);
    }
    collect(document);
    return res;
  });
}

// ─── OBSERVATION LAYER ───────────────────────────────────────────────────────
// Use snapshot() instead of page.textContent() — 90-95% fewer tokens for LLMs.
// The accessibility tree gives the agent structured, semantic understanding of
// what's on the page instead of a flat wall of text.

/**
 * Interactive ARIA roles that represent elements the user can interact with.
 * Used by filterInteractiveOnly() to strip decorative/static nodes.
 */
const INTERACTIVE_ROLES = new Set([
  'button', 'link', 'textbox', 'checkbox', 'radio', 'combobox',
  'listbox', 'option', 'menuitem', 'menuitemcheckbox', 'menuitemradio',
  'tab', 'switch', 'slider', 'spinbutton', 'searchbox', 'treeitem',
]);

/**
 * Post-process ariaSnapshot YAML to keep only interactive elements
 * and their ancestor structure. Strips decorative/static nodes
 * (headings, paragraphs, images, generic containers without interactive children).
 *
 * Two-pass algorithm:
 *   Pass 1: Scan all lines, mark lines whose role is in INTERACTIVE_ROLES.
 *   Pass 2: For each marked line, walk up the indent hierarchy to mark all
 *           ancestor lines so the structural tree remains valid.
 *   Emit:   Output only marked lines.
 *
 * @param {string} yaml — Raw ariaSnapshot YAML
 * @returns {string} Filtered YAML with only interactive elements and their ancestors
 */
function filterInteractiveOnly(yaml) {
  const lines = yaml.split('\n');
  const keep = new Array(lines.length).fill(false);
  const indents = [];

  // Pass 1: find interactive lines and record indent levels
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trimStart();
    const indent = line.length - trimmed.length;
    indents.push(indent);

    if (!trimmed) continue;
    // Extract role: "- role ..." or "- role:" (with children)
    const match = trimmed.match(/^-\s+(\w+)/);
    if (match && INTERACTIVE_ROLES.has(match[1])) {
      keep[i] = true;
    }
  }

  // Pass 2: for each kept line, mark all ancestors (lines with smaller indent above it)
  for (let i = 0; i < lines.length; i++) {
    if (!keep[i]) continue;
    const myIndent = indents[i];
    // Walk backwards to find ancestors at each decreasing indent level
    let targetIndent = myIndent;
    for (let j = i - 1; j >= 0 && targetIndent > 0; j--) {
      if (indents[j] < targetIndent && lines[j].trim()) {
        keep[j] = true;
        targetIndent = indents[j];
      }
    }
  }

  const result = lines.filter((_, i) => keep[i]);
  // If filtering removed everything, return original (safety)
  return result.length > 0 ? result.join('\n') : yaml;
}

/**
 * Capture a compact accessibility tree snapshot of the page or a region.
 * Returns a YAML string with roles, names, and attributes — structured
 * semantic understanding of the page that LLMs can reason about.
 *
 * **Use this INSTEAD of page.textContent().**
 *
 * @param {import('playwright').Page} page
 * @param {Object} [opts]
 * @param {string} [opts.selector='body']       — CSS selector to scope snapshot
 * @param {boolean} [opts.interactiveOnly=false] — Keep only interactive elements (buttons, inputs, links)
 * @param {number} [opts.maxLength=20000]        — Truncate result to N characters
 * @param {number} [opts.timeout=5000]           — Playwright timeout in ms
 * @returns {Promise<string>} YAML accessibility tree
 */
async function snapshot(page, opts = {}) {
  const {
    selector = 'body',
    interactiveOnly = false,
    maxLength = 20000,
    timeout = 5000,
  } = opts;

  const locator = page.locator(selector).first();
  let yaml = await locator.ariaSnapshot({ timeout });

  if (interactiveOnly) {
    yaml = filterInteractiveOnly(yaml);
  }

  if (yaml.length > maxLength) {
    yaml = yaml.slice(0, maxLength) + '\n... [truncated]';
  }

  return yaml;
}

// ─── AI SNAPSHOT (with refs) ────────────────────────────────────────────────
// Uses Playwright's _snapshotForAI() (available in 1.58+) which returns a
// structured accessibility tree with embedded [ref=eN] annotations.
// Agents can then click/fill/type by ref instead of guessing CSS selectors.
//
// Example output:
//   - navigation "Main" [ref=e1]:
//     - link "Home" [ref=e2]
//   - heading "Nike Air Jordan 1 Low" [ref=e3]
//   - list "Sizes" [ref=e4]:
//     - button "7" [ref=e5]
//     - button "8" [ref=e6]
//   - button "Add to Bag" [ref=e7]

/**
 * Capture an AI-optimized snapshot of the page with embedded element refs.
 *
 * Returns `{ snapshot, refs, truncated }` where `snapshot` is a formatted
 * string and `refs` is a set of available ref IDs (e.g. "e1", "e2").
 *
 * Falls back to ariaSnapshot() if _snapshotForAI is unavailable.
 *
 * @param {import('playwright').Page} page
 * @param {Object} [opts]
 * @param {number} [opts.maxChars=20000] — Truncate snapshot to N characters
 * @param {number} [opts.timeout=5000]   — Playwright timeout in ms
 * @returns {Promise<{snapshot: string, refs: Object<string, boolean>, truncated?: boolean}>}
 */
async function snapshotAI(page, opts = {}) {
  const { maxChars = 20000, timeout = 5000 } = opts;

  // _snapshotForAI is a private Playwright API (available in 1.58+)
  if (!page._snapshotForAI) {
    // Fallback to ariaSnapshot if not available
    const yaml = await snapshot(page, { maxLength: maxChars, timeout });
    return { snapshot: yaml, refs: {} };
  }

  const result = await page._snapshotForAI({
    timeout: Math.max(500, Math.min(60000, timeout)),
    track: 'response',
  });

  let snap = String(result?.full ?? '');
  let truncated = false;

  if (maxChars && snap.length > maxChars) {
    snap = snap.slice(0, maxChars) + '\n\n[...TRUNCATED - page too large]';
    truncated = true;
  }

  // Parse ref IDs from snapshot text: [ref=eN]
  const refs = {};
  const refRegex = /\[ref=(e\d+)\]/g;
  let m;
  while ((m = refRegex.exec(snap)) !== null) {
    refs[m[1]] = true;
  }

  return { snapshot: snap, refs, truncated: truncated || undefined };
}

// ─── REF-BASED INTERACTIONS ─────────────────────────────────────────────────
// Click, fill, and type using [ref=eN] from snapshotAI() output.
// Uses Playwright's aria-ref locator which resolves refs from the last
// _snapshotForAI() call automatically.

/**
 * Click an element by its ref ID from a previous snapshotAI() call.
 *
 * @param {import('playwright').Page} page
 * @param {string} ref — Ref ID (e.g. "e4") from snapshotAI() output
 * @param {Object} [opts]
 * @param {number} [opts.timeout=8000]
 * @param {'left'|'right'|'middle'} [opts.button='left']
 * @param {boolean} [opts.doubleClick=false]
 */
async function clickRef(page, ref, opts = {}) {
  const { timeout = 8000, button = 'left', doubleClick = false } = opts;
  const locator = page.locator(`aria-ref=${ref}`);
  if (doubleClick) {
    await locator.dblclick({ timeout, button });
  } else {
    await locator.click({ timeout, button });
  }
}

/**
 * Fill an input/textarea by its ref ID. Clears existing value first.
 *
 * @param {import('playwright').Page} page
 * @param {string} ref — Ref ID from snapshotAI()
 * @param {string} value — Value to fill
 * @param {Object} [opts]
 * @param {number} [opts.timeout=8000]
 */
async function fillRef(page, ref, value, opts = {}) {
  const { timeout = 8000 } = opts;
  const locator = page.locator(`aria-ref=${ref}`);
  await locator.fill(value, { timeout });
}

/**
 * Type text into an element by ref ID. Supports human-like slow typing.
 *
 * @param {import('playwright').Page} page
 * @param {string} ref — Ref ID from snapshotAI()
 * @param {string} text — Text to type
 * @param {Object} [opts]
 * @param {boolean} [opts.slowly=false] — Type character-by-character with delay
 * @param {boolean} [opts.submit=false] — Press Enter after typing
 * @param {number} [opts.timeout=8000]
 */
async function typeRef(page, ref, text, opts = {}) {
  const { slowly = false, submit = false, timeout = 8000 } = opts;
  const locator = page.locator(`aria-ref=${ref}`);
  if (slowly) {
    await locator.click({ timeout });
    await locator.type(text, { timeout, delay: 75 });
  } else {
    await locator.fill(text, { timeout });
  }
  if (submit) {
    await locator.press('Enter', { timeout });
  }
}

/**
 * Select an option in a <select> element by ref ID.
 *
 * @param {import('playwright').Page} page
 * @param {string} ref — Ref ID from snapshotAI()
 * @param {string} value — Option value or visible text
 * @param {Object} [opts]
 * @param {number} [opts.timeout=8000]
 */
async function selectRef(page, ref, value, opts = {}) {
  const { timeout = 8000 } = opts;
  const locator = page.locator(`aria-ref=${ref}`);
  await locator.selectOption(value, { timeout });
}

/**
 * Hover over an element by ref ID (useful for revealing tooltips/menus).
 *
 * @param {import('playwright').Page} page
 * @param {string} ref — Ref ID from snapshotAI()
 * @param {Object} [opts]
 * @param {number} [opts.timeout=8000]
 */
async function hoverRef(page, ref, opts = {}) {
  const { timeout = 8000 } = opts;
  const locator = page.locator(`aria-ref=${ref}`);
  await locator.hover({ timeout });
}

// ─── TEXT EXTRACTION ────────────────────────────────────────────────────────
// Inspired by PinchTab's /text endpoint (internal/handlers/text.go).
// Extracts clean readable text from pages, stripping navigation/ads/noise.

/**
 * Extract clean text from the page using readability heuristics.
 *
 * Two modes:
 *   - 'readability' (default): Finds the main content area (<article>, <main>,
 *     [role="main"]), or falls back to cloning <body> and stripping noise elements
 *     (nav, footer, ads, modals, cookie banners, etc.).
 *   - 'raw': Returns document.body.innerText as-is.
 *
 * @param {import('playwright').Page} page
 * @param {Object} [opts]
 * @param {'readability'|'raw'} [opts.mode='readability'] - Extraction mode
 * @param {number} [opts.maxChars] - Truncate text to N characters
 * @returns {Promise<{url: string, title: string, text: string, truncated: boolean}>}
 */
async function extractText(page, opts = {}) {
  const { mode = 'readability', maxChars } = opts;
  const url = page.url();
  const title = await page.title();

  let text;
  if (mode === 'raw') {
    text = await page.evaluate(() => document.body.innerText);
  } else {
    text = await page.evaluate(() => {
      // Try semantic containers first
      const selectors = ['article', '[role="main"]', 'main'];
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el && el.innerText.trim().length > 100) {
          return el.innerText.replace(/\n{3,}/g, '\n\n').trim();
        }
      }
      // Fallback: clone body and strip noise elements
      const clone = document.body.cloneNode(true);
      const noiseSelectors = [
        'nav', 'footer', 'aside', 'header',
        '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]',
        '.ad', '.ads', '.advertisement', '.sidebar',
        '.cookie-banner', '.cookie-consent', '.popup', '.modal',
        '.social-share', '.comments', '.related-posts',
        'script', 'style', 'noscript', 'svg', 'iframe',
        '[hidden]', '[aria-hidden="true"]',
      ];
      for (const sel of noiseSelectors) {
        clone.querySelectorAll(sel).forEach(el => el.remove());
      }
      return clone.innerText.replace(/\n{3,}/g, '\n\n').trim();
    });
  }

  let truncated = false;
  if (maxChars && text.length > maxChars) {
    text = text.slice(0, maxChars);
    truncated = true;
  }

  return { url, title, text, truncated };
}

// ─── COOKIE MANAGEMENT ──────────────────────────────────────────────────────
// Inspired by PinchTab's /cookies endpoint (internal/handlers/cookies.go).
// Wraps Playwright's BrowserContext cookie API with logging-friendly interface.

/**
 * Get cookies for the current browser context.
 *
 * @param {import('playwright').BrowserContext} ctx - Playwright browser context
 * @param {string|string[]} [urls] - Filter by URL(s). If omitted, returns all cookies.
 * @returns {Promise<Array<{name: string, value: string, domain: string, path: string, secure: boolean, httpOnly: boolean, sameSite: string, expires: number}>>}
 */
async function getCookies(ctx, urls) {
  if (urls) {
    return ctx.cookies(Array.isArray(urls) ? urls : [urls]);
  }
  return ctx.cookies();
}

/**
 * Set cookies on the browser context.
 *
 * Each cookie must have at least `name`, `value`, and either `url` or `domain`+`path`.
 *
 * @param {import('playwright').BrowserContext} ctx - Playwright browser context
 * @param {Array<{name: string, value: string, url?: string, domain?: string, path?: string, secure?: boolean, httpOnly?: boolean, sameSite?: 'Strict'|'Lax'|'None', expires?: number}>} cookies
 * @returns {Promise<{set: number, total: number}>}
 */
async function setCookies(ctx, cookies) {
  const cookieArray = Array.isArray(cookies) ? cookies : [cookies];
  await ctx.addCookies(cookieArray);
  return { set: cookieArray.length, total: cookieArray.length };
}

/**
 * Clear all cookies from the browser context.
 *
 * @param {import('playwright').BrowserContext} ctx
 * @returns {Promise<{cleared: true}>}
 */
async function clearCookies(ctx) {
  await ctx.clearCookies();
  return { cleared: true };
}

// ─── RICH TEXT EDITOR UTILITIES ───────────────────────────────────────────────

async function pasteIntoEditor(page, editorSelector, text) {
  const el = await page.$(editorSelector);
  if (!el) throw new Error('pasteIntoEditor: editor not found: ' + editorSelector);
  await el.click();
  await sleep(300);
  await page.evaluate((t) => {
    const ta = document.createElement('textarea');
    ta.value = t;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }, text);
  await page.keyboard.press('Control+a');
  await sleep(100);
  await page.keyboard.press('Control+v');
  await sleep(500);
}

// ─── SESSION LOG QUERIES ─────────────────────────────────────────────────────

/**
 * List all session log files, newest first.
 * @returns {Array<{ sessionId: string, file: string, mtime: string, size: number }>}
 */
function getSessionLogs() {
  if (!_fs.existsSync(LOGS_DIR)) return [];
  return _fs.readdirSync(LOGS_DIR)
    .filter(f => f.endsWith('.jsonl'))
    .map(f => {
      const full = _path.join(LOGS_DIR, f);
      const stat = _fs.statSync(full);
      return { sessionId: f.replace('.jsonl', ''), file: full, mtime: stat.mtime.toISOString(), size: stat.size };
    })
    .sort((a, b) => b.mtime.localeCompare(a.mtime));
}

/**
 * Read a specific session log by ID.
 * @param {string} sessionId
 * @returns {Array<Object>}
 */
function getSessionLog(sessionId) {
  const file = _path.join(LOGS_DIR, `${sessionId}.jsonl`);
  if (!_fs.existsSync(file)) return [];
  try {
    return _fs.readFileSync(file, 'utf-8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l));
  } catch (_) { return []; }
}

// ─── EXPORTS ──────────────────────────────────────────────────────────────────

module.exports = {
  // Main
  launchBrowser, closeBrowser, getCredentials, importCredentials,

  // Human-like interaction
  humanClick, humanMouseMove, humanType, humanScroll, humanRead,

  // CAPTCHA
  solveCaptcha,

  // Screenshots
  takeScreenshot, screenshotAndReport,

  // Observation layer (accessibility tree)
  snapshot, snapshotAI, dumpInteractiveElements,

  // Ref-based interactions (use with snapshotAI)
  clickRef, fillRef, typeRef, selectRef, hoverRef,

  // Text extraction (readability)
  extractText,

  // Cookie management
  getCookies, setCookies, clearCookies,

  // Batch actions
  batchActions,

  // Shadow DOM utilities
  shadowQuery, shadowFill, shadowClickButton,

  // Rich text editors
  pasteIntoEditor,

  // Internals (exposed for advanced users)
  makeProxy, buildDevice,

  // Logging
  getSessionLogs, getSessionLog,

  // Helpers
  sleep, rand, COUNTRY_META,
};

// ─── QUICK TEST ───────────────────────────────────────────────────────────────
if (require.main === module) {
  const country = process.argv[2] || 'us';
  console.log(`Testing Clawnet v1.0.0 — country: ${country.toUpperCase()}\n`);
  (async () => {
    const { browser, page } = await launchBrowser({ country, mobile: true });
    await page.goto('https://ipinfo.io/json', { waitUntil: 'domcontentloaded', timeout: 30000 });
    const info = JSON.parse(await page.textContent('body'));
    console.log(`IP:      ${info.ip}`);
    console.log(`Country: ${info.country} (${info.city})`);
    console.log(`Org:     ${info.org}`);
    console.log(`TZ:      ${info.timezone}`);
    const ua = await page.evaluate(() => navigator.userAgent);
    console.log(`UA:      ${ua.slice(0, 80)}...`);
    if (browser) {
      await browser.close();
    } else {
      await page.context().close();
    }
    console.log('\nClawnet v1.0.0 is ready.');
  })().catch(console.error);
}
