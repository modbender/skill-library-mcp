/**
 * TransactionExecutor
 * Executes blockchain actions (DEPOSIT, WITHDRAW, HARVEST, COMPOUND, REBALANCE)
 * Signs transactions with wallet private key and handles confirmations
 */
const ethers = require('ethers');
const fs = require('fs');
const path = require('path');

class TransactionExecutor {
  constructor(config = {}) {
    this.config = config;
    this.provider = new ethers.providers.JsonRpcProvider(
      config.rpcUrl || 'https://data-seed-prebsc-1-b.binance.org:8545'
    );
    
    // Initialize wallet from private key
    if (config.walletPrivateKey) {
      this.wallet = new ethers.Wallet(config.walletPrivateKey, this.provider);
      this.walletAddress = this.wallet.address;
      console.log(`✓ Wallet initialized: ${this.walletAddress}`);
    } else {
      console.warn('⚠ Wallet not initialized - private key not provided');
    }
    
    this.contracts = {};
    this.executionLog = [];
  }

  /**
   * Initialize contract instances for execution
   * @param {Array} contracts - Array of contract metadata { address, abi, vaultId }
   */
  async initializeContracts(contracts) {
    for (const contract of contracts) {
      try {
        // Create contract instance bound to signer (wallet)
        this.contracts[contract.vaultId] = new ethers.Contract(
          contract.address,
          contract.abi,
          this.wallet
        );
        console.log(`✓ Contract initialized for execution: ${contract.vaultId}`);
      } catch (error) {
        console.error(`✗ Failed to initialize contract ${contract.vaultId}:`, error.message);
        throw error;
      }
    }
  }

  /**
   * Execute transaction with retry logic
   * @param {string} action - Action type: DEPOSIT, WITHDRAW, HARVEST, COMPOUND, REBALANCE
   * @param {string} vaultId - Vault ID
   * @param {Object} params - Transaction parameters { amount, data, etc }
   * @param {number} maxRetries - Maximum retry attempts (default 3)
   * @returns {Object} Execution result with tx hash and confirmation
   */
  async execute(action, vaultId, params = {}, maxRetries = 3) {
    const executionId = this.generateExecutionId();
    const timestamp = new Date().toISOString();
    
    console.log(`\n→ EXECUTION START: ${action} on ${vaultId}`);
    console.log(`  ID: ${executionId} | Time: ${timestamp}`);

    if (!this.wallet) {
      const error = 'Wallet not initialized - cannot execute transactions';
      return this.logExecution(executionId, action, vaultId, 'FAILED', {
        error,
        timestamp
      });
    }

    const contract = this.contracts[vaultId];
    if (!contract) {
      const error = `Contract not initialized for ${vaultId}`;
      return this.logExecution(executionId, action, vaultId, 'FAILED', {
        error,
        timestamp
      });
    }

    let lastError;
    let txHash;
    let receipt;

    // Retry loop
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`  Attempt ${attempt}/${maxRetries}...`);

        let tx;
        switch (action) {
          case 'DEPOSIT':
            // params: { amount, token_address }
            tx = await contract.deposit(
              ethers.utils.parseEther(params.amount || '0'),
              { gasLimit: 500000 }
            );
            console.log(`  → Deposit tx initiated`);
            break;

          case 'WITHDRAW':
            // params: { shares_to_withdraw }
            tx = await contract.withdraw(
              ethers.utils.parseEther(params.shares_to_withdraw || '0'),
              { gasLimit: 500000 }
            );
            console.log(`  → Withdraw tx initiated`);
            break;

          case 'HARVEST':
            // Harvest accumulated rewards
            tx = await contract.harvest({ gasLimit: 300000 });
            console.log(`  → Harvest tx initiated`);
            break;

          case 'COMPOUND':
            // params: { min_output_amount }
            tx = await contract.compound(
              ethers.utils.parseEther(params.min_output_amount || '0'),
              { gasLimit: 400000 }
            );
            console.log(`  → Compound tx initiated`);
            break;

          case 'REBALANCE':
            // params: { from_vault, to_vault, amount }
            // Note: This would be a custom transaction across vaults
            tx = await contract.rebalance(
              params.from_vault || '',
              params.to_vault || '',
              ethers.utils.parseEther(params.amount || '0'),
              { gasLimit: 500000 }
            );
            console.log(`  → Rebalance tx initiated`);
            break;

          default:
            throw new Error(`Unknown action: ${action}`);
        }

        txHash = tx.hash;
        console.log(`  ✓ Tx sent: ${txHash}`);

        // Wait for confirmation with timeout
        console.log(`  ⏳ Waiting for confirmation...`);
        receipt = await this.waitForConfirmation(txHash, 40); // Max 40 blocks

        if (receipt.status === 1) {
          const result = {
            status: 'SUCCESS',
            tx_hash: txHash,
            block_number: receipt.blockNumber,
            gas_used: receipt.gasUsed.toString(),
            confirmation_time: new Date().toISOString(),
            timestamp
          };
          console.log(`  ✓ SUCCESS: ${action} confirmed`);
          return this.logExecution(executionId, action, vaultId, 'SUCCESS', result);
        } else {
          lastError = 'Transaction reverted (status 0)';
          console.log(`  ⚠ Attempt ${attempt}: ${lastError}`);
        }
      } catch (error) {
        lastError = error.message;
        console.log(`  ⚠ Attempt ${attempt} failed: ${lastError}`);

        // Check if error is retryable
        if (this.isRetryableError(error) && attempt < maxRetries) {
          const backoffMs = Math.pow(2, attempt - 1) * 3000; // Exponential backoff
          console.log(`  ⏳ Backing off ${backoffMs}ms before retry...`);
          await this.sleep(backoffMs);
        } else if (attempt === maxRetries) {
          console.log(`  ✗ FAILED after ${maxRetries} attempts`);
        } else {
          throw error;
        }
      }
    }

    // All retries exhausted
    const finalResult = {
      status: 'FAILED',
      error: lastError,
      attempts: maxRetries,
      tx_hash: txHash || null,
      timestamp
    };
    console.log(`  ✗ Execution failed: ${lastError}`);
    return this.logExecution(executionId, action, vaultId, 'FAILED', finalResult);
  }

  /**
   * Wait for transaction confirmation with timeout
   * @param {string} txHash - Transaction hash
   * @param {number} maxBlocks - Maximum blocks to wait
   * @returns {Object} Transaction receipt
   */
  async waitForConfirmation(txHash, maxBlocks = 40) {
    const startBlock = await this.provider.getBlockNumber();
    let receipt = null;

    while (true) {
      receipt = await this.provider.getTransactionReceipt(txHash);
      
      if (receipt) {
        return receipt;
      }

      const currentBlock = await this.provider.getBlockNumber();
      if (currentBlock - startBlock > maxBlocks) {
        throw new Error(`Transaction confirmation timeout after ${maxBlocks} blocks`);
      }

      // Wait before polling again
      await this.sleep(2000); // 2 second poll interval
    }
  }

  /**
   * Check if error is retryable
   * @param {Error} error - Error object
   * @returns {boolean} Whether error should trigger a retry
   */
  isRetryableError(error) {
    const message = error.message.toLowerCase();
    const retryableErrors = [
      'nonce',
      'gas price',
      'underpriced',
      'timeout',
      'econnrefused',
      'etimedout'
    ];
    return retryableErrors.some(e => message.includes(e));
  }

  /**
   * Log execution to both memory and file
   * @param {string} executionId - Unique execution ID
   * @param {string} action - Action type
   * @param {string} vaultId - Vault ID
   * @param {string} status - SUCCESS or FAILED
   * @param {Object} details - Additional execution details
   * @returns {Object} Full execution log entry
   */
  logExecution(executionId, action, vaultId, status, details = {}) {
    const logEntry = {
      execution_id: executionId,
      action,
      vault_id: vaultId,
      status,
      details,
      logged_at: new Date().toISOString()
    };

    this.executionLog.push(logEntry);

    // Persist to file
    const logPath = path.join(__dirname, 'execution.log.json');
    try {
      let allLogs = [];
      if (fs.existsSync(logPath)) {
        const content = fs.readFileSync(logPath, 'utf8');
        allLogs = JSON.parse(content || '[]');
      }
      allLogs.push(logEntry);
      
      // Keep last 1000 entries
      if (allLogs.length > 1000) {
        allLogs = allLogs.slice(-1000);
      }
      
      fs.writeFileSync(logPath, JSON.stringify(allLogs, null, 2));
    } catch (error) {
      console.error(`Failed to write execution log: ${error.message}`);
    }

    return logEntry;
  }

  /**
   * Get execution history
   * @param {string} vaultId - Optional filter by vault ID
   * @param {number} limit - Number of recent entries to return
   * @returns {Array} Recent execution entries
   */
  getExecutionHistory(vaultId = null, limit = 50) {
    let history = this.executionLog;
    
    if (vaultId) {
      history = history.filter(e => e.vault_id === vaultId);
    }
    
    return history.slice(-limit);
  }

  /**
   * Estimate gas for a transaction (dry run)
   * @param {string} action - Action type
   * @param {string} vaultId - Vault ID
   * @param {Object} params - Transaction parameters
   * @returns {Object} Gas estimate
   */
  async estimateGas(action, vaultId, params = {}) {
    const contract = this.contracts[vaultId];
    if (!contract) {
      throw new Error(`Contract not initialized: ${vaultId}`);
    }

    try {
      let gasEstimate;
      
      switch (action) {
        case 'DEPOSIT':
          gasEstimate = await contract.estimateGas.deposit(
            ethers.utils.parseEther(params.amount || '0')
          );
          break;
        case 'WITHDRAW':
          gasEstimate = await contract.estimateGas.withdraw(
            ethers.utils.parseEther(params.shares_to_withdraw || '0')
          );
          break;
        case 'HARVEST':
          gasEstimate = await contract.estimateGas.harvest();
          break;
        case 'COMPOUND':
          gasEstimate = await contract.estimateGas.compound(
            ethers.utils.parseEther(params.min_output_amount || '0')
          );
          break;
        default:
          throw new Error(`Cannot estimate gas for ${action}`);
      }

      const gasPrice = await this.provider.getGasPrice();
      const estimatedCost = gasEstimate.mul(gasPrice);

      return {
        action,
        vault_id: vaultId,
        estimated_gas: gasEstimate.toString(),
        gas_price: gasPrice.toString(),
        estimated_cost_eth: ethers.utils.formatEther(estimatedCost),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Gas estimation failed: ${error.message}`);
    }
  }

  /**
   * Get current gas price
   * @returns {Object} Current gas price info
   */
  async getGasPrice() {
    try {
      const gasPrice = await this.provider.getGasPrice();
      return {
        gas_price_wei: gasPrice.toString(),
        gas_price_gwei: ethers.utils.formatUnits(gasPrice, 'gwei'),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get gas price: ${error.message}`);
    }
  }

  /**
   * Generate unique execution ID
   * @returns {string} Unique ID
   */
  generateExecutionId() {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 9);
    return `exec_${timestamp}_${random}`;
  }

  /**
   * Sleep helper
   * @param {number} ms - Milliseconds to sleep
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Clear execution log (caution: destructive)
   */
  clearExecutionLog() {
    this.executionLog = [];
    const logPath = path.join(__dirname, 'execution.log.json');
    try {
      fs.writeFileSync(logPath, '[]');
      console.log('✓ Execution log cleared');
    } catch (error) {
      console.error(`Failed to clear log: ${error.message}`);
    }
  }
}

module.exports = TransactionExecutor;
