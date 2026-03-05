/**
 * NEAR DCA Skill Test Suite
 */

const { DCAManager } = require('../src/dca-manager');
const actions = require('../actions/index');

// Mock context
const mockContext = {
  config: {
    network: 'testnet',
    default_exchange: 'ref-finance',
    account_id: 'test.near',
    private_key: 'test-key',
    storage_path: './test-data/test_state.json'
  }
};

let testStrategyId = null;

console.log('=== NEAR DCA Skill Tests ===\n');

async function runTest(testName, testFn) {
  try {
    console.log(`\n🧪 ${testName}`);
    const result = await testFn();
    console.log(`✅ PASS: ${testName}`);
    if (result) console.log(`   Result:`, result);
    return true;
  } catch (error) {
    console.error(`❌ FAIL: ${testName}`);
    console.error(`   Error:`, error.message);
    return false;
  }
}

async function main() {
  let passed = 0;
  let failed = 0;

  // Test 1: Create Strategy
  if (await runTest('Create DCA Strategy', async () => {
    const result = await actions.createStrategy({
      name: 'Test Weekly Buy',
      amount: 25,
      frequency: 'weekly',
      exchange: 'ref-finance'
    }, mockContext);

    if (!result.success) throw new Error('Create strategy failed');
    testStrategyId = result.data.id;
    console.log(`   Strategy ID: ${testStrategyId}`);
    return result.data;
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 2: List Strategies
  if (await runTest('List All Strategies', async () => {
    const result = await actions.listStrategies({}, mockContext);

    if (!result.success) throw new Error('List strategies failed');
    if (result.count === 0) throw new Error('No strategies found');
    return { count: result.count };
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 3: Get Strategy
  if (await runTest('Get Strategy Details', async () => {
    const result = await actions.getStrategy({
      strategy_id: testStrategyId
    }, mockContext);

    if (!result.success) throw new Error('Get strategy failed');
    if (result.data.name !== 'Test Weekly Buy') throw new Error('Strategy name mismatch');
    return result.data;
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 4: Pause Strategy
  if (await runTest('Pause Strategy', async () => {
    const result = await actions.pauseStrategy({
      strategy_id: testStrategyId
    }, mockContext);

    if (!result.success) throw new Error('Pause strategy failed');
    if (result.data.status !== 'paused') throw new Error('Status not paused');
    return result.data;
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 5: Resume Strategy
  if (await runTest('Resume Strategy', async () => {
    const result = await actions.resumeStrategy({
      strategy_id: testStrategyId
    }, mockContext);

    if (!result.success) throw new Error('Resume strategy failed');
    if (result.data.status !== 'active') throw new Error('Status not active');
    return result.data;
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 6: Configure Alerts
  if (await runTest('Configure Alerts', async () => {
    const result = await actions.configureAlerts({
      strategy_id: testStrategyId,
      enabled: true,
      channels: ['discord', 'telegram'],
      on_success: true,
      on_failure: true
    }, mockContext);

    if (!result.success) throw new Error('Configure alerts failed');
    return result.data;
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 7: Get History
  if (await runTest('Get Execution History', async () => {
    const result = await actions.getHistory({
      strategy_id: testStrategyId,
      limit: 10
    }, mockContext);

    if (!result.success) throw new Error('Get history failed');
    return { count: result.count };
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 8: Calculate Cost Basis
  if (await runTest('Calculate Cost Basis', async () => {
    const result = await actions.calculateCostBasis({
      strategy_id: testStrategyId
    }, mockContext);

    if (!result.success) throw new Error('Calculate cost basis failed');
    return result.data;
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 9: Create Multiple Strategies
  if (await runTest('Create Multiple Strategies', async () => {
    const strategy2 = await actions.createStrategy({
      name: 'Daily Accumulation',
      amount: 10,
      frequency: 'daily',
      exchange: 'jumbo'
    }, mockContext);

    const strategy3 = await actions.createStrategy({
      name: 'Monthly Savings',
      amount: 200,
      frequency: 'monthly',
      exchange: 'bancor'
    }, mockContext);

    const list = await actions.listStrategies({}, mockContext);
    if (list.count < 3) throw new Error('Should have at least 3 strategies');
    return { totalStrategies: list.count };
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 10: Delete Strategy
  if (await runTest('Delete Strategy', async () => {
    const result = await actions.deleteStrategy({
      strategy_id: testStrategyId
    }, mockContext);

    if (!result.success) throw new Error('Delete strategy failed');

    // Verify it's deleted
    const get = await actions.getStrategy({
      strategy_id: testStrategyId
    }, mockContext);

    if (get.success) throw new Error('Strategy should not exist after deletion');
    return result.data;
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 11: Cost Basis for All Strategies
  if (await runTest('Calculate Cost Basis (All)', async () => {
    const result = await actions.calculateCostBasis({}, mockContext);

    if (!result.success) throw new Error('Calculate all cost basis failed');
    if (!Array.isArray(result.data)) throw new Error('Should return array');
    return { strategiesAnalyzed: result.data.length };
  })) {
    passed++;
  } else {
    failed++;
  }

  // Test 12: Execute Scheduled Purchases (no-op test)
  if (await runTest('Execute Scheduled Purchases', async () => {
    const result = await actions.executeScheduledPurchases({}, mockContext);

    if (!result.success) throw new Error('Execute scheduled failed');
    return { 
      executed: result.executed, 
      failed: result.failed 
    };
  })) {
    passed++;
  } else {
    failed++;
  }

  // Summary
  console.log('\n' + '='.repeat(50));
  console.log(`\n📊 Test Summary:`);
  console.log(`   ✅ Passed: ${passed}`);
  console.log(`   ❌ Failed: ${failed}`);
  console.log(`   📈 Success Rate: ${((passed / (passed + failed)) * 100).toFixed(1)}%`);
  console.log('\n' + '='.repeat(50));

  process.exit(failed > 0 ? 1 : 0);
}

main().catch(error => {
  console.error('Test suite error:', error);
  process.exit(1);
});
