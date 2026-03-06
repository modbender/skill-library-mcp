// ── Gateway WebSocket 連線管理 ──

import WebSocket from 'ws';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';

const OPENCLAW_DIR = path.join(os.homedir(), '.openclaw');
const IDENTITY_DIR = path.join(OPENCLAW_DIR, 'identity');
const DEVICE_IDENTITY_PATH = process.env.JARVIS_DEVICE_IDENTITY_PATH || path.join(IDENTITY_DIR, 'jarvis-device.json');
const DEVICE_AUTH_PATH = process.env.JARVIS_DEVICE_AUTH_PATH || path.join(IDENTITY_DIR, 'jarvis-device-auth.json');

const DEVICE_ROLE = 'operator';
const DEFAULT_SCOPES = ['operator.admin', 'operator.approvals', 'operator.pairing'];

const CLIENT_ID = 'openclaw-control-ui';
const CLIENT_VERSION = 'dev';
const CLIENT_PLATFORM = 'node';
const CLIENT_MODE = 'webchat';
const CLIENT_INSTANCE = 'jarvis-backend-1';

let gw = null;
let gwReady = false;
let gwPending = new Map();
let gwSeqId = 1;
let gwSessionKey = null;
let reconnectTimer = null;

let gwConnectNonce = null;
let gwConnectSent = false;
let gwConnectTimer = null;

let gatewayUrl = '';
let gatewayToken = '';
let configSessionKey = null;  // config 定義的 session key
let onChatEvent = null;  // 外部註冊的 chat 事件回呼

// ── Device identity helpers (from OpenClaw gateway client) ──
function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

const ED25519_SPKI_PREFIX = Buffer.from('302a300506032b6570032100', 'hex');

function base64UrlEncode(buf) {
  return buf.toString('base64').replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/g, '');
}

function derivePublicKeyRaw(publicKeyPem) {
  const spki = crypto.createPublicKey(publicKeyPem).export({ type: 'spki', format: 'der' });
  if (spki.length === ED25519_SPKI_PREFIX.length + 32 && spki.subarray(0, ED25519_SPKI_PREFIX.length).equals(ED25519_SPKI_PREFIX)) {
    return spki.subarray(ED25519_SPKI_PREFIX.length);
  }
  return spki;
}

function fingerprintPublicKey(publicKeyPem) {
  const raw = derivePublicKeyRaw(publicKeyPem);
  return crypto.createHash('sha256').update(raw).digest('hex');
}

function generateIdentity() {
  const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519');
  const publicKeyPem = publicKey.export({ type: 'spki', format: 'pem' }).toString();
  const privateKeyPem = privateKey.export({ type: 'pkcs8', format: 'pem' }).toString();
  return {
    deviceId: fingerprintPublicKey(publicKeyPem),
    publicKeyPem,
    privateKeyPem,
  };
}

function loadOrCreateDeviceIdentity(filePath = DEVICE_IDENTITY_PATH) {
  try {
    if (fs.existsSync(filePath)) {
      const raw = fs.readFileSync(filePath, 'utf8');
      const parsed = JSON.parse(raw);
      if (
        parsed?.version === 1 &&
        typeof parsed.deviceId === 'string' &&
        typeof parsed.publicKeyPem === 'string' &&
        typeof parsed.privateKeyPem === 'string'
      ) {
        const derivedId = fingerprintPublicKey(parsed.publicKeyPem);
        if (derivedId && derivedId !== parsed.deviceId) {
          const updated = { ...parsed, deviceId: derivedId };
          fs.writeFileSync(filePath, `${JSON.stringify(updated, null, 2)}\n`, { mode: 0o600 });
          try { fs.chmodSync(filePath, 0o600); } catch {}
          return { deviceId: derivedId, publicKeyPem: parsed.publicKeyPem, privateKeyPem: parsed.privateKeyPem };
        }
        return { deviceId: parsed.deviceId, publicKeyPem: parsed.publicKeyPem, privateKeyPem: parsed.privateKeyPem };
      }
    }
  } catch {}

  const identity = generateIdentity();
  ensureDir(filePath);
  const stored = {
    version: 1,
    deviceId: identity.deviceId,
    publicKeyPem: identity.publicKeyPem,
    privateKeyPem: identity.privateKeyPem,
    createdAtMs: Date.now(),
  };
  fs.writeFileSync(filePath, `${JSON.stringify(stored, null, 2)}\n`, { mode: 0o600 });
  try { fs.chmodSync(filePath, 0o600); } catch {}
  return identity;
}

function signDevicePayload(privateKeyPem, payload) {
  const key = crypto.createPrivateKey(privateKeyPem);
  return base64UrlEncode(crypto.sign(null, Buffer.from(payload, 'utf8'), key));
}

function publicKeyRawBase64UrlFromPem(publicKeyPem) {
  return base64UrlEncode(derivePublicKeyRaw(publicKeyPem));
}

function buildDeviceAuthPayload(params) {
  const version = params.version ?? (params.nonce ? 'v2' : 'v1');
  const scopes = params.scopes.join(',');
  const token = params.token ?? '';
  const base = [
    version,
    params.deviceId,
    params.clientId,
    params.clientMode,
    params.role,
    scopes,
    String(params.signedAtMs),
    token,
  ];
  if (version === 'v2') base.push(params.nonce ?? '');
  return base.join('|');
}

function normalizeDeviceAuthRole(role) {
  return role.trim();
}

function normalizeDeviceAuthScopes(scopes) {
  if (!Array.isArray(scopes)) return [];
  const out = new Set();
  for (const scope of scopes) {
    const trimmed = scope.trim();
    if (trimmed) out.add(trimmed);
  }
  return [...out].toSorted();
}

function readDeviceAuthStore(filePath) {
  try {
    if (!fs.existsSync(filePath)) return null;
    const raw = fs.readFileSync(filePath, 'utf8');
    const parsed = JSON.parse(raw);
    if (parsed?.version !== 1 || typeof parsed.deviceId !== 'string') return null;
    if (!parsed.tokens || typeof parsed.tokens !== 'object') return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeDeviceAuthStore(filePath, store) {
  ensureDir(filePath);
  fs.writeFileSync(filePath, `${JSON.stringify(store, null, 2)}\n`, { mode: 0o600 });
  try { fs.chmodSync(filePath, 0o600); } catch {}
}

function loadDeviceAuthToken(params) {
  const store = readDeviceAuthStore(DEVICE_AUTH_PATH);
  if (!store) return null;
  if (store.deviceId !== params.deviceId) return null;
  const role = normalizeDeviceAuthRole(params.role);
  const entry = store.tokens[role];
  if (!entry || typeof entry.token !== 'string') return null;
  return entry;
}

function storeDeviceAuthToken(params) {
  const existing = readDeviceAuthStore(DEVICE_AUTH_PATH);
  const role = normalizeDeviceAuthRole(params.role);
  const next = {
    version: 1,
    deviceId: params.deviceId,
    tokens: existing && existing.deviceId === params.deviceId && existing.tokens ? { ...existing.tokens } : {},
  };
  const entry = {
    token: params.token,
    role,
    scopes: normalizeDeviceAuthScopes(params.scopes),
    updatedAtMs: Date.now(),
  };
  next.tokens[role] = entry;
  writeDeviceAuthStore(DEVICE_AUTH_PATH, next);
  return entry;
}

function clearDeviceAuthToken(params) {
  const store = readDeviceAuthStore(DEVICE_AUTH_PATH);
  if (!store || store.deviceId !== params.deviceId) return;
  const role = normalizeDeviceAuthRole(params.role);
  if (!store.tokens[role]) return;
  const next = {
    version: 1,
    deviceId: store.deviceId,
    tokens: { ...store.tokens },
  };
  delete next.tokens[role];
  writeDeviceAuthStore(DEVICE_AUTH_PATH, next);
}

let deviceIdentity = null;
try {
  deviceIdentity = loadOrCreateDeviceIdentity();
} catch (err) {
  console.error('[GW] device identity init failed:', err?.message || err);
}

export function initGateway({ url, token, sessionKey, onChat }) {
  gatewayUrl = url;
  gatewayToken = token;
  configSessionKey = sessionKey;
  onChatEvent = onChat;
  connect();
}

export function isReady() { return gwReady; }
export function getSessionKey() { return gwSessionKey; }

function queueConnect() {
  gwConnectNonce = null;
  gwConnectSent = false;
  if (gwConnectTimer) clearTimeout(gwConnectTimer);
  gwConnectTimer = setTimeout(() => {
    gwConnectTimer = null;
    sendConnect();
  }, 750);
}

function sendConnect() {
  if (gwConnectSent) return;
  if (!gw || gw.readyState !== WebSocket.OPEN) return;
  gwConnectSent = true;
  if (gwConnectTimer) {
    clearTimeout(gwConnectTimer);
    gwConnectTimer = null;
  }

  const role = DEVICE_ROLE;
  const scopes = [...DEFAULT_SCOPES];
  const storedToken = deviceIdentity ? loadDeviceAuthToken({ deviceId: deviceIdentity.deviceId, role })?.token : null;
  const authToken = gatewayToken || storedToken || undefined;
  const auth = authToken ? { token: authToken } : undefined;

  const signedAtMs = Date.now();
  const nonce = gwConnectNonce ?? undefined;
  const device = (() => {
    if (!deviceIdentity) return undefined;
    const payload = buildDeviceAuthPayload({
      deviceId: deviceIdentity.deviceId,
      clientId: CLIENT_ID,
      clientMode: CLIENT_MODE,
      role,
      scopes,
      signedAtMs,
      token: authToken ?? null,
      nonce,
    });
    const signature = signDevicePayload(deviceIdentity.privateKeyPem, payload);
    return {
      id: deviceIdentity.deviceId,
      publicKey: publicKeyRawBase64UrlFromPem(deviceIdentity.publicKeyPem),
      signature,
      signedAt: signedAtMs,
      nonce,
    };
  })();

  gw.send(JSON.stringify({
    type: 'req',
    id: String(gwSeqId++),
    method: 'connect',
    params: {
      minProtocol: 3,
      maxProtocol: 3,
      client: {
        id: CLIENT_ID,
        version: CLIENT_VERSION,
        platform: CLIENT_PLATFORM,
        mode: CLIENT_MODE,
        instanceId: CLIENT_INSTANCE,
      },
      role,
      scopes,
      auth,
      device,
      caps: [],
      userAgent: 'jarvis-backend/1.0',
      locale: 'zh-TW',
    },
  }));
}

function connect() {
  if (gw) { try { gw.close(); } catch {} }
  gwReady = false;

  gw = new WebSocket(gatewayUrl, { origin: 'http://localhost:8001' });

  gw.on('open', () => {
    console.log('[GW] connected');
    queueConnect();
  });

  gw.on('message', (raw) => {
    const msg = JSON.parse(raw.toString());

    if (msg.event === 'connect.challenge') {
      const nonce = msg.payload && typeof msg.payload.nonce === 'string' ? msg.payload.nonce : null;
      if (nonce) {
        gwConnectNonce = nonce;
        sendConnect();
      }
      return;
    }

    if (msg.type === 'res' && msg.id) {
      if (msg.ok && msg.payload?.type === 'hello-ok') {
        gwReady = true;
        gwSessionKey = msg.payload?.session?.key || null;
        console.log('[GW] authenticated, session:', gwSessionKey);
        const authInfo = msg.payload?.auth;
        if (authInfo?.deviceToken && deviceIdentity) {
          storeDeviceAuthToken({
            deviceId: deviceIdentity.deviceId,
            role: authInfo.role ?? DEVICE_ROLE,
            token: authInfo.deviceToken,
            scopes: authInfo.scopes ?? DEFAULT_SCOPES,
          });
        }
      }
      const pending = gwPending.get(msg.id);
      if (pending) {
        gwPending.delete(msg.id);
        msg.ok ? pending.resolve(msg.payload || msg.result || {}) : pending.reject(msg.error || { message: 'unknown error' });
      }
      return;
    }

    if (msg.type === 'event' && msg.event === 'chat') {
      if (msg.payload?.sessionKey === configSessionKey && onChatEvent) {
        const p = msg.payload;
        const u = p.message?.usage;
        console.log(`[GW] jarvis: state=${p.state} model=${p.message?.model || '-'} usage=${u ? JSON.stringify(u) : 'none'}`);
        onChatEvent(msg.payload);
      }
    }

    const quietEvents = ['health', 'connect.challenge', 'tick', 'agent'];
    if (msg.type === 'event' && !quietEvents.includes(msg.event)) {
      console.log('[GW] event:', msg.event);
    }
  });

  gw.on('close', (code, reason) => {
    const reasonText = reason?.toString() || '';
    console.log('[GW] closed:', code, reasonText);
    gwReady = false;
    for (const [, pending] of gwPending) pending.reject(new Error('gateway disconnected'));
    gwPending.clear();

    if (code === 1008 && reasonText.toLowerCase().includes('device token mismatch') && deviceIdentity) {
      try {
        clearDeviceAuthToken({ deviceId: deviceIdentity.deviceId, role: DEVICE_ROLE });
        console.log('[GW] cleared stale device token');
      } catch {}
    }

    if (!reconnectTimer) {
      reconnectTimer = setTimeout(() => { reconnectTimer = null; connect(); }, 3000);
    }
  });

  gw.on('error', (err) => console.error('[GW] error:', err.message));
}

export function gwRequest(method, params) {
  return new Promise((resolve, reject) => {
    if (!gw || !gwReady) return reject(new Error('gateway not connected'));
    const id = String(gwSeqId++);
    gwPending.set(id, { resolve, reject });
    gw.send(JSON.stringify({ type: 'req', id, method, params }));
    setTimeout(() => {
      if (gwPending.has(id)) { gwPending.delete(id); reject(new Error('timeout')); }
    }, 60000);
  });
}
