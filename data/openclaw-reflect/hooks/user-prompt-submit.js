#!/usr/bin/env node
/**
 * user-prompt-submit.js — UserPromptSubmit hook for openclaw-reflect.
 * Injects a brief notice if there are pending proposals awaiting operator review,
 * or if applied learnings are active and should be surfaced.
 * Output goes to stdout and is injected into the agent context.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const REFLECT_DIR = path.join(process.cwd(), '.reflect');
const PENDING_FILE = path.join(REFLECT_DIR, 'pending.json');
const APPLIED_FILE = path.join(REFLECT_DIR, 'applied.jsonl');

function countPending() {
  try {
    const data = JSON.parse(fs.readFileSync(PENDING_FILE, 'utf8'));
    return Array.isArray(data) ? data.length : 0;
  } catch {
    return 0;
  }
}

function recentApplied(withinHours = 24) {
  try {
    const lines = fs.readFileSync(APPLIED_FILE, 'utf8').trim().split('\n').filter(Boolean);
    const cutoff = Date.now() - withinHours * 3600 * 1000;
    return lines
      .map(l => { try { return JSON.parse(l); } catch { return null; } })
      .filter(e => e && new Date(e.ts).getTime() > cutoff);
  } catch {
    return [];
  }
}

function main() {
  if (!fs.existsSync(REFLECT_DIR)) return;

  const pendingCount = countPending();
  const recent = recentApplied(24);
  const lines = [];

  if (pendingCount > 0) {
    lines.push(
      `[reflect] ${pendingCount} improvement proposal${pendingCount > 1 ? 's' : ''} ` +
      `awaiting your approval. Run: node .reflect/scripts/status.js --pending`
    );
  }

  if (recent.length > 0) {
    lines.push(
      `[reflect] ${recent.length} learning${recent.length > 1 ? 's' : ''} applied in the ` +
      `last 24h. Run: node .reflect/scripts/status.js --history`
    );
  }

  if (lines.length > 0) {
    // Output as a system note — will be injected into context
    console.log('\n' + lines.join('\n') + '\n');
  }
}

main();
