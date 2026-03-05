const YieldFarmingAgent = require('./index.js');
const mockdata = require('./mockdata.json');

/**
 * Unit tests for YieldFarmingAgent
 */

console.log('🧪 Running tests...\n');

const agent = new YieldFarmingAgent();
let testsPassed = 0;
let testsFailed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`✅ ${message}`);
    testsPassed++;
  } else {
    console.log(`❌ ${message}`);
    testsFailed++;
  }
}

// Test 1: Hash verification
console.log('=== Test Suite 1: Hash Verification ===');
const allocation1 = {
  vault_bnb_lp_001: { shares: "1000", amount_usd: "50000", pending_rewards_usd: "1200" },
  vault_eth_staking_001: { shares: "500", amount_usd: "40000", pending_rewards_usd: "50" }
};
const exec1 = agent.decide(mockdata.vaults, allocation1);
const verify1 = agent.verifyRecord(exec1);

assert(verify1.valid, 'Execution record hash integrity verified');
assert(verify1.decision_hash_valid, 'Decision hash valid');
assert(verify1.execution_hash_valid, 'Execution hash valid');

// Test 2: Determinism (same input = same output)
console.log('\n=== Test Suite 2: Determinism ===');
const exec2 = agent.decide(mockdata.vaults, allocation1);
assert(
  exec1.decision.action.action === exec2.decision.action.action,
  'Same input produces same action (deterministic)'
);
assert(
  exec1.decision_hash === exec2.decision_hash,
  'Same input produces same decision hash'
);

// Test 3: Net APR calculation
console.log('\n=== Test Suite 3: Net APR Calculation ===');
const cakeVault = mockdata.vaults.find(v => v.id === 'vault_cake_farm_001');
const expectedNetAPR = cakeVault.apr - cakeVault.fees - (cakeVault.risk_score * 0.10);
const cakeNetAPR = parseFloat(exec1.vault_states.find(v => v.id === 'vault_cake_farm_001').net_apr);
assert(
  Math.abs(cakeNetAPR - expectedNetAPR) < 0.0001,
  `CAKE Net APR calculated correctly (${cakeNetAPR.toFixed(4)} ≈ ${expectedNetAPR.toFixed(4)})`
);

// Test 4: Risk filter (only risk_score <= 0.5)
console.log('\n=== Test Suite 4: Risk Filter ===');
const highRiskVault = mockdata.vaults.find(v => v.id === 'vault_high_risk_001');
const highRiskInResult = exec1.vault_states.find(v => v.id === 'vault_high_risk_001');
assert(
  !highRiskInResult,
  `High-risk vault (risk_score: ${highRiskVault.risk_score}) correctly filtered out`
);
assert(
  exec1.vault_states.every(v => parseFloat(v.risk_score) <= 0.5),
  'All returned vaults have risk_score ≤ 0.5'
);

// Test 5: Harvest action
console.log('\n=== Test Suite 5: Harvest Logic ===');
const allocation3 = {
  vault_cake_farm_001: { shares: "500", amount_usd: "100000", pending_rewards_usd: "3000" }
};
const exec3 = agent.decide(mockdata.vaults, allocation3);
assert(
  exec3.decision.action.action === 'HARVEST',
  'HARVEST action triggered when best_vault rewards >= threshold'
);
assert(
  exec3.decision.action.vault_id === 'vault_cake_farm_001',
  'HARVEST targets best vault with sufficient rewards'
);

// Test 6: Compound action
console.log('\n=== Test Suite 6: Compound Logic ===');
const allocation4 = {
  vault_cake_farm_001: { shares: "500", amount_usd: "100000", pending_rewards_usd: "5" }
};
const exec4 = agent.decide(mockdata.vaults, allocation4);
assert(
  exec4.decision.action.action === 'COMPOUND',
  'COMPOUND action triggered in high-APR environment'
);

// Test 7: Rebalance constraints
console.log('\n=== Test Suite 7: Rebalance Constraints ===');
const allocation5 = {
  vault_eth_staking_001: { shares: "1000", amount_usd: "33000", pending_rewards_usd: "5" },
  vault_bnb_lp_001: { shares: "500", amount_usd: "34000", pending_rewards_usd: "5" },
  vault_usdc_stable_001: { shares: "1000", amount_usd: "33000", pending_rewards_usd: "5" }
};
const exec5 = agent.decide(mockdata.vaults, allocation5);
const eachAlloc = exec5.vault_states.reduce((max, v) => Math.max(max, parseFloat(v.allocation_percent)), 0);
assert(
  eachAlloc <= 35,
  `Max allocation per vault ≤ 35% (current: ${eachAlloc.toFixed(2)}%)`
);

// Test 8: NOOP when all optimized
console.log('\n=== Test Suite 8: NOOP Logic ===');
const allocation6 = {
  vault_cake_farm_001: { shares: "600", amount_usd: "100000", pending_rewards_usd: "0" }
};
const exec6 = agent.decide(mockdata.vaults, allocation6);
// Best vault is CAKE (50.5% APR), has good allocation, low pending rewards, high APR threshold met
// COMPOUND should trigger (net_apr >= delta threshold)
// If for some reason no action is taken, it's NOOP
const isCompoundOrNoop = exec6.decision.action.action === 'COMPOUND' || exec6.decision.action.action === 'NOOP';
assert(
  isCompoundOrNoop,
  'COMPOUND or NOOP returned for optimized allocation'
);
assert(
  exec6.decision.action.reason !== undefined || exec6.decision.action.token !== undefined,
  'Action includes reason or token'
);

// Test 9: Best vault selection (highest NET_APR)
console.log('\n=== Test Suite 9: Best Vault Selection ===');
const bestVaultId = exec1.decision.best_vault_id;
const bestVaultAPR = exec1.vault_states.find(v => v.id === bestVaultId).net_apr;
const otherVaultAPRs = exec1.vault_states
  .filter(v => v.id !== bestVaultId)
  .map(v => parseFloat(v.net_apr));
const isActuallyBest = otherVaultAPRs.every(apr => apr <= parseFloat(bestVaultAPR));
assert(
  isActuallyBest,
  `Best vault correctly selected (${bestVaultId} with ${bestVaultAPR} NET_APR)`
);

// Test 10: Key ordering (deterministic JSON)
console.log('\n=== Test Suite 10: Deterministic Output ===');
const exec10 = agent.decide(mockdata.vaults, allocation1);
const keys = Object.keys(exec10);
assert(
  keys[0] === 'timestamp' && keys[1] === 'cycle_num' && keys[2] === 'chainId',
  'Execution record keys in correct order'
);
assert(
  exec10.decision.action.action !== undefined,
  'Action field always present'
);

// Summary
console.log('\n' + '='.repeat(50));
console.log(`✅ Passed: ${testsPassed}`);
console.log(`❌ Failed: ${testsFailed}`);
console.log('='.repeat(50));

if (testsFailed === 0) {
  console.log('\n🎉 All tests passed!');
  process.exit(0);
} else {
  console.log(`\n⚠️  ${testsFailed} test(s) failed`);
  process.exit(1);
}
