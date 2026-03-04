#!/usr/bin/env node
/**
 * mark_done.js - Mark a quickstart task as completed
 *
 * Called by the AI immediately after the user completes a task action.
 *
 * Usage:
 *   node mark_done.js --task <1-8> [--workspace /path/to/workspace]
 *
 * Output: prints updated progress summary as JSON
 */

const fs = require('fs');
const path = require('path');

// Parse args
const args = process.argv.slice(2);
function getArg(name) {
  const idx = args.indexOf(name);
  return idx !== -1 ? args[idx + 1] : null;
}

const taskId = parseInt(getArg('--task'), 10);
const workspace = getArg('--workspace') || path.join(process.env.HOME, '.openclaw', 'workspace');

if (!taskId || taskId < 1 || taskId > 8) {
  console.error('Usage: node mark_done.js --task <1-8> [--workspace /path]');
  process.exit(1);
}

const progressFile = path.join(workspace, '.quickstart-progress.json');

// Load existing progress
let progress = {};
try {
  if (fs.existsSync(progressFile)) {
    progress = JSON.parse(fs.readFileSync(progressFile, 'utf8'));
  }
} catch {}

// Mark task as done
progress[`task${taskId}`] = {
  done: true,
  completedAt: new Date().toISOString(),
};

// Save
fs.writeFileSync(progressFile, JSON.stringify(progress, null, 2), 'utf8');

const completedCount = Object.values(progress).filter(v => v.done).length;
const total = 8;
const allDone = completedCount === total;

console.log(JSON.stringify({
  marked: taskId,
  completed: completedCount,
  total,
  all_done: allDone,
  progress,
}, null, 2));

if (allDone) {
  console.error('\n🎓 All tasks complete! Run cleanup_crons.js to remove reminders.');
}
