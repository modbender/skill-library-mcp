#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

const SCRIPT = path.join(__dirname, 'source-library.js');
let tmpDir;
let passed = 0, failed = 0;

function setup() {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'srclib-test-'));
}

function cleanup() {
  fs.rmSync(tmpDir, { recursive: true, force: true });
}

function run(args) {
  return execSync(`node "${SCRIPT}" ${args}`, {
    env: { ...process.env, OPENCLAW_WORKSPACE: tmpDir },
    encoding: 'utf8',
    timeout: 10000
  });
}

function test(name, fn) {
  try {
    fn();
    console.log(`✓ ${name}`);
    passed++;
  } catch (e) {
    console.log(`✗ ${name}: ${e.message}`);
    failed++;
  }
}

function assert(cond, msg) { if (!cond) throw new Error(msg); }

setup();

try {
  test('setup creates directories', () => {
    run('setup');
    assert(fs.existsSync(path.join(tmpDir, 'life', 'source')), 'life/source not created');
    assert(fs.existsSync(path.join(tmpDir, 'data')), 'data not created');
  });

  test('save creates source file with correct format', () => {
    const out = run('save --name "Test Article" --url "https://example.com/?utm_source=x" --slug "test-article" --tags "test, demo" --summary "A test"');
    assert(out.includes('Saved source: test-article'), 'save output missing');
    const file = path.join(tmpDir, 'life', 'source', 'test-article', 'summary.md');
    assert(fs.existsSync(file), 'summary.md not created');
    const content = fs.readFileSync(file, 'utf8');
    assert(content.includes('# Test Article'), 'title missing');
    assert(content.includes('https://example.com/'), 'canonicalized url missing');
    assert(content.includes('test, demo'), 'tags missing');
    assert(content.includes('## Summary\nA test'), 'summary missing');
  });

  test('save blocks overwrite without --force', () => {
    let failed = false;
    try {
      run('save --name "Test Article" --url "https://example.com" --slug "test-article"');
    } catch (e) {
      failed = e.stdout.includes('Source already exists') || e.stderr.includes('Source already exists');
    }
    assert(failed, 'overwrite should fail without --force');
  });

  test('list returns saved sources', () => {
    const out = run('list');
    assert(out.includes('test-article'), 'list does not show saved source');
    assert(out.includes('Test Article'), 'list missing title');
  });

  test('save with --force overwrites existing source', () => {
    const out = run('save --name "Test Article" --url "https://example.com" --slug "test-article" --tags "updated" --summary "Overwritten" --force');
    assert(out.includes('Saved source: test-article'), 'force save output missing');
    const file = path.join(tmpDir, 'life', 'source', 'test-article', 'summary.md');
    const content = fs.readFileSync(file, 'utf8');
    assert(content.includes('updated'), 'tags not overwritten');
    assert(content.includes('Overwritten'), 'summary not overwritten');
  });

  test('search returns relevant results', () => {
    const out = run('search "Test Article" --limit 5');
    assert(out.includes('test-article'), 'search did not find saved source');
    assert(out.includes('Score:'), 'search missing score');
  });

  test('stats shows correct count', () => {
    const out = run('stats');
    assert(out.includes('Total sources: 1'), 'stats count wrong');
  });

  test('save rejects unknown flags', () => {
    let rejected = false;
    try {
      run('save --name "Bad" --url "https://x.com" --bogus "flag"');
    } catch (e) {
      rejected = (e.stderr || '').includes('Unknown flag');
    }
    assert(rejected, 'unknown flags should be rejected');
  });

  test('save warns on missing --url', () => {
    const out = run('save --name "No URL Source" --slug "no-url-test" --tags "test"');
    assert(out.includes('Warning') || out.includes('Saved'), 'should save with warning or succeed');
    const file = path.join(tmpDir, 'life', 'source', 'no-url-test', 'summary.md');
    assert(fs.existsSync(file), 'source without url not created');
  });

  test('list shows empty message when no sources', () => {
    // Create a fresh empty workspace
    const emptyDir = fs.mkdtempSync(path.join(os.tmpdir(), 'srclib-empty-'));
    try {
      const out = execSync(`node "${SCRIPT}" setup`, {
        env: { ...process.env, OPENCLAW_WORKSPACE: emptyDir },
        encoding: 'utf8', timeout: 10000
      });
      const listOut = execSync(`node "${SCRIPT}" list`, {
        env: { ...process.env, OPENCLAW_WORKSPACE: emptyDir },
        encoding: 'utf8', timeout: 10000
      });
      assert(listOut.includes('No sources found'), 'empty list should show message');
    } finally {
      fs.rmSync(emptyDir, { recursive: true, force: true });
    }
  });

  test('invalid date falls back to today', () => {
    const out = run('save --name "Bad Date" --url "https://example.com/bad" --slug "bad-date-test" --date "not-a-date"');
    const file = path.join(tmpDir, 'life', 'source', 'bad-date-test', 'summary.md');
    const content = fs.readFileSync(file, 'utf8');
    const today = new Date().toISOString().split('T')[0];
    assert(content.includes(today), 'invalid date should fall back to today');
  });
} finally {
  cleanup();
}

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
