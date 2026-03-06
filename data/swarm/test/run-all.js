#!/usr/bin/env node
/**
 * Swarm Test Runner
 * Runs all test suites in sequence
 */

const { spawn } = require('child_process');
const path = require('path');

const TESTS = [
  { name: 'Unit Tests', file: 'unit.test.js' },
  { name: 'Integration Tests', file: 'integration.test.js' },
  { name: 'E2E Tests', file: 'e2e.test.js' },
];

async function runTest(test) {
  return new Promise((resolve) => {
    console.log(`\n${'='.repeat(50)}`);
    console.log(`Running: ${test.name}`);
    console.log('='.repeat(50));
    
    const proc = spawn('node', [path.join(__dirname, test.file)], {
      stdio: 'inherit',
      env: process.env,
    });
    
    proc.on('close', (code) => {
      resolve({ name: test.name, code });
    });
  });
}

async function main() {
  console.log('🐝 Swarm Test Suite');
  console.log('==================\n');
  
  const results = [];
  
  for (const test of TESTS) {
    const result = await runTest(test);
    results.push(result);
  }
  
  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('TEST SUMMARY');
  console.log('='.repeat(50) + '\n');
  
  let allPassed = true;
  for (const result of results) {
    const status = result.code === 0 ? '✅' : '❌';
    console.log(`${status} ${result.name}`);
    if (result.code !== 0) allPassed = false;
  }
  
  console.log('\n' + (allPassed ? '✅ All tests passed!' : '❌ Some tests failed'));
  
  process.exit(allPassed ? 0 : 1);
}

main();
