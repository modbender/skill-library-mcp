const fs = require('node:fs');
const path = require('node:path');
const { InvalidPrefixError } = require('./errors');

const CONFIG_ENV = 'ROUTER_CONFIG_PATH';
let cachedConfig = null;
let cachedMtimeMs = null;
let cachedPath = null;

function ensureNonEmptyString(value, message) {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new Error(message);
  }
}

function validateConfig(parsed) {
  if (!parsed || typeof parsed !== 'object') {
    throw new Error('router.config.json must be a JSON object');
  }

  if (!parsed.prefixMap || typeof parsed.prefixMap !== 'object' || Array.isArray(parsed.prefixMap)) {
    throw new Error('router.config.json missing prefixMap');
  }

  if (parsed.aliasMap !== undefined) {
    if (!parsed.aliasMap || typeof parsed.aliasMap !== 'object' || Array.isArray(parsed.aliasMap)) {
      throw new Error('aliasMap must be an object');
    }
    for (const [alias, target] of Object.entries(parsed.aliasMap)) {
      if (!alias.startsWith('@')) {
        throw new Error(`Invalid alias key: ${alias}. Alias must start with @`);
      }
      ensureNonEmptyString(target, `alias ${alias} must map to a non-empty prefix`);
      if (!target.startsWith('@')) {
        throw new Error(`Invalid alias target: ${target}. Target must start with @`);
      }
    }
  }

  for (const [prefix, route] of Object.entries(parsed.prefixMap)) {
    if (!prefix.startsWith('@')) {
      throw new Error(`Invalid prefix key: ${prefix}. Prefix must start with @`);
    }
    if (!route || typeof route !== 'object' || Array.isArray(route)) {
      throw new Error(`Invalid route config for ${prefix}`);
    }
    ensureNonEmptyString(route.model, `prefix ${prefix} missing model`);
    if (route.fallbackModel !== undefined) {
      ensureNonEmptyString(route.fallbackModel, `prefix ${prefix} fallbackModel must be non-empty string`);
    }
    if (route.fallbackModel && route.fallbackModel === route.model) {
      throw new Error(`prefix ${prefix} fallbackModel must differ from model`);
    }
  }

  if (parsed.retry !== undefined) {
    if (!parsed.retry || typeof parsed.retry !== 'object' || Array.isArray(parsed.retry)) {
      throw new Error('retry must be an object');
    }
    if (parsed.retry.maxRetries !== undefined && (!Number.isInteger(parsed.retry.maxRetries) || parsed.retry.maxRetries < 0)) {
      throw new Error('retry.maxRetries must be a non-negative integer');
    }
    if (parsed.retry.baseDelayMs !== undefined && (!Number.isInteger(parsed.retry.baseDelayMs) || parsed.retry.baseDelayMs < 0)) {
      throw new Error('retry.baseDelayMs must be a non-negative integer');
    }
  }

  if (parsed.auth !== undefined) {
    if (!parsed.auth || typeof parsed.auth !== 'object' || Array.isArray(parsed.auth)) {
      throw new Error('auth must be an object');
    }
    if (parsed.auth.requiredEnv !== undefined) {
      if (!Array.isArray(parsed.auth.requiredEnv)) {
        throw new Error('auth.requiredEnv must be an array');
      }
      for (const key of parsed.auth.requiredEnv) {
        ensureNonEmptyString(key, 'auth.requiredEnv entries must be non-empty strings');
      }
    }
  }

  if (parsed.safety !== undefined) {
    if (!parsed.safety || typeof parsed.safety !== 'object' || Array.isArray(parsed.safety)) {
      throw new Error('safety must be an object');
    }
    if (parsed.safety.rollbackOnFailure !== undefined && typeof parsed.safety.rollbackOnFailure !== 'boolean') {
      throw new Error('safety.rollbackOnFailure must be boolean');
    }
    if (parsed.safety.lockPath !== undefined) {
      ensureNonEmptyString(parsed.safety.lockPath, 'safety.lockPath must be non-empty string');
    }
  }

  if (parsed.sessionController !== undefined) {
    if (!parsed.sessionController || typeof parsed.sessionController !== 'object' || Array.isArray(parsed.sessionController)) {
      throw new Error('sessionController must be an object');
    }
  }

  return parsed;
}

function resolveConfigPath(configPath) {
  if (configPath) return configPath;
  if (process.env[CONFIG_ENV]) return process.env[CONFIG_ENV];
  return path.join(path.resolve(__dirname, '..'), 'router.config.json');
}

function loadConfig(configPath) {
  const resolved = resolveConfigPath(configPath);
  const stat = fs.statSync(resolved);
  if (cachedConfig && cachedPath === resolved && cachedMtimeMs === stat.mtimeMs) {
    return cachedConfig;
  }
  const raw = fs.readFileSync(resolved, 'utf8');
  const parsed = JSON.parse(raw);
  const validated = validateConfig(parsed);
  cachedConfig = validated;
  cachedMtimeMs = stat.mtimeMs;
  cachedPath = resolved;
  return validated;
}

function parsePrefix(input = '') {
  const trimmed = input.trim();
  if (!trimmed.startsWith('@')) {
    return { prefix: null, body: input };
  }

  const [headRaw, ...rest] = trimmed.split(/\s+/);
  const head = headRaw.replace(/[:：，,.;。!?！？]+$/, '');
  return {
    prefix: head.toLowerCase(),
    body: rest.join(' ').trim(),
  };
}

function resolveRoute(prefix, config) {
  if (!prefix) {
    return null;
  }
  const aliasTarget = config.aliasMap && config.aliasMap[prefix];
  const key = aliasTarget || prefix;
  const route = config.prefixMap[key];
  if (!route) {
    throw new InvalidPrefixError(prefix);
  }
  return { ...route, _resolvedPrefix: key };
}

module.exports = {
  loadConfig,
  parsePrefix,
  resolveRoute,
  validateConfig,
};
