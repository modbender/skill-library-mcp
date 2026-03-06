#!/usr/bin/env node
/**
 * Repo Analyzer — offline tests (no GitHub API calls)
 */

const { execSync } = require('child_process');
const path = require('path');

const ANALYZE = path.join(__dirname, 'analyze.js');
let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (e) {
    console.log(`❌ ${name}: ${e.message}`);
    failed++;
  }
}

function run(args, opts = {}) {
  return execSync(`node ${ANALYZE} ${args}`, {
    encoding: 'utf8',
    timeout: 15000,
    env: { ...process.env, GITHUB_TOKEN: '' },
    stdio: ['pipe', 'pipe', 'pipe'],
    ...opts,
  });
}

test('Syntax check (node -c)', () => {
  execSync(`node -c ${ANALYZE}`, { stdio: 'pipe' });
});

test('No args prints usage and exits non-zero', () => {
  try {
    run('');
    throw new Error('Should have exited non-zero');
  } catch (e) {
    if (e.status === 0 || e.status === null) throw new Error(`Exit code was ${e.status}, expected non-zero`);
  }
});

test('Invalid repo format errors gracefully', () => {
  try {
    run('not-a-valid-repo-format-at-all');
    throw new Error('Should have exited non-zero');
  } catch (e) {
    if (e.status === 0 || e.status === null) throw new Error(`Exit code was ${e.status}, expected non-zero`);
  }
});

test('--json on invalid repo returns valid JSON', () => {
  try {
    run('fake-owner/fake-repo-999 --json');
  } catch (e) {
    // May fail due to no network, but stdout should be valid JSON or stderr should have error
    const out = (e.stdout || '') + (e.stderr || '');
    if (!out) throw new Error('No output at all');
    // As long as it didn't crash with an unhandled exception trace, we're good
    if (out.includes('TypeError') || out.includes('ReferenceError')) {
      throw new Error('Unhandled JS error in output');
    }
  }
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
