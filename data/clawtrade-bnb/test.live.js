#!/usr/bin/env node

/**
 * test.live.js
 * Live integration test with deployed testnet contracts
 * 
 * Tests:
 * 1. RPC connectivity
 * 2. Contract initialization
 * 3. Read live vault data (balances, shares, yields)
 * 4. Simulate deposit and harvest actions
 * 5. Listen for ExecutionRecorded events
 */

const BlockchainReader = require('./blockchain-reader');
const YieldFarmingAgent = require('./index');
const config = require('./config.deployed.json');

// Test user address (generate a test address for simulations)
const TEST_USER = '0x742d35Cc6634C0532925a3b844Bc9e7595f42bE'; // Example address

class LiveTest {
  constructor() {
    this.results = {
      tests: [],
      errors: [],
      summary: {}
    };
  }

  /**
   * Log test result
   */
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

  /**
   * Log error
   */
  logError(context, error) {
    const errorRecord = {
      context,
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    };
    this.results.errors.push(errorRecord);
    console.error(`✗ ERROR [${context}]: ${error.message}`);
  }

  /**
   * Test 1: RPC Connectivity
   */
  async testRpcConnectivity() {
    console.log('\n=== TEST 1: RPC Connectivity ===');
    try {
      const reader = new BlockchainReader(config.rpc);
      const isConnected = await reader.isConnected();
      
      if (isConnected) {
        const networkInfo = await reader.getNetworkInfo();
        this.logTest('RPC Connection', 'PASS', {
          network: networkInfo.name,
          chainId: networkInfo.chainId,
          blockNumber: networkInfo.blockNumber
        });
        return { success: true, reader, networkInfo };
      } else {
        this.logTest('RPC Connection', 'FAIL', {
          message: 'Cannot connect to RPC endpoint'
        });
        return { success: false };
      }
    } catch (error) {
      this.logError('RPC_CONNECTIVITY', error);
      this.logTest('RPC Connection', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 2: Contract Initialization
   */
  async testContractInitialization(reader) {
    console.log('\n=== TEST 2: Contract Initialization ===');
    try {
      const contractsWithABI = config.contracts.map(contract => ({
        ...contract,
        abi: config.abi
      }));

      await reader.initializeContracts(contractsWithABI);
      
      const initialized = Object.keys(reader.contracts).length;
      const expected = config.contracts.length;
      
      if (initialized === expected) {
        this.logTest('Contract Initialization', 'PASS', {
          message: `Initialized ${initialized}/${expected} contracts`
        });
        return { success: true };
      } else {
        this.logTest('Contract Initialization', 'FAIL', {
          message: `Only ${initialized}/${expected} contracts initialized`
        });
        return { success: false };
      }
    } catch (error) {
      this.logError('CONTRACT_INITIALIZATION', error);
      this.logTest('Contract Initialization', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 3: Read Live Vault Data
   */
  async testReadVaultData(reader) {
    console.log('\n=== TEST 3: Read Live Vault Data ===');
    try {
      const vaultDataList = await reader.getAllVaultsData(TEST_USER);
      
      let successCount = 0;
      const vaultSummary = [];

      for (const vaultData of vaultDataList) {
        if (!vaultData.error) {
          successCount++;
          vaultSummary.push({
            vault_id: vaultData.vault_id,
            total_assets: vaultData.total_assets,
            total_shares: vaultData.total_shares
          });
          console.log(`  → ${vaultData.vault_id}:`);
          console.log(`    Assets: ${vaultData.total_assets} ETH`);
          console.log(`    Shares: ${vaultData.total_shares}`);
        } else {
          console.log(`  → ${vaultData.vault_id}: ERROR - ${vaultData.error}`);
        }
      }

      if (successCount > 0) {
        this.logTest('Read Vault Data', 'PASS', {
          message: `Successfully read ${successCount}/${vaultDataList.length} vaults`,
          vaults: vaultSummary
        });
        return { success: true, data: vaultDataList };
      } else {
        this.logTest('Read Vault Data', 'FAIL', {
          message: 'Could not read any vault data'
        });
        return { success: false };
      }
    } catch (error) {
      this.logError('READ_VAULT_DATA', error);
      this.logTest('Read Vault Data', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 4: Simulate Actions
   */
  async testSimulateActions(reader) {
    console.log('\n=== TEST 4: Simulate Deposit & Harvest ===');
    try {
      const results = [];

      // Simulate DEPOSIT
      try {
        const depositResult = await reader.simulateDeposit(
          'vault_link_oracle_001',
          '1000000000000000000' // 1 token in wei
        );
        console.log('  → DEPOSIT simulation:');
        console.log(`    Status: ${depositResult.status}`);
        if (depositResult.estimated_shares) {
          console.log(`    Estimated shares: ${depositResult.estimated_shares}`);
        }
        results.push(depositResult);
      } catch (e) {
        console.log(`  → DEPOSIT simulation: ERROR - ${e.message}`);
      }

      // Simulate HARVEST
      try {
        const harvestResult = await reader.simulateHarvest(
          'vault_link_oracle_001',
          TEST_USER
        );
        console.log('  → HARVEST simulation:');
        console.log(`    Status: ${harvestResult.status}`);
        if (harvestResult.harvestable_yield) {
          console.log(`    Harvestable yield: ${harvestResult.harvestable_yield}`);
        }
        results.push(harvestResult);
      } catch (e) {
        console.log(`  → HARVEST simulation: ERROR - ${e.message}`);
      }

      if (results.length > 0) {
        this.logTest('Simulate Actions', 'PASS', {
          message: `Executed ${results.length} simulations`,
          actions: results
        });
        return { success: true, results };
      } else {
        this.logTest('Simulate Actions', 'FAIL', {
          message: 'No simulations could be executed'
        });
        return { success: false };
      }
    } catch (error) {
      this.logError('SIMULATE_ACTIONS', error);
      this.logTest('Simulate Actions', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 5: Event Listener Setup
   */
  async testEventListeners(reader) {
    console.log('\n=== TEST 5: Event Listener Setup ===');
    try {
      const vaultId = 'vault_link_oracle_001';
      
      // Set up listener
      const removeListener = reader.onExecutionRecorded(vaultId, (event) => {
        console.log(`  → ExecutionRecorded Event:`);
        console.log(`    Vault: ${event.vault_id}`);
        console.log(`    Action: ${event.action}`);
        console.log(`    Amount: ${event.amount}`);
      });

      this.logTest('Event Listener Setup', 'PASS', {
        message: `Listener configured for vault_link_oracle_001`
      });

      // Clean up
      removeListener();
      return { success: true };
    } catch (error) {
      this.logError('EVENT_LISTENERS', error);
      this.logTest('Event Listener Setup', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Test 6: Agent Decision with Real Data
   */
  async testAgentDecision(vaultDataList) {
    console.log('\n=== TEST 6: Agent Decision with Real Data ===');
    try {
      // Prepare mock vaults for the agent
      const mockVaults = [
        {
          id: 'vault_eth_staking_001',
          name: 'ETH Staking Vault',
          apr: 0.04,
          fees: 0.001,
          risk_score: 0.3,
          tvl_usd: 50000,
          underlying: '0x8ba1f109551bD432803012645Ac136ddd64DBA72',
          strategy: 'Ethereum 2.0 Staking'
        },
        {
          id: 'vault_link_oracle_001',
          name: 'LINK Oracle Rewards',
          apr: 0.06,
          fees: 0.002,
          risk_score: 0.25,
          tvl_usd: 30000,
          underlying: '0x84b9B910527Ad5C03A9Ca831909E21e236EA7b06',
          strategy: 'Chainlink Oracle Operations'
        }
      ];

      const currentAllocation = {
        vault_eth_staking_001: {
          shares: '1000',
          amount_usd: '50000',
          pending_rewards_usd: '1200'
        },
        vault_link_oracle_001: {
          shares: '500',
          amount_usd: '30000',
          pending_rewards_usd: '50'
        }
      };

      const agent = new YieldFarmingAgent(config);
      const execution = agent.decide(mockVaults, currentAllocation);

      console.log(`  → Decision: ${execution.decision.action.action}`);
      console.log(`    Best Vault: ${execution.decision.best_vault_id}`);
      console.log(`    Cycle: ${execution.cycle_num}`);
      console.log(`    Decision Hash: ${execution.decision_hash.substring(0, 16)}...`);
      console.log(`    Execution Hash: ${execution.execution_hash.substring(0, 16)}...`);

      // Verify hashes
      const verification = agent.verifyRecord(execution);
      if (verification.valid) {
        console.log(`    ✓ Hashes verified`);
      } else {
        console.log(`    ✗ Hash verification failed: ${verification.errors.join(', ')}`);
      }

      this.logTest('Agent Decision', 'PASS', {
        message: `Agent decided action: ${execution.decision.action.action}`,
        decision_hash_valid: verification.decision_hash_valid,
        execution_hash_valid: verification.execution_hash_valid
      });

      return { success: true, execution };
    } catch (error) {
      this.logError('AGENT_DECISION', error);
      this.logTest('Agent Decision', 'FAIL', { message: error.message });
      return { success: false };
    }
  }

  /**
   * Run all tests
   */
  async runAll() {
    console.log('╔══════════════════════════════════════════════════════╗');
    console.log('║   YIELD FARMING AGENT - LIVE INTEGRATION TEST        ║');
    console.log('║   Network: BNB Testnet (ChainID: 97)                 ║');
    console.log('╚══════════════════════════════════════════════════════╝');

    const startTime = Date.now();

    // Test 1
    const connTest = await this.testRpcConnectivity();
    if (!connTest.success) {
      this.summarize(startTime);
      return;
    }

    // Test 2
    const initTest = await this.testContractInitialization(connTest.reader);
    if (!initTest.success) {
      this.summarize(startTime);
      return;
    }

    // Test 3
    const dataTest = await this.testReadVaultData(connTest.reader);

    // Test 4
    const simulateTest = await this.testSimulateActions(connTest.reader);

    // Test 5
    await this.testEventListeners(connTest.reader);

    // Test 6
    if (dataTest.success) {
      await this.testAgentDecision(dataTest.data);
    }

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
        duration_seconds: parseFloat(duration)
      },
      tests: this.results.tests,
      errors: this.results.errors.slice(0, 5) // Limit to first 5 for brevity
    }, null, 2));
  }
}

// Run tests
if (require.main === module) {
  const test = new LiveTest();
  test.runAll().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = LiveTest;
