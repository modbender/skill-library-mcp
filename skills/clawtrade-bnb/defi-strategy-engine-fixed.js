/**
 * DeFi Strategy Engine - FIXED
 * Real blockchain transactions using actual vault contract methods
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

class DeFiStrategyEngine {
  constructor(deployedConfig, walletPrivateKey, rpcUrl) {
    this.deployedConfig = deployedConfig;
    this.provider = new ethers.providers.JsonRpcProvider(rpcUrl);
    this.wallet = new ethers.Wallet(walletPrivateKey, this.provider);
    this.vaults = deployedConfig.contracts;
    this.abi = deployedConfig.abi;
    this.logFile = path.join(__dirname, 'execution-log.jsonl');
    this.performanceFile = path.join(__dirname, 'performance-metrics.json');
    
    // Initialize performance tracker
    this.performance = this.loadPerformanceMetrics();
  }

  loadPerformanceMetrics() {
    if (fs.existsSync(this.performanceFile)) {
      try {
        return JSON.parse(fs.readFileSync(this.performanceFile, 'utf8'));
      } catch {
        return this.initializePerformance();
      }
    }
    return this.initializePerformance();
  }

  initializePerformance() {
    return {
      startTime: Date.now(),
      totalDeposited: 0,
      totalHarvested: 0,
      totalCompounded: 0,
      vaults: this.vaults.reduce((acc, v) => {
        acc[v.vaultId] = {
          deposits: 0,
          harvested: 0,
          compounded: 0,
          realizedAPR: 0,
          cumulativeYield: 0,
        };
        return acc;
      }, {}),
    };
  }

  savePerformanceMetrics() {
    fs.writeFileSync(this.performanceFile, JSON.stringify(this.performance, null, 2));
  }

  /**
   * STRATEGY 1: Compound Yield
   * Automatically call compound() on vault
   */
  async compoundYieldStrategy() {
    console.log('\n🔄 Executing Compound Yield Strategy...');
    
    const results = [];
    
    for (const vault of this.vaults) {
      try {
        const vaultContract = new ethers.Contract(
          vault.address,
          this.abi,
          this.wallet
        );

        // Check user yield
        const userYield = await vaultContract.calculateUserYield(this.wallet.address);
        const yieldAmount = parseFloat(ethers.utils.formatEther(userYield));

        console.log(`\n📊 ${vault.vaultId}`);
        console.log(`  Pending yield: ${yieldAmount.toFixed(6)} tokens`);

        // Only compound if there's meaningful yield
        if (yieldAmount > 0.001) {
          console.log(`  ⚡ Calling compound()...`);
          
          const tx = await vaultContract.compound({ gasLimit: 200000 });
          console.log(`  📝 TX submitted: ${tx.hash}`);
          
          const receipt = await tx.wait(1);
          console.log(`  ✅ TX confirmed in block ${receipt.blockNumber}`);

          this.logAction({
            action: 'COMPOUND_YIELD',
            vault: vault.vaultId,
            vault_name: vault.name,
            amount_tokens: yieldAmount,
            tx_hash: tx.hash,
            block: receipt.blockNumber,
            confidence: 0.95,
          });

          this.performance.totalCompounded += yieldAmount;
          this.performance.vaults[vault.vaultId].compounded += yieldAmount;

          results.push({
            vault: vault.vaultId,
            status: 'success',
            tx: tx.hash,
            yield: yieldAmount,
          });
        } else {
          console.log(`  ⏸️  Yield too low, skipping`);
        }
      } catch (error) {
        console.error(`❌ Error in ${vault.vaultId}:`, error.message.slice(0, 100));
        
        this.logAction({
          action: 'COMPOUND_ERROR',
          vault: vault.vaultId,
          error: error.message.slice(0, 200),
        });

        results.push({
          vault: vault.vaultId,
          status: 'error',
          error: error.message,
        });
      }
    }

    return results;
  }

  /**
   * STRATEGY 2: Harvest
   * Call harvest() on a vault to claim yield
   */
  async harvestStrategy() {
    console.log('\n🌾 Executing Harvest Strategy...');

    const results = [];

    for (const vault of this.vaults) {
      try {
        const vaultContract = new ethers.Contract(
          vault.address,
          this.abi,
          this.wallet
        );

        // Check yield
        const userYield = await vaultContract.calculateUserYield(this.wallet.address);
        const yieldAmount = parseFloat(ethers.utils.formatEther(userYield));

        if (yieldAmount > 0.001) {
          console.log(`\n✓ ${vault.vaultId}: Harvesting ${yieldAmount.toFixed(6)} tokens`);

          const tx = await vaultContract.harvest({ gasLimit: 200000 });
          console.log(`  TX: ${tx.hash}`);
          
          const receipt = await tx.wait(1);
          console.log(`  ✅ Confirmed`);

          this.logAction({
            action: 'HARVEST',
            vault: vault.vaultId,
            amount_harvested: yieldAmount,
            tx_hash: tx.hash,
            block: receipt.blockNumber,
          });

          this.performance.totalHarvested += yieldAmount;
          this.performance.vaults[vault.vaultId].harvested += yieldAmount;

          results.push({
            vault: vault.vaultId,
            harvested: yieldAmount,
            tx: tx.hash,
          });
        }
      } catch (error) {
        console.error(`❌ Harvest error in ${vault.vaultId}:`, error.message.slice(0, 80));
      }
    }

    return results;
  }

  /**
   * STRATEGY 3: Deposit
   * Deposit tokens into highest-yield vault
   */
  async depositStrategy(depositAmount) {
    console.log('\n💰 Executing Deposit Strategy...');

    try {
      // Find best vault (highest yield)
      const vaultYields = [];

      for (const vault of this.vaults) {
        const vaultContract = new ethers.Contract(vault.address, this.abi, this.provider);
        const info = await vaultContract.getVaultInfo();
        
        vaultYields.push({
          vault,
          yield: parseFloat(ethers.utils.formatEther(info.yield || 0)),
        });
      }

      // Sort by yield (descending)
      vaultYields.sort((a, b) => b.yield - a.yield);
      const bestVault = vaultYields[0];

      console.log(`\n📈 Best vault: ${bestVault.vault.vaultId}`);
      console.log(`  Yield: ${bestVault.yield.toFixed(2)}`);

      // Deposit to best vault
      const vaultContract = new ethers.Contract(
        bestVault.vault.address,
        this.abi,
        this.wallet
      );

      const amountWei = ethers.utils.parseEther(depositAmount.toString());
      console.log(`  Depositing: ${depositAmount} tokens`);

      const tx = await vaultContract.deposit(amountWei, { gasLimit: 200000 });
      console.log(`  TX: ${tx.hash}`);

      const receipt = await tx.wait(1);
      console.log(`  ✅ Confirmed`);

      this.logAction({
        action: 'DEPOSIT',
        vault: bestVault.vault.vaultId,
        amount_deposited: depositAmount,
        tx_hash: tx.hash,
        block: receipt.blockNumber,
      });

      this.performance.totalDeposited += depositAmount;
      this.performance.vaults[bestVault.vault.vaultId].deposits += depositAmount;

      return { status: 'success', tx: tx.hash };
    } catch (error) {
      console.error('❌ Deposit strategy failed:', error.message.slice(0, 100));
      return { status: 'error', error: error.message };
    }
  }

  logAction(data) {
    const record = {
      timestamp: Math.floor(Date.now() / 1000),
      cycle: this.getCycleNumber(),
      wallet: this.wallet.address,
      ...data,
    };

    fs.appendFileSync(this.logFile, JSON.stringify(record) + '\n');
  }

  getCycleNumber() {
    if (!fs.existsSync(this.logFile)) return 1;
    const lines = fs.readFileSync(this.logFile, 'utf8').split('\n').filter(l => l);
    return lines.length + 1;
  }

  async executeFullCycle() {
    console.log(`\n${'═'.repeat(60)}`);
    console.log(`DeFi Strategy Engine - REAL Transactions`);
    console.log(`${new Date().toISOString()}`);
    console.log(`${'═'.repeat(60)}`);

    const cycleResults = {
      timestamp: Date.now(),
      compound: await this.compoundYieldStrategy(),
      harvest: await this.harvestStrategy(),
    };

    this.savePerformanceMetrics();

    console.log(`\n📊 Cycle Summary:`);
    console.log(`  Compound actions: ${cycleResults.compound.length}`);
    console.log(`  Harvest actions: ${cycleResults.harvest.length}`);
    console.log(`  Total Harvested: ${this.performance.totalHarvested.toFixed(6)}`);
    console.log(`  Total Compounded: ${this.performance.totalCompounded.toFixed(6)}`);

    return cycleResults;
  }
}

module.exports = DeFiStrategyEngine;
