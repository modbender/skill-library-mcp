#!/usr/bin/env node
/**
 * setup_reminder_cron.js - Set up quickstart cron jobs via OpenClaw CLI
 *
 * Creates two cron jobs:
 *   1. quickstart-heartbeat  — every 30 min: scan progress, auto-mark done, cleanup if all done
 *   2. quickstart-reminder   — daily at 9 AM: remind user of pending tasks
 *
 * Usage:
 *   node setup_reminder_cron.js [--hour 9] [--minute 0]
 */

const { spawnSync } = require('child_process');
const path = require('path');

// Parse args
const args = process.argv.slice(2);
function getArg(name, def) {
  const idx = args.indexOf(name);
  return idx !== -1 ? parseInt(args[idx + 1], 10) : def;
}
const hour   = getArg('--hour', 9);
const minute = getArg('--minute', 0);

// Resolve scripts dir (same folder as this file)
const scriptsDir = path.resolve(__dirname);

// ── Cron definitions ──────────────────────────────────────────────────────────
const CRONS = [
  {
    name:     'quickstart-heartbeat',
    schedule: '*/30 * * * *',   // every 30 minutes
    task: [
      `Run: node ${scriptsDir}/check_progress.js --mark-done`,
      'Parse the JSON output.',
      'If all_done is true: run cleanup_crons.js, then send the user a 🎓 graduation congratulations message.',
      'If newly_completed has entries: send a brief "✅ TaskN marked complete!" notification.',
      'Otherwise: do nothing (stay silent).',
    ].join(' '),
  },
  {
    name:     'quickstart-reminder',
    schedule: `${minute} ${hour} * * *`,   // daily at specified time
    task: [
      `Run: node ${scriptsDir}/check_progress.js`,
      'Parse the JSON output.',
      'If all_done is true: run cleanup_crons.js, send 🎓 graduation message, stop.',
      'Otherwise: send the user a friendly reminder listing completed (✅) and pending (⬜) tasks,',
      'highlight the next_task, and encourage them to complete it today.',
    ].join(' '),
  },
];

// ── Register crons ────────────────────────────────────────────────────────────
let allOk = true;

for (const cron of CRONS) {
  console.log(`\nSetting up cron "${cron.name}" [${cron.schedule}]...`);
  const cmd    = ['openclaw', 'cron', 'add', '--name', cron.name, '--cron', cron.schedule, '--message', cron.task];
  const result = spawnSync(cmd[0], cmd.slice(1), { encoding: 'utf8' });

  if (result.error?.code === 'ENOENT') {
    console.error(`  ⚠️  'openclaw' CLI not found in PATH.`);
    allOk = false;
  } else if (result.status === 0) {
    console.log(`  ✅ Created "${cron.name}"`);
    if (result.stdout) console.log(' ', result.stdout.trim());
  } else {
    console.warn(`  ⚠️  Exit code ${result.status}`);
    if (result.stdout) console.log('  stdout:', result.stdout.trim());
    if (result.stderr) console.error('  stderr:', result.stderr.trim());
    allOk = false;
  }
}

console.log('\n' + (allOk
  ? `✅ All crons registered!\n   Heartbeat: every 30 min (auto-detect & mark done)\n   Reminder:  daily at ${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')} (push notification)`
  : `⚠️  Some crons failed. Add them manually via: openclaw cron add ...`
));
