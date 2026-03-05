#!/usr/bin/env node
/**
 * set-sleep-mode.js
 * Toggle sleep mode on/off. Called by cron at sleep-start and wake-time,
 * and also when the user runs /sleep or /wake manually.
 *
 * Usage:
 *   node set-sleep-mode.js --mode sleep
 *   node set-sleep-mode.js --mode wake
 */

const fs   = require('fs');
const path = require('path');

const DATA_DIR  = path.join(process.env.HOME, '.openclaw', 'skills', 'sleep-snooze', 'data');
const STATE_FILE = path.join(DATA_DIR, 'state.json');

const args = process.argv.slice(2);
const mode = args[args.indexOf('--mode') + 1];

if (!['sleep', 'wake'].includes(mode)) {
  console.error('Usage: node set-sleep-mode.js --mode <sleep|wake>');
  process.exit(1);
}

try {
  const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  state.isSleeping      = mode === 'sleep';
  state.manualOverride  = false;
  if (mode === 'wake') state.lastDigestAt = new Date().toISOString();
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  console.log(`Sleep mode: ${mode === 'sleep' ? '🌙 activated' : '☀️  deactivated'}`);
} catch (err) {
  console.error('Could not update state:', err.message);
  process.exit(1);
}
