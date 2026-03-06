// ============================================================================
// config.js — Configuration management
//
// Config dir: ~/.openclawmp/
// Stores: auth tokens, preferences
// ============================================================================

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const CONFIG_DIR = path.join(os.homedir(), '.openclawmp');
const AUTH_FILE = path.join(CONFIG_DIR, 'auth.json');
const CREDENTIALS_FILE = path.join(CONFIG_DIR, 'credentials.json');

// Default API base — can be overridden by --api flag or OPENCLAWMP_API env
let API_BASE = 'https://openclawmp.cc';

// OpenClaw state directory (for lockfile, install dirs, device identity)
const OPENCLAW_STATE_DIR = process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), '.openclaw');
const LOCKFILE = path.join(OPENCLAW_STATE_DIR, 'seafood-lock.json');
const DEVICE_JSON = path.join(OPENCLAW_STATE_DIR, 'identity', 'device.json');

// Valid asset types and their install subdirectories
const ASSET_TYPES = {
  skill:      'skills',
  plugin:     'extensions',
  trigger:    'triggers',
  channel:    'extensions',
  experience: 'experiences',
};

/**
 * Ensure config directory exists
 */
function ensureConfigDir() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

/**
 * Get the install directory for a given asset type
 */
function installDirForType(type) {
  const subdir = ASSET_TYPES[type];
  if (!subdir) {
    throw new Error(`Unknown asset type: ${type}. Valid types: ${Object.keys(ASSET_TYPES).join(', ')}`);
  }
  return path.join(OPENCLAW_STATE_DIR, subdir);
}

/**
 * Get/set API base URL
 */
function getApiBase() {
  return API_BASE;
}

function setApiBase(url) {
  // Strip trailing slash
  API_BASE = url.replace(/\/+$/, '');
}

/**
 * Read auth token (priority: env var > auth.json > credentials.json)
 */
function getAuthToken() {
  // 1. Environment variable (highest priority)
  if (process.env.OPENCLAWMP_TOKEN) {
    return process.env.OPENCLAWMP_TOKEN;
  }

  ensureConfigDir();

  // 2. auth.json (format: { token: "sk-xxx" })
  if (fs.existsSync(AUTH_FILE)) {
    try {
      const data = JSON.parse(fs.readFileSync(AUTH_FILE, 'utf-8'));
      if (data.token) return data.token;
    } catch {}
  }

  // 3. credentials.json (format: { api_key: "sk-xxx" })
  if (fs.existsSync(CREDENTIALS_FILE)) {
    try {
      const data = JSON.parse(fs.readFileSync(CREDENTIALS_FILE, 'utf-8'));
      if (data.api_key) return data.api_key;
    } catch {}
  }

  return null;
}

/**
 * Save auth token
 */
function saveAuthToken(token, extra = {}) {
  ensureConfigDir();
  const data = { token, savedAt: new Date().toISOString(), ...extra };
  fs.writeFileSync(AUTH_FILE, JSON.stringify(data, null, 2) + '\n');
}

/**
 * Read the OpenClaw device ID
 */
function getDeviceId() {
  if (!fs.existsSync(DEVICE_JSON)) return null;
  try {
    const data = JSON.parse(fs.readFileSync(DEVICE_JSON, 'utf-8'));
    return data.deviceId || null;
  } catch {
    return null;
  }
}

// === Lockfile operations ===

/**
 * Initialize lockfile if it doesn't exist
 */
function initLockfile() {
  if (!fs.existsSync(LOCKFILE)) {
    const dir = path.dirname(LOCKFILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(LOCKFILE, JSON.stringify({ version: 1, installed: {} }, null, 2) + '\n');
  }
}

/**
 * Read the lockfile
 */
function readLockfile() {
  initLockfile();
  try {
    return JSON.parse(fs.readFileSync(LOCKFILE, 'utf-8'));
  } catch {
    return { version: 1, installed: {} };
  }
}

/**
 * Update a lockfile entry
 */
function updateLockfile(key, version, location) {
  const lock = readLockfile();
  lock.installed[key] = {
    version,
    installedAt: new Date().toISOString(),
    location,
  };
  fs.writeFileSync(LOCKFILE, JSON.stringify(lock, null, 2) + '\n');
}

/**
 * Remove a lockfile entry
 */
function removeLockfile(key) {
  const lock = readLockfile();
  delete lock.installed[key];
  fs.writeFileSync(LOCKFILE, JSON.stringify(lock, null, 2) + '\n');
}

module.exports = {
  CONFIG_DIR,
  OPENCLAW_STATE_DIR,
  LOCKFILE,
  DEVICE_JSON,
  ASSET_TYPES,
  ensureConfigDir,
  installDirForType,
  getApiBase,
  setApiBase,
  getAuthToken,
  saveAuthToken,
  getDeviceId,
  initLockfile,
  readLockfile,
  updateLockfile,
  removeLockfile,
};
