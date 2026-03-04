#!/usr/bin/env node
/**
 * Test script for Human-Like Memory Skill
 *
 * Usage:
 *   node test/test-memory.mjs
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const MEMORY_SCRIPT = join(__dirname, '..', 'scripts', 'memory.mjs');

// Test results tracking
const results = [];
let passed = 0;
let failed = 0;

/**
 * Run a command and capture output
 */
function runCommand(args) {
  return new Promise((resolve) => {
    const proc = spawn('node', [MEMORY_SCRIPT, ...args], {
      env: process.env,
      cwd: join(__dirname, '..'),
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      resolve({
        code,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
      });
    });
  });
}

/**
 * Run a test case
 */
async function test(name, args, validator) {
  process.stdout.write(`  Testing: ${name}... `);

  const startTime = Date.now();
  const result = await runCommand(args);
  const duration = Date.now() - startTime;

  try {
    const validation = validator(result);
    if (validation.pass) {
      console.log(`✅ PASS (${duration}ms)`);
      passed++;
      results.push({ name, status: 'PASS', duration, details: validation.message });
    } else {
      console.log(`❌ FAIL`);
      console.log(`     Reason: ${validation.message}`);
      failed++;
      results.push({ name, status: 'FAIL', duration, details: validation.message, output: result });
    }
  } catch (error) {
    console.log(`❌ ERROR`);
    console.log(`     Error: ${error.message}`);
    failed++;
    results.push({ name, status: 'ERROR', duration, details: error.message, output: result });
  }
}

/**
 * Main test suite
 */
async function runTests() {
  console.log('\n╔══════════════════════════════════════════════════════════════════╗');
  console.log('║        Human-Like Memory Skill - Test Suite                      ║');
  console.log('╚══════════════════════════════════════════════════════════════════╝\n');

  // Test 1: Help command
  console.log('📋 CLI Tests:');

  await test('help command', ['help'], (result) => {
    const hasUsage = result.stdout.includes('Usage:');
    const hasCommands = result.stdout.includes('Commands:');
    return {
      pass: hasUsage && hasCommands,
      message: hasUsage && hasCommands ? 'Help output is correct' : 'Missing expected help content',
    };
  });

  // Test 2: Config command
  await test('config command', ['config'], (result) => {
    try {
      const config = JSON.parse(result.stdout);
      const hasBaseUrl = 'baseUrl' in config;
      const hasUserId = 'userId' in config;
      const hasApiKeyConfigured = 'apiKeyConfigured' in config;
      return {
        pass: hasBaseUrl && hasUserId && hasApiKeyConfigured,
        message: hasBaseUrl && hasUserId && hasApiKeyConfigured
          ? `Config loaded: apiKey=${config.apiKeyConfigured}, userId=${config.userId}`
          : 'Missing expected config fields',
      };
    } catch (e) {
      return { pass: false, message: `Invalid JSON: ${e.message}` };
    }
  });

  // Test 3: Unknown command
  await test('unknown command error', ['unknown_cmd'], (result) => {
    const hasError = result.stdout.includes('Unknown command') || result.code !== 0;
    return {
      pass: hasError,
      message: hasError ? 'Correctly handles unknown command' : 'Should error on unknown command',
    };
  });

  // Test 4: Recall without query
  await test('recall without query', ['recall'], (result) => {
    const hasError = result.stderr.includes('required') || result.code !== 0;
    return {
      pass: hasError,
      message: hasError ? 'Correctly requires query' : 'Should require query parameter',
    };
  });

  // API Tests (only if API key is configured)
  console.log('\n🌐 API Tests:');

  const configResult = await runCommand(['config']);
  let apiKeyConfigured = false;
  try {
    const config = JSON.parse(configResult.stdout);
    apiKeyConfigured = config.apiKeyConfigured;
  } catch (e) {
    // ignore
  }

  if (!apiKeyConfigured) {
    console.log('  ⚠️  Skipping API tests: HUMAN_LIKE_MEM_API_KEY not configured');
    console.log('     Set the API key to run full integration tests.\n');
  } else {
    // Test 5: Memory recall
    await test('memory recall API', ['recall', '测试记忆召回功能'], (result) => {
      try {
        const response = JSON.parse(result.stdout);
        const hasSuccess = 'success' in response;
        const hasCount = 'count' in response;
        return {
          pass: hasSuccess && response.success,
          message: response.success
            ? `Retrieved ${response.count} memories`
            : `API error: ${response.error || 'Unknown error'}`,
        };
      } catch (e) {
        // Check stderr for error JSON
        try {
          const errorResponse = JSON.parse(result.stderr);
          return {
            pass: false,
            message: `API error: ${errorResponse.error || 'Unknown error'}`,
          };
        } catch {
          return { pass: false, message: `Invalid response: ${e.message}` };
        }
      }
    });

    // Test 6: Memory save
    await test('memory save API', ['save', '这是一条测试消息', '好的，我记住了'], (result) => {
      try {
        const response = JSON.parse(result.stdout);
        return {
          pass: response.success === true,
          message: response.success
            ? `Saved successfully`
            : `Save failed: ${response.error || 'Unknown error'}`,
        };
      } catch (e) {
        try {
          const errorResponse = JSON.parse(result.stderr);
          return {
            pass: false,
            message: `API error: ${errorResponse.error || 'Unknown error'}`,
          };
        } catch {
          return { pass: false, message: `Invalid response: ${e.message}` };
        }
      }
    });

    // Test 7: Memory search
    await test('memory search API', ['search', '测试'], (result) => {
      try {
        const response = JSON.parse(result.stdout);
        return {
          pass: response.success === true,
          message: response.success
            ? `Search returned ${response.count} results`
            : `Search failed: ${response.error || 'Unknown error'}`,
        };
      } catch (e) {
        try {
          const errorResponse = JSON.parse(result.stderr);
          return {
            pass: false,
            message: `API error: ${errorResponse.error || 'Unknown error'}`,
          };
        } catch {
          return { pass: false, message: `Invalid response: ${e.message}` };
        }
      }
    });
  }

  // Summary
  console.log('\n══════════════════════════════════════════════════════════════════');
  console.log(`📊 Test Summary: ${passed} passed, ${failed} failed, ${passed + failed} total`);

  if (failed === 0) {
    console.log('✅ All tests passed!\n');
  } else {
    console.log('❌ Some tests failed.\n');

    // Show failed tests details
    console.log('Failed tests:');
    results
      .filter(r => r.status !== 'PASS')
      .forEach(r => {
        console.log(`  - ${r.name}: ${r.details}`);
      });
    console.log('');
  }

  process.exit(failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(console.error);
