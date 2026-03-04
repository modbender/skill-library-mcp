#!/usr/bin/env node
/**
 * Test Script for BaseCred SDK Skill
 * Tests with known addresses
 */

import { checkReputation, getSummary } from './lib/basecred.mjs';

const TESTS = [
  {
    name: 'Vitalik Buterin (vitalik.eth)',
    address: '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
  },
  {
    name: 'Mr. Tee (main wallet)',
    address: '0x134820820d4f631ff949625189950bA7B3C57e41',
  },
];

console.log('🧪 BaseCred SDK Skill - Test Suite\n');

for (const test of TESTS) {
  console.log(`Testing: ${test.name}`);
  console.log(`Address: ${test.address}\n`);

  try {
    const result = await checkReputation(test.address, { skipWarnings: true });

    if (result.error) {
      console.log(`❌ Error: ${result.message}\n`);
      continue;
    }

    const summary = getSummary(result);

    console.log('✅ Success!');
    console.log('📊 Summary:');
    console.log(JSON.stringify(summary, null, 2));
    console.log('\n' + '='.repeat(60) + '\n');

  } catch (error) {
    console.log(`❌ Test failed: ${error.message}\n`);
  }
}

console.log('✅ Test suite complete');
