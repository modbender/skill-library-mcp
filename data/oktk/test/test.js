/**
 * oktk test suite
 */

// Safe test utilities (no shell execution)

class OktkTests {
  constructor() {
    this.passed = 0;
    this.failed = 0;
    this.tests = [];
  }

  /**
   * Run a test
   */
  test(name, fn) {
    try {
      fn();
      this.passed++;
      this.tests.push({ name, status: 'PASS' });
      console.log(`✅ ${name}`);
    } catch (error) {
      this.failed++;
      this.tests.push({ name, status: 'FAIL', error: error.message });
      console.log(`❌ ${name}`);
      console.log(`   ${error.message}`);
    }
  }

  /**
   * Assert value is truthy
   */
  assert(value, message) {
    if (!value) {
      throw new Error(message || 'Assertion failed');
    }
  }

  /**
   * Assert equality
   */
  assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(message || `Expected ${expected}, got ${actual}`);
    }
  }

  /**
   * Assert exception thrown
   */
  async assertThrows(fn, message) {
    try {
      await fn();
      throw new Error(message || 'Expected exception to be thrown');
    } catch (error) {
      if (error.message === message || !message) {
        // Expected exception
        return;
      }
      throw error;
    }
  }

  /**
   * Print summary
   */
  summary() {
    console.log(``);
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    console.log(`Tests: ${this.passed + this.failed}`);
    console.log(`✅ Passed: ${this.passed}`);
    if (this.failed > 0) {
      console.log(`❌ Failed: ${this.failed}`);
    }
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);

    return this.failed === 0;
  }
}

// Import filters
const BaseFilter = require('../scripts/filters/BaseFilter');
const PassthroughFilter = require('../scripts/filters/PassthroughFilter');
const GitFilter = require('../scripts/filters/GitFilter');
const TestFilter = require('../scripts/filters/TestFilter');
const FilesFilter = require('../scripts/filters/FilesFilter');
const NetworkFilter = require('../scripts/filters/NetworkFilter');
const SearchFilter = require('../scripts/filters/SearchFilter');
const Cache = require('../scripts/cache');

/**
 * BaseFilter tests
 */
async function testBaseFilter() {
  console.log(`\n🧪 Testing BaseFilter`);

  const tests = new OktkTests();
  const filter = new BaseFilter();

  // Test ANSI code removal
  tests.test('removes ANSI codes', () => {
    const input = '\x1b[31mError\x1b[0m message';
    const output = filter.removeAnsiCodes(input);
    tests.assertEqual(output, 'Error message');
  });

  // Test binary detection
  tests.test('detects binary output', () => {
    const binary = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0e';
    tests.assert(filter.isBinary(binary));
  });

  // Test text is not binary
  tests.test('text is not binary', () => {
    const text = 'Hello, world!';
    tests.assert(!filter.isBinary(text));
  });

  // Test truncation
  tests.test('truncates large output', () => {
    const large = 'a'.repeat(100000);
    const truncated = filter.truncate(large, 100);
    tests.assert(truncated.length < 200); // 100 + truncation message
    tests.assert(truncated.includes('characters hidden'));
  });

  // Test small output not truncated
  tests.test('small output not truncated', () => {
    const small = 'Hello, world!';
    const truncated = filter.truncate(small, 100);
    tests.assertEqual(truncated, small);
  });

  // Test secret redaction
  tests.test('redacts API keys', () => {
    const input = 'api_key=secret123 token=abc456';
    const redacted = filter.redactSecrets(input);
    tests.assert(redacted.includes('***'));
    tests.assert(!redacted.includes('secret123'));
    tests.assert(!redacted.includes('abc456'));
  });

  // Test byte formatting
  tests.test('formats bytes', () => {
    tests.assertEqual(filter.formatBytes(100), '100 B');
    tests.assertEqual(filter.formatBytes(1024), '1 KB');
    tests.assertEqual(filter.formatBytes(1024 * 1024), '1 MB');
  });

  // Test duration formatting
  tests.test('formats duration', () => {
    tests.assertEqual(filter.formatDuration(500), '500ms');
    tests.assertEqual(filter.formatDuration(2000), '2.0s');
    tests.assertEqual(filter.formatDuration(60000), '1m 0s');
  });

  return tests.summary();
}

/**
 * PassthroughFilter tests
 */
async function testPassthroughFilter() {
  console.log(`\n🧪 Testing PassthroughFilter`);

  const tests = new OktkTests();
  const filter = new PassthroughFilter();

  // Test removes ANSI codes
  tests.test('removes ANSI codes', async () => {
    const input = '\x1b[31mError\x1b[0m message\n\x1b[32mSuccess\x1b[0m';
    const output = await filter.apply(input);
    tests.assert(!output.includes('\x1b'));
  });

  // Test removes excessive whitespace
  tests.test('removes excessive whitespace', async () => {
    const input = 'Line 1\n\n\n\n\nLine 2';
    const output = await filter.apply(input);
    tests.assert(!output.includes('\n\n\n'));
  });

  // Test normal output preserved
  tests.test('normal output preserved', async () => {
    const input = 'Line 1\nLine 2\nLine 3';
    const output = await filter.apply(input);
    tests.assertEqual(output.trim(), input);
  });

  // Test large output truncated
  tests.test('large output truncated', async () => {
    const large = 'a'.repeat(2000000);
    const output = await filter.apply(large);
    tests.assert(output.length < 2000000);
    tests.assert(output.includes('truncated'));
  });

  return tests.summary();
}

/**
 * GitFilter tests
 */
async function testGitFilter() {
  console.log(`\n🧪 Testing GitFilter`);

  const tests = new OktkTests();
  const filter = new GitFilter();

  // Test git status filtering
  tests.test('filters git status', async () => {
    const input = `On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to include in what will be committed)
  (use "git restore <file>..." to discard changes in working directory)

  modified:   file1.js
  modified:   file2.js

Untracked files:
  (use "git add <file>..." to include in what will be committed)
  file3.js

no changes added to commit (use "git add" and/or "git commit -a")`;

    const output = await filter.apply(input, { command: 'git status' });
    tests.assert(output.includes('📍 main'));
    tests.assert(output.includes('✓ Up to date'));
    tests.assert(output.includes('✏️  Modified: 2'));
    tests.assert(output.includes('❓ Untracked: 1'));
  });

  // Test git log filtering
  tests.test('filters git log', async () => {
    const input = `commit abc123
Author: John Doe <john@example.com>
Date: Mon Feb 12 10:00:00 2026

    Fix bug in parser

commit def456
Author: Jane Smith <jane@example.com>
Date: Mon Feb 11 15:30:00 2026

    Add new feature`;

    const output = await filter.apply(input, { command: 'git log' });
    tests.assert(output.includes('abc123'));
    tests.assert(output.includes('Fix bug'));
  });

  return tests.summary();
}

/**
 * TestFilter tests
 */
async function testTestFilter() {
  console.log(`\n🧪 Testing TestFilter`);

  const tests = new OktkTests();
  const filter = new TestFilter();

  // Test npm test filtering
  tests.test('filters npm test', async () => {
    const input = `PASS  src/utils.test.js
  ✓ should format date
  ✓ should format currency
PASS  src/components.test.js
  ✓ should render button

Test Suites: 2 passed, 2 total
Tests:       3 passed, 3 total
Snapshots:   0 total
Time:        2.345 s`;

    const output = await filter.apply(input, { command: 'npm test' });
    tests.assert(output.includes('✅ All tests passed'));
    tests.assert(output.includes('📊 3 total tests'));
    tests.assert(output.includes('✅ Passed: 3'));
    tests.assert(output.includes('📦 2 test suite'));
  });

  return tests.summary();
}

/**
 * FilesFilter tests
 */
async function testFilesFilter() {
  console.log(`\n🧪 Testing FilesFilter`);

  const tests = new OktkTests();
  const filter = new FilesFilter();

  // Test ls filtering
  tests.test('filters ls -la', async () => {
    const input = `total 128
drwxr-xr-x  10 user  staff   320 Feb 12 22:00 .
drwxr-xr-x   5 user  staff   160 Feb 12 21:00 ..
-rw-r--r--   1 user  staff  2048 Feb 12 22:00 file1.js
-rw-r--r--   1 user  staff  1024 Feb 12 22:00 file2.js
drwxr-xr-x   2 user  staff    64 Feb 12 22:00 node_modules`;

    const output = await filter.apply(input, { command: 'ls -la' });
    tests.assert(output.includes('📁 .'));
    tests.assert(output.includes('📄 Files'));
  });

  return tests.summary();
}

/**
 * NetworkFilter tests
 */
async function testNetworkFilter() {
  console.log(`\n🧪 Testing NetworkFilter`);

  const tests = new OktkTests();
  const filter = new NetworkFilter();

  // Test JSON filtering
  tests.test('filters JSON output', async () => {
    const input = JSON.stringify({
      name: 'test',
      version: '1.0.0',
      dependencies: {
        express: '4.18.0',
        lodash: '4.17.21'
      }
    });

    const output = await filter.apply(input, { command: 'curl https://api.example.com' });
    tests.assert(output.includes('📦 JSON'));
  });

  // Test HTML filtering
  tests.test('filters HTML output', async () => {
    const input = `<!DOCTYPE html>
<html>
<head>
  <title>Test Page</title>
</head>
<body>
  <h1>Hello</h1>
  <a href="/link1">Link 1</a>
  <a href="/link2">Link 2</a>
</body>
</html>`;

    const output = await filter.apply(input, { command: 'curl https://example.com' });
    tests.assert(output.includes('🌐 HTML'));
    tests.assert(output.includes('Test Page'));
    tests.assert(output.includes('Links: 2'));
  });

  return tests.summary();
}

/**
 * SearchFilter tests
 */
async function testSearchFilter() {
  console.log(`\n🧪 Testing SearchFilter`);

  const tests = new OktkTests();
  const filter = new SearchFilter();

  // Test grep filtering
  tests.test('filters grep output', async () => {
    const input = `src/app.js:42:const x = 1;
src/app.js:50:const y = 2;
src/utils.js:10:const z = 3;
src/utils.js:20:const w = 4;`;

    const output = await filter.apply(input, { command: 'grep "const"' });
    tests.assert(output.includes('🔍 Found 4 matches'));
    tests.assert(output.includes('src/app.js'));
    tests.assert(output.includes('src/utils.js'));
  });

  // Test no matches
  tests.test('handles no matches', async () => {
    const output = await filter.apply('', { command: 'grep "xyz"' });
    tests.assertEqual(output, 'No matches found');
  });

  return tests.summary();
}

/**
 * Cache tests
 */
async function testCache() {
  console.log(`\n🧪 Testing Cache`);

  const tests = new OktkTests();

  // Note: These tests create a temporary cache directory
  const tempDir = '/tmp/oktk-test-cache';
  const cache = new Cache({ cacheDir: tempDir, ttl: 1 });

  // Test cache set and get
  tests.test('sets and gets value', async () => {
    await cache.set('test-key', { value: 'test-data' });
    const result = await cache.get('test-key');
    tests.assert(result !== null);
    tests.assertEqual(result.value.value, 'test-data');
  });

  // Test cache miss
  tests.test('returns null for missing key', async () => {
    const result = await cache.get('non-existent');
    tests.assertEqual(result, null);
  });

  // Test cache deletion
  tests.test('deletes value', async () => {
    await cache.set('delete-key', { value: 'delete-me' });
    await cache.delete('delete-key');
    const result = await cache.get('delete-key');
    tests.assertEqual(result, null);
  });

  // Test clear cache
  tests.test('clears all cache', async () => {
    await cache.set('key1', { value: '1' });
    await cache.set('key2', { value: '2' });
    await cache.clear();
    const result1 = await cache.get('key1');
    const result2 = await cache.get('key2');
    tests.assertEqual(result1, null);
    tests.assertEqual(result2, null);
  });

  // Cleanup using fs (safer than shell rm -rf)
  try {
    fs.rmSync(tempDir, { recursive: true, force: true });
  } catch {
    // Ignore cleanup errors
  }

  return tests.summary();
}

/**
 * Main test runner
 */
async function runTests(filter = null) {
  console.log(`🚀 Running oktk tests\n`);

  let allPassed = true;

  if (!filter || filter === 'base') {
    const passed = await testBaseFilter();
    allPassed = allPassed && passed;
  }

  if (!filter || filter === 'passthrough') {
    const passed = await testPassthroughFilter();
    allPassed = allPassed && passed;
  }

  if (!filter || filter === 'git') {
    const passed = await testGitFilter();
    allPassed = allPassed && passed;
  }

  if (!filter || filter === 'test') {
    const passed = await testTestFilter();
    allPassed = allPassed && passed;
  }

  if (!filter || filter === 'files') {
    const passed = await testFilesFilter();
    allPassed = allPassed && passed;
  }

  if (!filter || filter === 'network') {
    const passed = await testNetworkFilter();
    allPassed = allPassed && passed;
  }

  if (!filter || filter === 'search') {
    const passed = await testSearchFilter();
    allPassed = allPassed && passed;
  }

  if (!filter || filter === 'cache') {
    const passed = await testCache();
    allPassed = allPassed && passed;
  }

  console.log(`\n${allPassed ? '✅ All tests passed!' : '❌ Some tests failed'}`);

  process.exit(allPassed ? 0 : 1);
}

// Run tests if called directly
if (require.main === module) {
  const filter = process.argv[2] || null;
  runTests(filter);
}

module.exports = { runTests };
