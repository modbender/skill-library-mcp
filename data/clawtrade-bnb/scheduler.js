/**
 * AutonomousScheduler
 * Executes agent decision cycle on schedule
 * Reads blockchain data → calculates decision → executes transactions
 */
const fs = require('fs');
const path = require('path');
const YieldFarmingAgent = require('./index');
const BlockchainReader = require('./blockchain-reader');
const TransactionExecutor = require('./tx-executor');

class AutonomousScheduler {
  constructor(config = {}) {
    // Load default scheduler config
    const defaultSchedulerConfig = {
      execution_interval_seconds: 3600, // 1 hour
      enabled: true,
      timezone: 'UTC',
      max_concurrent_executions: 1,
      retry_failed_cycles: true,
      retry_delay_seconds: 300
    };

    this.config = { ...defaultSchedulerConfig, ...config };
    this.agent = new YieldFarmingAgent(config.agent || {});
    this.reader = new BlockchainReader(config.rpcUrl, config.reader || {});
    this.executor = new TransactionExecutor(config.executor || {});

    this.isRunning = false;
    this.cycleNumber = 0;
    this.lastCycleTimestamp = null;
    this.cycleHistory = [];
    this.schedulerIntervalId = null;
  }

  /**
   * Initialize scheduler dependencies
   * @param {Array} contracts - Contract metadata array
   * @param {Array} vaults - Vault configuration array
   */
  async initialize(contracts, vaults) {
    console.log('\n🔧 Initializing Autonomous Scheduler...');
    
    try {
      await this.reader.initializeContracts(contracts);
      console.log('✓ BlockchainReader initialized');
    } catch (error) {
      console.error('✗ BlockchainReader initialization failed:', error.message);
      throw error;
    }

    try {
      await this.executor.initializeContracts(contracts);
      console.log('✓ TransactionExecutor initialized');
    } catch (error) {
      console.error('✗ TransactionExecutor initialization failed:', error.message);
      throw error;
    }

    this.vaults = vaults;
    this.contracts = contracts;
    console.log('✓ Scheduler fully initialized');
  }

  /**
   * Start the autonomous execution loop
   */
  start() {
    if (this.isRunning) {
      console.warn('⚠ Scheduler is already running');
      return;
    }

    console.log('\n▶️  STARTING AUTONOMOUS SCHEDULER');
    console.log(`   Interval: ${this.config.execution_interval_seconds} seconds (${(this.config.execution_interval_seconds / 60).toFixed(1)} min)`);
    console.log(`   Timezone: ${this.config.timezone}`);
    console.log(`   Status: ENABLED\n`);

    this.isRunning = true;

    // Execute first cycle immediately
    this.executeCycle();

    // Set up periodic execution
    this.schedulerIntervalId = setInterval(() => {
      if (this.isRunning) {
        this.executeCycle();
      }
    }, this.config.execution_interval_seconds * 1000);
  }

  /**
   * Stop the autonomous execution loop
   */
  stop() {
    if (!this.isRunning) {
      console.warn('⚠ Scheduler is not running');
      return;
    }

    console.log('\n⏹️  STOPPING AUTONOMOUS SCHEDULER');
    this.isRunning = false;

    if (this.schedulerIntervalId) {
      clearInterval(this.schedulerIntervalId);
      this.schedulerIntervalId = null;
    }

    console.log('✓ Scheduler stopped\n');
  }

  /**
   * Execute a single decision cycle
   * Step 1: Read blockchain data
   * Step 2: Calculate agent decision
   * Step 3: Execute transactions
   * Step 4: Log results
   */
  async executeCycle() {
    this.cycleNumber++;
    const cycleId = `cycle_${this.cycleNumber}_${Date.now()}`;
    const cycleStartTime = new Date();
    const cycleTimestamp = cycleStartTime.toISOString();

    console.log(`\n${'='.repeat(70)}`);
    console.log(`📊 DECISION CYCLE #${this.cycleNumber}`);
    console.log(`   ID: ${cycleId}`);
    console.log(`   Time: ${cycleTimestamp}`);
    console.log(`${'='.repeat(70)}`);

    const cycleRecord = {
      cycle_id: cycleId,
      cycle_number: this.cycleNumber,
      start_time: cycleTimestamp,
      end_time: null,
      duration_ms: null,
      status: 'RUNNING',
      steps: [],
      decision: null,
      executions: [],
      errors: []
    };

    try {
      // STEP 1: Read blockchain data
      console.log('\n[1/4] 📡 Reading blockchain data...');
      const vaultDataStep = await this.executeStep('READ_BLOCKCHAIN', async () => {
        const vaultData = {};
        
        for (const vault of this.vaults) {
          try {
            const data = await this.reader.getVaultData(vault.id);
            vaultData[vault.id] = {
              id: vault.id,
              apr: vault.apr,
              fees: vault.fees,
              risk_score: vault.risk_score,
              tvl: data.total_assets,
              user_shares: data.user_data.shares,
              user_amount: data.user_data.amount_usd,
              user_pending_rewards: data.user_data.pending_rewards_usd,
              timestamp: data.timestamp
            };
            console.log(`  ✓ ${vault.id}: TVL ${data.total_assets} | Pending ${data.user_data.pending_rewards_usd}`);
          } catch (error) {
            console.error(`  ✗ Failed to read ${vault.id}: ${error.message}`);
            throw error;
          }
        }
        
        return vaultData;
      });

      if (!vaultDataStep.success) {
        throw new Error(`Blockchain read failed: ${vaultDataStep.error}`);
      }

      cycleRecord.steps.push(vaultDataStep);
      const vaultData = vaultDataStep.result;

      // STEP 2: Calculate agent decision
      console.log('\n[2/4] 🤖 Calculating agent decision...');
      const decisionStep = await this.executeStep('CALCULATE_DECISION', async () => {
        // Get current allocation from vault data
        const currentAllocation = {};
        Object.entries(vaultData).forEach(([vaultId, data]) => {
          currentAllocation[vaultId] = {
            shares: data.user_shares,
            amount_usd: data.user_amount,
            pending_rewards_usd: data.user_pending_rewards
          };
        });

        // Run agent decision
        const vaultArray = Object.values(vaultData);
        const decision = this.agent.decide(vaultArray, currentAllocation);
        
        console.log(`  ✓ Decision calculated`);
        console.log(`  ├─ Recommendation: ${decision.recommended_action}`);
        console.log(`  ├─ Target vault: ${decision.target_vault_id}`);
        console.log(`  ├─ Confidence: ${(decision.confidence_score * 100).toFixed(1)}%`);
        console.log(`  └─ Risk: ${(decision.rebalance_risk * 100).toFixed(1)}%`);

        return decision;
      });

      if (!decisionStep.success) {
        throw new Error(`Decision calculation failed: ${decisionStep.error}`);
      }

      cycleRecord.steps.push(decisionStep);
      const decision = decisionStep.result;
      cycleRecord.decision = decision;

      // STEP 3: Execute transactions (if recommended)
      console.log('\n[3/4] 💾 Executing transactions...');
      const executionStep = await this.executeStep('EXECUTE_TRANSACTIONS', async () => {
        const executions = [];

        // Determine actions based on decision
        const actions = this.buildExecutionActions(decision, vaultData);

        if (actions.length === 0) {
          console.log('  ℹ️  No actions recommended - holding position');
          return [];
        }

        for (const action of actions) {
          try {
            console.log(`\n  → Executing: ${action.type} on ${action.vault_id}`);
            
            // Estimate gas first
            const gasEstimate = await this.executor.estimateGas(
              action.type,
              action.vault_id,
              action.params
            );
            console.log(`    Gas estimate: ${gasEstimate.estimated_cost_eth} ETH`);

            // Execute transaction
            const result = await this.executor.execute(
              action.type,
              action.vault_id,
              action.params
            );

            executions.push(result);
            console.log(`    Result: ${result.status}`);
            
            if (result.status === 'SUCCESS') {
              console.log(`    TxHash: ${result.details.tx_hash}`);
            } else {
              console.log(`    Error: ${result.details.error}`);
            }
          } catch (error) {
            console.error(`  ✗ Execution failed: ${error.message}`);
            executions.push({
              action: action.type,
              vault_id: action.vault_id,
              status: 'FAILED',
              error: error.message
            });
          }
        }

        return executions;
      });

      if (!executionStep.success) {
        console.error(`Transaction execution failed: ${executionStep.error}`);
      }

      cycleRecord.steps.push(executionStep);
      cycleRecord.executions = executionStep.result || [];

      // STEP 4: Log and report
      console.log('\n[4/4] 📝 Logging cycle results...');
      const loggingStep = await this.executeStep('LOG_RESULTS', async () => {
        this.logCycle(cycleRecord);
        console.log('  ✓ Cycle logged successfully');
        return cycleRecord;
      });

      cycleRecord.steps.push(loggingStep);

      // Mark cycle as complete
      cycleRecord.status = 'SUCCESS';
      cycleRecord.end_time = new Date().toISOString();
      cycleRecord.duration_ms = new Date(cycleRecord.end_time).getTime() - cycleStartTime.getTime();

      console.log(`\n✅ CYCLE COMPLETE`);
      console.log(`   Duration: ${cycleRecord.duration_ms}ms`);
      console.log(`   Executions: ${cycleRecord.executions.length}`);
      console.log(`   Status: ${cycleRecord.status}\n`);

    } catch (error) {
      console.error(`\n❌ CYCLE FAILED: ${error.message}\n`);
      
      cycleRecord.status = 'FAILED';
      cycleRecord.end_time = new Date().toISOString();
      cycleRecord.duration_ms = new Date(cycleRecord.end_time).getTime() - cycleStartTime.getTime();
      cycleRecord.errors.push({
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString()
      });

      // Log failed cycle
      this.logCycle(cycleRecord);

      // Trigger retry if configured
      if (this.config.retry_failed_cycles) {
        console.log(`⏳ Will retry failed cycle in ${this.config.retry_delay_seconds} seconds...\n`);
        setTimeout(() => this.executeCycle(), this.config.retry_delay_seconds * 1000);
      }
    }

    this.lastCycleTimestamp = new Date();
  }

  /**
   * Execute a step with error handling
   * @param {string} stepName - Step name
   * @param {Function} stepFunction - Async function to execute
   * @returns {Object} Step result with status and timing
   */
  async executeStep(stepName, stepFunction) {
    const startTime = Date.now();
    
    try {
      const result = await stepFunction();
      const duration = Date.now() - startTime;
      
      return {
        step: stepName,
        status: 'SUCCESS',
        result,
        duration_ms: duration,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      
      return {
        step: stepName,
        status: 'FAILED',
        error: error.message,
        duration_ms: duration,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Build execution actions from agent decision
   * @param {Object} decision - Agent decision object
   * @param {Object} vaultData - Current vault data
   * @returns {Array} Array of action objects to execute
   */
  buildExecutionActions(decision, vaultData) {
    const actions = [];

    // If confidence is too low, don't execute
    if (decision.confidence_score < 0.6) {
      console.log('  ℹ️  Confidence too low - skipping execution');
      return actions;
    }

    // If risk is too high, don't execute
    if (decision.rebalance_risk > 0.3) {
      console.log('  ℹ️  Risk too high - skipping execution');
      return actions;
    }

    switch (decision.recommended_action) {
      case 'HARVEST':
        // Harvest rewards from high-yield vault
        if (vaultData[decision.target_vault_id]) {
          const pendingRewards = parseFloat(
            vaultData[decision.target_vault_id].user_pending_rewards || 0
          );
          
          if (pendingRewards > 0.1) { // Only harvest if rewards > 0.1 units
            actions.push({
              type: 'HARVEST',
              vault_id: decision.target_vault_id,
              params: {
                amount: pendingRewards.toString()
              }
            });
          }
        }
        break;

      case 'COMPOUND':
        // Compound rewards back into vault
        if (vaultData[decision.target_vault_id]) {
          actions.push({
            type: 'COMPOUND',
            vault_id: decision.target_vault_id,
            params: {
              min_output_amount: '0'
            }
          });
        }
        break;

      case 'REBALANCE':
        // Move funds from lower-yield to higher-yield vault
        if (decision.from_vault_id && decision.to_vault_id) {
          const fromVault = vaultData[decision.from_vault_id];
          const toVault = vaultData[decision.to_vault_id];
          
          if (fromVault && toVault) {
            const rebalanceAmount = (
              parseFloat(fromVault.user_amount || 0) * 0.25 // Move 25%
            ).toString();

            actions.push({
              type: 'WITHDRAW',
              vault_id: decision.from_vault_id,
              params: {
                shares_to_withdraw: rebalanceAmount
              }
            });

            actions.push({
              type: 'DEPOSIT',
              vault_id: decision.to_vault_id,
              params: {
                amount: rebalanceAmount
              }
            });
          }
        }
        break;

      case 'HOLD':
      default:
        // No action
        break;
    }

    return actions;
  }

  /**
   * Log cycle to file and history
   * @param {Object} cycleRecord - Complete cycle record
   */
  logCycle(cycleRecord) {
    this.cycleHistory.push(cycleRecord);

    // Keep only last 100 cycles in memory
    if (this.cycleHistory.length > 100) {
      this.cycleHistory = this.cycleHistory.slice(-100);
    }

    // Persist to file
    const logsPath = path.join(__dirname, 'scheduler.cycles.log.json');
    try {
      let allCycles = [];
      if (fs.existsSync(logsPath)) {
        const content = fs.readFileSync(logsPath, 'utf8');
        allCycles = JSON.parse(content || '[]');
      }
      
      allCycles.push(cycleRecord);
      
      // Keep last 500 cycles
      if (allCycles.length > 500) {
        allCycles = allCycles.slice(-500);
      }
      
      fs.writeFileSync(logsPath, JSON.stringify(allCycles, null, 2));
    } catch (error) {
      console.error(`Failed to write cycle log: ${error.message}`);
    }
  }

  /**
   * Get cycle history
   * @param {number} limit - Number of recent cycles
   * @returns {Array} Recent cycle records
   */
  getCycleHistory(limit = 20) {
    return this.cycleHistory.slice(-limit);
  }

  /**
   * Get scheduler status
   * @returns {Object} Current status information
   */
  getStatus() {
    return {
      is_running: this.isRunning,
      cycle_number: this.cycleNumber,
      last_cycle_time: this.lastCycleTimestamp,
      interval_seconds: this.config.execution_interval_seconds,
      cycle_history_length: this.cycleHistory.length,
      status: this.isRunning ? 'RUNNING' : 'STOPPED',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get summary statistics
   * @returns {Object} Summary stats from recent cycles
   */
  getStats() {
    const recentCycles = this.cycleHistory.slice(-20);
    const successCount = recentCycles.filter(c => c.status === 'SUCCESS').length;
    const failureCount = recentCycles.filter(c => c.status === 'FAILED').length;
    const avgDuration = recentCycles.length > 0
      ? recentCycles.reduce((sum, c) => sum + (c.duration_ms || 0), 0) / recentCycles.length
      : 0;

    const totalExecutions = recentCycles.reduce(
      (sum, c) => sum + (c.executions || []).length,
      0
    );

    return {
      recent_cycles: recentCycles.length,
      success_count: successCount,
      failure_count: failureCount,
      success_rate: recentCycles.length > 0 ? (successCount / recentCycles.length * 100).toFixed(1) : 'N/A',
      average_cycle_duration_ms: avgDuration.toFixed(0),
      total_executions: totalExecutions,
      timestamp: new Date().toISOString()
    };
  }
}

module.exports = AutonomousScheduler;
