#!/usr/bin/env node
/**
 * cleanup_crons.js - Remove all quickstart-related cron jobs
 *
 * Called automatically when all 8 tasks are completed.
 * Looks up crons by name and removes them by id.
 * Targets: quickstart-reminder, quickstart-heartbeat
 *
 * Usage:
 *   node cleanup_crons.js
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const TARGET_NAMES = new Set(['quickstart-reminder', 'quickstart-heartbeat']);

// ── Clean up HEARTBEAT.md ─────────────────────────────────────────────────────
const args = process.argv.slice(2);
const wsIdx = args.indexOf('--workspace');
const workspace = wsIdx !== -1 ? args[wsIdx + 1] : path.join(process.env.HOME, '.openclaw', 'workspace');
const heartbeatFile = path.join(workspace, 'HEARTBEAT.md');

console.log('🧹 Cleaning up HEARTBEAT.md...');
try {
  let content = fs.readFileSync(heartbeatFile, 'utf8');
  // Remove the quickstart block between markers
  const startMarker = '## OpenClaw Quickstart Progress Check';
  const endMarker = '## End OpenClaw Quickstart';
  const startIdx = content.indexOf(startMarker);
  const endIdx = content.indexOf(endMarker);
  if (startIdx !== -1 && endIdx !== -1) {
    // Remove from the blank line before start marker to end of end marker line
    const before = content.slice(0, startIdx).trimEnd();
    const after = content.slice(endIdx + endMarker.length).replace(/^\n/, '');
    content = before + (after ? '\n' + after : '\n');
    fs.writeFileSync(heartbeatFile, content, 'utf8');
    console.log('  ✅ Quickstart block removed from HEARTBEAT.md');
  } else {
    console.log('  ℹ️  Quickstart block not found in HEARTBEAT.md (already removed)');
  }
} catch (e) {
  console.warn(`  ⚠️  Could not update HEARTBEAT.md: ${e.message}`);
}

function openclaw(...args) {
  const result = spawnSync('openclaw', args, { encoding: 'utf8' });
  if (result.error?.code === 'ENOENT') {
    console.error("⚠️  'openclaw' CLI not found in PATH.");
    process.exit(1);
  }
  // stdout may have decorative warning boxes before the JSON — find last { that parses
  const raw = result.stdout || '';
  // Try to find the JSON object by scanning for lines starting with '{'
  const lines = raw.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trimStart().startsWith('{')) {
      try { return JSON.parse(lines.slice(i).join('\n')); } catch {}
    }
  }
  return null;
}

// Step 1: list all crons
console.log('Fetching cron list...');
const list = openclaw('cron', 'list', '--json');
if (!list || !Array.isArray(list.jobs)) {
  console.error('⚠️  Could not retrieve cron list.');
  process.exit(1);
}

// Step 2: find matching crons by name
const toRemove = list.jobs.filter(j => TARGET_NAMES.has(j.name));

if (toRemove.length === 0) {
  console.log('ℹ️  No quickstart crons found (already removed or never created).');
  console.log('🎓 Congratulations on completing all OpenClaw onboarding tasks!');
  process.exit(0);
}

// Step 3: remove each by id
let allOk = true;
for (const job of toRemove) {
  console.log(`Removing "${job.name}" (${job.id})...`);
  const res = openclaw('cron', 'rm', job.id, '--json');
  if (res?.ok || res?.removed) {
    console.log(`  ✅ Removed`);
  } else {
    console.warn(`  ⚠️  Unexpected response:`, JSON.stringify(res));
    allOk = false;
  }
}

if (allOk) {
  console.log('\n✅ All quickstart crons removed. No more reminders!');
  console.log('🎓 Congratulations on completing all OpenClaw onboarding tasks!');
} else {
  console.log('\n⚠️  Some crons may not have been removed. Check: openclaw cron list');
}
