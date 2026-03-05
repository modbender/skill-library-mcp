#!/usr/bin/env node
/**
 * OpenClaw entrypoint (skill.js)
 *
 * Commands:
 *   node skill.js monitor_once
 *   node skill.js monitor_loop
 *   node skill.js worker_once
 *   node skill.js worker_loop
 *   node skill.js smoke_test
 *
 * Config:
 *   - secrets via env (recommended): UPBIT_OPEN_API_ACCESS_KEY / UPBIT_OPEN_API_SECRET_KEY
 *   - config.json is optional; non-secret defaults can come from config.example.json
 */

const { Logger } = require('./scripts/execution/upbitClient');
const { loadConfig } = require('./scripts/config');
const { ensureResources } = require('./scripts/state/resources');
const { securityCheck } = require('./scripts/security/securityCheck');

function printHelp() {
  console.log(`Usage: node skill.js <command>

Commands:
  monitor_once   Run market scan + position check once (recommended for cron)
  monitor_loop   Run monitor loop (local/dev)
  worker_once    Process events once (recommended for cron)
  worker_loop    Run worker loop (local/dev)
  smoke_test     Validate config + hit public endpoints (no trading)

Files:
  config.json          required (do not commit)
  config.example.json  template

Examples:
  node skill.js smoke_test
  node skill.js monitor_once
  node skill.js worker_once
`);
}

async function smokeTest() {
  const cfg = loadConfig();
  const marketData = require('./scripts/data/marketData');

  Logger.info(`[smoke_test] watchlist=${cfg.trading.watchlist.join(',')}`);
  const tickers = await marketData.getTickers(cfg.trading.watchlist);
  for (const t of tickers) {
    Logger.info(`[ticker] ${t.market} ${t.trade_price}`);
  }
  Logger.info('[smoke_test] OK');
}

async function main() {
  const cmd = process.argv[2];

  if (cmd === 'security_check') {
    const result = securityCheck();
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.ok ? 0 : 2);
  }
  if (!cmd || cmd === '-h' || cmd === '--help') {
    printHelp();
    process.exit(0);
  }

  try {
    // Validate config early
    loadConfig();

    // Ensure local state stores exist (resources/events.json, resources/positions.json)
    await ensureResources();

    if (cmd === 'monitor_once') {
      const { monitorOnce } = require('./scripts/workers/monitor');
      await monitorOnce();
      return;
    }
    if (cmd === 'monitor_loop') {
      const { monitorLoop } = require('./scripts/workers/monitor');
      monitorLoop();
      return;
    }
    if (cmd === 'worker_once') {
      const { workerOnce } = require('./scripts/workers/eventWorker');
      await workerOnce();
      return;
    }
    if (cmd === 'worker_loop') {
      const { workerLoop } = require('./scripts/workers/eventWorker');
      workerLoop();
      return;
    }
    if (cmd === 'smoke_test') {
      await smokeTest();
      return;
    }

    Logger.error(`Unknown command: ${cmd}`);
    printHelp();
    process.exit(1);
  } catch (err) {
    Logger.error(err?.stack || err?.message || String(err));
    process.exit(1);
  }
}

main();
