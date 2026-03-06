#!/usr/bin/env node
/**
 * session-end.js — SessionEnd hook for openclaw-reflect.
 * Runs classify → propose → evaluate → apply/queue pipeline.
 * This is the core of the self-improvement loop.
 */
'use strict';

const { execFileSync, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const SCRIPTS_DIR = path.join(__dirname, '..', 'scripts');
const REFLECT_DIR = path.join(process.cwd(), '.reflect');

// Copy scripts to .reflect/scripts so they run from workspace context
function ensureScripts() {
  const dest = path.join(REFLECT_DIR, 'scripts');
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });

  const scripts = ['observe.js', 'classify.js', 'propose.js', 'evaluate.js',
                   'apply.js', 'rollback.js', 'status.js'];
  for (const s of scripts) {
    const src = path.join(SCRIPTS_DIR, s);
    const dst = path.join(dest, s);
    if (fs.existsSync(src) && !fs.existsSync(dst)) {
      fs.copyFileSync(src, dst);
    }
  }
}

function run(script, args = []) {
  const scriptPath = path.join(SCRIPTS_DIR, script);
  try {
    const output = execFileSync(process.execPath, [scriptPath, ...args], {
      cwd: process.cwd(),
      timeout: 30000,
      encoding: 'utf8',
    });
    return { ok: true, output: output.trim() };
  } catch (e) {
    return { ok: false, output: e.message };
  }
}

function main() {
  if (!fs.existsSync(REFLECT_DIR)) {
    fs.mkdirSync(REFLECT_DIR, { recursive: true });
  }

  ensureScripts();

  console.log('[reflect] Session end — running improvement pipeline...');

  // Step 1: Classify outcomes into patterns
  const classify = run('classify.js');
  if (!classify.ok) {
    console.log('[reflect] classify: ' + classify.output);
    return;
  }
  console.log('[reflect] classify: ' + (classify.output || 'no new patterns'));

  // Step 2: Generate proposals from qualifying patterns
  const propose = run('propose.js');
  if (!propose.ok) {
    console.log('[reflect] propose: ' + propose.output);
    return;
  }
  console.log('[reflect] propose: ' + (propose.output || 'no proposals generated'));

  // Step 3: Evaluate proposals (separate evaluator invocation)
  const evaluate = run('evaluate.js');
  if (!evaluate.ok) {
    console.log('[reflect] evaluate: ' + evaluate.output);
    // Don't exit — unevaluated proposals queue for next session
  } else {
    console.log('[reflect] evaluate: ' + (evaluate.output || 'done'));
  }

  // Step 4: Apply approved proposals (auto-apply Tier 1-2, queue Tier 3)
  const apply = run('apply.js', ['--auto']);
  console.log('[reflect] apply: ' + (apply.output || 'nothing to apply'));

  // Summary
  const status = run('status.js', ['--brief']);
  if (status.ok && status.output) {
    console.log('[reflect] ' + status.output);
  }
}

main();
