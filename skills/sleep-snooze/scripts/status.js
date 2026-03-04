#!/usr/bin/env node
/**
 * status.js
 * Returns current sleep mode status and queue size for /snooze-status command.
 *
 * Outputs JSON to stdout for OpenClaw to read and format for the user.
 */

const fs   = require('fs');
const path = require('path');

const DATA_DIR   = path.join(process.env.HOME, '.openclaw', 'skills', 'sleep-snooze', 'data');
const STATE_FILE = path.join(DATA_DIR, 'state.json');
const DB_FILE    = path.join(DATA_DIR, 'queue.db');

try {
  const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));

  let queueCount = 0;
  try {
    const Database = require('better-sqlite3');
    const db = new Database(DB_FILE);
    queueCount = db.prepare(`SELECT COUNT(*) as c FROM queue WHERE delivered = 0`).get().c;
    db.close();
  } catch { /* DB not set up yet */ }

  console.log(JSON.stringify({
    isSleeping:    state.isSleeping,
    sleepStart:    state.sleepStart,
    wakeTime:      state.wakeTime,
    timezone:      state.timezone,
    manualOverride: state.manualOverride,
    queuedMessages: queueCount,
    lastDigestAt:  state.lastDigestAt,
  }));

  process.exit(0);
} catch (err) {
  console.log(JSON.stringify({ error: 'Sleep Snooze not configured. Run /snooze-setup to get started.' }));
  process.exit(1);
}
