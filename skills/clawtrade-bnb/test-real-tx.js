#!/usr/bin/env node
/**
 * Test: Make REAL transactions
 * Verifies integration with actual vault contracts
 */

const fs = require('fs');
const path = require('path');
const DeFiStrategyEngine = require('./defi-strategy-engine-fixed');

// Load config
const deployedConfig = JSON.parse(fs.readFileSync('./config.deployed.json', 'utf8'));
const env = {};
fs.readFileSync('.env', 'utf8').split('\n').forEach(line => {
  const [k, v] = line.split('=');
  if (k && v) env[k.trim()] = v.trim();
});

const PRIVATE_KEY = env.PRIVATE_KEY;
const RPC_URL = deployedConfig.rpc;

async function main() {
  if (!PRIVATE_KEY) {
    console.error('❌ PRIVATE_KEY not in .env');
    process.exit(1);
  }

  console.log(`
╔════════════════════════════════════════════════════════════╗
║         TEST: Real Transactions to BNB Testnet             ║
╠════════════════════════════════════════════════════════════╣
║  Network: ${deployedConfig.network}
║  RPC: ${RPC_URL.slice(0, 40)}...
║  Chain: ${deployedConfig.chainId}
║  Wallet: ${PRIVATE_KEY.slice(0, 10)}...
║  Vaults: ${deployedConfig.contracts.length}
╚════════════════════════════════════════════════════════════╝
  `);

  try {
    // Initialize engine with REAL contract methods
    const engine = new DeFiStrategyEngine(deployedConfig, PRIVATE_KEY, RPC_URL);

    console.log('✓ Engine initialized');
    console.log(`  Vaults loaded: ${engine.vaults.length}`);
    console.log(`  ABI methods: ${engine.abi.filter(a => a.type === 'function').length}`);

    // Run full cycle (will make REAL transactions)
    const results = await engine.executeFullCycle();

    console.log(`\n✅ Test completed`);
    console.log(`  Logs saved to: execution-log.jsonl`);
    console.log(`\n🔍 Check transactions on:`);
    console.log(`  https://testnet.bscscan.com`);

    // Print actual results
    if (results.compound.length > 0) {
      console.log(`\n📋 Compound actions:`);
      results.compound.forEach(r => {
        if (r.status === 'success') {
          console.log(`  ✅ ${r.vault}: ${r.tx}`);
          console.log(`     https://testnet.bscscan.com/tx/${r.tx}`);
        } else {
          console.log(`  ❌ ${r.vault}: ${r.error}`);
        }
      });
    }

    if (results.harvest.length > 0) {
      console.log(`\n🌾 Harvest actions:`);
      results.harvest.forEach(r => {
        console.log(`  ✅ ${r.vault}: ${r.tx}`);
        console.log(`     https://testnet.bscscan.com/tx/${r.tx}`);
      });
    }

    process.exit(0);
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

main();
