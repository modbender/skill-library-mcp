const api = require('../index.js');
const fs = require('fs');

async function test() {
  console.log('Running api-tester functional tests...');

  // Test 1: Import check
  if (typeof api.request !== 'function') {
    console.error('Test failed: request function not exported.');
    process.exit(1);
  }

  // Test 2: Basic HTTP GET (mockable with a known stable URL like example.com)
  try {
    const result = await api.request('GET', 'http://example.com');
    if (result.status === 200 && result.data.includes('Example Domain')) {
      console.log('Test passed: example.com GET successful.');
    } else {
      console.error('Test failed: example.com GET returned status', result.status);
      process.exit(1);
    }
  } catch (e) {
    console.error('Test failed: exception during request', e);
    process.exit(1);
  }

  // Test 3: Error handling (invalid URL)
  try {
    const result = await api.request('GET', 'http://invalid.url.that.does.not.exist');
    if (result.error) {
      console.log('Test passed: invalid URL handled gracefully.');
    } else {
      console.error('Test failed: invalid URL did not return error object.');
      process.exit(1);
    }
  } catch (e) {
    console.error('Test failed: exception during error handling test', e);
    process.exit(1);
  }

  console.log('All tests passed.');
}

test();
