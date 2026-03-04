const fs = require('fs');
const path = require('path');

function readJson(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(raw);
}

function assertString(name, v) {
  if (typeof v !== 'string' || v.trim().length === 0) {
    throw new Error(`Invalid config: ${name} must be a non-empty string`);
  }
}

function assertNumber(name, v) {
  if (typeof v !== 'number' || Number.isNaN(v)) {
    throw new Error(`Invalid config: ${name} must be a number`);
  }
}

function assertArray(name, v) {
  if (!Array.isArray(v)) {
    throw new Error(`Invalid config: ${name} must be an array`);
  }
}

function assertBoolean(name, v) {
  if (typeof v !== 'boolean') {
    throw new Error(`Invalid config: ${name} must be a boolean`);
  }
}

function parseWatchlistEnv(v) {
  if (!v || typeof v !== 'string') return null;
  const list = v.split(',').map(s => s.trim()).filter(Boolean);
  return list.length ? list : null;
}

/**
 * loadConfig
 *
 * ClawHub/OpenClaw friendly:
 * - Secrets should NOT be stored in config.json.
 * - Reads Upbit keys from environment variables first:
 *   UPBIT_OPEN_API_ACCESS_KEY / UPBIT_OPEN_API_SECRET_KEY
 * - config.json is optional; if missing, we fall back to config.example.json for defaults.
 */
function loadConfig() {
  const projectRoot = path.resolve(__dirname, '..', '..');
  const cfgPath = path.join(projectRoot, 'config.json');
  const examplePath = path.join(projectRoot, 'config.example.json');

  /** base config without secrets */
  let cfg = {};
  if (fs.existsSync(cfgPath)) {
    cfg = readJson(cfgPath);
  } else if (fs.existsSync(examplePath)) {
    cfg = readJson(examplePath);
  }

  cfg.upbit = cfg.upbit || {};
  cfg.trading = cfg.trading || {};
  cfg.execution = cfg.execution || {};
  cfg.logging = cfg.logging || {};
  cfg.aggressive = cfg.aggressive || {};

  // ---- Secrets (ENV first) ----
  const envAccessKey = process.env.UPBIT_OPEN_API_ACCESS_KEY || process.env.UPBIT_ACCESS_KEY;
  const envSecretKey = process.env.UPBIT_OPEN_API_SECRET_KEY || process.env.UPBIT_SECRET_KEY;

  if (envAccessKey) cfg.upbit.accessKey = envAccessKey;
  if (envSecretKey) cfg.upbit.secretKey = envSecretKey;

  // If still missing, give a very explicit error message (ClawHub warning mitigation)
  if (!cfg?.upbit?.accessKey || !cfg?.upbit?.secretKey) {
    const hint = `Missing Upbit API credentials. Set environment variables:
  - UPBIT_OPEN_API_ACCESS_KEY
  - UPBIT_OPEN_API_SECRET_KEY
(Recommended: store secrets in OpenClaw Skills Config / secret store, not in config.json.)`;
    throw new Error(hint);
  }

  assertString('upbit.accessKey', cfg.upbit.accessKey);
  assertString('upbit.secretKey', cfg.upbit.secretKey);

  // ---- Defaults / non-secret settings ----
  // WATCHLIST env overrides config
  const wlEnv = parseWatchlistEnv(process.env.WATCHLIST);
  cfg.trading.watchlist = wlEnv || cfg.trading.watchlist || ['KRW-BTC', 'KRW-ETH', 'KRW-SOL'];
  assertArray('trading.watchlist', cfg.trading.watchlist);

  cfg.trading.scanIntervalMs = cfg.trading.scanIntervalMs ?? 300000;
  cfg.trading.priceCheckIntervalMs = cfg.trading.priceCheckIntervalMs ?? 10000;
  assertNumber('trading.scanIntervalMs', cfg.trading.scanIntervalMs);
  assertNumber('trading.priceCheckIntervalMs', cfg.trading.priceCheckIntervalMs);

  cfg.trading.targetProfit = cfg.trading.targetProfit ?? 0.05;
  cfg.trading.stopLoss = cfg.trading.stopLoss ?? -0.05;
  assertNumber('trading.targetProfit', cfg.trading.targetProfit);
  assertNumber('trading.stopLoss', cfg.trading.stopLoss);

  cfg.trading.budgetKRW = cfg.trading.budgetKRW ?? 10000;
  assertNumber('trading.budgetKRW', cfg.trading.budgetKRW);

  cfg.trading.maxPositions = cfg.trading.maxPositions ?? 3;
  assertNumber('trading.maxPositions', cfg.trading.maxPositions);

  cfg.trading.k = cfg.trading.k ?? 0.5;
  assertNumber('trading.k', cfg.trading.k);

  cfg.execution.dryRun = cfg.execution.dryRun ?? true;
  assertBoolean('execution.dryRun', cfg.execution.dryRun);

  cfg.execution.minOrderKrw = cfg.execution.minOrderKrw ?? 5000;
  assertNumber('execution.minOrderKrw', cfg.execution.minOrderKrw);

  cfg.execution.slippageBps = cfg.execution.slippageBps ?? 30;
  assertNumber('execution.slippageBps', cfg.execution.slippageBps);

  cfg.execution.maxRetries = cfg.execution.maxRetries ?? 3;
  assertNumber('execution.maxRetries', cfg.execution.maxRetries);

  cfg.logging.verbose = cfg.logging.verbose ?? true;
  assertBoolean('logging.verbose', cfg.logging.verbose);

  // Aggressive strategy / pressure options (defaults are safe)
  cfg.aggressive.enabled = cfg.aggressive.enabled ?? false;
  assertBoolean('aggressive.enabled', cfg.aggressive.enabled);

  cfg.aggressive.reentryCooldownMinutes = cfg.aggressive.reentryCooldownMinutes ?? 30;
  assertNumber('aggressive.reentryCooldownMinutes', cfg.aggressive.reentryCooldownMinutes);

  cfg.aggressive.pressure = cfg.aggressive.pressure || {};
  cfg.aggressive.pressure.enabled = cfg.aggressive.pressure.enabled ?? true;
  assertBoolean('aggressive.pressure.enabled', cfg.aggressive.pressure.enabled);

  cfg.aggressive.pressure.candleUnitMinutes = cfg.aggressive.pressure.candleUnitMinutes ?? 5;
  cfg.aggressive.pressure.candles = cfg.aggressive.pressure.candles ?? 5;
  cfg.aggressive.pressure.buyMin = cfg.aggressive.pressure.buyMin ?? 2;
  cfg.aggressive.pressure.sellMin = cfg.aggressive.pressure.sellMin ?? 3;

  assertNumber('aggressive.pressure.candleUnitMinutes', cfg.aggressive.pressure.candleUnitMinutes);
  assertNumber('aggressive.pressure.candles', cfg.aggressive.pressure.candles);
  assertNumber('aggressive.pressure.buyMin', cfg.aggressive.pressure.buyMin);
  assertNumber('aggressive.pressure.sellMin', cfg.aggressive.pressure.sellMin);

  cfg.aggressive.pressure.entryMode = cfg.aggressive.pressure.entryMode || 'filter';
  cfg.aggressive.pressure.requireOneHourBull = cfg.aggressive.pressure.requireOneHourBull ?? true;
  assertBoolean('aggressive.pressure.requireOneHourBull', cfg.aggressive.pressure.requireOneHourBull);

  cfg.aggressive.pressure.sellReduceRatio = cfg.aggressive.pressure.sellReduceRatio ?? 0.5;
  cfg.aggressive.pressure.sellReduceMinKrw = cfg.aggressive.pressure.sellReduceMinKrw ?? 5000;
  assertNumber('aggressive.pressure.sellReduceRatio', cfg.aggressive.pressure.sellReduceRatio);
  assertNumber('aggressive.pressure.sellReduceMinKrw', cfg.aggressive.pressure.sellReduceMinKrw);

  // Event dedupe (default TTLs)
  cfg.eventDedupe = cfg.eventDedupe || {};
  cfg.eventDedupe.ttlMs = cfg.eventDedupe.ttlMs ?? 3600000;
  assertNumber('eventDedupe.ttlMs', cfg.eventDedupe.ttlMs);

  cfg.eventDedupe.byType = cfg.eventDedupe.byType || {};
  cfg.eventDedupe.byType.STOPLOSS_HIT = cfg.eventDedupe.byType.STOPLOSS_HIT ?? 300000; // 5m
  cfg.eventDedupe.byType.SELL_PRESSURE_HIT = cfg.eventDedupe.byType.SELL_PRESSURE_HIT ?? 300000;

  // Everything else can remain as-is in the JSON files (we don't hard-fail unknown fields).
  return cfg;
}

module.exports = { loadConfig };
