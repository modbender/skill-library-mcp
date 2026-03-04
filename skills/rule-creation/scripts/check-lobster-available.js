#!/usr/bin/env node
/**
 * check-lobster-available.js
 *
 * Preflight check: is the Lobster workflow plugin enabled in this OpenClaw instance?
 *
 * Runs `openclaw plugins list` and inspects the Lobster row.
 * Returns a stable JSON result so callers can make wiring decisions without
 * crashing on unavailable tooling.
 *
 * Output (stdout JSON):
 *   {
 *     available: boolean,   // true only when status is "loaded"
 *     reason:   string      // human-readable explanation
 *   }
 */

'use strict';

const { execSync } = require('child_process');

let available = false;
let reason = '';

try {
  // 2>/dev/null suppresses plugin-load noise; timeout keeps it snappy
  const raw = execSync('openclaw plugins list 2>/dev/null', {
    encoding: 'utf8',
    timeout: 10_000
  });

  if (/lobster[^\n]*loaded/i.test(raw)) {
    available = true;
    reason = 'Lobster plugin is loaded and available.';
  } else if (/lobster[^\n]*disabled/i.test(raw)) {
    available = false;
    reason =
      'Lobster plugin is installed but disabled. ' +
      'Enable it with: openclaw plugins enable lobster';
  } else if (/lobster/i.test(raw)) {
    available = false;
    reason = 'Lobster plugin found but status is unrecognised.';
  } else {
    available = false;
    reason = 'Lobster plugin not found in `openclaw plugins list` output.';
  }
} catch (err) {
  available = false;
  reason = `Could not run \`openclaw plugins list\`: ${err.message}`;
}

process.stdout.write(JSON.stringify({ available, reason }, null, 2) + '\n');
process.exit(0);
