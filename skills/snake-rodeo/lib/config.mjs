/**
 * Configuration management for Snake Game
 *
 * Loads config from multiple sources with precedence:
 * 1. CLI arguments (highest)
 * 2. Environment variables
 * 3. Config file (~/.config/snake-rodeo/settings.json)
 * 4. Defaults (lowest)
 *
 * All paths use XDG Base Directory conventions and are isolated
 * to snake-rodeo's own directories. No access to host agent internals.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const HOME = process.env.HOME;

// XDG Base Directory support
const XDG_CONFIG = process.env.XDG_CONFIG_HOME || join(HOME, '.config');
const XDG_STATE  = process.env.XDG_STATE_HOME  || join(HOME, '.local/state');
const XDG_DATA   = process.env.XDG_DATA_HOME   || join(HOME, '.local/share');

const CONFIG_DIR  = join(XDG_CONFIG, 'snake-rodeo');
const STATE_DIR   = join(XDG_STATE,  'snake-rodeo');
const DATA_DIR    = join(XDG_DATA,   'snake-rodeo');

// Ensure dirs exist on first use (lazy, per-path)
function ensureDir(dir) {
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
}

const SETTINGS_FILE = join(CONFIG_DIR, 'settings.json');
const PID_FILE      = join(STATE_DIR,  'daemon.pid');
const LOG_FILE      = join(DATA_DIR,   'daemon.log');
const STATE_FILE    = join(STATE_DIR,  'daemon.state');

// Auth token file — populated by the user or trifle-auth skill explicitly.
// The skill never reads from the host agent's internal workspace.
const AUTH_FILE     = join(CONFIG_DIR, 'auth.json');

export const PATHS = {
  settings:  SETTINGS_FILE,
  pidFile:   PID_FILE,
  logFile:   LOG_FILE,
  stateFile: STATE_FILE,
  authFile:  AUTH_FILE,
  // Expose dir helpers so callers can mkdirSync before writing
  _dirs: { config: CONFIG_DIR, state: STATE_DIR, data: DATA_DIR, ensureDir },
};

export const SERVERS = {
  live: 'https://bot.trifle.life',
  staging: 'https://bot-staging.trifle.life',
};

export const DEFAULTS = {
  server: 'live',
  strategy: 'expected-value',
  minBalance: 5,
  pollIntervalMs: 1000,
  maxRoundBudgetPct: 0.2,
  telegramChatId: null,
  telegramBotToken: null,
  logToConsole: true,
  logToTelegram: true,
  logToFile: true,
  paused: false,
  // Strategy-specific defaults
  strategyOptions: {
    'expected-value': {
      minExpectedValue: 0.5,
      switchThreshold: 1.5, // Switch teams if EV is 50% better
    },
    'aggressive': {
      bidMultiplier: 2,
      alwaysOutbid: true,
    },
    'underdog': {
      maxPoolSize: 10,
      minPayoutMultiplier: 2.0,
    },
    'conservative': {
      maxBidAmount: 1,
      skipIfBehind: true,
    },
    'random': {
      // No options
    },
  },
};

/**
 * Load settings from file
 */
export function loadSettings() {
  try {
    if (existsSync(SETTINGS_FILE)) {
      const data = JSON.parse(readFileSync(SETTINGS_FILE, 'utf8'));
      return { ...DEFAULTS, ...data };
    }
  } catch (e) {
    console.error(`Warning: Could not load settings: ${e.message}`);
  }
  return { ...DEFAULTS };
}

/**
 * Save settings to file
 */
export function saveSettings(settings) {
  ensureDir(CONFIG_DIR);
  // Only save non-default values
  const toSave = {};
  for (const [key, value] of Object.entries(settings)) {
    if (key !== 'strategyOptions' && value !== DEFAULTS[key]) {
      toSave[key] = value;
    }
  }
  // Always save strategyOptions if modified
  if (settings.strategyOptions) {
    toSave.strategyOptions = settings.strategyOptions;
  }
  writeFileSync(SETTINGS_FILE, JSON.stringify(toSave, null, 2));
}

/**
 * Get a specific config value
 */
export function getConfig(key) {
  const settings = loadSettings();
  return key.split('.').reduce((obj, k) => obj?.[k], settings);
}

/**
 * Set a specific config value
 */
export function setConfig(key, value) {
  const settings = loadSettings();
  const keys = key.split('.');
  let obj = settings;
  for (let i = 0; i < keys.length - 1; i++) {
    if (!obj[keys[i]]) obj[keys[i]] = {};
    obj = obj[keys[i]];
  }

  // Parse value types
  if (value === 'true') value = true;
  else if (value === 'false') value = false;
  else if (value === 'null') value = null;
  else if (!isNaN(value) && value !== '') value = Number(value);

  obj[keys[keys.length - 1]] = value;
  saveSettings(settings);
  return settings;
}

/**
 * Get the backend URL based on server setting
 */
export function getBackendUrl(settings = null) {
  settings = settings || loadSettings();
  return process.env.TRIFLE_BACKEND_URL || SERVERS[settings.server] || SERVERS.live;
}

/**
 * Load daemon state (paused, current team, etc.)
 */
export function loadDaemonState() {
  try {
    if (existsSync(STATE_FILE)) {
      return JSON.parse(readFileSync(STATE_FILE, 'utf8'));
    }
  } catch {}
  return {
    paused: false,
    currentTeam: null,
    lastRound: -1,
    gamesPlayed: 0,
    votesPlaced: 0,
    wins: 0,
    startedAt: null,
  };
}

/**
 * Save daemon state
 */
export function saveDaemonState(state) {
  ensureDir(STATE_DIR);
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

/**
 * Merge CLI options with config
 */
export function mergeOptions(cliOptions) {
  const settings = loadSettings();
  return {
    ...settings,
    ...Object.fromEntries(
      Object.entries(cliOptions).filter(([_, v]) => v !== undefined)
    ),
  };
}
