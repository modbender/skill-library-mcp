/**
 * BlockchainReader
 * Reads vault data from deployed smart contracts on testnet
 */
const ethers = require('ethers');

class BlockchainReader {
  constructor(rpcUrl = 'https://data-seed-prebsc-1-b.binance.org:8545', config = {}) {
    this.provider = new ethers.providers.JsonRpcProvider(rpcUrl);
    this.config = config;
    this.contracts = {};
  }

  /**
   * Initialize contract instances
   * @param {Array} contracts - Array of contract metadata { address, abi, vaultId }
   */
  async initializeContracts(contracts) {
    for (const contract of contracts) {
      try {
        this.contracts[contract.vaultId] = new ethers.Contract(
          contract.address,
          contract.abi,
          this.provider
        );
        console.log(`✓ Initialized contract: ${contract.vaultId} at ${contract.address}`);
      } catch (error) {
        console.error(`✗ Failed to initialize ${contract.vaultId}:`, error.message);
      }
    }
  }

  /**
   * Get vault information from blockchain
   * @param {string} vaultId - Vault identifier
   * @param {string} userAddress - Optional user address to get user-specific data
   * @returns {Object} Vault data with live balances and yields
   */
  async getVaultData(vaultId, userAddress = null) {
    const contract = this.contracts[vaultId];
    if (!contract) {
      throw new Error(`Contract not initialized: ${vaultId}`);
    }

    try {
      // Get vault info
      const [vaultIdStr, tokenAddr, totalAssets, totalShares] = await contract.getVaultInfo();
      
      let userData = {
        shares: "0",
        amount_usd: "0",
        pending_rewards_usd: "0"
      };

      // Get user-specific data if address provided
      if (userAddress && ethers.utils.isAddress(userAddress)) {
        try {
          const shares = await contract.getShareBalance(userAddress);
          const yieldAmount = await contract.calculateUserYield(userAddress);
          
          userData = {
            shares: shares.toString(),
            amount_usd: ethers.utils.formatEther(totalAssets) || "0", // Simplified: full vault TVL
            pending_rewards_usd: ethers.utils.formatEther(yieldAmount) || "0"
          };
        } catch (e) {
          console.warn(`Could not fetch user data for ${userAddress}:`, e.message);
        }
      }

      return {
        vault_id: vaultIdStr,
        total_assets: ethers.utils.formatEther(totalAssets),
        total_shares: ethers.utils.formatEther(totalShares),
        user_data: userData,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to read vault data for ${vaultId}: ${error.message}`);
    }
  }

  /**
   * Get all vaults data in parallel
   * @param {string} userAddress - Optional user address
   * @returns {Array} Array of vault data objects
   */
  async getAllVaultsData(userAddress = null) {
    const vaultIds = Object.keys(this.contracts);
    
    try {
      const promises = vaultIds.map(vaultId => 
        this.getVaultData(vaultId, userAddress).catch(err => ({
          vault_id: vaultId,
          error: err.message,
          timestamp: new Date().toISOString()
        }))
      );

      const results = await Promise.all(promises);
      return results;
    } catch (error) {
      console.error('Failed to fetch all vaults:', error.message);
      return [];
    }
  }

  /**
   * Listen to ExecutionRecorded events
   * @param {string} vaultId - Vault identifier
   * @param {Function} callback - Callback to execute on event
   * @returns {Function} Listener removal function
   */
  onExecutionRecorded(vaultId, callback) {
    const contract = this.contracts[vaultId];
    if (!contract) {
      throw new Error(`Contract not initialized: ${vaultId}`);
    }

    const listener = (vaultIdLog, action, user, amount, shares, timestamp) => {
      callback({
        vault_id: vaultIdLog,
        action,
        user,
        amount: amount.toString(),
        shares: shares.toString(),
        timestamp: timestamp.toNumber(),
        event_timestamp: new Date().toISOString()
      });
    };

    contract.on('ExecutionRecorded', listener);
    
    // Return cleanup function
    return () => contract.removeListener('ExecutionRecorded', listener);
  }

  /**
   * Simulate deposit action (read-only, no transaction)
   * @param {string} vaultId - Vault identifier
   * @param {string} amount - Amount in wei
   * @returns {Object} Simulation result
   */
  async simulateDeposit(vaultId, amount) {
    const contract = this.contracts[vaultId];
    if (!contract) {
      throw new Error(`Contract not initialized: ${vaultId}`);
    }

    try {
      // This would normally be a static call to estimate output
      // For now, return a mock calculation
      const shares = await contract.calculateSharesFromAssets(amount);
      
      return {
        action: 'DEPOSIT',
        vault_id: vaultId,
        input_amount: amount.toString(),
        estimated_shares: shares.toString(),
        status: 'simulated'
      };
    } catch (error) {
      return {
        action: 'DEPOSIT',
        vault_id: vaultId,
        input_amount: amount.toString(),
        error: error.message,
        status: 'failed'
      };
    }
  }

  /**
   * Simulate harvest action (read-only)
   * @param {string} vaultId - Vault identifier
   * @param {string} userAddress - User address
   * @returns {Object} Simulation result
   */
  async simulateHarvest(vaultId, userAddress) {
    const contract = this.contracts[vaultId];
    if (!contract) {
      throw new Error(`Contract not initialized: ${vaultId}`);
    }

    try {
      if (!ethers.utils.isAddress(userAddress)) {
        throw new Error('Invalid user address');
      }

      const yieldAmount = await contract.calculateUserYield(userAddress);
      
      return {
        action: 'HARVEST',
        vault_id: vaultId,
        user: userAddress,
        harvestable_yield: yieldAmount.toString(),
        status: 'simulated'
      };
    } catch (error) {
      return {
        action: 'HARVEST',
        vault_id: vaultId,
        user: userAddress,
        error: error.message,
        status: 'failed'
      };
    }
  }

  /**
   * Check RPC connectivity
   * @returns {Promise<boolean>} True if connected
   */
  async isConnected() {
    try {
      const blockNumber = await this.provider.getBlockNumber();
      return blockNumber > 0;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get network info
   * @returns {Promise<Object>} Network details
   */
  async getNetworkInfo() {
    try {
      const network = await this.provider.getNetwork();
      const blockNumber = await this.provider.getBlockNumber();
      
      return {
        name: network.name,
        chainId: network.chainId,
        blockNumber,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }
}

module.exports = BlockchainReader;
