/**
 * Basic tests for NEAR Multi-Account Manager
 */

const skill = require('../src/index.js');

// ANSI color codes for output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function assert(condition, message) {
  if (!condition) {
    log(`✗ FAILED: ${message}`, 'red');
    return false;
  }
  log(`✓ PASSED: ${message}`, 'green');
  return true;
}

async function runTests() {
  log('\n=== NEAR Multi-Account Manager Tests ===\n', 'blue');

  let passed = 0;
  let failed = 0;

  try {
    // Test 1: list_accounts with no accounts
    log('Test 1: List accounts (empty)', 'yellow');
    const result1 = await skill.list_accounts();
    if (assert(result1.success === true, 'list_accounts returns success')) passed++; else failed++;
    if (assert(result1.count === 0, 'No accounts initially')) passed++; else failed++;
    log('');

    // Test 2: get_all_balances with no accounts
    log('Test 2: Get all balances (empty)', 'yellow');
    const result2 = await skill.get_all_balances();
    if (assert(result2.success === true, 'get_all_balances returns success')) passed++; else failed++;
    if (assert(result2.count === 0, 'No balances initially')) passed++; else failed++;
    log('');

    // Test 3: account_summary with no accounts
    log('Test 3: Account summary (empty)', 'yellow');
    const result3 = await skill.account_summary();
    if (assert(result3.success === true, 'account_summary returns success')) passed++; else failed++;
    if (assert(result3.totalAccounts === 0, 'No accounts in summary')) passed++; else failed++;
    log('');

    // Test 4: export_accounts with no accounts
    log('Test 4: Export accounts (empty)', 'yellow');
    const result4 = await skill.export_accounts();
    if (assert(result4.success === true, 'export_accounts returns success')) passed++; else failed++;
    if (assert(Array.isArray(result4.export.accounts), 'Export has accounts array')) passed++; else failed++;
    log('');

    // Test 5: get_balance without active account
    log('Test 5: Get balance without active account', 'yellow');
    const result5 = await skill.get_balance();
    if (assert(result5.success === false, 'Fails without active account')) passed++; else failed++;
    if (assert(result5.error.includes('No active account'), 'Correct error message')) passed++; else failed++;
    log('');

    // Test 6: add_account with missing parameters
    log('Test 6: Add account with missing parameters', 'yellow');
    const result6a = await skill.add_account({});
    if (assert(result6a.success === false, 'Fails without accountId')) passed++; else failed++;

    const result6b = await skill.add_account({ accountId: 'test.near' });
    if (assert(result6b.success === false, 'Fails without privateKey')) passed++; else failed++;

    const result6c = await skill.add_account({ accountId: 'test.near', privateKey: 'invalid-key' });
    if (assert(result6c.success === false, 'Fails with invalid key format')) passed++; else failed++;
    log('');

    // Test 7: set_active_account with non-existent account
    log('Test 7: Set active account (non-existent)', 'yellow');
    const result7 = await skill.set_active_account({ accountId: 'nonexistent.near' });
    if (assert(result7.success === false, 'Fails for non-existent account')) passed++; else failed++;
    log('');

    // Test 8: remove_account without confirmation
    log('Test 8: Remove account without confirmation', 'yellow');
    const result8 = await skill.remove_account({ accountId: 'test.near' });
    if (assert(result8.success === false, 'Fails without confirmation')) passed++; else failed++;
    log('');

    // Test 9: transfer with missing parameters
    log('Test 9: Transfer with missing parameters', 'yellow');
    const result9 = await skill.transfer({});
    if (assert(result9.success === false, 'Fails without parameters')) passed++; else failed++;

    const result9b = await skill.transfer({ to: 'receiver.near' });
    if (assert(result9b.success === false, 'Fails without amount')) passed++; else failed++;
    log('');

    // Test 10: import_account
    log('Test 10: Import account', 'yellow');
    const result10 = await skill.import_account({ accountId: 'imported.near', name: 'Test Import' });
    if (assert(result10.success === true, 'Import succeeds')) passed++; else failed++;
    if (assert(result10.needsPrivateKey === true, 'Requires private key')) passed++; else failed++;
    log('');

  } catch (error) {
    log(`\nTest suite error: ${error.message}`, 'red');
    console.error(error);
  }

  // Summary
  log('\n=== Test Summary ===', 'blue');
  log(`Passed: ${passed}`, 'green');
  log(`Failed: ${failed}`, failed > 0 ? 'red' : 'green');
  log(`Total:  ${passed + failed}\n`, 'blue');

  return failed === 0;
}

// Run tests
runTests().then(success => {
  process.exit(success ? 0 : 1);
});
