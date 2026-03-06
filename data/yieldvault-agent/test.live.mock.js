#!/usr/bin/env node

/**
 * test.live.mock.js
 * Integration test with mocked blockchain data
 * 
 * Simulates what test.live.js would do when RPC is accessible
 * Useful for validating the integration without live network
 */

const YieldFarmingAgent = require('./index');
const config = require('./config.deployed.json');
const mockdata = require('./mockdata.json');

class MockBlockchainTest {
  constructor() {
    this.results = {
      tests: [],
      errors: [],
      summary: {}
    };
  }

  logTest(name, status, details = {}) {
    const result = {
      name,
      status,
      timestamp: new Date().toISOString(),
      ...details
    };
    this.results.tests.push(result);
    
    const emoji = status === 'PASS' ? '✓' : status === 'FAIL' ? '✗' : '⚠';
    console.log(`${emoji} [${status}] ${name}`);
    if (details.message) console.log(`  → ${details.message}`);
  }

  logError(context, error) {
    const errorRecord = {
      context,
      message: error.message,
      timestamp: new Date().toISOString()
    };
    this.results.errors.push(errorRecord);
    console.error(`✗ ERROR [${context}]: ${error.message}`);
  }

  /**
   * Test 1: Configuration Validation
   */
  testConfiguration() {
    console.log('\n=== TEST 1: Configuration Validation ===');
    try {
      if (!config.contracts || config.contracts.length === 0) {
        throw new Error('No contracts in configuration');
      }
      if (!config.abi || config.abi.length === 0) {
        throw new Error('No ABI in configuration');
      }

      const contractCount = config.contracts.length;
      const eventCount = config.abi.filter(item => item.type === 'event').length;
      
      console.log(`  → Contracts: ${contractCount}`);
      console.log(`  → Contract addresses:`);
      config.contracts.forEach(c => {
        console.log(`    - ${c.vaultId}: ${c.address}`);
      });
      console.log(`  → ABI events: ${eventCount}`);

      // Verify ExecutionRecorded event exists
      const hasExecutionRecorded = config.abi.some(
        item => item.type === 'event' && item.name === 'ExecutionRecorded'
      );

      if (!hasExecutionRecorded) {
        throw new Error('ExecutionRecorded event not found in ABI');
      }

      this.logTest('Configuration Validation', 'PASS', {
        message: `${contractCount} contracts with ${eventCount} events configured`,
        contracts: config.contracts.map(c => ({
          id: c.vaultId,
          address: c.address,
          risk_score: c.risk_score
        }))
      });

      return { success: true };
    } catch (error) {
      this.logError('CONFIG_VALIDATION', error);
      this.logTest('Configuration Validation', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 2: Simulate Live Vault Data
   */
  testMockVaultData() {
    console.log('\n=== TEST 2: Simulate Live Vault Data ===');
    try {
      if (!mockdata.vaults || mockdata.vaults.length === 0) {
        throw new Error('No vaults in mockdata');
      }

      const vaultSummary = mockdata.vaults.map(v => ({
        id: v.id,
        name: v.name,
        apr: `${(v.apr * 100).toFixed(2)}%`,
        risk_score: v.risk_score,
        tvl_usd: `$${v.tvl_usd.toLocaleString()}`
      }));

      console.log(`  → Mock vaults loaded: ${mockdata.vaults.length}`);
      vaultSummary.forEach(v => {
        console.log(`    - ${v.id}: ${v.name}`);
        console.log(`      APR: ${v.apr}, Risk: ${v.risk_score}, TVL: ${v.tvl_usd}`);
      });

      this.logTest('Mock Vault Data', 'PASS', {
        message: `Loaded ${mockdata.vaults.length} mock vaults`,
        vaults: vaultSummary
      });

      return { success: true, vaults: mockdata.vaults };
    } catch (error) {
      this.logError('MOCK_VAULT_DATA', error);
      this.logTest('Mock Vault Data', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 3: Agent Decision Making
   */
  testAgentDecision(vaults) {
    console.log('\n=== TEST 3: Agent Decision Making ===');
    try {
      const currentAllocation = {
        vault_bnb_lp_001: {
          shares: "1000",
          amount_usd: "50000",
          pending_rewards_usd: "1200"
        },
        vault_eth_staking_001: {
          shares: "500",
          amount_usd: "40000",
          pending_rewards_usd: "50"
        },
        vault_usdc_stable_001: {
          shares: "2000",
          amount_usd: "30000",
          pending_rewards_usd: "15"
        }
      };

      const agent = new YieldFarmingAgent(config);
      const execution = agent.decide(vaults, currentAllocation);

      console.log(`  → Agent Decision:`);
      console.log(`    Action: ${execution.decision.action.action}`);
      console.log(`    Best Vault: ${execution.decision.best_vault_id}`);
      console.log(`    Best Net APR: ${(parseFloat(execution.decision.best_vault_net_apr) * 100).toFixed(4)}%`);
      console.log(`    Rationale: ${execution.decision.rationale}`);
      console.log(`    Cycle: ${execution.cycle_num}`);
      console.log(`    Decision Hash: ${execution.decision_hash.substring(0, 16)}...`);
      console.log(`    Execution Hash: ${execution.execution_hash.substring(0, 16)}...`);

      // Verify integrity
      const verification = agent.verifyRecord(execution);
      console.log(`    Hash Verification: ${verification.valid ? '✓' : '✗'}`);

      if (!verification.valid) {
        console.log(`    Errors: ${verification.errors.join(', ')}`);
      }

      this.logTest('Agent Decision', 'PASS', {
        message: `Decision made: ${execution.decision.action.action}`,
        decision_hash_valid: verification.decision_hash_valid,
        execution_hash_valid: verification.execution_hash_valid,
        decision: execution.decision
      });

      return { success: true, execution };
    } catch (error) {
      this.logError('AGENT_DECISION', error);
      this.logTest('Agent Decision', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 4: Hash Verification
   */
  testHashVerification(execution) {
    console.log('\n=== TEST 4: Hash Verification ===');
    try {
      const agent = new YieldFarmingAgent(config);
      const verification = agent.verifyRecord(execution);

      console.log(`  → Decision Hash Valid: ${verification.decision_hash_valid ? '✓' : '✗'}`);
      console.log(`  → Execution Hash Valid: ${verification.execution_hash_valid ? '✓' : '✗'}`);
      console.log(`  → Overall Valid: ${verification.valid ? '✓' : '✗'}`);

      if (!verification.valid) {
        console.log(`  → Errors: ${verification.errors.join(', ')}`);
      }

      this.logTest('Hash Verification', verification.valid ? 'PASS' : 'FAIL', {
        message: verification.valid ? 'All hashes verified' : verification.errors.join(', '),
        decision_hash_valid: verification.decision_hash_valid,
        execution_hash_valid: verification.execution_hash_valid
      });

      return { success: verification.valid };
    } catch (error) {
      this.logError('HASH_VERIFICATION', error);
      this.logTest('Hash Verification', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 5: Event ABI Validation
   */
  testEventAbiValidation() {
    console.log('\n=== TEST 5: Event ABI Validation ===');
    try {
      const events = config.abi.filter(item => item.type === 'event');
      const expectedEvents = [
        'ExecutionRecorded',
        'ActionExecuted',
        'Deposit',
        'Harvest',
        'Withdraw',
        'Compound'
      ];

      const foundEvents = events.map(e => e.name);
      const missingEvents = expectedEvents.filter(e => !foundEvents.includes(e));

      console.log(`  → Events found: ${foundEvents.length}`);
      foundEvents.forEach(e => {
        console.log(`    ✓ ${e}`);
      });

      if (missingEvents.length > 0) {
        console.log(`  → Missing events: ${missingEvents.join(', ')}`);
      }

      const executionRecordedEvent = events.find(e => e.name === 'ExecutionRecorded');
      if (executionRecordedEvent) {
        console.log(`  → ExecutionRecorded event signature:`);
        executionRecordedEvent.inputs.forEach(input => {
          console.log(`    - ${input.name} (${input.type})`);
        });
      }

      this.logTest('Event ABI Validation', missingEvents.length === 0 ? 'PASS' : 'WARN', {
        message: `Found ${foundEvents.length}/${expectedEvents.length} expected events`,
        found_events: foundEvents,
        missing_events: missingEvents
      });

      return { success: true };
    } catch (error) {
      this.logError('EVENT_ABI_VALIDATION', error);
      this.logTest('Event ABI Validation', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 6: Risk Filter Test
   */
  testRiskFilter(vaults) {
    console.log('\n=== TEST 6: Risk Filter Test ===');
    try {
      const riskThreshold = 0.5;
      const filtered = vaults.filter(v => v.risk_score <= riskThreshold);
      const filtered_out = vaults.filter(v => v.risk_score > riskThreshold);

      console.log(`  → Risk threshold: ${riskThreshold}`);
      console.log(`  → Vaults within threshold: ${filtered.length}`);
      filtered.forEach(v => {
        console.log(`    ✓ ${v.id} (risk: ${v.risk_score})`);
      });

      if (filtered_out.length > 0) {
        console.log(`  → Vaults filtered out: ${filtered_out.length}`);
        filtered_out.forEach(v => {
          console.log(`    ✗ ${v.id} (risk: ${v.risk_score})`);
        });
      }

      this.logTest('Risk Filter', filtered.length > 0 ? 'PASS' : 'FAIL', {
        message: `${filtered.length} vaults pass risk filter`,
        passed: filtered.map(v => v.id),
        filtered: filtered_out.map(v => v.id)
      });

      return { success: filtered.length > 0 };
    } catch (error) {
      this.logError('RISK_FILTER', error);
      this.logTest('Risk Filter', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Run all tests
   */
  async runAll() {
    console.log('╔══════════════════════════════════════════════════════╗');
    console.log('║   YIELD FARMING AGENT - MOCK INTEGRATION TEST        ║');
    console.log('║   Mode: Offline (no RPC connectivity required)       ║');
    console.log('║   Network: BNB Testnet (ChainID: 97)                 ║');
    console.log('╚══════════════════════════════════════════════════════╝');

    const startTime = Date.now();

    // Test 1
    const configTest = await this.testConfiguration();
    if (!configTest.success) {
      this.summarize(startTime);
      return;
    }

    // Test 2
    const vaultTest = this.testMockVaultData();
    if (!vaultTest.success) {
      this.summarize(startTime);
      return;
    }

    // Test 3
    const decisionTest = this.testAgentDecision(vaultTest.vaults);
    if (!decisionTest.success) {
      this.summarize(startTime);
      return;
    }

    // Test 4
    await this.testHashVerification(decisionTest.execution);

    // Test 5
    await this.testEventAbiValidation();

    // Test 6
    await this.testRiskFilter(vaultTest.vaults);

    this.summarize(startTime);
  }

  /**
   * Generate test summary
   */
  summarize(startTime) {
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    const passed = this.results.tests.filter(t => t.status === 'PASS').length;
    const failed = this.results.tests.filter(t => t.status === 'FAIL').length;
    const warned = this.results.tests.filter(t => t.status === 'WARN').length;

    console.log('\n╔══════════════════════════════════════════════════════╗');
    console.log('║   TEST SUMMARY                                       ║');
    console.log('╚══════════════════════════════════════════════════════╝');
    console.log(`Total Tests: ${this.results.tests.length}`);
    console.log(`✓ Passed: ${passed}`);
    console.log(`✗ Failed: ${failed}`);
    console.log(`⚠ Warned: ${warned}`);
    console.log(`Duration: ${duration}s`);
    console.log(`\nStatus: ${failed === 0 ? '✓ ALL TESTS PASSED' : `✗ ${failed} TESTS FAILED`}`);

    if (this.results.errors.length > 0) {
      console.log(`\nErrors (${this.results.errors.length}):`);
      this.results.errors.forEach((err, i) => {
        console.log(`  ${i + 1}. [${err.context}] ${err.message}`);
      });
    }

    console.log('\n=== TEST RESULTS JSON ===');
    console.log(JSON.stringify({
      summary: {
        total: this.results.tests.length,
        passed,
        failed,
        warned,
        duration_seconds: parseFloat(duration),
        status: failed === 0 ? 'PASSED' : 'FAILED'
      },
      tests: this.results.tests,
      errors: this.results.errors.slice(0, 5)
    }, null, 2));
  }
}

// Run tests
if (require.main === module) {
  const test = new MockBlockchainTest();
  test.runAll().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = MockBlockchainTest;
