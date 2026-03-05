#!/usr/bin/env node
/**
 * Strategy Scheduler
 * Runs DeFi Strategy Engine on schedule with on-chain logging
 */

const fs = require('fs');
const path = require('path');
const DeFiStrategyEngine = require('./defi-strategy-engine');
const OnChainLogger = require('./on-chain-logger');

// Load config
const deployedConfig = JSON.parse(fs.readFileSync('./config.deployed.json', 'utf8'));
const envPath = './.env';
let envConfig = {};
if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const [key, val] = line.split('=');
    if (key && val) envConfig[key.trim()] = val.trim();
  });
}

const PRIVATE_KEY = envConfig.PRIVATE_KEY;
const RPC_URL = envConfig.RPC_URL || deployedConfig.rpc;
const EXECUTION_INTERVAL = 60; // seconds

// Initialize
const engine = new DeFiStrategyEngine(deployedConfig, PRIVATE_KEY, RPC_URL);
const logger = new OnChainLogger(PRIVATE_KEY, RPC_URL);

let cycleNumber = 0;

async function executeCycle() {
  cycleNumber++;
  
  console.log(`\n${'═'.repeat(70)}`);
  console.log(`Strategy Execution Cycle #${cycleNumber}`);
  console.log(`${new Date().toISOString()}`);
  console.log(`${'═'.repeat(70)}`);

  try {
    // Run all strategies
    const results = await engine.executeFullCycle();

    // Log to blockchain
    if (results.compound.length > 0) {
      for (const action of results.compound) {
        await logger.logAction('COMPOUND_YIELD', action.vault, action.rewards);
      }
    }

    if (results.rebalance.status === 'success') {
      await logger.logAction('REBALANCE', results.rebalance.from || 'portfolio', 0);
    }

    if (results.harvest.length > 0) {
      for (const action of results.harvest) {
        await logger.logAction('DYNAMIC_HARVEST', action.vault, action.harvested);
      }
    }

    console.log(`\n✅ Cycle #${cycleNumber} completed successfully`);
    console.log(`  Next cycle in ${EXECUTION_INTERVAL}s`);
    
  } catch (error) {
    console.error(`\n❌ Cycle #${cycleNumber} failed:`, error.message);
    
    // Log error
    engine.logAction({
      action: 'CYCLE_ERROR',
      vault: 'system',
      error: error.message,
      cycle: cycleNumber,
    });
  }
}

// Scheduler
async function startScheduler() {
  console.log(`
╔═══════════════════════════════════════════════════════════════════╗
║  DeFi Strategy Scheduler - LIVE                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  Engine: ${deployedConfig.network}
║  Wallet: ${PRIVATE_KEY ? PRIVATE_KEY.slice(0, 10) + '...' : 'Not loaded'}
║  RPC: ${RPC_URL.slice(0, 40)}...
║  Strategies: Compound Yield, Rebalance, Dynamic Harvest           ║
║  Cycle Interval: ${EXECUTION_INTERVAL}s                           ║
║  On-Chain Logging: ENABLED                                        ║
╚═══════════════════════════════════════════════════════════════════╝
  `);

  if (!PRIVATE_KEY) {
    console.error('❌ PRIVATE_KEY not found in .env');
    process.exit(1);
  }

  // Execute immediately
  await executeCycle();

  // Schedule
  setInterval(executeCycle, EXECUTION_INTERVAL * 1000);
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log(`\n\n🛑 Strategy Scheduler Shutting Down`);
  console.log(`📊 Total Cycles: ${cycleNumber}`);
  console.log(`💰 Total Harvested: $${engine.performance.totalHarvested.toFixed(2)}`);
  console.log(`⚙️ Total Compounded: $${engine.performance.totalCompounded.toFixed(2)}`);
  process.exit(0);
});

// Start
if (require.main === module) {
  startScheduler().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}

module.exports = { engine, logger, executeCycle };
