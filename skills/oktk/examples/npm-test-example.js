#!/usr/bin/env node

/**
 * Example: npm test filtering
 */

const TestFilter = require('../scripts/filters/TestFilter');

const sampleNpmTest = `PASS  src/utils.test.js
  ✓ should format date (15ms)
  ✓ should format currency (8ms)
  ✓ should calculate total (12ms)
PASS  src/components/Button.test.js
  ✓ should render button (20ms)
  ✓ should handle click (15ms)
  ✓ should show loading state (10ms)
  ✓ should be disabled when disabled (8ms)
PASS  src/components/Input.test.js
  ✓ should render input (18ms)
  ✓ should handle change (12ms)
  ✓ should validate email (14ms)
PASS  src/api/client.test.js
  ✓ should fetch data (45ms)
  ✓ should handle errors (12ms)
  ✓ should retry on failure (38ms)

Test Suites: 4 passed, 4 total
Tests:       12 passed, 12 total
Snapshots:   0 total
Time:        2.345 s
Ran all test suites.`;

async function runExample() {
  console.log('========================================');
  console.log('NPM Test Example');
  console.log('========================================\n');

  console.log('Original output:');
  console.log('----------------------------------------');
  console.log(sampleNpmTest);
  console.log('----------------------------------------\n');

  const originalTokens = sampleNpmTest.split(/\s+/).length;
  console.log(`Original tokens: ${originalTokens}\n`);

  const filter = new TestFilter();
  const filtered = await filter.apply(sampleNpmTest, { command: 'npm test' });

  console.log('Filtered output:');
  console.log('----------------------------------------');
  console.log(filtered);
  console.log('----------------------------------------\n');

  const filteredTokens = filtered.split(/\s+/).length;
  const savings = ((originalTokens - filteredTokens) / originalTokens * 100).toFixed(1);

  console.log(`Filtered tokens: ${filteredTokens}`);
  console.log(`Tokens saved: ${originalTokens - filteredTokens}`);
  console.log(`Savings: ${savings}%`);
}

runExample().catch(console.error);
