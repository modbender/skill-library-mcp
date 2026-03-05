// config.mjs — KG skill configuration management
//
// Pattern: kg-defaults.json (shipped with skill, git-tracked) + kg-config.json (user overrides, gitignored)
// Like .env.example → .env but for agent skills.
//
// - kg-defaults.json: all default values, updated when skill is updated (git pull)
// - kg-config.json: user overrides only, never touched by skill updates
// - loadConfig() = deep merge(defaults, user overrides)

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, '..', 'data');
const DEFAULTS_PATH = join(DATA_DIR, 'kg-defaults.json');
const CONFIG_PATH = join(DATA_DIR, 'kg-config.json');

// ── Load defaults from kg-defaults.json (shipped with skill) ───────────────

function loadDefaults() {
  if (!existsSync(DEFAULTS_PATH)) {
    console.warn(`⚠️  kg-defaults.json not found at ${DEFAULTS_PATH}. Using empty defaults.`);
    return {};
  }
  try {
    return JSON.parse(readFileSync(DEFAULTS_PATH, 'utf8'));
  } catch (e) {
    console.warn(`⚠️  Failed to parse kg-defaults.json: ${e.message}. Using empty defaults.`);
    return {};
  }
}

/** Exported for CLI display and diff calculation. Always returns a fresh deep clone. */
export function getDefaults() {
  return JSON.parse(JSON.stringify(loadDefaults()));
}

// ── Deep merge helper ──────────────────────────────────────────────────────

function deepMerge(target, source) {
  const result = { ...target };
  for (const key of Object.keys(source)) {
    if (
      source[key] !== null &&
      typeof source[key] === 'object' &&
      !Array.isArray(source[key]) &&
      typeof target[key] === 'object' &&
      !Array.isArray(target[key])
    ) {
      result[key] = deepMerge(target[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

// ── Load / Save ────────────────────────────────────────────────────────────

/** Load config, merged with defaults. Always returns complete config. */
export function loadConfig() {
  const defaults = getDefaults();
  let userConfig = {};
  if (existsSync(CONFIG_PATH)) {
    try {
      userConfig = JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
    } catch (e) {
      console.warn(`⚠️  Failed to parse kg-config.json: ${e.message}. Using defaults.`);
    }
  }
  return deepMerge(defaults, userConfig);
}

/** Save user overrides (only saves non-default values). */
export function saveConfig(config) {
  const defaults = getDefaults();
  const diff = getDiff(defaults, config);
  writeFileSync(CONFIG_PATH, JSON.stringify(diff, null, 2) + '\n');
  return diff;
}

/** Get diff between defaults and current config (only user overrides). */
function getDiff(defaults, current) {
  const diff = {};
  for (const key of Object.keys(current)) {
    if (!(key in defaults)) {
      diff[key] = current[key]; // unknown key, preserve it
      continue;
    }
    if (
      typeof current[key] === 'object' &&
      current[key] !== null &&
      !Array.isArray(current[key]) &&
      typeof defaults[key] === 'object'
    ) {
      const sub = getDiff(defaults[key], current[key]);
      if (Object.keys(sub).length > 0) diff[key] = sub;
    } else if (current[key] !== defaults[key]) {
      diff[key] = current[key];
    }
  }
  return diff;
}

/** Get a nested config value by dot-separated path. */
export function getConfigValue(path) {
  const config = loadConfig();
  const parts = path.split('.');
  let current = config;
  for (const part of parts) {
    if (current === undefined || current === null) return undefined;
    current = current[part];
  }
  return current;
}

/** Set a nested config value by dot-separated path. */
export function setConfigValue(path, value) {
  const config = loadConfig();
  const parts = path.split('.');
  let current = config;
  for (let i = 0; i < parts.length - 1; i++) {
    if (typeof current[parts[i]] !== 'object' || current[parts[i]] === null) {
      current[parts[i]] = {};
    }
    current = current[parts[i]];
  }
  current[parts[parts.length - 1]] = value;
  return saveConfig(config);
}

/** Reset a nested config value to default by removing user override. */
export function resetConfigValue(path) {
  const defaults = getDefaults();
  const config = loadConfig();
  const parts = path.split('.');
  let current = config;
  for (let i = 0; i < parts.length - 1; i++) {
    if (typeof current[parts[i]] !== 'object') return;
    current = current[parts[i]];
  }
  // Get default value
  let defaultVal = defaults;
  for (const part of parts) {
    if (defaultVal === undefined) break;
    defaultVal = defaultVal[part];
  }
  current[parts[parts.length - 1]] = defaultVal;
  return saveConfig(config);
}

/** List all config keys with current values + defaults + whether overridden. */
export function listConfig() {
  const defaults = getDefaults();
  const config = loadConfig();
  let userConfig = {};
  if (existsSync(CONFIG_PATH)) {
    try { userConfig = JSON.parse(readFileSync(CONFIG_PATH, 'utf8')); } catch {}
  }

  const entries = [];
  function walk(obj, defs, user, prefix) {
    for (const key of Object.keys(obj)) {
      const path = prefix ? `${prefix}.${key}` : key;
      const val = obj[key];
      const def = defs?.[key];
      const usr = user?.[key];

      if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
        walk(val, def || {}, usr || {}, path);
      } else {
        entries.push({
          path,
          value: val,
          default: def,
          overridden: usr !== undefined && usr !== def,
        });
      }
    }
  }
  walk(config, defaults, userConfig, '');
  return entries;
}

export { CONFIG_PATH };
