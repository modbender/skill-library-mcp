#!/usr/bin/env node
/**
 * hook-pipeline.js — Claude Code Stop hook for openclaw-reflect.
 *
 * Runs at session end: classify → propose → evaluate → apply --auto
 * Uses a fixed workspace path so it works regardless of Claude Code's cwd.
 *
 * Only runs the pipeline if there are outcomes to process.
 * All steps are best-effort — failures are logged but don't block Claude Code.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// Derive paths from script location: scripts/ → openclaw-reflect/ → skills/ → workspace/
const WORKSPACE_DIR = path.join(__dirname, '..', '..', '..');
const SKILLS_DIR = __dirname;
const REFLECT_DIR = path.join(WORKSPACE_DIR, '.reflect');
const OUTCOMES_FILE = path.join(REFLECT_DIR, 'outcomes.jsonl');
const LOG_FILE = path.join(REFLECT_DIR, 'pipeline.log');
const NODE = process.execPath;

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  try { fs.appendFileSync(LOG_FILE, line + '\n', 'utf8'); } catch {}
  process.stderr.write(line + '\n');
}

function run(script, args = []) {
  const scriptPath = path.join(SKILLS_DIR, script);
  try {
    const out = execFileSync(NODE, [scriptPath, ...args], {
      cwd: WORKSPACE_DIR,
      timeout: 30000,
      encoding: 'utf8',
    });
    log(`${script}: ${(out || '').trim() || 'ok'}`);
    return true;
  } catch (e) {
    log(`${script} FAILED: ${e.message.slice(0, 200)}`);
    return false;
  }
}

function main() {
  // Read stdin (Stop hook sends JSON but we don't need it)
  let raw = '';
  process.stdin.on('data', chunk => raw += chunk);
  process.stdin.on('end', () => {
    // Only run if there's data to process
    if (!fs.existsSync(OUTCOMES_FILE)) {
      process.exit(0);
      return;
    }

    const lines = fs.readFileSync(OUTCOMES_FILE, 'utf8').trim().split('\n').filter(Boolean);
    if (lines.length === 0) {
      process.exit(0);
      return;
    }

    log(`pipeline starting — ${lines.length} outcome(s) in log`);

    run('classify.js');
    run('propose.js');
    run('evaluate.js');
    run('apply.js', ['--auto']);

    log('pipeline complete');
    process.exit(0);
  });
}

main();
