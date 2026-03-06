/**
 * Event Worker (worker_once)
 * - Consumes resources/events.json
 * - Executes trades via TradeExecutor (OrderService + RiskManager + PositionsRepo)
 * - Marks events processed with result payload
 *
 * Important:
 * - Do NOT rely on process.cwd() (OpenClaw cron may run with different CWD)
 * - Use scripts/state/resources.js for stable paths
 */

const fs = require('fs').promises;
const { loadConfig } = require('../config');
const { UpbitClient, Logger } = require('../execution/upbitClient');
const OrderService = require('../execution/orderService');
const TradeExecutor = require('../execution/tradeExecutor');
const { ensureResources, getResourcePaths } = require('../state/resources');
const { acquireLock, releaseLock } = require('../state/lock');

const cfg = loadConfig();
const ACCESS_KEY = cfg.upbit.accessKey;
const SECRET_KEY = cfg.upbit.secretKey;

const PATHS = getResourcePaths();
const EVENTS_FILE = PATHS.eventsFile;
const WORKER_LOCK_FILE = PATHS.workerLockFile;

const LOCK_TTL_MS = cfg.trading?.workerLockTtlMs || 120000;

async function readEvents() {
  await ensureResources();
  try {
    const raw = await fs.readFile(EVENTS_FILE, 'utf8');
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

async function writeEvents(events) {
  await ensureResources();
  await fs.writeFile(EVENTS_FILE, JSON.stringify(events, null, 2), 'utf8');
}

function shouldProcess(e) {
  if (!e || e.processed) return false;
  // Guard: avoid re-trying forever on broken events
  const attempts = Number(e.attempts || 0);
  const maxAttempts = cfg.execution?.maxEventAttempts ?? 5;
  return attempts < maxAttempts;
}

async function workerOnce() {
  const _paths = await ensureResources();
  Logger.info(`[paths] projectRoot=${_paths.dir.replace(/\\resources$/, '')} resourcesDir=${_paths.dir}`);

  const lock = await acquireLock(WORKER_LOCK_FILE, LOCK_TTL_MS, { kind: 'worker' });
  if (!lock.ok) {
    Logger.warn(`LOCKED worker (ageMs=${lock.ageMs}) - skip`);
    return;
  }

  const started = Date.now();
  try {
    const events = await readEvents();
    const pending = events.filter(shouldProcess);
    Logger.info(`[worker] pending=${pending.length}`);

    if (pending.length === 0) {
      Logger.info('SUMMARY worker pending=0 processed=0 skipped=0 errors=0');
      return;
    }

    const client = new UpbitClient(ACCESS_KEY, SECRET_KEY);
    const orderService = new OrderService(client);
    const cooldownMin = Number(cfg.trading?.aggressive?.reentryCooldownMinutes || 0);
    const cooldownMs = cooldownMin > 0 ? cooldownMin * 60000 : 0;
    const executor = new TradeExecutor(orderService, { dryRun: !!cfg.execution?.dryRun, reentryCooldownMs: cooldownMs });

    let processed = 0;
    let skipped = 0;
    let errors = 0;

    // Event priority: ensure urgent exits fire before other actions.
    const priority = {
      STOPLOSS_HIT: 0,
      SELL_PRESSURE_HIT: 1,
      TRAILING_STOP_HIT: 2,
      TARGET_HIT: 3,
      TAKEPROFIT_HARD: 3,
      BUY_SIGNAL: 10,
    };

    // Process by priority, then chronological order (createdAt)
    pending.sort((a, b) => {
      const pa = priority[a.type] ?? 5;
      const pb = priority[b.type] ?? 5;
      if (pa !== pb) return pa - pb;
      return new Date(a.createdAt || 0).getTime() - new Date(b.createdAt || 0).getTime();
    });

    for (const e of pending) {
      e.attempts = Number(e.attempts || 0) + 1;
      e.lastAttemptAt = new Date().toISOString();

      try {
        const res = await executor.execute(e);
        e.processed = true;
        e.processedAt = new Date().toISOString();
        e.result = res;
        processed += 1;
      } catch (ex) {
        e.lastError = String(ex?.message || ex);
        Logger.error(`[worker] ERROR id=${e.id} type=${e.type} market=${e.market} msg=${e.lastError}`);
        errors += 1;
        // Keep unprocessed so it can retry (up to maxEventAttempts)
      }
    }

    // mark events array back
    await writeEvents(events);

    const dur = Date.now() - started;
    Logger.info(`[worker] processed=${processed} skipped=${skipped} errors=${errors} durationMs=${dur}`);
    Logger.info(`SUMMARY worker pending=${pending.length} processed=${processed} skipped=${skipped} errors=${errors} durationMs=${dur}`);
  } finally {
    await releaseLock(WORKER_LOCK_FILE);
  }
}

function workerLoop() {
  const interval = cfg.execution?.eventPollIntervalMs ?? 5000;
  (async function loop() {
    await workerOnce();
    setTimeout(loop, interval);
  })();
}

module.exports = { workerOnce, workerLoop };

if (require.main === module) {
  workerOnce().catch(e => {
    Logger.error(`Worker Fatal: ${e?.stack || e}`);
    process.exit(1);
  });
}
