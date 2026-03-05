#!/usr/bin/env node

/**
 * Simple Test Runner for Janitor
 *
 * Runs all tests without external dependencies
 */

const fs = require('fs');
const path = require('path');

// Test results
const results = {
  passed: 0,
  failed: 0,
  tests: []
};

// ANSI colors
const GREEN = '\x1b[32m';
const RED = '\x1b[31m';
const YELLOW = '\x1b[33m';
const BLUE = '\x1b[34m';
const RESET = '\x1b[0m';

// Test utilities
function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(message || `Expected ${expected}, got ${actual}`);
  }
}

function assertDefined(value, message) {
  if (value === undefined || value === null) {
    throw new Error(message || 'Value is undefined or null');
  }
}

async function runTest(name, testFn) {
  process.stdout.write(`  ${name}... `);

  try {
    await testFn({ assert, assertEqual, assertDefined });
    console.log(`${GREEN}✓${RESET}`);
    results.passed++;
    results.tests.push({ name, status: 'passed' });
  } catch (error) {
    console.log(`${RED}✗${RESET}`);
    console.log(`    Error: ${error.message}`);
    results.failed++;
    results.tests.push({ name, status: 'failed', error: error.message });
  }
}

// Test Suite
async function main() {
  console.log(`\n${BLUE}Running Janitor Tests${RESET}\n`);

  // Test 1: Session Monitor
  console.log('Session Monitor:');
  await runTest('Initialize monitor', async ({ assertDefined }) => {
    const SessionMonitor = require('../src/session-management/monitor');
    const monitor = new SessionMonitor({ maxTokens: 200000 });
    assertDefined(monitor);
    assertDefined(monitor.config);
  });

  await runTest('Format tokens', async ({ assertEqual }) => {
    const SessionMonitor = require('../src/session-management/monitor');
    const monitor = new SessionMonitor();
    assertEqual(monitor.formatTokens(500), '500');
    assertEqual(monitor.formatTokens(1500), '1.5k');
    assertEqual(monitor.formatTokens(1500000), '1.5M');
  });

  // Test 2: Session Pruner
  console.log('\nSession Pruner:');
  await runTest('Initialize pruner', async ({ assertDefined }) => {
    const SessionMonitor = require('../src/session-management/monitor');
    const SessionPruner = require('../src/session-management/pruner');
    const monitor = new SessionMonitor();
    const pruner = new SessionPruner(monitor);
    assertDefined(pruner);
    assertDefined(pruner.config);
  });

  await runTest('Get recommended strategy', async ({ assert }) => {
    const SessionMonitor = require('../src/session-management/monitor');
    const SessionPruner = require('../src/session-management/pruner');
    const monitor = new SessionMonitor();
    const pruner = new SessionPruner(monitor);

    assertEqual(pruner.getRecommendedStrategy(50), 'conservative');
    assertEqual(pruner.getRecommendedStrategy(80), 'moderate');
    assertEqual(pruner.getRecommendedStrategy(90), 'aggressive');
    assertEqual(pruner.getRecommendedStrategy(96), 'emergency');
  });

  // Test 3: Session Archiver
  console.log('\nSession Archiver:');
  await runTest('Initialize archiver', async ({ assertDefined }) => {
    const SessionArchiver = require('../src/session-management/archiver');
    const archiver = new SessionArchiver();
    assertDefined(archiver);
    assertDefined(archiver.config);
  });

  await runTest('Format bytes', async ({ assertEqual }) => {
    const SessionArchiver = require('../src/session-management/archiver');
    const archiver = new SessionArchiver();
    assertEqual(archiver._formatBytes(0), '0 Bytes');
    assertEqual(archiver._formatBytes(1024), '1 KB');
    assertEqual(archiver._formatBytes(1024 * 1024), '1 MB');
  });

  // Test 4: Emergency Cleanup
  console.log('\nEmergency Cleanup:');
  await runTest('Initialize emergency', async ({ assertDefined }) => {
    const SessionMonitor = require('../src/session-management/monitor');
    const SessionPruner = require('../src/session-management/pruner');
    const SessionArchiver = require('../src/session-management/archiver');
    const EmergencyCleanup = require('../src/session-management/emergency');

    const monitor = new SessionMonitor();
    const pruner = new SessionPruner(monitor);
    const archiver = new SessionArchiver();
    const emergency = new EmergencyCleanup(monitor, pruner, archiver);

    assertDefined(emergency);
    assertDefined(emergency.config);
  });

  await runTest('Get status', async ({ assertDefined, assertEqual }) => {
    const SessionMonitor = require('../src/session-management/monitor');
    const SessionPruner = require('../src/session-management/pruner');
    const SessionArchiver = require('../src/session-management/archiver');
    const EmergencyCleanup = require('../src/session-management/emergency');

    const monitor = new SessionMonitor();
    const pruner = new SessionPruner(monitor);
    const archiver = new SessionArchiver();
    const emergency = new EmergencyCleanup(monitor, pruner, archiver);

    const status = emergency.getStatus();
    assertDefined(status);
    assertEqual(status.enabled, true);
  });

  // Test 5: Dashboard
  console.log('\nDashboard:');
  await runTest('Initialize dashboard', async ({ assertDefined }) => {
    const SessionMonitor = require('../src/session-management/monitor');
    const Dashboard = require('../src/utils/dashboard');

    const monitor = new SessionMonitor();
    const dashboard = new Dashboard(monitor);

    assertDefined(dashboard);
  });

  // Test 6: Session Analyzer
  console.log('\nSession Analyzer:');
  await runTest('Initialize analyzer', async ({ assertDefined }) => {
    const SessionAnalyzer = require('../src/session-management/analyzer');
    const analyzer = new SessionAnalyzer();

    assertDefined(analyzer);
    assertDefined(analyzer.config);
  });

  // Test 7: Notifier
  console.log('\nNotifier:');
  await runTest('Initialize notifier', async ({ assertDefined }) => {
    const Notifier = require('../src/services/notifier');
    const notifier = new Notifier();

    assertDefined(notifier);
    assertDefined(notifier.config);
  });

  await runTest('Get status', async ({ assertDefined }) => {
    const Notifier = require('../src/services/notifier');
    const notifier = new Notifier();

    const status = notifier.getStatus();
    assertDefined(status);
    assertDefined(status.channels);
  });

  // Test 8: Config Manager
  console.log('\nConfig Manager:');
  await runTest('Initialize config manager', async ({ assertDefined }) => {
    const ConfigManager = require('../src/utils/config-manager');
    const config = new ConfigManager();

    assertDefined(config);
    assertDefined(config.config);
  });

  await runTest('Get/Set config', async ({ assertEqual }) => {
    const ConfigManager = require('../src/utils/config-manager');
    const config = new ConfigManager();

    config.set('test.key', 'value');
    assertEqual(config.get('test.key'), 'value');

    config.set('test.number', '42');
    assertEqual(config.get('test.number'), 42);

    config.delete('test.key');
    assertEqual(config.get('test.key'), undefined);
  });

  await runTest('Validate config', async ({ assert }) => {
    const ConfigManager = require('../src/utils/config-manager');
    const config = new ConfigManager();

    const validation = config.validate();
    assert(validation.valid === true || validation.valid === false);
  });

  // Test 9: Core Janitor
  console.log('\nCore Janitor:');
  await runTest('Initialize Janitor', async ({ assertDefined }) => {
    const Janitor = require('../janitor');
    const janitor = new Janitor();

    assertDefined(janitor);
    assertDefined(janitor.config);
    assertDefined(janitor.stats);
  });

  await runTest('Get stats', async ({ assertDefined }) => {
    const Janitor = require('../janitor');
    const janitor = new Janitor();

    const stats = janitor.getStats();
    assertDefined(stats);
    assertDefined(stats.totalCleanups);
  });

  // Print results
  console.log(`\n${'='.repeat(60)}`);
  console.log(`\nTest Results:`);
  console.log(`  ${GREEN}Passed:${RESET} ${results.passed}`);
  console.log(`  ${RED}Failed:${RESET} ${results.failed}`);
  console.log(`  Total: ${results.passed + results.failed}`);

  if (results.failed > 0) {
    console.log(`\n${RED}Some tests failed!${RESET}\n`);
    process.exit(1);
  } else {
    console.log(`\n${GREEN}All tests passed!${RESET}\n`);
    process.exit(0);
  }
}

// Run tests
main().catch(error => {
  console.error(`\n${RED}Test runner failed:${RESET}`, error.message);
  process.exit(1);
});
